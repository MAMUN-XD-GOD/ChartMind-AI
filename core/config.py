import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

MAX_UPLOAD_SIZE_MB = 5

APP_NAME = "ChartMind AI"
APP_OWNER = "David Mamun William"

DEBUG_MODE = True
