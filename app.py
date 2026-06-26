from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

latest_response = None
LINE_IMAGE_API_URL = "https://api.line.me/v2/bot/message/push"

# 🎯 請在這裡填入你原本在 monitor_ai.py 裡使用的 LINE 憑證與 USER ID
CHANNEL_ACCESS_TOKEN = "eX2uFZylvOYBqr1goTxKrsrA3y5aleT1U/m23BLpAUOz5++wVlJ3rnPzxVnV+rNGWsGRaOvk91KMQY2l+k+kVThZBHTb7z1qGzxCEgKacFLO2dmuLPblIlEnJX9AvHc85Yl5Y4VW/pr2K/32qyygXwdB04t89/1O/w1cDnyilFU="
USER_ID = "Uf7a3e3109c5c33ddec5f30582f143315"

@app.route("/callback", methods=["POST"])
def line_webhook():
    global latest_response
    body = request.json
    events = body.get("events", [])
    
    for event in events:
        if event.get("type") == "postback":
            data = event["postback"]["data"]
            if "action=" in data:
                latest_response = data.split("=")[1]
        elif event.get("type") == "message" and event["message"]["type"] == "text":
            user_text = event["message"]["text"].strip()
            latest_response = user_text
            print(f"【中繼站】已暫存手機任意輸入: {user_text}")
                
    return jsonify({"status": "ok"})

@app.route("/get_answer", methods=["GET"])
def get_answer():
    global latest_response
    ans = latest_response
    latest_response = None
    return jsonify({"answer": ans})

# 🎯 【新增】接收公司主機上傳的截圖，並直接發送圖片給使用者的 LINE
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"status": "no file"}), 400
        
    file = request.files['file']
    # 藉由當前 Render 服務的對外網址，產生暫時的公開圖片連結
    # Render 會給你一個 URL（例如 https://xxxx.onrender.com）
    host_url = request.host_url.rstrip('/')
    
    # 將圖片儲存在 Render 伺服器本地供 LINE 調閱
    file.save("static_snapshot.png")
    image_url = f"{host_url}/static_snapshot.png"
    
    # 發送 LINE 圖片訊息
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": USER_ID,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            }
        ]
    }
    requests.post(LINE_IMAGE_API_URL, json=payload, headers=headers)
    return jsonify({"status": "success", "url": image_url})

# 讓 LINE 的伺服器可以抓取到這張圖片
@app.route("/static_snapshot.png", methods=["GET"])
def serve_image():
    try:
        with open("static_snapshot.png", "rb") as f:
            return f.read(), 200, {'Content-Type': 'image/png'}
    except:
        return "No image", 404

@app.route("/", methods=["GET"])
def home():
    return "LINE Claude Relay Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
