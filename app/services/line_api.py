# app/services/line_api.py
import os, requests
from flask import current_app

LINE_REPLY_API = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_API = "https://api.line.me/v2/bot/message/push"

def _headers():
    return {
        "Authorization": f"Bearer {current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }

def reply_message(reply_token, text):
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    r = requests.post(LINE_REPLY_API, headers=_headers(), json=body)
    print("LINE reply response:", r.status_code, r.text)
    r.raise_for_status()
    return r


def push_message(to, text):
    body = {"to": to, "messages":[{"type":"text","text": text}]}
    r = requests.post(LINE_PUSH_API, headers=_headers(), json=body)
    print("LINE push response:", r.status_code, r.text)
    r.raise_for_status()
    return r

def send_message(to, messages):
    """複数メッセージやFlexに対応した送信用"""
    body = {"to": to, "messages": messages}

    r = requests.post(LINE_PUSH_API, headers=_headers(), json=body)
    print("LINE generic push:", r.status_code, r.text)
    r.raise_for_status()
    return r
