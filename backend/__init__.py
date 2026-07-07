from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# =========================
# INITIALIZE EXTENSIONS
# =========================
db = SQLAlchemy()


# =========================
# CREATE APP
# =========================
def create_app():
    app = Flask(__name__)

    # =========================
    # CORS CONFIGURATION
    # Sessions need credentials support to work across requests
    # =========================
    CORS(app, supports_credentials=True)

    # =========================
    # PROJECT PATHS
    # =========================
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(
        basedir,
        "..",
        "instance",
        "SmartFarmScan.db"
    )

    # =========================
    # DATABASE CONFIGURATION
    # =========================
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + db_path
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # =========================
    # SECRET KEY (required for sessions/login to work)
    # =========================
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        "SmartFarmScan_secret_key"
    )

    # =========================
    # SESSION COOKIE CONFIG (needed for frontend fetch() with credentials)
    # =========================
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False  # set True only when using HTTPS

    # =========================
    # INITIALIZE DATABASE
    # =========================
    db.init_app(app)

    # =========================
    # IMPORT MODELS
    # =========================
    from backend.models.scan_model import Scan
    from backend.models.farmer_model import Farmer

    # =========================
    # CREATE DATABASE TABLES
    # =========================
    with app.app_context():
        db.create_all()

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    from backend.routes.scan_route import scan
    app.register_blueprint(
        scan,
        url_prefix="/api/scans"
    )

    from backend.routes.auth_route import auth
    app.register_blueprint(
        auth,
        url_prefix="/api/auth"
    )

    # =========================
    # HOME ROUTE
    # =========================
    @app.route("/")
    def home():
        return {
            "status": "success",
            "message": "Smart Farm Scanner API is running."
        }

    return app