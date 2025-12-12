from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
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
    start_dt = start_at

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


# ===========================================================
# 📌 時刻リスト（10分刻み）と予約 / ブロックの無効リストを返す API
# ===========================================================
@reservation_bp.route("/api/time-slots")
def api_time_slots():
    date_str = request.args.get("date")
    duration = request.args.get("duration", type=int)

    if not date_str:
        return jsonify({"error": "date required"}), 400

    if not duration:
        duration = 60  # デフォルト60分（フォームがあるので基本入る）

    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # 営業時間 9:00〜22:00
    t = datetime.combine(selected_date, datetime.strptime("09:00", "%H:%M").time())
    end = datetime.combine(selected_date, datetime.strptime("22:00", "%H:%M").time())

    # 10分刻みの全候補
    time_slots = []
    while t <= end:
        time_slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=10)

    # -----------------------------
    # 予約とブロックを取得
    # -----------------------------
    reservations = Reservation.query.filter(
        db.func.date(Reservation.start_at) == selected_date
    ).all()

    blocks = Block.query.filter(
        db.func.date(Block.start_at) == selected_date
    ).all()

    disabled = set()

    # -----------------------------
    # 予約：開始時間＋duration に基づき後続枠も全部無効化
    # -----------------------------
    for r in reservations:
        cur = r.start_at
        end_dt = r.end_at  # end_at は duration + 30分 で計算済み
        while cur < end_dt:
            disabled.add(cur.strftime("%H:%M"))
            cur += timedelta(minutes=10)

    # -----------------------------
    # ブロックも同様に全枠を無効化
    # -----------------------------
    for b in blocks:
        cur = b.start_at
        end_dt = b.end_at
        while cur < end_dt:
            disabled.add(cur.strftime("%H:%M"))
            cur += timedelta(minutes=10)

    # -----------------------------
    # 当日なら過ぎた時間も無効
    # -----------------------------
    now = datetime.now()
    if selected_date == now.date():
        for ts in time_slots:
            slot_dt = datetime.strptime(f"{date_str} {ts}", "%Y-%m-%d %H:%M")
            if slot_dt <= now:
                disabled.add(ts)

    # -----------------------------
    # この日の基準で「予約 duration の連続枠が取れない開始時刻」も無効化
    # -----------------------------
    # for ts in time_slots:
    #     start_dt = datetime.strptime(f"{date_str} {ts}", "%Y-%m-%d %H:%M")
    #     end_dt = start_dt + timedelta(minutes=duration + 30)

    #     cur = start_dt
    #     invalid = False
    #     while cur < end_dt:
    #         if cur.strftime("%H:%M") in disabled:
    #             invalid = True
    #             break
    #         cur += timedelta(minutes=10)

    #     if invalid:
    #         disabled.add(ts)

    return jsonify({
        "time_slots": time_slots,
        "disabled": list(disabled)
    })
