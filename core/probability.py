from core.feedback import get_feedback_history
from core.news import fetch_market_news
from core.analyzer import analyze_chart
import random

def compute_signal_probability(signal_context):
    """
    Compute AI probability score (0-100) for given signal
    """
    score = 50  # Base neutral probability

    # 1. Historical performance adjustment
    history = get_feedback_history(signal_context["market"], signal_context["pair"])
    if history:
        wins = sum(1 for h in history if h["result"]=="win")
        total = len(history)
        score += int((wins/total) * 20)  # max +20%

    # 2. News / Fundamental impact
    news_list = fetch_market_news()[:5]
    news_impact = sum([n["impact_score"] for n in news_list])
    score += int(news_impact)  # adds/subtracts impact

    # 3. Trend + Technical analysis weight
    trend = signal_context["vision"]["trend_bias"]
    if trend=="up" and signal_context["signal"]["direction"]=="up":
        score += 10
    elif trend=="down" and signal_context["signal"]["direction"]=="down":
        score +=10
    else:
        score -=5

    # 4. SMC / BOS / FVG / OB confirmation
    confirmations = signal_context["confirmations"]  # number of confirmations
    score += confirmations * 5

    # 5. Random minor adjustment to simulate uncertainty
    score += random.randint(-2,2)

    # Clamp between 0–100
    score = max(0, min(100, score))
    return score
