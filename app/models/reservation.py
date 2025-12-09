from app import db
from app.models.block import Block
from datetime import datetime


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    google_event_id = db.Column(db.String, nullable=True)
    line_user_id = db.Column(db.String(255), nullable=True)

    @staticmethod
    def check_block_overlap(start_dt, end_dt):
        """ブロック時間と予約が重複していないか確認"""
        overlap = Block.query.filter(
            Block.start_at < end_dt,
            Block.end_at > start_dt
        ).first()

        if overlap:
            return overlap.reason

        return None
