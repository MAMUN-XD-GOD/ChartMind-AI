from flask import Flask, request, jsonify, render_template
from core.analyzer import analyze_chart
from core.feedback import record_feedback, compute_accuracy, get_feedback_stats
from core.news import fetch_market_news
import os
import json

# ----------------------
# Flask Setup
# ----------------------
app = Flask(__name__, template_folder='ui', static_folder='ui')

# ----------------------
# Folders
# ----------------------
UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
FEEDBACK_FILE = os.path.join(UPLOAD_FOLDER, "feedback.json")
if not os.path.exists(FEEDBACK_FILE):
    with open(FEEDBACK_FILE, "w") as f:
        json.dump([], f)

# ----------------------
# Routes
# ----------------------

# Home Page → Phase 8 UI
@app.route('/')
def home():
    return render_template('index.html')

# Analyze uploaded chart(s) → Phase 1–7 logic
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'charts' not in request.files:
        return jsonify({"error":"No chart uploaded"}), 400

    files = request.files.getlist('charts')
    responses = []

    for file in files:
        filename = file.filename
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # FULL Phase 1–7 analysis
        context = analyze_chart(path)  # returns full signal, market, session, trend, entry/TP/SL, etc
        responses.append(context)

        # Delete temp file
        os.remove(path)

    # Return first chart's context for dashboard
    return jsonify(responses[0])

# Feedback → Win/Loss + Accuracy (Phase 10)
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    required_keys = ["signal_id", "market", "pair", "result"]
    if not data or any(k not in data for k in required_keys):
        return jsonify({"error":"Invalid feedback data"}), 400

    record_feedback(data["signal_id"], data["market"], data["pair"], data["result"])
    overall_accuracy = compute_accuracy()
    stats_summary = get_feedback_stats()

    return jsonify({
        "status": "Feedback recorded",
        "overall_accuracy": overall_accuracy,
        "market_pair_stats": stats_summary
    }), 200

# Accuracy stats endpoint
@app.route('/accuracy', methods=['GET'])
def accuracy():
    overall_accuracy = compute_accuracy()
    stats_summary = get_feedback_stats()
    return jsonify({
        "overall_accuracy": overall_accuracy,
        "market_pair_stats": stats_summary
    })

# Phase 11 → News / Fundamental Analysis
@app.route('/news', methods=['GET'])
def news():
    news_data = fetch_market_news()
    return jsonify(news_data)

# ----------------------
# Run Server
# ----------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
