from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import time

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze_chart():
    if "chart" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["chart"]
    image_bytes = file.read()

    # Load image
    try:
        img = Image.open(io.BytesIO(image_bytes))
        width, height = img.size
    except:
        return jsonify({"error": "Invalid image"}), 400

    # Basic chart quality check (real)
    if width < 300 or height < 200:
        return jsonify({
            "status": "blocked",
            "reason": "Chart too small / unclear"
        })

    # Timestamp logic (basic latency guard)
    current_time = int(time.time())
    upload_time = int(request.form.get("timestamp", current_time))
    delay = current_time - upload_time

    if delay > 120:
        return jsonify({
            "status": "warning",
            "reason": "Late screenshot detected",
            "delay_sec": delay
        })

    # Temporary signal (real pipeline placeholder)
    return jsonify({
        "status": "ok",
        "market": request.form.get("market"),
        "signal": "CALL",
        "confidence": 66,
        "note": "Clean structure detected"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
