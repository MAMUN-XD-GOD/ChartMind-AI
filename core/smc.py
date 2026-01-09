from core.logger import log

def detect_bos_choc(candles):
    """
    Detect Break of Structure (BOS) and Change of Character (CHoCH)
    using simple candle highs/lows.
    """

    bos = None
    choch = None

    if len(candles) < 3:
        return {"BOS": bos, "CHoCH": choch}

    last = candles[-1]["height"]
    prev = candles[-2]["height"]
    prev2 = candles[-3]["height"]

    # simplistic early detection
    if last > prev and prev > prev2:
        bos = "bullish"
    elif last < prev and prev < prev2:
        bos = "bearish"

    # Change of Character
    if bos == "bullish" and prev < prev2:
        choch = "upward"
    elif bos == "bearish" and prev > prev2:
        choch = "downward"

    return {"BOS": bos, "CHoCH": choch}

def detect_fvg_ob(candles):
    """
    Detect Fair Value Gaps (FVG) and Order Blocks (OB)
    using candle body gaps and reversals.
    """
    fvg = []
    ob = []

    for i in range(1, len(candles)):
        prev = candles[i-1]
        curr = candles[i]

        # FVG detection
        if abs(curr["height"] - prev["height"]) > 10:  # threshold
            fvg.append({"from": prev["height"], "to": curr["height"]})

        # OB detection
        if (curr["height"] > prev["height"] and prev["height"] < candles[i-2]["height"]):
            ob.append({"type": "bullish", "level": prev["height"]})
        elif (curr["height"] < prev["height"] and prev["height"] > candles[i-2]["height"]):
            ob.append({"type": "bearish", "level": prev["height"]})

    return {"FVG": fvg, "OB": ob}

def smc_analyze(vision_data):
    candles_count = vision_data.get("candles_detected", 0)
    avg_size = vision_data.get("avg_candle_size", 0)

    # Fake candle objects for now (replace with real price later)
    candles = [{"height": avg_size}] * max(candles_count, 3)

    structure = detect_bos_choc(candles)
    zones = detect_fvg_ob(candles)

    smc_data = {
        "structure": structure,
        "zones": zones
    }

    log(f"SMC analysis: {smc_data}")
    return smc_data
