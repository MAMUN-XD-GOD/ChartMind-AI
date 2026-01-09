from core.logger import log
from core.vision import vision_analyze
from core.ocr import detect_pair
from core.market import detect_market
from core.session import detect_session

def analyze_chart(image_path, meta=None):
    log(f"Phase-4 analyze start: {image_path}")

    context = {
        "market": "auto",
        "pair": "unknown",
        "session": "auto",
        "timeframe": "auto",
        "vision": {},
        "state": "context_detected"
    }

    # Vision
    vision_data = vision_analyze(image_path)
    context["vision"] = vision_data

    # Pair OCR
    pair = detect_pair(image_path)
    context["pair"] = pair

    # Market
    market = detect_market(pair, vision_data)
    context["market"] = market

    # Session
    session = detect_session()
    context["session"] = session

    return context
