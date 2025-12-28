if __name__ == "__main__":
    pair = "btcidr"

    history = load_history()
    trades = get_trades(pair)
    new_candles = build_candles(trades)

    df = pd.concat([history, new_candles]).drop_duplicates(subset=["date"])
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

    print("EMA50 :", last["ema50"])
    print("EMA200:", last["ema200"])
    print("RSI14 :", last["rsi"])
    print("VOLUME OK:", volume_ok)

    if trend_ok and rsi_ok and volume_ok:
        print("SIGNAL CANDIDATE: MOMENTUM + VOLUME VALID")
    else:
        print("NO TRADE: Trend / RSI / Volume belum valid")

    save_history(df)
