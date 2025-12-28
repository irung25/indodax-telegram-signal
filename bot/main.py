import requests
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator

PAIR = "btc_idr"
TIMEFRAME = "4h"
LIMIT = 200

def fetch_candles(pair, tf, limit):
    url = f"https://indodax.com/api/chart/{pair}/{tf}"
    r = requests.get(url)
    data = r.json()

    candles = data["data"][-limit:]

    df = pd.DataFrame(candles, columns=[
        "timestamp", "open", "high", "low", "close", "volume"
    ])

    df[["open", "high", "low", "close", "volume"]] = df[
        ["open", "high", "low", "close", "volume"]
    ].astype(float)

    return df

def calculate_indicators(df):
    df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(df["close"], window=200).ema_indicator()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
    return df

if __name__ == "__main__":
    df = fetch_candles(PAIR, TIMEFRAME, LIMIT)
    df = calculate_indicators(df)

    last = df.iloc[-1]

    print("PAIR:", PAIR.upper())
    print("Close:", last["close"])
    print("EMA50:", round(last["ema50"], 2))
    print("EMA200:", round(last["ema200"], 2))
    print("RSI:", round(last["rsi"], 2))
