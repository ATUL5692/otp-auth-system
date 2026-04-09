import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp import OTP

OTP_EXPIRY_MINUTES = 5


def generate_otp():
    return str(random.randint(1000, 9999))


def create_otp(db: Session, phone_number: str):
    otp = generate_otp()

    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    db_otp = OTP(
        phone_number=phone_number,
        otp_code=otp,   # later we hash this
        expires_at=expires_at
    )

    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)

    return otp


def verify_otp(db: Session, phone_number: str, otp: str):
    record = (
        db.query(OTP)
        .filter(OTP.phone_number == phone_number)
        .order_by(OTP.created_at.desc())
        .first()
    )

    if not record:
        return False, "OTP not found"

    if record.is_used:
        return False, "OTP already used"

    if record.expires_at < datetime.utcnow():
        return False, "OTP expired"

    if record.otp_code != otp:
        return False, "Invalid OTP"

    record.is_used = True
    db.commit()

    return True, "OTP verified"