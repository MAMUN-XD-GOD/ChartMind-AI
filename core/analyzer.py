from core.logger import log
from core.vision import vision_analyze

def analyze_chart(image_path, meta=None):
    """
    Central analysis pipeline.
    """

    log(f"Pipeline analyze start: {image_path}")

    context = {
        "market": "auto",
        "pair": "auto",
        "timeframe": "unknown",
        "session": "auto",
        "vision": {},
        "state": "vision_processed"
    }

    # Phase-3 Vision
    try:
        vision_data = vision_analyze(image_path)
        context["vision"] = vision_data
    except Exception as e:
        log(f"Vision error: {e}", level="ERROR")
        context["vision_error"] = str(e)

    return context
