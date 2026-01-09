import datetime

def log(message, level="INFO"):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {time} :: {message}")
