from flask import Blueprint, render_template, redirect, request, flash, url_for
from app import db
from app.models.reservation import Reservation
from app.models.block import Block
from datetime import datetime, timedelta
from app.services.google_calendar import update_event
from app.services.google_calendar import delete_event

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
def admin_dashboard():
    reservations = Reservation.query.order_by(Reservation.start_at).all()
    return render_template("admin/dashboard.html", reservations=reservations)

@admin_bp.route("/delete/<int:resv_id>")
def delete_reservation(resv_id):
    r = Reservation.query.get(resv_id)
    if r:
        delete_event(r)  # ← カレンダー削除
        db.session.delete(r)
        db.session.commit()
    return redirect("/admin")

# -----------------------------
# 予約編集（GET:画面表示, POST:更新）
# -----------------------------
@admin_bp.route("/edit/<int:resv_id>", methods=["GET", "POST", "HEAD"])
def edit_reservation(resv_id):
    r = Reservation.query.get_or_404(resv_id)

    if request.method == "GET":
        return render_template(
            "admin/edit.html",
            r=r,
            date=r.start_at.strftime("%Y-%m-%d"),
            time=r.start_at.strftime("%H:%M"),
        )

    # --------------------
    # POST
    # --------------------
    r.customer_name = request.form["customer_name"]
    r.phone = request.form["phone"]
    r.menu = request.form["menu"]

    duration = int(request.form["duration"])
    date_str = request.form["date"]
    time_str = request.form["time"]

    start_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(minutes=duration + 30)

    # --------------------
    # 重複チェック（自分以外）
    # --------------------
    overlap_resv = Reservation.query.filter(
        Reservation.id != r.id,
        Reservation.start_at < end_dt,
        Reservation.end_at > start_dt
    ).first()

    if overlap_resv:
        flash("この時間帯はすでに予約があります。", "error")
        return redirect(url_for("admin.edit_reservation", resv_id=r.id))

    # --------------------
    # ブロックチェック
    # --------------------
    overlap_block = Block.query.filter(
        Block.start_at < end_dt,
        Block.end_at > start_dt
    ).first()

    if overlap_block:
        flash("この時間帯はブロックされています。", "error")
        return redirect(url_for("admin.edit_reservation", resv_id=r.id))

    # --------------------
    # 更新
    # --------------------
    r.duration = duration
    r.start_at = start_dt
    r.end_at = end_dt

    db.session.commit()

    # --------------------
    # Google カレンダー更新
    # --------------------
    try:
        update_event(r)
    except Exception as e:
        print("Google カレンダー更新エラー:", e)

    return redirect(url_for("admin.admin_dashboard"))


