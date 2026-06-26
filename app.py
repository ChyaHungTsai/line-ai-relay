from flask import Flask, request, jsonify

app = Flask(__name__)

latest_response = None

@app.route("/callback", methods=["POST"])
def line_webhook():
    global latest_response
    body = request.json
    events = body.get("events", [])
    
    for event in events:
        # 1. 偵測按鈕
        if event.get("type") == "postback":
            data = event["postback"]["data"]
            if "action=" in data:
                latest_response = data.split("=")[1]
                
        # 2. 萬能轉發打字：不管使用者打什麼，通通原封不動傳給公司主機！
        elif event.get("type") == "message" and event["message"]["type"] == "text":
            user_text = event["message"]["text"].strip()
            latest_response = user_text
            print(f"【中繼站】已暫存手機任意輸入: {user_text}")
                
    return jsonify({"status": "ok"})

@app.route("/get_answer", methods=["GET"])
def get_answer():
    global latest_response
    ans = latest_response
    latest_response = None  # 領完清空
    return jsonify({"answer": ans})

@app.route("/", methods=["GET"])
def home():
    return "LINE Claude Relay Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
