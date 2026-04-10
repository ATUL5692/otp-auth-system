import random
from datetime import datetime, timedelta
from jose import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db import get_db
from models import User, OTP

router = APIRouter()

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

security = HTTPBearer()

# Send OTP (store in DB)
@router.post("/send-otp")
def send_otp(phone_number: str, db: Session = Depends(get_db)):
    otp = str(random.randint(1000, 9999))

    otp_entry = OTP(
        phone_number=phone_number,
        otp_code=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        is_used=False
    )

    db.add(otp_entry)
    db.commit()

    return {"otp": otp}  # testing only


# Verify OTP
@router.post("/verify-otp")
def verify_otp(phone_number: str, otp: str, db: Session = Depends(get_db)):

    # get latest unused OTP
    otp_record = db.query(OTP).filter(
        OTP.phone_number == phone_number,
        OTP.is_used == False
    ).order_by(OTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not found")

    # Expiry check
    if datetime.utcnow() > otp_record.expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")

    # Match check
    if otp_record.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Mark as used
    otp_record.is_used = True
    db.commit()

    # User check/create
    user = db.query(User).filter(User.phone_number == phone_number).first()

    if not user:
        user = User(phone_number=phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate token
    payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# Get current user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# Protected route
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "phone_number": current_user.phone_number
    }
