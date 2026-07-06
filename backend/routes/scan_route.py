from flask import Blueprint, request, jsonify
from datetime import date
from werkzeug.utils import secure_filename
import os
import uuid
import json

from backend import db
from backend.models.scan_model import Scan

# =====================================
# BLUEPRINT
# =====================================
scan = Blueprint("scan", __name__)

# =====================================
# UPLOAD FOLDER SETUP
# =====================================
UPLOAD_FOLDER = os.path.join("backend", "static", "uploads")
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_VIDEO_EXT = {"mp4", "mov", "avi", "webm"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, allowed_extensions):
    """Saves a single uploaded file with a unique name, returns its relative URL path."""
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename, allowed_extensions):
        return None

    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)

    # Stored as a path the frontend can request via Flask's static route
    return f"/static/uploads/{unique_name}"


# =====================================
# CREATE A NEW SCAN
# AI --> Backend
# POST: /api/scans
# Accepts multipart/form-data (text fields + video + multiple images)
# =====================================
@scan.route("", methods=["POST"])
def create_scan():

    # ---------- READ TEXT FIELDS (from form-data, not JSON) ----------
    crop_type = request.form.get("crop_type")
    status = request.form.get("status")
    disease_name = request.form.get("disease_name") or None
    severity = request.form.get("severity") or None
    confidence = request.form.get("confidence")
    recommendation = request.form.get("recommendation") or None
    temperature = request.form.get("temperature") or None
    humidity = request.form.get("humidity") or None
    soil_moisture = request.form.get("soil_moisture") or None
    location = request.form.get("location") or None
    rover_id = request.form.get("rover_id") or None

    # ---------- BASIC VALIDATION ----------
    if not crop_type or not status or not confidence:
        return jsonify({
            "status": "error",
            "message": "Missing required fields: crop_type, status, confidence."
        }), 400

    # ---------- HANDLE VIDEO UPLOAD (single file) ----------
    video_file = request.files.get("video")
    video_url = save_uploaded_file(video_file, ALLOWED_VIDEO_EXT) if video_file else None

    # ---------- HANDLE IMAGE UPLOADS (multiple files) ----------
    image_files = request.files.getlist("images")
    saved_image_urls = []
    for img in image_files:
        saved_url = save_uploaded_file(img, ALLOWED_IMAGE_EXT)
        if saved_url:
            saved_image_urls.append(saved_url)

    # First image stays in image_url for backward compatibility.
    # ALL images get stored as a JSON string in image_urls.
    image_url = saved_image_urls[0] if saved_image_urls else None
    image_urls_json = json.dumps(saved_image_urls) if saved_image_urls else None

    # ---------- CREATE AND SAVE SCAN ----------
    new_scan = Scan(
        crop_type=crop_type,
        status=status,
        disease_name=disease_name,
        severity=severity,
        confidence=float(confidence),
        image_url=image_url,
        image_urls=image_urls_json,
        video_url=video_url,
        temperature=float(temperature) if temperature else None,
        humidity=float(humidity) if humidity else None,
        soil_moisture=float(soil_moisture) if soil_moisture else None,
        recommendation=recommendation,
        location=location,
        rover_id=rover_id
    )

    db.session.add(new_scan)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Scan saved successfully.",
        "scan": new_scan.to_dict()
    }), 201


# =====================================
# GET TODAY'S SCANS
# Dashboard --> Backend
# GET: /api/scans/today
# =====================================
@scan.route("/today", methods=["GET"])
def get_today_scans():
    today = date.today()

    scans = (
        Scan.query
        .filter(db.func.date(Scan.timestamp) == today)
        .order_by(Scan.timestamp.desc())
        .all()
    )

    return jsonify({
        "status": "success",
        "total_scans": len(scans),
        "scans": [scan.to_dict() for scan in scans]
    })


# =====================================
# GET A SINGLE SCAN
# Dashboard --> Backend
# GET: /api/scans/<scan_id>
# =====================================
@scan.route("/<int:scan_id>", methods=["GET"])
def get_scan(scan_id):
    scan_data = Scan.query.get_or_404(scan_id)

    return jsonify({
        "status": "success",
        "scan": scan_data.to_dict()
    })


# =====================================
# GET SCAN HISTORY
# Dashboard --> Backend
# GET: /api/scans/history
# =====================================
@scan.route("/history", methods=["GET"])
def get_history():
    scans = (
        Scan.query
        .order_by(Scan.timestamp.desc())
        .all()
    )

    return jsonify({
        "status": "success",
        "total_records": len(scans),
        "history": [scan.to_dict() for scan in scans]
    })