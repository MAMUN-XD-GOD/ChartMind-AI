"""
Phase-1 memory placeholder.
Later phases will expand this into:
- win/loss memory
- pair behaviour memory
- market regime memory
"""

GLOBAL_MEMORY = {
    "total_requests": 0,
    "last_upload_time": None
}

def increment_request():
    GLOBAL_MEMORY["total_requests"] += 1

def get_memory():
    return GLOBAL_MEMORY
