from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import threading
import requests
import time

app = Flask(__name__)

# הגדרת דף הבית כדי לוודא שהשרת פועל
@app.route('/')
def home():
    return "Gemini API"

# קביעת מפתח API של Gemini מהסביבה
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# הגדרת מודל
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

# מסלול API לשליחת הודעה ל-Gemini
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_input = data.get("input", "")

    if not user_input:
        return jsonify({"error": "Missing input"}), 400

    response = chat_session.send_message(user_input)
    return jsonify({"response": response.text})

# פונקציה ששולחת פינג לשרת כל כמה דקות כדי לשמור עליו דלוק
def keep_alive():
    url = os.environ.get("RAILWAY_URL")  # כתובת האתר של הפרויקט
    if not url:
        print("⚠️ לא נמצא משתנה RAILWAY_URL בסביבה!")
        return

    while True:
        try:
            requests.get(url)
            print(f"✅ Ping sent to {url}")
        except Exception as e:
            print(f"⚠️ Ping failed: {e}")
        time.sleep(600)  # שולח פינג כל 10 דקות

# הפעלת הפינג ברקע
threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
