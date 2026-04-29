import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

AV_KEY = "Q0W4P1XGUXPMYJZ3"
ANT_KEY = os.environ.get("ANTHROPIC_KEY", "")

def ask_claude(symbol, price, indicator, value):
    prompt = f"""TradingView alert for {symbol}.
Price: {price}
Indicator: {indicator} = {value}
Respond ONLY JSON: {{"signal":"BUY","confidence":75,"reasoning":"2 sentences in Russian"}}"""
    r = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key":ANT_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
        json={"model":"claude-opus-4-5","max_tokens":300,"messages":[{"role":"user","content":prompt}]})
    return json.loads(r.json()["content"][0]["text"].replace("```json","").replace("```","").strip())

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"TradingView alert: {data}")
    result = ask_claude(
        data.get("symbol","EUR/USD"),
        data.get("price","0"),
        data.get("indicator","RSI"),
        data.get("value","0")
    )
    print(f"Signal: {result}")
    return jsonify(result)

@app.route("/")
def home():
    return "Trading Bot работает!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
