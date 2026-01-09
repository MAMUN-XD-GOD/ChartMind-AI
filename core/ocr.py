import pytesseract
import cv2
import re
from core.logger import log

PAIR_REGEX = r"(XAUUSD|EURUSD|GBPUSD|USDJPY|GBPJPY|AUDUSD|USDCAD|BTCUSDT|ETHUSDT)"

def detect_pair(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "unknown"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray).upper()

    match = re.search(PAIR_REGEX, text)
    if match:
        pair = match.group(1)
        log(f"Pair detected via OCR: {pair}")
        return pair

    log("Pair OCR failed")
    return "unknown"
