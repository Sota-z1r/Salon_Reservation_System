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
    r.raise_for_status()
    return r

def push_message(to, text):
    body = {"to": to, "messages":[{"type":"text","text": text}]}
    r = requests.post(LINE_PUSH_API, headers=_headers(), json=body)
    r.raise_for_status()
    return r
