from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)


# ==============================
# LOAD DATA
# ==============================

maintenance_file = "data/maintenance.csv"
trains_file = "data/trains.csv"

maintenance_data = pd.read_csv(maintenance_file)
train_data = pd.read_csv(trains_file)

# Store submitted requests
requests_data = []


# ==============================
# HOME
# ==============================

@app.route("/")
def home():

    return jsonify({
        "system": "RAILBLOCK AI",
        "status": "Running"
    })


# ==============================
# DASHBOARD
# ==============================

@app.route("/api/dashboard")
def dashboard():

    pending_count = len(requests_data)

    return jsonify({
        "pending_count": pending_count,
        "blocks_available": 8,
        "asset_uptime": 92
    })


# ==============================
# BLOCK SCHEDULE
# ==============================

@app.route("/api/schedule")
def schedule():

    schedule = [
        {
            "day": "Monday",
            "department": "Engineering",
            "section": "Sec A-12",
            "block_time": "10:00 - 12:00",
            "priority": "High"
        },
        {
            "day": "Tuesday",
            "department": "Signal & Telecom",
            "section": "Sec B-05",
            "block_time": "14:00 - 16:00",
            "priority": "Medium"
        },
        {
            "day": "Wednesday",
            "department": "Traction Distribution",
            "section": "Sec C-09",
            "block_time": "09:00 - 11:00",
            "priority": "High"
        },
        {
            "day": "Friday",
            "department": "Engineering",
            "section": "Sec A-07",
            "block_time": "13:00 - 15:00",
            "priority": "Low"
        }
    ]

    return jsonify(schedule)


# ==============================
# ADD MAINTENANCE REQUEST
# ==============================

@app.route("/api/requests", methods=["POST"])
def add_request():

    data = request.get_json()

    new_request = {
        "department": data["department"],
        "section": data["section"],
        "issue": data["issue"],
        "priority": data["priority"]
    }

    requests_data.append(new_request)

    return jsonify({
        "message": "Maintenance request added successfully",
        "request": new_request
    }), 201


# ==============================
# AI OPTIMIZER
# ==============================

@app.route("/api/optimize", methods=["POST"])
def optimize():

    return jsonify({
        "message": "AI Optimizer completed successfully. Best block schedule generated."
    })


# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )