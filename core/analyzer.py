from core.logger import log
from core.vision import vision_analyze
from core.ocr import detect_pair
from core.market import detect_market
from core.session import detect_session
from core.technical import technical_analyze

def analyze_chart(image_path, meta=None):
    log(f"Phase-5 analyze start: {image_path}")

    context = {
        "market": "auto",
        "pair": "unknown",
        "session": "auto",
        "timeframe": "auto",
        "vision": {},
        "technical": {},
        "state": "technical_processed"
    }

    # Vision
    vision_data = vision_analyze(image_path)
    context["vision"] = vision_data

    # Pair / Market / Session
    pair = detect_pair(image_path)
    context["pair"] = pair
    context["market"] = detect_market(pair, vision_data)
    context["session"] = detect_session()

    # Technical Core
    technical = technical_analyze(vision_data)
    context["technical"] = technical

    return context
