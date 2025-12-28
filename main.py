import requests

def get_ticker(pair):
    url = f"https://indodax.com/api/ticker/{pair}"
    response = requests.get(url)
    data = response.json()
    return data["ticker"]["last"]

if __name__ == "__main__":
    price = get_ticker("btcidr")
    print(f"Harga BTC/IDR saat ini: {price}")
