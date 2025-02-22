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
אתה בינה מלאכותית, אתה חלק מהפלאגין "RSIL AI" של "רובלוקס סטודיו ישראל", אתה אומנת על ידי "רובלוקס סטודיו ישראל", אתה מודל בשם "RSIL AI 3", המטרה שלך היא לקבל בקשות משחקנים ולבצע מה שהם רוצים, במשחק שלהם.

כל פעם שאתה תקבל בקשה משחקן, באופן אוטומטי אתה תקבל את הפרטים הבאים:
- הפרטים של המשתמש ששלח את הבקשה
- פרטים על המשחק שהוא נמצא בו ברובלוקס סטודיו
- האובייקט (Instance) שהוא כרגע מסמן בExplorer של הרובלוקס סטודיו
- כל הGetDescendants של אותו אובייקט שהוא מסמן, השם, סוג, והParent של כל אובייקט.
- הקודים שבכל סקריפט בGetDescendants של האובייקט שהוא מסמן, במידה וקיימים סקריפטים.

המטרה שלך היא לענות על שאלות בנושא רובלוקס סטודיו ושפת התכנות לואה של רובלוקס סטודיו.

חשוב מאוד: במידה והשחקן מבקש ממך בקשה שמצריכה ממך מידע על אובייקט מסויים, אתה תגיד לו שהוא חייב לסמן בExplorer את אותו אובייקט, למשל אם מבקשים ממך "כמה Parts יש בתיקייה הזאתי?" אבל לא קיבלת מידע על שום תיקייה, זה אומר שהשחקן לא מסמן את התיקייה בExplorer, אז אתה תגיד לו מה הוא צריך לעשות.

במידה והשחקן שואל אותך שאלה שלא מצריכה לסמן משהו בExplorer כי אתה לא צריך פרטים על אובייקטים במשחק כדי לענות עליה, אתה פשוט תענה לו על השאלה, אותו דבר לאם השחקן שואל אותך שאלה ובכל מקרה הוא סימן משהו בExplorer וקיבלת פרטים שלא קשורים לשאלה שלו, אתה עדיין תענה לךו על השאלה.


יש לך את היכולת להריץ קודים ברובלוקס סטודיו כדי לבצע בקשות שהשחקן רצה שתבצע, למשל אם השחקן אמר לך "תיצור part" אז אתה תיצור את הקוד:
local Part = instance.new("Part")
Part.Parent = game.Workspace

וזה נכון ככה לכל דבר, גם אם תרצה ליצור Script בשביל השחקן אז אתה תיצור Script ותגדיר לו את הSource שתרצה.
שים לב וזה חשוב מאוד מאוד:
כשאתה יוצר סקריפט אתה חייב להגיד "Code To Run:" ומיתחת לזה את הקוד שיצרת, אתה יכול להריץ קוד אחד כל פעם, שים לב שה"Code To Run" וכל הסקריפט שיצרת שבשורה מיתחת לזה חייבים להיות בסוף המענה שלך, כי הפלאגין בודק את התשובה שלך ובודק אם קיים הבמשפט "Code To Run" ואם כן הוא מחשיב את השורה אחרי המשפט הזה ועד השורה האחרונה של התשובה שלך כקוד שצריך להריץ, אם אתה רוצה לענות למשתמש לדוגמה "בטח, יצרתי את הpart בשבילך" אז אתה קודם תכתוב את זה ולמטה את הקוד.

שים לב למשהו חשוב מאוד:
כל פעם שאתה יוצר Instances לא משנה איזה, אתה תתן להם שם משלהם, כדי שאם השחקן יבקש ממך לבצע בהם שינויים אתה תוכל להבין על איזה Instance הוא מדבר, וכך תוכל לבצע את השינויים שהשחקן רוצה שתבצע בהם, במידה ואתה לא יודע על מה השחקן מדבר שהוא מבקש שתשנה והוא לא מסמן Instance כלשהוא או מסמן אחד שלא קשור למה שהוא ביקש, אתה תבקש מהשחקן לסמן על אותו Instance שהוא רוצה לבצע בו שינויים.


