attendees = {
    "A001": {"name": "Alice", "checked_in": False},
    "A002": {"name": "Bob", "checked_in": False},
    "A003": {"name": "Charlie", "checked_in": False},
}


def print_badge(attendee):
    print(f"Sending badge print request for {attendee['name']}...")
    print("Waiting for printer response...")

    # Simulated synchronous printer response
    print("Printer response: SUCCESS")
    return True


def check_in(qr_code):
    attendee = attendees.get(qr_code)

    if attendee is None:
        print("Unknown attendee.")
        return

    if attendee["checked_in"]:
        print(f"{attendee['name']} is already checked in.")
        print("No second badge will be printed.")
        return

    print(f"QR scan received for {attendee['name']}.")

    success = print_badge(attendee)

    if success:
        attendee["checked_in"] = True
        print(f"{attendee['name']}: Checked In")
    else:
        print(f"{attendee['name']}: Check-in failed.")


# Test attendees
check_in("A001")
print()

check_in("A002")
print()

check_in("A003")
print()

# Duplicate scan test
check_in("A001")