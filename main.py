import requests
import pandas as pd
from ta.momentum import RSIIndicator
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
DATA_FILE = "data.csv"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_trades(pair):
    return requests.get(f"https://indodax.com/api/trades/{pair}").json()

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
    a = df.iloc[-1]
    b = df.iloc[-2]
    return a["high"] > b["high"] and a["low"] > b["low"]

if __name__ == "__main__":
    pair = "BTC/IDR"
    symbol = "btcidr"

    history = load_history()
    trades = get_trades(symbol)
    new = build_candles(trades)

    df = pd.concat([history, new]).drop_duplicates(subset=["date"]).sort_values("date")

    if len(df) < 50:
        save_history(df)
        send_telegram(f"🚫 NO TRADE\nPair: {pair}\nAlasan: Data candle belum cukup")
        exit()

    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()
    df["rsi"] = RSIIndicator(df["close"], 14).rsi()
    df["vol_ma20"] = df["volume"].rolling(20).mean()

    last = df.iloc[-1]

    trend_ok = last["ema50"] > last["ema200"]
    rsi_ok = 55 <= last["rsi"] <= 68
    volume_ok = last["volume"] > last["vol_ma20"]
    structure_ok = market_structure_ok(df)

    if not (trend_ok and rsi_ok and volume_ok and structure_ok):
        send_telegram(
            f"🚫 NO TRADE\nPair: {pair}\nAlasan: Trend / RSI / Volume / Struktur belum valid"
        )
        save_history(df)
        exit()

    entry = last["close"]
    risk = entry * 0.01
    sl = entry - risk
    tp1 = entry + risk
    tp2 = entry + risk * 2
    tp3 = entry + risk * 3
    tp4 = entry + risk * 4

    msg = (
        f"📈 SIGNAL BUY\n"
        f"Pair: {pair}\n"
        f"Entry: {entry:,.0f}\n"
        f"Stop Loss: {sl:,.0f}\n"
        f"TP1: {tp1:,.0f}\n"
        f"TP2: {tp2:,.0f}\n"
        f"TP3: {tp3:,.0f}\n"
        f"TP4: {tp4:,.0f}\n"
        f"Timeframe: 4H\n"
        f"Confidence: High"
    )

    send_telegram(msg)
    save_history(df)
