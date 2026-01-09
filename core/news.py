import requests
from datetime import datetime

# Example: free news API
NEWS_API = "https://finnhub.io/api/v1/news?category=forex&token=YOUR_API_KEY"

def fetch_market_news():
    """
    Fetch latest Forex/Crypto news
    """
    try:
        response = requests.get(NEWS_API, timeout=5)
        news_data = response.json()
        processed_news = []

        for item in news_data[:10]:  # latest 10 news
            processed_news.append({
                "headline": item.get("headline"),
                "source": item.get("source"),
                "datetime": item.get("datetime"),
                "impact_score": calculate_impact(item.get("headline"))
            })

        return processed_news

    except Exception as e:
        return {"error": str(e)}

def calculate_impact(headline):
    """
    Simple impact scoring logic
    """
    headline = headline.lower()
    score = 0
    if "interest rate" in headline or "fed" in headline:
        score += 5
    if "inflation" in headline:
        score += 4
    if "crash" in headline or "plunge" in headline:
        score += 5
    if "bullish" in headline:
        score += 3
    if "bearish" in headline:
        score -= 3
    return score
