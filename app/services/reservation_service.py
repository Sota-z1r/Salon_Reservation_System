# app/services/reservation_service.py
from app.extensions import db
from app.models.reservation import Reservation
from datetime import datetime
import uuid

def create_reservation(name: str, phone: str, email: str, menu_duration: int, start_dt: datetime, end_dt: datetime):
    token = uuid.uuid4().hex
    r = Reservation(
        customer_name=name,
        phone=phone,
        email=email,
        menu_duration=menu_duration,
        start_time=start_dt,
        end_time=end_dt,
        cancel_token=token
    )
    db.session.add(r)
    db.session.commit()
    return r

def cancel_reservation_by_token(token: str):
    r = Reservation.query.filter_by(cancel_token=token, canceled=False).first()
    if not r:
        return False
    r.canceled = True
    db.session.commit()
    return True

def list_reservations_between(start_dt: datetime, end_dt: datetime):
    return Reservation.query.filter(Reservation.canceled == False, Reservation.start_time < end_dt, Reservation.end_time > start_dt).all()
