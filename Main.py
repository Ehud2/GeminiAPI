from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import threading
import requests
import time

app = Flask(__name__)

# שימוש במפתח API של גוגל
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.route("/gemini", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    model = genai.GenerativeModel("gemini-2.0-pro")
    response = model.generate_content(user_message)

    return jsonify({"response": response.text})

# 🔹 פונקציה ששולחת Ping לשרת כל 10 דקות
def keep_alive():
    while True:
        try:
            url = "https://your-app.up.railway.app/gemini"  # הכנס את ה-URL שלך
            requests.post(url, json={"message": "ping"})
            print("✅ Sent ping to keep server alive")
        except Exception as e:
            print(f"⚠️ Error sending ping: {e}")
        time.sleep(600)  # מחכה 10 דקות

# 🔹 הרצת הפינג בתהליכון נפרד
threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
