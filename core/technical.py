import numpy as np
from core.logger import log

def estimate_support_resistance(candles):
    """
    Use candle heights distribution to estimate zones.
    """
    if not candles:
        return {"support": None, "resistance": None}

    heights = np.array([c["height"] for c in candles])
    support = float(np.percentile(heights, 25))
    resistance = float(np.percentile(heights, 75))

    return {
        "support": round(support, 2),
        "resistance": round(resistance, 2)
    }

def momentum_score(candles):
    """
    Simple momentum: recent vs older candle size.
    """
    if len(candles) < 10:
        return 0

    recent = np.mean([c["height"] for c in candles[:5]])
    past = np.mean([c["height"] for c in candles[-5:]])

    score = recent - past
    return round(score, 2)

def volatility_level(candles):
    if len(candles) < 10:
        return "low"

    heights = np.array([c["height"] for c in candles])
    std = np.std(heights)

    if std < 10:
        return "low"
    elif std < 25:
        return "medium"
    return "high"

def round_number_gravity(avg_candle_size):
    """
    Bigger candles → stronger round number attraction
    """
    if avg_candle_size > 40:
        return "strong"
    elif avg_candle_size > 20:
        return "medium"
    return "weak"

def technical_analyze(vision_data):
    candles_count = vision_data.get("candles_detected", 0)

    # Fake candle objects for Phase-5 (real price candles come later)
    candles = [{"height": vision_data.get("avg_candle_size", 0)}] * candles_count

    sr = estimate_support_resistance(candles)
    momentum = momentum_score(candles)
    volatility = volatility_level(candles)
    round_force = round_number_gravity(vision_data.get("avg_candle_size", 0))

    bias_score = 0
    bias_score += 1 if momentum > 0 else -1
    bias_score += 1 if volatility == "medium" else 0
    bias_score += 1 if round_force == "strong" else 0

    tech = {
        "support_resistance": sr,
        "momentum": momentum,
        "volatility": volatility,
        "round_number_force": round_force,
        "bias_score": bias_score
    }

    log(f"Technical analysis: {tech}")
    return tech
