from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime

from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, APP_NAME, APP_OWNER
from core.logger import log
from core.response import success, error
from storage.memory import increment_request, get_memory

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET"])
def home():
    return jsonify(success({
        "app": APP_NAME,
        "owner": APP_OWNER,
        "phase": 1,
        "status": "Foundation ready"
    }))


@app.route("/health", methods=["GET"])
def health():
    return jsonify(success({
        "server_time": datetime.utcnow().isoformat(),
        "memory": get_memory()
    }))


@app.route("/upload", methods=["POST"])
def upload():
    increment_request()

    if "file" not in request.files:
        return jsonify(error("No file part")), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify(error("No selected file")), 400

    if not allowed_file(file.filename):
        return jsonify(error("Unsupported file type")), 400

    filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + file.filename
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(filepath)

    log(f"File uploaded: {filename}")

    return jsonify(success({
        "filename": filename,
        "message": "Upload successful (analysis will be added in next phases)"
    }))


if __name__ == "__main__":
    log("Starting ChartMind AI - Phase 1")
    app.run(host="0.0.0.0", port=5000, debug=True)
