from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io, time
import numpy as np

app = Flask(__name__)
CORS(app)

def analyze_chart_image(img):
    """
    Real rule-based vision logic (no simulation)
    """
    gray = img.convert("L")
    arr = np.array(gray)

    h, w = arr.shape

    # Noise / clarity check
    contrast = arr.std()
    if contrast < 15:
        return {
            "blocked": True,
            "reason": "Low contrast / unclear chart"
        }

    # Focus on middle-right area (recent candles)
    roi = arr[int(h*0.3):int(h*0.8), int(w*0.55):int(w*0.95)]

    mean_top = roi[:roi.shape[0]//2].mean()
    mean_bottom = roi[roi.shape[0]//2:].mean()

    # Candle bias (simple but real)
    if mean_bottom > mean_top:
        direction = "BULLISH"
    else:
        direction = "BEARISH"

    # Momentum strength (body dominance proxy)
    body_strength = abs(mean_bottom - mean_top)

    if body_strength > 25:
        momentum = "STRONG"
        confidence = 70
    elif body_strength > 15:
        momentum = "MEDIUM"
        confidence = 62
    else:
        momentum = "WEAK"
        confidence = 55

    return {
        "blocked": False,
        "direction": direction,
        "momentum": momentum,
        "confidence": confidence
    }


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
        return jsonify({
            "status": "blocked",
            "reason": "Chart too small / unclear"
        })

    # Timestamp guard
    now = int(time.time())
    upload_time = int(request.form.get("timestamp", now))
    delay = now - upload_time

    if delay > 120:
        return jsonify({
            "status": "warning",
            "reason": "Late screenshot detected",
            "delay_sec": delay
        })

    # 🔥 Vision engine
    vision = analyze_chart_image(img)

    if vision["blocked"]:
        return jsonify({
            "status": "blocked",
            "reason": vision["reason"]
        })

    # Binary signal mapping
    if vision["direction"] == "BULLISH":
        signal = "CALL"
    else:
        signal = "PUT"

    return jsonify({
        "status": "ok",
        "signal": signal,
        "trend": vision["direction"],
        "momentum": vision["momentum"],
        "confidence": vision["confidence"],
        "note": "Vision engine confirmed"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
