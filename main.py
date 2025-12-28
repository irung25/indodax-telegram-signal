import requests
import pandas as pd

def get_candles(pair, timeframe):
    url = f"https://indodax.com/api/chart/{pair}/{timeframe}"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df

if __name__ == "__main__":
    df = get_candles("btcidr", "4h")
    print(df.tail())
