import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator

def get_trades(pair):
    url = f"https://indodax.com/api/trades/{pair}"
    return requests.get(url).json()

def build_candles(trades, timeframe="4h"):
    df = pd.DataFrame(trades)
    df["date"] = pd.to_datetime(df["date"], unit="s")
    df["price"] = df["price"].astype(float)
    df["amount"] = df["amount"].astype(float)

    df.set_index("date", inplace=True)

    ohlc = df["price"].resample(timeframe).ohlc()
    volume = df["amount"].resample(timeframe).sum()

    candles = ohlc.copy()
    candles["volume"] = volume
    candles.dropna(inplace=True)
    return candles

def calculate_ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    rsi = RSIIndicator(close=df["close"], window=period)
    return rsi.rsi()

if __name__ == "__main__":
    trades = get_trades("btcidr")
    df = build_candles(trades)

    df["ema50"] = calculate_ema(df, 50)
    df["ema200"] = calculate_ema(df, 200)
    df["rsi"] = calculate_rsi(df)

    last = df.iloc[-1]

    print("EMA50 :", last["ema50"])
    print("EMA200:", last["ema200"])
    print("RSI14 :", last["rsi"])

    trend_ok = last["ema50"] > last["ema200"]
    rsi_ok = 55 <= last["rsi"] <= 68

    if trend_ok and rsi_ok:
        print("MOMENTUM: VALID (BOLEH CARI ENTRY)")
    else:
        print("NO TRADE: Momentum / Trend belum valid")
