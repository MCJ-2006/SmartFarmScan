from datetime import datetime
import json
from backend import db


class Scan(db.Model):
    __tablename__ = "scans"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # Scan Timestamp
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Crop Information
    crop_type = db.Column(db.String(50), nullable=False)

    # Scan Result
    status = db.Column(db.String(20), nullable=False)  # healthy | diseased

    disease_name = db.Column(db.String(100), nullable=True)

    severity = db.Column(db.String(20), nullable=True)  # low | medium | high

    confidence = db.Column(db.Float, nullable=False)

    # Media
    image_url = db.Column(db.String(255), nullable=True)   # first image (kept for backward compatibility)
    image_urls = db.Column(db.Text, nullable=True)          # JSON list of ALL image URLs
    video_url = db.Column(db.String(255), nullable=True)

    # Environmental Data
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    soil_moisture = db.Column(db.Float, nullable=True)

    # AI Recommendation
    recommendation = db.Column(db.Text, nullable=True)

    # Scan Location
    location = db.Column(db.String(100), nullable=True)

    # Future Support (Multiple Rovers)
    rover_id = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        # Decode the stored JSON string back into a real list for the frontend
        try:
            images_list = json.loads(self.image_urls) if self.image_urls else []
        except (TypeError, ValueError):
            images_list = []

        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "crop_type": self.crop_type,
            "status": self.status,
            "disease_name": self.disease_name,
            "severity": self.severity,
            "confidence": self.confidence,
            "image_url": self.image_url,
            "images": images_list,
            "video_url": self.video_url,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "soil_moisture": self.soil_moisture,
            "recommendation": self.recommendation,
            "location": self.location,
            "rover_id": self.rover_id
        }

    def __repr__(self):
        return (
            f"<Scan {self.id}: "
            f"{self.crop_type} | "
            f"{self.status}>"
        )