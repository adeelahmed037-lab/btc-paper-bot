import json, os, urllib.request

FEE = 0.006
START = 1000.0
URL = ("https://api.exchange.coinbase.com/"
       "products/BTC-EUR/candles?granularity=86400")

def get_closes():
    req = urllib.request.Request(
        URL, headers={"User-Agent": "paper-bot"})
    data = json.load(urllib.request.urlopen(req, timeout=20))
    data.sort(key=lambda c: c[0])
    return [c[4] for c in data]

def sma(v, n):
    return sum(v[-n:]) / n

def load():
    if os.path.exists("state.json"):
        return json.load(open("state.json"))
    return {"cash": START, "btc": 0.0,
            "fees": 0.0, "trades": 0}

closes = get_closes()
price = closes[-1]
fast, slow = sma(closes, 20), sma(closes, 50)
s = load()
action = "HOLD"

if fast > slow and s["cash"] > 0:
    fee = s["cash"] * FEE
    s["btc"] = (s["cash"] - fee) / price
    s["fees"] += fee
    s["cash"] = 0.0
    s["trades"] += 1
    action = "BUY"
elif fast < slow and s["btc"] > 0:
    gross = s["btc"] * price
    fee = gross * FEE
    s["cash"] = gross - fee
    s["fees"] += fee
    s["btc"] = 0.0
    s["trades"] += 1
    action = "SELL"

value = s["cash"] + s["btc"] * price
profit = value - START

json.dump(s, open("state.json", "w"))
with open("log.csv", "a") as f:
    f.write(f"{action},{price:.2f},{value:.2f},"
            f"{profit:.2f},{s['fees']:.2f}\n")
print(f"{action} | BTC price: {price:.2f} EUR")
print(f"Value: {value:.2f} EUR | "
      f"Profit/Loss: {profit:.2f} EUR | "
      f"Fees paid: {s['fees']:.2f} EUR")
