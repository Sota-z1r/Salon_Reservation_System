import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "../../token.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "../../credentials.json")

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_service():
    """Google Calendar API のサービスインスタンスを返す"""
    creds = None

    # token.json から読み込み
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # トークンが無効なら更新
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # credentials.json から新規認証
    if not creds or not creds.valid:
        raise Exception("Google API の認証がまだ完了していません。OAuth を先に実行してください。")

    # サービス作成
    return build("calendar", "v3", credentials=creds)


def create_event(resv):
    """予約を Google カレンダーへ登録"""
    service = get_service()

    event = {
        "summary": f"{resv.customer_name} 様 予約",
        "description": f"電話番号: {resv.phone}",
        "start": {"dateTime": resv.start_at.isoformat(), "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": resv.end_at.isoformat(), "timeZone": "Asia/Tokyo"},
    }

    created = service.events().insert(
        calendarId="primary", body=event
    ).execute()

    return created["id"]


def update_event(resv):
    """予約データを元に Google カレンダーを更新"""
    if not resv.google_event_id:
        return None

    service = get_service()

    try:
        event = service.events().get(
            calendarId="primary", eventId=resv.google_event_id
        ).execute()

        # 更新項目
        event["summary"] = f"{resv.customer_name} 様 予約"
        event["description"] = f"電話番号: {resv.phone}"
        event["start"] = {
            "dateTime": resv.start_at.isoformat(),
            "timeZone": "Asia/Tokyo"
        }
        event["end"] = {
            "dateTime": resv.end_at.isoformat(),
            "timeZone": "Asia/Tokyo"
        }

        updated = service.events().update(
            calendarId="primary",
            eventId=resv.google_event_id,
            body=event,
        ).execute()

        return updated["id"]

    except HttpError as e:
        print("Update error:", e)
        return None


def delete_event(resv):
    """Google カレンダーから削除"""
    if not resv.google_event_id:
        return

    service = get_service()

    try:
        service.events().delete(
            calendarId="primary", eventId=resv.google_event_id
        ).execute()
    except HttpError as e:
        print("Delete error:", e)


from .google_calendar import get_service

def create_block_event(block):
    service = get_service()
    event = {
        "summary": f"ブロック: {block.reason or 'なし'}",
        "description": f"管理用ブロック",
        "start": {"dateTime": block.start_at.isoformat(), "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": block.end_at.isoformat(), "timeZone": "Asia/Tokyo"},
        "colorId": "8", 
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return created["id"]

def update_block_event(block):
    if not block.google_event_id:
        return None
    service = get_service()
    try:
        event = service.events().get(calendarId="primary", eventId=block.google_event_id).execute()
        event["summary"] = f"ブロック: {block.reason or 'なし'}"
        event["start"] = {"dateTime": block.start_at.isoformat(), "timeZone": "Asia/Tokyo"}
        event["end"] = {"dateTime": block.end_at.isoformat(), "timeZone": "Asia/Tokyo"}
        event["colorId"] = "8" 
        updated = service.events().update(calendarId="primary", eventId=block.google_event_id, body=event).execute()
        return updated["id"]
    except HttpError as e:
        print("Google Calendar update error:", e)
        return None

def delete_block_event(block):
    if not block.google_event_id:
        return
    service = get_service()
    try:
        service.events().delete(calendarId="primary", eventId=block.google_event_id).execute()
    except HttpError as e:
        print("Google Calendar delete error:", e)
