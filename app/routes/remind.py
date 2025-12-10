from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from app import db
from app.models.reservation import Reservation
from app.services.line_api import push_message

remind_bp = Blueprint("remind", __name__, url_prefix="/remind")

@remind_bp.route("/daily", methods=["GET"])
def send_daily_reminders():
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    # 翌日分の予約を抽出
    reservations = Reservation.query.filter(
        Reservation.date == tomorrow
    ).all()

    for r in reservations:
        if r.line_user_id:
            push_message(
                r.line_user_id,
                f"【予約リマインド】\n明日 {r.date} {r.time} に予約があります！"
            )

    return jsonify({"sent": len(reservations)})
