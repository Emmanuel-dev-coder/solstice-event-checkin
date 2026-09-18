from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

STREAM_NAME = "print-requests"

attendees = {
    "A001": {"name": "Alice", "status": "NOT_CHECKED_IN"},
    "A002": {"name": "Bob", "status": "NOT_CHECKED_IN"},
    "A003": {"name": "Charlie", "status": "NOT_CHECKED_IN"},
    "A004": {"name":"Kelvin","status":"NOT_CHECKED_IN"},
}


@app.route("/check-in/<attendee_id>", methods=["POST"])
def check_in(attendee_id):
    attendee = attendees.get(attendee_id)

    if attendee is None:
        return jsonify({"error": "Unknown attendee"}), 404

    # Prevent duplicate badges
    if attendee["status"] in ["PENDING", "CHECKED_IN"]:
        return jsonify({
            "message": f"{attendee['name']} is already being processed or checked in.",
            "status": attendee["status"]
        }), 200

    # Mark as pending before sending the print request
    attendee["status"] = "PENDING"

    message_id = r.xadd(
        STREAM_NAME,
        {
            "attendee_id": attendee_id,
            "attendee_name": attendee["name"]
        }
    )

    print(
        f"{attendee['name']} is PENDING. "
        f"Print request queued: {message_id}"
    )

    return jsonify({
        "attendee": attendee["name"],
        "status": "PENDING",
        "message_id": message_id
    }), 202


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    attendee_id = data.get("attendee_id")
    status = data.get("status")

    attendee = attendees.get(attendee_id)

    if attendee is None:
        return jsonify({"error": "Unknown attendee"}), 404

    if status == "printed":
        attendee["status"] = "CHECKED_IN"

        print(
            f"Webhook received for {attendee['name']}. "
            f"Status changed to CHECKED_IN."
        )

    return jsonify({
        "message": "Webhook processed",
        "attendee": attendee["name"],
        "status": attendee["status"]
    }), 200


@app.route("/status/<attendee_id>", methods=["GET"])
def status(attendee_id):
    attendee = attendees.get(attendee_id)

    if attendee is None:
        return jsonify({"error": "Unknown attendee"}), 404

    return jsonify({
        "attendee": attendee["name"],
        "status": attendee["status"]
    })


if __name__ == "__main__":
    print("Solstice check-in application started.")
    print("Webhook available at http://localhost:5000/webhook")
    app.run(host="localhost", port=5000)