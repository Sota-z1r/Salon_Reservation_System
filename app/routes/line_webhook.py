# app/routes/line_webhook.py
import os
import json
import hmac
import hashlib
from flask import Blueprint, request, current_app, jsonify
from app.services.line_api import reply_message

line_bp = Blueprint("line", __name__, url_prefix="/line")

def validate_signature(request_body, signature, channel_secret):
    hash = hmac.new(channel_secret.encode('utf-8'), request_body, hashlib.sha256).digest()
    import base64
    expected = base64.b64encode(hash).decode('utf-8')
    return expected == signature

@line_bp.route("/webhook", methods=["POST"])
def webhook():
    channel_secret = current_app.config.get("LINE_CHANNEL_SECRET")
    signature = request.headers.get("X-Line-Signature", "")

    body = request.get_data()
    if not validate_signature(body, signature, channel_secret):
        return "Invalid signature", 400

    payload = request.get_json()
    events = payload.get("events", [])
    for ev in events:
        # handle message event
        if ev.get("type") == "message" and ev["message"]["type"] == "text":
            user_id = ev["source"].get("userId")
            text = ev["message"].get("text", "").strip().lower()

            # simple keyword: send LIFF url when user asks "予約"
            if "予約" in text or "よやく" in text or "reserve" in text:
                # build LIFF URL (公開URL)
                liff_url = current_app.config.get("LIFF_RESERVE_URL")
                reply_text = f"予約はこちらからどうぞ：\n{liff_url}"
                reply_message(ev["replyToken"], reply_text)
            else:
                # default reply (short guidance)
                reply_message(ev["replyToken"], "予約をする場合は「予約」と入力してください。")

        # handle follow event / postback etc (optional)
    return "OK", 200
