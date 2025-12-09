from app import db


class Block(db.Model):
    __tablename__ = "blocks"

    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    google_event_id = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Block {self.start_at} - {self.end_at} {self.reason}>"
