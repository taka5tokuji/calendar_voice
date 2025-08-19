import speech_recognition as sr
import dateparser
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# 1. 音声認識
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    print("予定を話してください...")
    audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)

text = recognizer.recognize_google(audio, language="ja-JP")
print("入力内容:", text)

# 2. 日付と内容を分ける（超シンプルな例）
event_time = dateparser.parse(text)  # 「明日の15時」などが使える
event_title = text.replace("明日の15時に", "")  # 本当はNLPが必要

# 3. Google Calendar API認証（事前にOAuth認証が必要）
creds = Credentials.from_authorized_user_file("token.json")
service = build("calendar", "v3", credentials=creds)

event = {
    "summary": event_title,
    "start": {"dateTime": event_time.isoformat(), "timeZone": "Asia/Tokyo"},
    "end": {"dateTime": (event_time + timedelta(hours=1)).isoformat(), "timeZone": "Asia/Tokyo"},
    "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]}
}

service.events().insert(calendarId="primary", body=event).execute()
print("予定をカレンダーに追加しました！")
