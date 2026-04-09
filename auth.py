import random
from datetime import datetime, timedelta
from jose import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db import get_db
from models import User

router = APIRouter()

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

security = HTTPBearer()

otp_store = {}  # {phone: otp}


# 🔥 Send OTP
@router.post("/send-otp")
def send_otp(phone_number: str):
    otp = str(random.randint(1000, 9999))
    otp_store[phone_number] = otp

    return {"otp": otp}  # testing only


# 🔥 Verify OTP
@router.post("/verify-otp")
def verify_otp(phone_number: str, otp: str, db: Session = Depends(get_db)):
    if phone_number not in otp_store or otp_store[phone_number] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # check user
    user = db.query(User).filter(User.phone_number == phone_number).first()

    if not user:
        user = User(phone_number=phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    # create token
    payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# 🔥 Get current user
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

    return user


# 🔥 Protected route
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "phone_number": current_user.phone_number
    }
