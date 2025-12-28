import requests
import pandas as pd

def get_trades(pair):
    url = f"https://indodax.com/api/trades/{pair}"
    r = requests.get(url)
    return r.json()

def build_candles(trades, timeframe="4H"):
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

if __name__ == "__main__":
    trades = get_trades("btcidr")
    candles_4h = build_candles(trades, "4H")
    print(candles_4h.tail())
