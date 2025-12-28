import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

PAIR = "btc_idr"
TIMEFRAME = "4h"
LIMIT = 200

def fetch_candles():
    url = f"https://indodax.com/api/chart/{PAIR}/{TIMEFRAME}"
    r = requests.get(url)
    data = r.json()["data"][-LIMIT:]

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])

    df[["open","high","low","close","volume"]] = df[
        ["open","high","low","close","volume"]
    ].astype(float)

    return df

def indicators(df):
    df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()
    df["ema200"] = EMAIndicator(df["close"], 200).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], 14).rsi()
    return df

if __name__ == "__main__":
    df = fetch_candles()
    df = indicators(df)
    last = df.iloc[-1]

    print("===== INDODAX INDICATOR =====")
    print("PAIR:", PAIR.upper())
    print("CLOSE:", last["close"])
    print("EMA50:", round(last["ema50"], 2))
    print("EMA200:", round(last["ema200"], 2))
    print("RSI:", round(last["rsi"], 2))
    print("============================")
