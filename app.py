from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, APP_NAME, APP_OWNER
from core.logger import log
from core.response import success, error
from storage.memory import increment_request, get_memory
from core.analyzer import analyze_chart

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def home():
    return jsonify(success({
        "app": APP_NAME,
        "owner": APP_OWNER,
        "phase": 2,
        "status": "Web core ready"
    }))


@app.route("/health", methods=["GET"])
def health():
    return jsonify(success({
        "server_time": datetime.utcnow().isoformat(),
        "memory": get_memory()
    }))


@app.route("/analyze", methods=["POST"])
def analyze():
    increment_request()

    if "file" not in request.files:
        return jsonify(error("No file uploaded")), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify(error("Empty filename")), 400

    if not allowed_file(file.filename):
        return jsonify(error("Unsupported file type")), 400

    filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + file.filename
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    log(f"Chart received: {filename}")

    context = analyze_chart(filepath)

    return jsonify(success({
        "context": context,
        "note": "Signal engine will activate in next phases"
    }))


if __name__ == "__main__":
    log("Starting ChartMind AI - Phase 2")
    app.run(host="0.0.0.0", port=5000, debug=True)
