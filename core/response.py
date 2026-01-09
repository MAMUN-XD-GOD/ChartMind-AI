def success(data=None, message="OK"):
    return {
        "status": "success",
        "message": message,
        "data": data or {}
    }

def error(message="Error", code=400):
    return {
        "status": "error",
        "message": message,
        "code": code
    }
