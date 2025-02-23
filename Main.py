from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import threading
import requests
import time

app = Flask(__name__)

# הגדרת דף הבית כדי לוודא שהשרת פועל
@app.route('/')
def home():
    return "Gemini API"

# קביעת מפתח API של Gemini  - עכשיו ישירות בקוד!
genai.configure(api_key="AIzaSyDUdcllIkENNJFbE88YCBhf2PdOWkKTmEA")



system_instruction = """
אתה בינה מלאכותית, אתה חלק מהפלאגין "RSIL AI" של "רובלוקס סטודיו ישראל", אתה אומנת על ידי "רובלוקס סטודיו ישראל" ולא על ידי אף חברה אחרת, אתה מודל בשם "RSIL AI 3", המטרה שלך היא לקבל בקשות משחקנים ולבצע מה שהם רוצים, במשחק שלהם.

כל פעם שאתה תקבל בקשה משחקן, באופן אוטומתי אתה תקבל את הפרטים הבאים:
- הפרטים של המשתמש ששלח את הבקשה
- פרטים על המשחק שהוא נמצא בו ברובלוקס סטודיו
- האובייקט (Instance) שהוא כרגע מסמן בExplorer של הרובלוקס סטודיו
- כל הGetDescendants של אותו אובייקט שהוא מסמן, השם, סוג, והParent של כל אובייקט.
- הקודים שבכל סקריפט בGetDescendants של האובייקט שהוא מסמן, במידה וקיימים סקריפטים.

המטרה שלך היא לענות על שאלות בנושא רובלוקס סטודיו ושפת התכנות לואה של רובלוקס סטודיו.

חשוב מאוד: במידה והשחקן מבקש ממך בקשה שמצריכה ממך מידע על אובייקט מסויים, אתה תגיד לו שהוא חייב לסמן בExplorer את אותו אובייקט, למשל אם מבקשים ממך "כמה Parts יש בתיקייה הזאתי?" אבל לא קיבלת מידע על שום תיקייה, זה אומר שהשחקן לא מסמן את התיקייה בExplorer, אז אתה תגיד לו מה הוא צריך לעשות.

במידה והשחקן שואל אותך שאלה שלא מצריכה לסמן משהו בExplorer כי אתה לא צריך פרטים על אובייקטים במשחק כדי לענות עליה, אתה פשוט תענה לו על השאלה, אותו דבר לאם השחקן שואל אותך שאלה ובכל מקרה הוא סימן משהו בExplorer וקיבלת פרטים שלא קשורים לשאלה שלו, אתה עדיין תענה לךו על השאלה.
"""

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
    system_instruction=system_instruction
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

# מסלול API חדש לקבלת קלט מ-URL
@app.route('/get_now')
def get_now():
    user_input = request.args.get("Hello", "") # מקבל את הערך של הפרמטר 'Hello' מה-URL

    if not user_input:
        return "Please provide input in the 'Hello' parameter (e.g., /get_now?Hello=your_message)"

    response = chat_session.send_message(user_input)
    return render_template_string(f"<h1>Gemini Response:</h1><p>{response.text}</p>")

# פונקציה ששולחת פינג לשרת כל כמה דקות כדי לשמור עליו דלוק
def keep_alive():
    # מחכה 5 דקות לפני שמתחיל לשלוח פינגים
    print("Waiting 5 minutes before starting keep-alive pings...")
    time.sleep(300)  # 300 שניות = 5 דקות
    print("Starting keep-alive pings.")

    url = "https://web-production-d4e5.up.railway.app/"  # **חשוב:** החלף את זה בכתובת ה-URL האמיתית של הפרויקט שלך!
    if not url:
        print("⚠️  לא הוגדר URL לפינג.  ודא שאתה מחליף את YOUR_RAILWAY_URL_HERE בכתובת האמיתית.")
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
