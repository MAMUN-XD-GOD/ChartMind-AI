import json
import os

FEEDBACK_FILE = "temp_uploads/feedback.json"
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f)

def record_feedback(signal_id, result):
    """ Record user feedback: Win or Loss """
    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)

    feedback_data.append({"signal_id": signal_id, "result": result})

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_data, f, indent=4)

def compute_accuracy(signal_id=None):
    """ Compute accuracy % for all signals or a specific signal """
    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)

    total = 0
    wins = 0

    for entry in feedback_data:
        if signal_id is None or entry["signal_id"] == signal_id:
            total += 1
            if entry["result"].lower() == "win":
                wins += 1

    return round((wins / total) * 100, 2) if total > 0 else 0.0
