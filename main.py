import requests
import pandas as pd

def get_candles(pair, timeframe):
    url = f"https://indodax.com/api/chart/{pair}/{timeframe}"
    response = requests.get(url)
    raw = response.json()

    # DEBUG: tampilkan struktur raw (sementara)
    print("RAW RESPONSE TYPE:", type(raw))

    # CASE 1: langsung list
    if isinstance(raw, list):
        candles = raw

    # CASE 2: dict berisi 'data'
    elif isinstance(raw, dict) and "data" in raw:
        candles = raw["data"]

    # CASE 3: dict berisi key lain (fallback)
    elif isinstance(raw, dict):
        # ambil value pertama yang berupa list
        candles = next(
            (v for v in raw.values() if isinstance(v, list)),
            None
        )
        if candles is None:
            raise ValueError("Format API tidak dikenali")

    else:
        raise ValueError("Format API tidak dikenali")

    df = pd.DataFrame(
        candles,
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    return df


if __name__ == "__main__":
    df = get_candles("btcidr", "4h")
    print(df.tail())
