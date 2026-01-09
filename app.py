from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io, time
import numpy as np

app = Flask(__name__)
CORS(app)

# -----------------------------
# GLOBAL STATE (session memory)
# -----------------------------
STATE = {
    "consecutive_losses": 0,
    "trades_taken": 0,
    "cooldown_until": 0,
    "last_trade_time": 0
}

# -----------------------------
# PHASE 3: VISION ENGINE
# -----------------------------
def analyze_chart_image(img):
    gray = img.convert("L")
    arr = np.array(gray)
    h, w = arr.shape

    # Clarity / noise check
    if arr.std() < 15:
        return {"blocked": True, "reason": "Low contrast / unclear chart"}

    # Recent candles ROI
    roi = arr[int(h*0.3):int(h*0.8), int(w*0.55):int(w*0.95)]
    mean_top = roi[:roi.shape[0]//2].mean()
    mean_bottom = roi[roi.shape[0]//2:].mean()

    direction = "BULLISH" if mean_bottom > mean_top else "BEARISH"
    body_strength = abs(mean_bottom - mean_top)

    if body_strength > 25:
        momentum, confidence = "STRONG", 72
    elif body_strength > 15:
        momentum, confidence = "MEDIUM", 64
    else:
        momentum, confidence = "WEAK", 55

    return {
        "blocked": False,
        "direction": direction,
        "momentum": momentum,
        "confidence": confidence
    }

# -----------------------------
# PHASE 4: SIGNAL ENGINE
# -----------------------------
def binary_signal_engine(vision):
    if vision["confidence"] < 60 or vision["momentum"] == "WEAK":
        return {"trade": False, "reason": "Low quality setup"}

    signal = "CALL" if vision["direction"] == "BULLISH" else "PUT"
    if vision["momentum"] == "STRONG":
        expiry, conf = "2–3 candles", min(78, vision["confidence"] + 6)
    else:
        expiry, conf = "1–2 candles", vision["confidence"]

    return {
        "trade": True,
        "type": "BINARY",
        "signal": signal,
        "expiry": expiry,
        "confidence": conf
    }

def forex_signal_engine(vision):
    if vision["confidence"] < 60:
        return {"trade": False, "reason": "Low confidence"}

    direction = "BUY" if vision["direction"] == "BULLISH" else "SELL"
    if vision["momentum"] == "STRONG":
        style, rr = "SCALPING / INTRADAY", "1:1.5 – 1:2"
    else:
        style, rr = "INTRADAY / SWING", "1:2 – 1:3"

    return {
        "trade": True,
        "type": "FOREX",
        "direction": direction,
        "style": style,
        "risk_reward": rr,
        "confidence": vision["confidence"]
    }

# -----------------------------
# PHASE 5: RISK + SMART MTG
# -----------------------------
def risk_guard(vision):
    now = int(time.time())

    # Cooldown active?
    if STATE["cooldown_until"] > now:
        return {"allow": False, "reason": "Cooldown active after losses"}

    # Overtrade guard (max 15/session)
    if STATE["trades_taken"] >= 15:
        return {"allow": False, "reason": "Overtrade limit reached"}

    # Rapid-fire guard (min 30s gap)
    if now - STATE["last_trade_time"] < 30:
        return {"allow": False, "reason": "Wait before next trade"}

    # Escalation: after losses require higher quality
    if STATE["consecutive_losses"] >= 2:
        if vision["confidence"] < 68 or vision["momentum"] != "STRONG":
            return {"allow": False, "reason": "Quality insufficient after losses"}

    return {"allow": True}

def smart_mtg_advice(vision):
    """
    Optional guidance only. No auto-martingale.
    """
    if STATE["consecutive_losses"] == 1:
        if vision["confidence"] >= 70 and vision["momentum"] == "STRONG":
            return {
                "mtg": "OPTIONAL",
                "cap": "x1.5 (MAX)",
                "note": "Recovery allowed only if next setup confirms"
            }
    return {"mtg": "BLOCKED"}

# -----------------------------
# API
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze_chart():
    if "chart" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["chart"]
    image_bytes = file.read()

    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
    except:
        return jsonify({"error": "Invalid image"}), 400

    if width < 300 or height < 200:
        return jsonify({"status": "blocked", "reason": "Chart too small / unclear"})

    now = int(time.time())
    upload_time = int(request.form.get("timestamp", now))
    if now - upload_time > 120:
        return jsonify({"status": "warning", "reason": "Late screenshot"})

    market = request.form.get("market", "binary").lower()

    vision = analyze_chart_image(img)
    if vision["blocked"]:
        return jsonify({"status": "blocked", "reason": vision["reason"]})

    guard = risk_guard(vision)
    if not guard["allow"]:
        return jsonify({"status": "no_trade", "reason": guard["reason"]})

    # Signal
    if market == "binary":
        out = binary_signal_engine(vision)
    else:
        out = forex_signal_engine(vision)

    if not out["trade"]:
        return jsonify({"status": "no_trade", "reason": out["reason"], "confidence": vision["confidence"]})

    # Update state
    STATE["trades_taken"] += 1
    STATE["last_trade_time"] = now

    return jsonify({
        "status": "ok",
        "vision": vision,
        "signal": out,
        "risk": {
            "consecutive_losses": STATE["consecutive_losses"],
            "mtg_advice": smart_mtg_advice(vision)
        }
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    """
    User clicks WIN or LOSS after trade.
    """
    result = request.json.get("result")
    now = int(time.time())

    if result == "win":
        STATE["consecutive_losses"] = 0
    elif result == "loss":
        STATE["consecutive_losses"] += 1
        # Cooldown after 3 losses
        if STATE["consecutive_losses"] >= 3:
            STATE["cooldown_until"] = now + 10 * 60  # 10 minutes

    return jsonify({"ok": True, "state": STATE})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
