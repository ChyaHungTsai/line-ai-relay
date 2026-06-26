from flask import Flask, request, jsonify

app = Flask(__name__)

# 用來暫存手機端傳回的答案 (ENTER, Y, 或 RIGHT)
latest_response = None

@app.route("/callback", methods=["POST"])
def line_webhook():
    global latest_response
    body = request.json
    events = body.get("events", [])
    
    for event in events:
        # 1. 偵測樣式按鈕 (Postback 事件)
        if event.get("type") == "postback":
            data = event["postback"]["data"]
            if "action=" in data:
                latest_response = data.split("=")[1]
                print(f"【中繼站】收到按鈕回應指令: {latest_response}")
                
        # 2. 偵測使用者直接在 LINE 聊天室打字傳送 (Message 事件)
        elif event.get("type") == "message" and event["message"]["type"] == "text":
            user_text = event["message"]["text"].strip().lower()
            
            # 放行/回車 鍵 (Enter)
            if user_text in ['y', 'yes', '1', 'go', 'enter', '繼續', '回車']:
                latest_response = "ENTER"
                print("【中繼站】收到手機指令: 模擬放行 ENTER (↩)")
                
            # 🎯 【新增】方向鍵右鍵 (Right Arrow)
            elif user_text in ['r', 'right', '右', '2', '右鍵']:
                latest_response = "RIGHT"
                print("【中繼站】收到手機指令: 模擬鍵盤方向右鍵 (➔)")
                
            # 強迫輸入 Y + Enter
            elif user_text in ['force-y', 'y+enter']:
                latest_response = "Y"
                print("【中繼站】收到手機指令: 模擬輸入 Y + Enter")
                
    return jsonify({"status": "ok"})

@app.route("/get_answer", methods=["GET"])
def get_answer():
    global latest_response
    ans = latest_response
    if ans:
        print(f"【中繼站】OA 主機已成功領走指令: {ans}")
    latest_response = None  # 領完後立刻清空
    return jsonify({"answer": ans})

@app.route("/", methods=["GET"])
def home():
    return "LINE Claude Relay Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
