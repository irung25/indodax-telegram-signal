import requests

def get_ticker(pair):
    url = f"https://indodax.com/api/ticker/{pair}"
    response = requests.get(url)
    data = response.json()
    return data["ticker"]["last"]

if __name__ == "__main__":
    pairs = ["btcidr", "ethidr", "bnbidr"]

    for pair in pairs:
        price = get_ticker(pair)
        print(f"Harga {pair.upper()} : {price}")
