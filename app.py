import os
import re
import uuid
from datetime import date, datetime, timezone

from dotenv import load_dotenv
from flask import Flask, current_app, jsonify, render_template, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Karan TrailQuest")
APP_VERSION = os.getenv("APP_VERSION", "3.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "karan_trailquest")

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^\d{10}$")

TOURS = [
    {"slug":"manali","name":"Manali","state":"Himachal Pradesh","duration":"4 Nights / 5 Days","price":"₹7,999","best_time":"March–June & October–January","activities":["Trekking","Paragliding","River Rafting","Camping"],"includes":["Hotel stay","Breakfast","Local sightseeing","Selected adventure activities"],"summary":"Snowy peaks, riverside cafés and high-energy mountain adventures.","image":"https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=80"},
    {"slug":"ladakh","name":"Ladakh","state":"Ladakh","duration":"5 Nights / 6 Days","price":"₹14,999","best_time":"May–September","activities":["Bike expedition","Pangong visit","Monastery trail","Stargazing"],"includes":["Hotel/camp stay","Breakfast","Local transfers","Sightseeing plan"],"summary":"High-altitude roads, blue lakes and dramatic Himalayan landscapes.","image":"https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=1200&q=80"},
    {"slug":"rishikesh","name":"Rishikesh","state":"Uttarakhand","duration":"2 Nights / 3 Days","price":"₹4,999","best_time":"September–June","activities":["River rafting","Bungee jumping","Camping","Ganga aarti"],"includes":["Camp stay","Breakfast","Rafting session","Local assistance"],"summary":"River adventures, forest camps and spiritual energy by the Ganga.","image":"https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=80"},
    {"slug":"kashmir","name":"Kashmir","state":"Jammu & Kashmir","duration":"4 Nights / 5 Days","price":"₹11,999","best_time":"March–October","activities":["Gondola ride","Shikara ride","Valley sightseeing","Photography"],"includes":["Hotel stay","Breakfast","Local sightseeing","Airport assistance"],"summary":"Alpine valleys, lakes, meadows and unforgettable mountain scenery.","image":"https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80"},
    {"slug":"auli","name":"Auli","state":"Uttarakhand","duration":"3 Nights / 4 Days","price":"₹9,499","best_time":"December–March","activities":["Skiing","Chairlift","Snow trek","Mountain views"],"includes":["Hotel stay","Breakfast","Local transfers","Skiing orientation"],"summary":"A compact snow adventure with ski slopes and Himalayan panoramas.","image":"https://images.unsplash.com/photo-1454496522488-7a8e488e8606?auto=format&fit=crop&w=1200&q=80"},
    {"slug":"spiti-valley","name":"Spiti Valley","state":"Himachal Pradesh","duration":"6 Nights / 7 Days","price":"₹16,999","best_time":"May–October","activities":["Road trip","Village trail","Monastery visit","Night photography"],"includes":["Stay","Breakfast","Route assistance","Sightseeing plan"],"summary":"Remote mountain villages, monasteries and rugged trans-Himalayan roads.","image":"https://images.unsplash.com/photo-1486911278844-a81c5267e227?auto=format&fit=crop&w=1200&q=80"}
]

ALLOWED_DESTINATIONS = {tour["name"] for tour in TOURS}
_mongo_client = None

def get_database():
    global _mongo_client
    mongo_uri = os.getenv("MONGO_URI", "").strip()
    if not mongo_uri or mongo_uri == "YOUR_MONGODB_ATLAS_URI":
        raise RuntimeError("MONGO_URI is not configured")
    if _mongo_client is None:
        _mongo_client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            retryWrites=True,
        )
    return _mongo_client[os.getenv("MONGO_DB_NAME", MONGO_DB_NAME)]

def get_bookings_collection():
    injected = current_app.config.get("BOOKINGS_COLLECTION")
    if injected is not None:
        return injected
    return get_database()["bookings"]

def validate_booking(payload):
    errors = {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    phone = re.sub(r"\s+", "", str(payload.get("phone", "")).strip())
    destination = str(payload.get("destination", "")).strip()
    custom_destination = str(payload.get("custom_destination", "")).strip()
    travel_date_raw = str(payload.get("travel_date", "")).strip()
    message = str(payload.get("message", "")).strip()

    if len(name) < 2 or len(name) > 80:
        errors["name"] = "Name must be between 2 and 80 characters."
    if not EMAIL_PATTERN.fullmatch(email):
        errors["email"] = "Enter a valid email address, for example name@example.com."
    if not PHONE_PATTERN.fullmatch(phone):
        errors["phone"] = "Phone number must contain exactly 10 digits."

    if destination == "Other / Custom Destination":
        if len(custom_destination) < 2 or len(custom_destination) > 60:
            errors["custom_destination"] = "Enter a custom destination between 2 and 60 characters."
        final_destination = custom_destination
    elif destination in ALLOWED_DESTINATIONS:
        final_destination = destination
    else:
        final_destination = destination
        errors["destination"] = "Please select a valid destination."

    try:
        travelers = int(payload.get("travelers", 0))
        if not 1 <= travelers <= 30:
            errors["travelers"] = "Travelers must be between 1 and 30."
    except (TypeError, ValueError):
        travelers = 0
        errors["travelers"] = "Please select a valid number of travelers."

    try:
        parsed_date = date.fromisoformat(travel_date_raw)
        if parsed_date < date.today():
            errors["travel_date"] = "Travel date cannot be in the past."
    except ValueError:
        parsed_date = None
        errors["travel_date"] = "Please select a valid travel date."

    if len(message) > 500:
        errors["message"] = "Message cannot exceed 500 characters."

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "destination": final_destination,
        "travelers": travelers,
        "travel_date": parsed_date.isoformat() if parsed_date else travel_date_raw,
        "message": message,
    }, errors

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(APP_NAME=APP_NAME, APP_VERSION=APP_VERSION, ENVIRONMENT=ENVIRONMENT)
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def index():
        return render_template("index.html", tours=TOURS, app_name=app.config["APP_NAME"], app_version=app.config["APP_VERSION"])

    @app.get("/health")
    def health():
        return jsonify(status="healthy", app=app.config["APP_NAME"], version=app.config["APP_VERSION"], environment=app.config["ENVIRONMENT"]), 200

    @app.get("/ready")
    def ready():
        try:
            get_database().command("ping")
            return jsonify(status="ready", database="connected"), 200
        except Exception as exc:
            app.logger.warning("Readiness check failed: %s", type(exc).__name__)
            return jsonify(status="not_ready", database="unavailable"), 503

    @app.get("/api/tours")
    def api_tours():
        return jsonify({"status":"success","tours":TOURS}), 200

    @app.post("/api/bookings")
    def create_booking():
        payload = request.get_json(silent=True) or {}
        booking, errors = validate_booking(payload)
        if errors:
            return jsonify({"status":"error","message":"Please correct the form.","errors":errors}), 400

        booking["booking_reference"] = f"TQ-{uuid.uuid4().hex[:8].upper()}"
        booking["status"] = "pending"
        booking["created_at"] = datetime.now(timezone.utc)

        try:
            result = get_bookings_collection().insert_one(booking)
        except (PyMongoError, RuntimeError) as exc:
            app.logger.error("Booking save failed: %s", type(exc).__name__)
            return jsonify({"status":"error","message":"Booking service is temporarily unavailable."}), 503

        return jsonify({
            "status":"success",
            "message":"Your adventure request has been received.",
            "booking_reference":booking["booking_reference"],
            "id":str(result.inserted_id),
        }), 201

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "0") == "1")