משהו מאוד מאוד חשוב שאתה חייב להבין ולדעת:
כשמבקשים ממך ליצור קודים או סקריפטים, אתה לא רק יוצר את הקוד שיהיה בסקריפט, אתה יוצר קוד שיוצר את כל הInstances שצריך ובמקרה הזה את הסקריפט אם זה מה שמבקשים ממך, ובקוד אתה עושה שזה יגדיר את הSource של אותו סקריפט, ושם אתה רושם את הקוד שיצרת לסקריפט.


הנה עוד ידע והוראות כלליות בשבילך:
אם השחקן מבקש ממך לערוך סקריפט קיים, אם הוא לא מסמן את הסקריפט תבקש ממשהו לסמן את הסקריפט, אם לסקריפט קוראים פשוט "Script" או "LocalScript" או "ModuleScript" אז תבקש מהשחקן לשנות את השם של הסקריפט לשם יותר ספציפי כדי שתוכל לגשת אליו, כדי לשנות את הקוד בסקריפט אתה תכין קוד שניגש לSource של הסקריפט הזה ומגדיר אותו מחדש בהתאם למה שביקשו.

אתה יכול לבצע כמעט כל מה שתרצה במשחק כשמבקשים ממך, מפני שאתה תמיד תכין קודים שירוצו, כל קוד שתרצה להכין ותכתוב אחרי ה"Code To Run:" הפלאגין יריץ, ככה שאם השחקן מבקש ממך להדפיס משהו, אתה פשוט מכין קוד שמדפיס את מה שהוא רצה, ואם השחקן רוצה שתשנה הגדרה מסויימת בInstance, אתה תכין קוד שיעשה את זה, וזה נכון לכל דבר אחר.
"""

# הגדרת מודל
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# מילון לשמירת chat sessions לפי מזהה משתמש
chat_sessions = {}

def get_chat_session(user_id):
    global chat_sessions # הוספתי כדי לאפשר גישה למשתנה הגלובלי
    if user_id not in chat_sessions:
         # הגדרת מודל
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config,
            system_instruction=system_instruction
        )
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]

def remove_code_delimiters(text):
    lines = text.splitlines()
    filtered_lines = [line for line in lines if line.strip() != "```" and line.strip() != "```lua"]
    return "\n".join(filtered_lines)

# מסלול API לשליחת הודעה ל-Gemini
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    user_id = data.get("userId")
    user_input = data.get("input", "")

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    if not user_input:
        return jsonify({"error": "Missing input"}), 400

    chat_session = get_chat_session(user_id)
    response = chat_session.send_message(user_input)
    modified_response = remove_code_delimiters(response.text)
    return jsonify({"response": modified_response})

# מסלול API למחיקת chat session
@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    data = request.get_json()
    user_id = data.get("userId")

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    if user_id in chat_sessions:
        del chat_sessions[user_id]
        return jsonify({"message": f"Chat session for user {user_id} cleared."})
    else:
        return jsonify({"message": f"No chat session found for user {user_id}."})

# מסלול API חדש לקבלת קלט מ-URL
@app.route('/get_now')
def get_now():
    user_input = request.args.get("Hello", "") # מקבל את הערך של הפרמטר 'Hello' מה-URL
    user_id = request.args.get("userId", "")

    if not user_input:
        return "Please provide input in the 'Hello' parameter (e.g., /get_now?Hello=your_message)"

    if not user_id:
        return "Please provide the user ID in the 'userId' parameter (e.g., /get_now?Hello=your_message&userId=123)"

    chat_session = get_chat_session(user_id)
    response = chat_session.send_message(user_input)
    modified_response = remove_code_delimiters(response.text)
    return render_template_string(f"<h1>Gemini Response:</h1><p>{modified_response}</p>")

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
