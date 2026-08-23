import redis
import json
import urllib.request

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

STREAM_NAME = "print-requests"


def send_webhook(attendee_id, attendee_name):
    url = "http://localhost:5000/webhook"

    data = json.dumps({
        "attendee_id": attendee_id,
        "status": "printed"
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request) as response:
            print(f"Webhook sent for {attendee_name}: {response.status}")
    except Exception as e:
        print(f"Webhook failed for {attendee_name}: {e}")


print("Printer worker started.")
print("Waiting for print requests...")

last_id = "0-0"

while True:
    try:
        messages = r.xread(
            {STREAM_NAME: last_id},
            count=1,
            block=5000
        )

        if not messages:
            continue

        for stream, entries in messages:
            for message_id, data in entries:
                last_id = message_id

                attendee_id = data["attendee_id"]
                attendee_name = data["attendee_name"]

                print(f"Received print request for {attendee_name}.")
                print("Simulating badge printing...")
                print("Badge printed successfully.")

                send_webhook(attendee_id, attendee_name)

    except redis.exceptions.TimeoutError:
        print("Redis read timed out. Continuing to wait...")
        continue