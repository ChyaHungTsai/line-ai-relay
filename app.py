from flask import Flask, request, jsonify

app = Flask(__name__)

# 用來暫存手機端傳回的答案 (Y 或 N)
latest_response = None

@app.route("/callback", methods=["POST"])
def line_webhook():
    global latest_response
    body = request.json
    events = body.get("events", [])
    
    for event in events:
        # 偵測使用者是否點擊了我們發送的按鈕 (Postback 事件)
        if event.get("type") == "postback":
            data = event["postback"]["data"]  # 這裡會拿到 "action=Y" 或 "action=N"
            if "action=" in data:
                latest_response = data.split("=")[1]
                print(f"收到手機端回應: {latest_response}")
                
    return jsonify({"status": "ok"})

@app.route("/get_answer", methods=["GET"])
def get_answer():
    global latest_response
    # OA 主機來詢問是否有新答案，領完後就清空，避免重複讀取
    ans = latest_response
    latest_response = None
    return jsonify({"answer": ans})

@app.route("/", methods=["GET"])
def home():
    return "LINE Claude Relay Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
