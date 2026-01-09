import cv2
import numpy as np
from core.logger import log

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image could not be read")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    return img, gray, edges


def detect_candles(edges):
    """
    Rough candle body detection using contours.
    """
    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    candles = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # filter tiny noise
        if h < 10 or w < 3:
            continue

        body_ratio = h / max(w, 1)

        candles.append({
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "body_ratio": round(body_ratio, 2)
        })

    return candles


def analyze_trend(candles):
    """
    Very early trend slope estimation.
    """
    if len(candles) < 5:
        return "unknown"

    heights = [c["height"] for c in candles[:10]]

    if heights[-1] > heights[0]:
        return "bullish_bias"
    elif heights[-1] < heights[0]:
        return "bearish_bias"
    return "range_bias"


def vision_analyze(image_path):
    log("Vision analysis started")

    img, gray, edges = preprocess_image(image_path)
    candles = detect_candles(edges)
    trend = analyze_trend(candles)

    avg_body = (
        sum(c["height"] for c in candles) / len(candles)
        if candles else 0
    )

    vision_data = {
        "candles_detected": len(candles),
        "avg_candle_size": round(avg_body, 2),
        "trend_bias": trend
    }

    log(f"Vision data: {vision_data}")

    return vision_data
