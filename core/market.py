from core.logger import log

def detect_market(pair, vision):
    """
    Decide market type using pair + vision hints
    """

    if pair in ["BTCUSDT", "ETHUSDT"]:
        market = "crypto"
    elif pair == "XAUUSD":
        market = "forex_gold"
    elif pair.endswith("USD") or pair.endswith("JPY"):
        market = "forex"
    else:
        market = "binary"

    # vision based override
    if vision.get("avg_candle_size", 0) < 15:
        market = "binary"

    log(f"Market detected: {market}")
    return market
