from flask import Flask, request, jsonify, render_template
from core.analyzer import analyze_chart
import os
import json

app = Flask(__name__, template_folder='ui', static_folder='ui')

# Temporary folder
UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Win/Loss storage
feedback_file = os.path.join(UPLOAD_FOLDER, "feedback.json")
if not os.path.exists(feedback_file):
    with open(feedback_file, "w") as f:
        json.dump([], f)

# Home Page → Mobile UI
@app.route('/')
def home():
    return render_template('index.html')

# Analyze chart(s)
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
        context = analyze_chart(path)

        responses.append(context)

        # Delete temp file after analysis
        os.remove(path)

    # Return first chart's context for dashboard (can extend to multiple)
    return jsonify(responses[0])

# Win/Loss Feedback → improve future signal quality
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    if not data or "signal_id" not in data or "result" not in data:
        return jsonify({"error":"Invalid feedback data"}), 400

    # Load existing
    with open(feedback_file,"r") as f:
        feedback_data = json.load(f)

    feedback_data.append(data)

    with open(feedback_file,"w") as f:
        json.dump(feedback_data,f, indent=4)

    return jsonify({"status":"Feedback recorded"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
