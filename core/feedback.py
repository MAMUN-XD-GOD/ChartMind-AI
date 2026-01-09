import json
import os
from datetime import datetime

FEEDBACK_FILE = "temp_uploads/feedback.json"
os.makedirs("temp_uploads", exist_ok=True)

# Ensure feedback file exists
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f)

def record_feedback(signal_id, market, pair, result):
    """ Record user feedback: Win or Loss """
    feedback_entry = {
        "signal_id": signal_id,
        "market": market,
        "pair": pair,
        "result": result.lower(),
        "timestamp": str(datetime.now())
    }

    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)

    feedback_data.append(feedback_entry)

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback_data, f, indent=4)

def compute_accuracy(signal_id=None, market=None, pair=None):
    """
    Compute accuracy % for all signals or filtered by signal_id/market/pair
    Returns float % value
    """
    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)

    total = 0
    wins = 0

    for entry in feedback_data:
        if (signal_id is None or entry["signal_id"] == signal_id) and \
           (market is None or entry["market"] == market) and \
           (pair is None or entry["pair"] == pair):
            total += 1
            if entry["result"] == "win":
                wins += 1

    return round((wins / total) * 100, 2) if total > 0 else 0.0

def get_feedback_stats():
    """ Return summary stats by market/pair """
    with open(FEEDBACK_FILE, "r") as f:
        feedback_data = json.load(f)

    stats = {}
    for entry in feedback_data:
        key = f"{entry['market']}|{entry['pair']}"
        if key not in stats:
            stats[key] = {"total":0, "wins":0}
        stats[key]["total"] += 1
        if entry["result"] == "win":
            stats[key]["wins"] += 1

    summary = {}
    for key, val in stats.items():
        summary[key] = round((val["wins"]/val["total"])*100,2)

    return summary
