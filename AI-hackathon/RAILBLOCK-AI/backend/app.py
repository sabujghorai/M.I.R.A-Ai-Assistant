from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from backend.priority import calculate_priority
from backend.optimizer import find_best_block


# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)
CORS(app)


# =========================================
# LOAD RAILWAY DATA
# =========================================

maintenance_data = pd.read_csv("data/maintenance.csv")
train_data = pd.read_csv("data/trains.csv")


# The base weekly schedule. Submitted requests are appended to this
# at read time in /api/schedule — they used to be tracked in a
# separate list that /api/schedule never looked at, so new requests
# never appeared anywhere.
BASE_SCHEDULE = [
    {
        "day": "Monday",
        "department": "Engineering",
        "section": "SDAH-BWN",
        "block_time": "10:00 - 12:00",
        "priority": "High"
    },
    {
        "day": "Tuesday",
        "department": "Signal & Telecom",
        "section": "BWN-KNJ",
        "block_time": "14:00 - 16:00",
        "priority": "Medium"
    },
    {
        "day": "Wednesday",
        "department": "Traction Distribution",
        "section": "KNJ-CPLE",
        "block_time": "09:00 - 11:00",
        "priority": "High"
    },
    {
        "day": "Friday",
        "department": "Engineering",
        "section": "CPLE-RHA",
        "block_time": "13:00 - 15:00",
        "priority": "Low"
    }
]

# Store maintenance requests submitted from the frontend.
# Each item: department, section, issue, priority, and — once the
# optimizer has run for it — day / block_time.
requests_data = []


# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return jsonify({
        "system": "RAILBLOCK AI",
        "status": "Running"
    })


# =========================================
# DASHBOARD API
# =========================================

@app.route("/api/dashboard")
def dashboard():

    unscheduled_count = sum(
        1 for r in requests_data if "block_time" not in r
    )

    return jsonify({
        "pending_count": unscheduled_count,
        "blocks_available": 8,
        "asset_uptime": 92
    })


# =========================================
# BLOCK SCHEDULE API
# =========================================

@app.route("/api/schedule")
def schedule():

    schedule_data = list(BASE_SCHEDULE)

    # Include every submitted request. Ones the optimizer has already
    # assigned a slot to show their real day/time; the rest show as
    # Unscheduled so it's clear they're still waiting.
    for r in requests_data:
        schedule_data.append({
            "day": r.get("day", "Unscheduled"),
            "department": r["department"],
            "section": r["section"],
            "block_time": r.get("block_time", "TBD"),
            "priority": r["priority"]
        })

    return jsonify(schedule_data)


# =========================================
# ADD MAINTENANCE REQUEST
# =========================================

@app.route("/api/requests", methods=["POST"])
def add_request():

    data = request.get_json()

    # Check if data was received
    if not data:
        return jsonify({
            "message": "No request data received."
        }), 400

    # Get values from frontend
    department = data.get("department")
    section = data.get("section")
    issue = data.get("issue")
    priority = data.get("priority")

    # Validate required fields
    if not department or not section or not issue or not priority:

        return jsonify({
            "message": "All fields are required."
        }), 400

    # Create maintenance request
    new_request = {
        "department": department,
        "section": section,
        "issue": issue,
        "priority": priority
    }

    # Store request
    requests_data.append(new_request)

    return jsonify({
        "message": "Maintenance request added successfully.",
        "request": new_request
    }), 201


# =========================================
# AI BLOCK OPTIMIZER
# =========================================

@app.route("/api/optimize", methods=["POST"])
def optimize():

    # Work on the oldest request that hasn't been scheduled yet.
    # The old version always grabbed requests_data[-1] (the newest
    # one), so re-running the optimizer kept re-scheduling the same
    # latest request and older pending ones were never reached.
    unscheduled = [r for r in requests_data if "block_time" not in r]

    if not unscheduled:
        return jsonify({
            "message": "No unscheduled maintenance requests available."
        }), 400

    target_request = unscheduled[0]

    section = target_request["section"]
    priority = target_request["priority"]

    # -------------------------------------
    # Calculate priority score
    # -------------------------------------

    priority_score = calculate_priority(priority)

    # -------------------------------------
    # Find trains on requested section
    # -------------------------------------

    section_trains = train_data[
        train_data["section"] == section
    ]

    train_times = section_trains["time"].tolist()

    # -------------------------------------
    # Find best maintenance block
    # -------------------------------------

    # For now, maintenance duration
    # is assumed to be 2 hours.
    result = find_best_block(
        2,
        train_times
    )

    # -------------------------------------
    # If no block is available
    # -------------------------------------

    if result is None:

        return jsonify({
            "message": f"No suitable block found for section {section}."
        }), 400

    # -------------------------------------
    # Persist the result — this is the part that used to be missing.
    # Without it, /api/schedule had no way of knowing a slot had
    # been assigned, so the row stayed "Unscheduled / TBD" forever.
    # -------------------------------------

    target_request["block_time"] = f"{result['start']} - {result['end']}"
    target_request["day"] = "Pending confirmation"

    # -------------------------------------
    # Send result to frontend
    # -------------------------------------

    return jsonify({

        "message":
            "AI optimization completed successfully.",

        "section":
            section,

        "priority":
            priority,

        "priority_score":
            priority_score,

        "recommended_block":
            target_request["block_time"],

        "conflicts":
            result["conflicts"]
    })



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )