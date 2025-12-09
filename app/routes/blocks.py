from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.block import Block
from datetime import datetime

# 追加
from app.services.google_calendar import (
    create_block_event,
    update_block_event,
    delete_block_event
)

blocks_bp = Blueprint("blocks", __name__, url_prefix="/admin/blocks")


# ----------------------
# ブロック一覧
# ----------------------
@blocks_bp.route("/")
def list_blocks():
    blocks = Block.query.order_by(Block.start_at).all()
    return render_template("admin/blocks/blocks.html", blocks=blocks)


# ----------------------
# 新規ブロック追加
# ----------------------
@blocks_bp.route("/new", methods=["GET", "POST"])
def add_block():
    if request.method == "GET":
        return render_template("admin/blocks/add_block.html")

    start_at = datetime.fromisoformat(request.form["start_at"])
    end_at = datetime.fromisoformat(request.form["end_at"])
    reason = request.form.get("reason", "")

    b = Block(start_at=start_at, end_at=end_at, reason=reason)
    db.session.add(b)
    db.session.commit()

    # Google カレンダー登録
    try:
        event_id = create_block_event(b)
        b.google_event_id = event_id
        db.session.commit()
    except Exception as e:
        print("Google Calendar ブロック登録エラー:", e)

    flash("ブロックを登録しました")
    return redirect(url_for("blocks.list_blocks"))


# ----------------------
# 編集
# ----------------------
@blocks_bp.route("/edit/<int:block_id>", methods=["GET", "POST"])
def edit_block(block_id):
    b = Block.query.get_or_404(block_id)

    if request.method == "GET":
        return render_template("admin/blocks/edit_block.html", b=b)

    b.start_at = datetime.fromisoformat(request.form["start_at"])
    b.end_at = datetime.fromisoformat(request.form["end_at"])
    b.reason = request.form["reason"]

    db.session.commit()

    # Google カレンダー更新
    try:
        update_block_event(b)
    except Exception as e:
        print("Google Calendar ブロック更新エラー:", e)

    flash("ブロックを更新しました")
    return redirect(url_for("blocks.list_blocks"))


# ----------------------
# 削除
# ----------------------
@blocks_bp.route("/delete/<int:block_id>")
def delete_block(block_id):
    b = Block.query.get_or_404(block_id)

    # Google カレンダー削除
    try:
        delete_block_event(b)
    except Exception as e:
        print("Google Calendar ブロック削除エラー:", e)

    db.session.delete(b)
    db.session.commit()

    flash("ブロックを削除しました")
    return redirect(url_for("blocks.list_blocks"))
