import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)
ANT_KEY = os.environ.get("ANTHROPIC_KEY", "")
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(msg):
    if TG_TOKEN and TG_CHAT:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": msg, "parse_mode": "HTML"})

def ask_claude(symbol, price):
    prompt = f"Analyze forex {symbol} at price {price}. JSON only: {{\"signal\":\"BUY\",\"confidence\":75,\"reasoning\":\"2 sentences in Russian\"}}"
    r = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key":ANT_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
        json={"model":"claude-opus-4-5","max_tokens":300,"messages":[{"role":"user","content":prompt}]})
    return json.loads(r.json()["content"][0]["text"].replace("```json","").replace("```","").strip())

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("symbol","EUR/USD")
    price = data.get("price","0")
    sig = ask_claude(symbol, price)
    msg = f"🎯 <b>{symbol}</b>\n📊 Сигнал: <b>{sig['signal']}</b> ({sig['confidence']}%)\n💬 {sig['reasoning']}\n💰 Цена: {price}"
    send_telegram(msg)
    return jsonify(sig)

@app.route("/setup", methods=["GET"])
def setup():
    chat_id = request.args.get("chat_id")
    if chat_id:
        return f"Chat ID: {chat_id} - добавь в Railway как TELEGRAM_CHAT_ID"
    r = requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates")
    updates = r.json().get("result", [])
    if updates:
        chat_id = updates[-1]["message"]["chat"]["id"]
        return f"Твой Chat ID: <b>{chat_id}</b> - добавь в Railway как TELEGRAM_CHAT_ID"
    return "Напиши /start своему боту и обнови страницу"

@app.route("/")
def home():
    return "Trading Bot работает!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
