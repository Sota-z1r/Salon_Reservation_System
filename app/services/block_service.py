# app/services/block_service.py
from app.extensions import db
from app.models.block import Block
from datetime import datetime

def add_block(start_dt: datetime, end_dt: datetime, reason: str = None):
    b = Block(start_at=start_dt, end_at=end_dt, reason=reason)
    db.session.add(b)
    db.session.commit()
    return b

def delete_block(block_id: int):
    b = Block.query.get(block_id)
    if not b:
        return False
    db.session.delete(b)
    db.session.commit()
    return True

def list_blocks_between(start_dt: datetime, end_dt: datetime):
    return Block.query.filter(Block.start_at < end_dt, Block.end_time > start_dt).all()
