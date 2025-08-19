import speech_recognition as sr
import dateparser
from datetime import timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# 音声認識
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=2)  # ノイズ調整
    print("予定を話してください...")
    audio = recognizer.listen(source, timeout=10)

try:
    text = recognizer.recognize_google(audio, language="ja-JP")
    print("入力内容:", text)
except sr.UnknownValueError:
    print("音声が理解できませんでした")
    exit()
except sr.RequestError as e:
    print("音声サービスに接続できません; {0}".format(e))
    exit()

# 日時解析
event_time = dateparser.parse(text, default=dateparser.parse("2025-01-01"))
if event_time is None:
    print("日時を解析できませんでした")
    exit()

# タイトル解析
event_title = text  #簡易化のため全文をタイトルに

# 確認プロンプト
print(f"予定を確認してください:")
print(f"タイトル: {event_title}")
print(f"日時: {event_time.strftime('%Y年%m月%d日 %H:%M')} から 1時間後")
response = input("この予定を登録しますか？ (yes/no): ")

if response.lower() != "yes":
    print("登録をキャンセルしました。")
    exit()

# Google Calendar API 認証
creds = Credentials.from_authorized_user_file("token.json")
service = build("calendar", "v3", credentials=creds)

# 予定登録
event = {
    "summary": event_title,
    "start": {"dateTime": event_time.isoformat(), "timeZone": "Asia/Tokyo"},
    "end": {"dateTime": (event_time + timedelta(hours=1)).isoformat(), "timeZone": "Asia/Tokyo"},
    "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 10}]}
}

created_event = service.events().insert(calendarId="primary", body=event).execute()
print(f"予定をカレンダーに追加しました: {created_event.get('htmlLink')}")
