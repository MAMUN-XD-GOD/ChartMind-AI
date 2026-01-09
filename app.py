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
    "last_trade_time": 0,
    "learning": {
        "binary_bias": 0.0,   # + improves confidence, - reduces
        "forex_bias": 0.0,
        "recent_results": [] # last N results
    }
}

MAX_RECENT = 20

# -----------------------------
# PHASE 3: VISION ENGINE
# -----------------------------
def analyze_chart_image(img):
    gray = img.convert("L")
    arr = np.array(gray)
    h, w = arr.shape

    if arr.std() < 15:
        return {"blocked": True, "reason": "Low contrast / unclear chart"}

    roi = arr[int(h*0.3):int(h*0.8), int(w*0.55):int(w*0.95)]
    mean_top = roi[:roi.shape[0]//2].mean()
    mean_bottom = roi[roi.shape[0]//2:].mean()

    direction = "BULLISH" if mean_bottom > mean_top else "BEARISH"
    body_strength = abs(mean_bottom - mean_top)

    if body_strength > 25:
        momentum, base_conf = "STRONG", 72
    elif body_strength > 15:
        momentum, base_conf = "MEDIUM", 64
    else:
        momentum, base_conf = "WEAK", 55

    return {
        "blocked": False,
        "direction": direction,
        "momentum": momentum,
        "base_confidence": base_conf
    }

# -----------------------------
# PHASE 4: SIGNAL ENGINE
# -----------------------------
def binary_signal_engine(vision, adj_conf):
    if adj_conf < 60 or vision["momentum"] == "WEAK":
        return {"trade": False, "reason": "Low quality setup"}

    signal = "CALL" if vision["direction"] == "BULLISH" else "PUT"
    if vision["momentum"] == "STRONG":
        expiry = "2–3 candles"
    else:
        expiry = "1–2 candles"

    return {
        "trade": True,
        "type": "BINARY",
        "signal": signal,
        "expiry": expiry,
        "confidence": adj_conf
    }

def forex_signal_engine(vision, adj_conf):
    if adj_conf < 60:
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
        "confidence": adj_conf
    }

# -----------------------------
# PHASE 5: RISK + MTG GUARD
# -----------------------------
def risk_guard(adj_conf):
    now = int(time.time())

    if STATE["cooldown_until"] > now:
        return {"allow": False, "reason": "Cooldown active after losses"}

    if STATE["trades_taken"] >= 15:
        return {"allow": False, "reason": "Overtrade limit reached"}

    if now - STATE["last_trade_time"] < 30:
        return {"allow": False, "reason": "Wait before next trade"}

    if STATE["consecutive_losses"] >= 2 and adj_conf < 68:
        return {"allow": False, "reason": "Higher quality required after losses"}

    return {"allow": True}

def smart_mtg_advice(adj_conf, momentum):
    if STATE["consecutive_losses"] == 1 and adj_conf >= 70 and momentum == "STRONG":
        return {"mtg": "OPTIONAL", "cap": "x1.5 (MAX)"}
    return {"mtg": "BLOCKED"}

# -----------------------------
# PHASE 6: LEARNING
# -----------------------------
def apply_learning(market, base_conf):
    bias = STATE["learning"]["binary_bias"] if market == "binary" else STATE["learning"]["forex_bias"]
    recent = STATE["learning"]["recent_results"]

    # Recent performance penalty/boost
    if len(recent) >= 5:
        winrate = sum(1 for r in recent[-5:] if r == "win") / 5
        perf_adj = (winrate - 0.5) * 10  # -5 .. +5
    else:
        perf_adj = 0

    adj = base_conf + bias + perf_adj
    return int(max(50, min(85, adj)))

def update_learning(market, result):
    L = STATE["learning"]
    if result == "win":
        delta = 1.0
        STATE["consecutive_losses"] = 0
    else:
        delta = -1.5
        STATE["consecutive_losses"] += 1
        if STATE["consecutive_losses"] >= 3:
            STATE["cooldown_until"] = int(time.time()) + 10 * 60

    if market == "binary":
        L["binary_bias"] = max(-5, min(5, L["binary_bias"] + delta))
    else:
        L["forex_bias"] = max(-5, min(5, L["forex_bias"] + delta))

    L["recent_results"].append(result)
    if len(L["recent_results"]) > MAX_RECENT:
        L["recent_results"].pop(0)

# -----------------------------
# API
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze_chart():
    if "chart" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    img = Image.open(io.BytesIO(request.files["chart"].read()))
    w, h = img.size
    if w < 300 or h < 200:
        return jsonify({"status": "blocked", "reason": "Chart too small / unclear"})

    now = int(time.time())
    upload_time = int(request.form.get("timestamp", now))
    if now - upload_time > 120:
        return jsonify({"status": "warning", "reason": "Late screenshot"})

    market = request.form.get("market", "binary").lower()

    vision = analyze_chart_image(img)
    if vision["blocked"]:
        return jsonify({"status": "blocked", "reason": vision["reason"]})

    adj_conf = apply_learning(market, vision["base_confidence"])
    guard = risk_guard(adj_conf)
    if not guard["allow"]:
        return jsonify({"status": "no_trade", "reason": guard["reason"], "confidence": adj_conf})

    if market == "binary":
        out = binary_signal_engine(vision, adj_conf)
    else:
        out = forex_signal_engine(vision, adj_conf)

    if not out["trade"]:
        return jsonify({"status": "no_trade", "reason": out["reason"], "confidence": adj_conf})

    STATE["trades_taken"] += 1
    STATE["last_trade_time"] = now

    return jsonify({
        "status": "ok",
        "vision": vision,
        "signal": out,
        "risk": {
            "consecutive_losses": STATE["consecutive_losses"],
            "mtg_advice": smart_mtg_advice(adj_conf, vision["momentum"])
        },
        "learning": {
            "binary_bias": STATE["learning"]["binary_bias"],
            "forex_bias": STATE["learning"]["forex_bias"]
        }
    })

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json or {}
    result = data.get("result")
    market = data.get("market", "binary")
    if result not in ("win", "loss"):
        return jsonify({"error": "Invalid result"}), 400

    update_learning(market, result)
    return jsonify({"ok": True, "learning": STATE["learning"], "state": STATE})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
