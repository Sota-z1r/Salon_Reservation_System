from flask import Blueprint, render_template, request, redirect, flash, url_for
from app import db
from app.models.reservation import Reservation
from app.models.block import Block
from datetime import timedelta, datetime

reservation_bp = Blueprint("reservation", __name__)


@reservation_bp.route("/reserve", methods=["GET", "POST", "HEAD"])
def reserve():
    if request.method == "GET":
        return render_template("reserve_form.html")
    
    if request.method == "HEAD":
        return "", 200

    # POST
    name = request.form.get("customer_name")
    phone = request.form.get("phone")
    duration = int(request.form.get("duration"))
    date_str = request.form["date"]
    time_str = request.form["time"]

    start_at = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    # start_at = request.form.get("start_at")
    
    # LIFF から入ってくる LINE ユーザーID（Web経由なら空）
    line_user_id = request.form.get("line_user_id")

    # 文字列 → datetime
    start_dt = datetime.fromisoformat(start_at)

    # 予約終了時刻（施術 + 片付け）
    end_dt = start_dt + timedelta(minutes=duration + 30)

    
    # ==================================================
    # ---- 予約同士の重複チェック ----
    # ==================================================
    existing = Reservation.query.filter(
        Reservation.start_at < end_dt,
        Reservation.end_at > start_dt
    ).first()

    if existing:
        flash("この時間帯はすでに埋まっています。別の時間を選んでください。", "error")
        return redirect(url_for("reservation.reserve"))
    # --------------------------------

    # ==================================================
    # 🔒 ブロックとの重複チェック
    # ==================================================
    overlap = Block.query.filter(
        Block.start_at < end_dt,
        Block.end_at > start_dt
    ).first()

    if overlap:
        flash("この時間は予約できません。", "error")
        return redirect(url_for("reservation.reserve"))

    # ==================================================
    # 📝 予約データ作成
    # ==================================================

    new_resv = Reservation(
        customer_name=name,
        phone=phone,
        start_at=start_dt,
        end_at=end_dt,
        duration=duration,
        line_user_id=line_user_id
    )

    db.session.add(new_resv)
    db.session.commit()
    
    print("DEBUG: line_user_id =", line_user_id)

    # --- LINE プッシュ通知 ---
    from app.services.line_api import push_message

    if line_user_id:
        try:
            push_message(
                line_user_id,
                f"予約が完了しました！\n\n"
                f"日時: {start_dt.strftime('%Y-%m-%d %H:%M')}\n"
                f"施術時間: {duration}分"
            )
        except Exception as e:
            print("LINE プッシュ通知エラー:", e)

    # ==================================================
    # 📅 Google Calendar へ登録
    # ==================================================
    try:
        from app.services.google_calendar import create_event
        event_id = create_event(new_resv)
        new_resv.google_event_id = event_id
        db.session.commit()  # GoogleID 反映
    except Exception as e:
        print("Google カレンダー登録エラー:", e)

    return render_template("complete_reservation.html")
