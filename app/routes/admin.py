from flask import Blueprint, render_template, redirect, request
from app import db
from app.models.reservation import Reservation
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
@admin_bp.route("/edit/<int:resv_id>", methods=["GET", "POST"])
def edit_reservation(resv_id):
    r = Reservation.query.get_or_404(resv_id)

    if request.method == "GET":
        return render_template("admin/edit.html", r=r)

    # POST → 更新処理
    r.customer_name = request.form["customer_name"]
    r.phone = request.form["phone"]
    duration = int(request.form["duration"])
    start_at = datetime.fromisoformat(request.form["start_at"])

    r.duration = duration
    r.start_at = start_at
    r.end_at = start_at + timedelta(minutes=duration + 30)  # 30分余白

    db.session.commit()
    update_event(r)
    
    return redirect("/admin")

