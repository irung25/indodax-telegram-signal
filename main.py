import requests
import pandas as pd
from ta.momentum import RSIIndicator
import os

DATA_FILE = "data.csv"

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
    return candles.reset_index()

def load_history():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["date"])
    return pd.DataFrame()

def save_history(df):
    df.to_csv(DATA_FILE, index=False)

def market_structure_ok(df):
    if len(df) < 3:
        return False
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return last["high"] > prev["high"] and last["low"] > prev["low"]

if __name__ == "__main__":
    pair = "btcidr"

    history = load_history()
    trades = get_trades(pair)
    new_candles = build_candles(trades)

    df = pd.concat([history, new_candles])
    df = df.drop_duplicates(subset=["date"])
    df = df.sort_values("date")

    if len(df) < 20:
        save_history(df)
        print("NO TRADE: Data candle belum cukup")
        exit()

    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
    df["vol_ma20"] = df["volume"].rolling(20).mean()

    last = df.iloc[-1]

    trend_ok = last["ema50"] > last["ema200"]
    rsi_ok = 55 <= last["rsi"] <= 68
    volume_ok = last["volume"] > last["vol_ma20"]
    structure_ok = market_structure_ok(df)

    print("EMA50 :", last["ema50"])
    print("EMA200:", last["ema200"])
    print("RSI14 :", last["rsi"])
    print("VOLUME OK:", volume_ok)
    print("STRUCTURE OK:", structure_ok)

    if trend_ok and rsi_ok and volume_ok and structure_ok:
        print("SIGNAL BUY CANDIDATE (SEMUA FILTER LOLOS)")
    else:
        print("NO TRADE: Filter belum lengkap")

    save_history(df)
