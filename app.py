from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io, time
import numpy as np

app = Flask(__name__)
CORS(app)

# ---------- Vision Engine (Phase 3) ----------
def analyze_chart_image(img):
    gray = img.convert("L")
    arr = np.array(gray)
    h, w = arr.shape

    # Clarity check
    contrast = arr.std()
    if contrast < 15:
        return {"blocked": True, "reason": "Low contrast / unclear chart"}

    # Recent candles ROI
    roi = arr[int(h*0.3):int(h*0.8), int(w*0.55):int(w*0.95)]

    mean_top = roi[:roi.shape[0]//2].mean()
    mean_bottom = roi[roi.shape[0]//2:].mean()

    direction = "BULLISH" if mean_bottom > mean_top else "BEARISH"
    body_strength = abs(mean_bottom - mean_top)

    if body_strength > 25:
        momentum = "STRONG"; confidence = 72
    elif body_strength > 15:
        momentum = "MEDIUM"; confidence = 64
    else:
        momentum = "WEAK"; confidence = 55

    return {
        "blocked": False,
        "direction": direction,
        "momentum": momentum,
        "confidence": confidence
    }

# ---------- Signal Engine (Phase 4) ----------
def binary_signal_engine(vision):
    # No-trade filter
    if vision["confidence"] < 60 or vision["momentum"] == "WEAK":
        return {"trade": False, "reason": "Low quality setup"}

    signal = "CALL" if vision["direction"] == "BULLISH" else "PUT"

    # Expiry logic (rule-based)
    if vision["momentum"] == "STRONG":
        expiry = "2–3 candles"
        conf = min(78, vision["confidence"] + 6)
    else:
        expiry = "1–2 candles"
        conf = vision["confidence"]

    return {
        "trade": True,
        "type": "BINARY",
        "signal": signal,
        "expiry": expiry,
        "confidence": conf
    }

def forex_signal_engine(vision):
    # No-trade filter
    if vision["confidence"] < 60:
        return {"trade": False, "reason": "Low confidence"}

    direction = "BUY" if vision["direction"] == "BULLISH" else "SELL"

    # Style detect
    if vision["momentum"] == "STRONG":
        style = "SCALPING / INTRADAY"
        rr = "1:1.5 – 1:2"
    else:
        style = "INTRADAY / SWING"
        rr = "1:2 – 1:3"

    return {
        "trade": True,
        "type": "FOREX",
        "direction": direction,
        "style": style,
        "risk_reward": rr,
        "confidence": vision["confidence"]
    }

# ---------- API ----------
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

    # Size guard
    if width < 300 or height < 200:
        return jsonify({"status": "blocked", "reason": "Chart too small / unclear"})

    # Timestamp guard
    now = int(time.time())
    upload_time = int(request.form.get("timestamp", now))
    delay = now - upload_time
    if delay > 120:
        return jsonify({"status": "warning", "reason": "Late screenshot", "delay_sec": delay})

    market = request.form.get("market", "binary").lower()

    # Vision
    vision = analyze_chart_image(img)
    if vision["blocked"]:
        return jsonify({"status": "blocked", "reason": vision["reason"]})

    # Signal by market
    if market == "binary":
        out = binary_signal_engine(vision)
    else:
        out = forex_signal_engine(vision)

    if not out["trade"]:
        return jsonify({
            "status": "no_trade",
            "reason": out["reason"],
            "confidence": vision["confidence"]
        })

    return jsonify({
        "status": "ok",
        "vision": vision,
        "signal": out
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
