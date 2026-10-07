from datetime import datetime
import os
import platform
import socket
import threading

from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "Karan DevOps Dashboard")
APP_VERSION = os.getenv("APP_VERSION", "3.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "Development")

MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "karan_dashboard")

_mongo_client = None
_mongo_init_lock = threading.Lock()
_db_initialized = False


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "environment": ENVIRONMENT,
    }


def get_mongo_client():
    global _mongo_client

    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is not configured")

    if _mongo_client is None:
        with _mongo_init_lock:
            if _mongo_client is None:
                _mongo_client = MongoClient(
                    MONGO_URI,
                    server_api=ServerApi(
                        version="1",
                        strict=True,
                        deprecation_errors=True,
                    ),
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                )

    return _mongo_client


def get_db():
    return get_mongo_client()[MONGO_DB_NAME]


def initialize_database():
    global _db_initialized

    if _db_initialized:
        return

    with _mongo_init_lock:
        if _db_initialized:
            return

        db = get_db()

        skills = [
            ("Linux", 82),
            ("Git & GitHub", 78),
            ("Docker", 80),
            ("Jenkins", 70),
            ("Kubernetes", 68),
            ("Bash Scripting", 74),
            ("Python", 72),
            ("MongoDB", 70),
        ]

        for name, level in skills:
            db.skills.update_one(
                {"name": name},
                {"$set": {"name": name, "level": level}},
                upsert=True,
            )

        pipeline = [
            (1, "Checkout", "success", "Source code downloaded from GitHub"),
            (2, "Syntax Check", "success", "Python syntax validated"),
            (3, "Unit Tests", "success", "Application unit tests executed"),
            (4, "Docker Build", "success", "Docker image built successfully"),
            (5, "Docker Push", "success", "Docker image pushed to Docker Hub"),
            (6, "Kubernetes Deploy", "success", "Application deployed to Kubernetes"),
            (7, "Health Check", "success", "Application health endpoint verified"),
        ]

        for order, stage, status, description in pipeline:
            db.pipeline_stages.update_one(
                {"stage_order": order},
                {
                    "$set": {
                        "stage_order": order,
                        "stage": stage,
                        "status": status,
                        "description": description,
                    }
                },
                upsert=True,
            )

        _db_initialized = True


def check_database():
    get_mongo_client().admin.command("ping")
    return True


@app.route("/")
def home():
    return render_template(
        "index.html",
        app_name=APP_NAME,
        version=APP_VERSION,
        environment=ENVIRONMENT,
        year=datetime.now().year,
    )


@app.route("/api/status")
def api_status():
    try:
        database_status = "connected" if check_database() else "disconnected"
    except (PyMongoError, RuntimeError):
        database_status = "disconnected"

    return jsonify({
        "app": APP_NAME,
        "status": "running",
        "health": "healthy" if database_status == "connected" else "degraded",
        "database": database_status,
        "database_type": "MongoDB Atlas",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
    })


@app.route("/api/skills")
def api_skills():
    try:
        initialize_database()
        skills = list(
            get_db().skills.find(
                {},
                {"_id": 0, "name": 1, "level": 1},
            ).sort("name", 1)
        )
        return jsonify({"skills": skills})
    except (PyMongoError, RuntimeError):
        return jsonify({"error": "MongoDB is not available"}), 503


@app.route("/api/pipeline")
def api_pipeline():
    try:
        initialize_database()
        pipeline = list(
            get_db().pipeline_stages.find(
                {},
                {"_id": 0, "stage": 1, "status": 1, "description": 1},
            ).sort("stage_order", 1)
        )
        return jsonify({"pipeline": pipeline})
    except (PyMongoError, RuntimeError):
        return jsonify({"error": "MongoDB is not available"}), 503


@app.route("/health")
def health():
    try:
        initialize_database()
        check_database()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "database_type": "MongoDB Atlas",
            "service": "karan-devops-dashboard",
            "version": APP_VERSION,
        }), 200
    except (PyMongoError, RuntimeError):
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "database_type": "MongoDB Atlas",
            "service": "karan-devops-dashboard",
            "version": APP_VERSION,
        }), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
