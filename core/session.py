from datetime import datetime

def detect_session():
    hour = datetime.utcnow().hour

    if 0 <= hour < 7:
        return "asia"
    elif 7 <= hour < 13:
        return "london"
    elif 13 <= hour < 20:
        return "new_york"
    else:
        return "overlap"
