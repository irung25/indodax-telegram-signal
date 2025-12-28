import requests
import pandas as pd
import os
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PAIRS = {
    "BTC/IDR": "btcidr",
    "ETH/IDR": "ethidr",
    "BNB/IDR": "bnbidr",
    "SOL/IDR": "solidr",
    "XRP/IDR": "xrpidr",
    "AVAX/IDR": "avaxidr",
    "DOGE/IDR": "dogeidr",
    "ADA/IDR": "adaidr"
}

def send_telegram(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def get_trades(symbol):
    return requests.get(f"https://indodax.com/api/trades/{symbol}").json()

def build_candles(trades, tf="4h"):
    df = pd.DataFrame(trades)
    df["date"] = pd.to_datetime(pd.to_numeric(df["date"]), unit="s")
    df["price"] = df["price"].astype(float)
    df["amount"] = df["amount"].astype(float)
    df.set_index("date", inplace=True)
    ohlc = df["price"].resample(tf).ohlc()
    vol = df["amount"].resample(tf).sum()
    out = ohlc.copy()
    out["volume"] = vol
    out.dropna(inplace=True)
    return out.reset_index()

def structure_ok(df):
    if len(df) < 3:
        return False
    a, b = df.iloc[-1], df.iloc[-2]
    return a["high"] > b["high"] and a["low"] > b["low"]

def load_csv(name):
    return pd.read_csv(name, parse_dates=["date"]) if os.path.exists(name) else pd.DataFrame()

def save_csv(name, df):
    df.to_csv(name, index=False)

def trend_state(df):
    return "UP" if df.iloc[-1]["ema50"] > df.iloc[-1]["ema200"] else "DOWN"

def send_stats():
    if not os.path.exists("stats.csv"):
        return
    df = pd.read_csv("stats.csv")
    if df.empty:
        return
    msg = "📊 STATISTIK SIGNAL (MINGGUAN)\n\n"
    for _, r in df.iterrows():
        total = r["win"] + r["loss"]
        if total == 0:
            continue
        wr = r["win"] / total * 100
        msg += f"{r['pair']}\nWin: {r['win']} | Loss: {r['loss']}\nWinrate: {wr:.2f}%\n\n"
    send_telegram(msg)

def update_stats(pair, win):
    f = "stats.csv"
    df = pd.read_csv(f) if os.path.exists(f) else pd.DataFrame(columns=["pair","win","loss"])
    if pair not in df["pair"].values:
        df = pd.concat([df, pd.DataFrame([[pair,0,0]], columns=df.columns)])
    i = df.index[df["pair"] == pair][0]
    df.at[i,"win" if win else "loss"] += 1
    df.to_csv(f, index=False)

if __name__ == "__main__":
    for pair, symbol in PAIRS.items():
        hist = load_csv(f"data_{symbol}.csv")
        trades = get_trades(symbol)
        new = build_candles(trades)
        df = pd.concat([hist, new]).drop_duplicates(subset=["date"]).sort_values("date")

        if len(df) < 80:
            save_csv(f"data_{symbol}.csv", df)
            continue

        df["ema50"] = df["close"].ewm(span=50).mean()
        df["ema200"] = df["close"].ewm(span=200).mean()
        df["rsi"] = RSIIndicator(df["close"], 14).rsi()
        df["vol_ma20"] = df["volume"].rolling(20).mean()
        df["atr"] = AverageTrueRange(df["high"], df["low"], df["close"], 14).average_true_range()

        last = df.iloc[-1]
        prev = df.iloc[-2]

        ema_slope = df["ema50"].iloc[-1] - df["ema50"].iloc[-3]
        breakout_ok = last["close"] > prev["high"]
        atr_ok = last["atr"] > df["atr"].rolling(20).mean().iloc[-1]

        if not (
            last["ema50"] > last["ema200"]
            and 58 <= last["rsi"] <= 65
            and ema_slope > 0
            and last["volume"] > last["vol_ma20"]
            and structure_ok(df)
            and breakout_ok
            and atr_ok
        ):
            save_csv(f"data_{symbol}.csv", df)
            continue

        trend_file = f"trend_{symbol}.txt"
        cur_trend = trend_state(df)
        prev_trend = open(trend_file).read() if os.path.exists(trend_file) else ""
        if cur_trend == prev_trend:
            save_csv(f"data_{symbol}.csv", df)
            continue

        atr_ratio = last["atr"] / last["close"]
        if atr_ratio > 0.02:
            target_r = 4
        elif atr_ratio > 0.015:
            target_r = 3
        else:
            save_csv(f"data_{symbol}.csv", df)
            continue

        entry = last["close"]
        sl = entry - max(last["atr"] * 1.5, entry * 0.01)
        risk = entry - sl
        tp = entry + risk * target_r
        rr = (tp - entry) / risk

        if rr < 3:
            save_csv(f"data_{symbol}.csv", df)
            continue

        msg = (
            f"📈 SIGNAL BUY\n"
            f"Pair: {pair}\n"
            f"Entry: {entry:,.0f}\n"
            f"Stop Loss: {sl:,.0f}\n"
            f"Target ({target_r}R): {tp:,.0f}\n"
            f"RR: 1:{rr:.1f}\n"
            f"Timeframe: 4H\n"
            f"Confidence: Very High"
        )

        send_telegram(msg)
        open(trend_file,"w").write(cur_trend)
        save_csv(f"data_{symbol}.csv", df)

    send_stats()
