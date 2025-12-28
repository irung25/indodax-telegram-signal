import requests
import pandas as pd

def get_candles(pair, timeframe):
    url = f"https://indodax.com/api/chart/{pair}/{timeframe}"
    response = requests.get(url)
    raw = response.json()

    candles = raw["data"]

    df = pd.DataFrame(
        candles,
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df

if __name__ == "__main__":
    df = get_candles("btcidr", "4h")
    print(df.tail())
