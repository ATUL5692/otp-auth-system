from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.otp_service import create_otp, verify_otp
from app.core.security import create_access_token
from app.services.user_service import get_user_by_phone, create_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/send-otp")
def send_otp(phone_number: str, db: Session = Depends(get_db)):
    otp = create_otp(db, phone_number)

    return {
        "message": "OTP sent successfully",
        "otp": otp   # ⚠️ only for testing
    }


@router.post("/verify-otp")
def verify(phone_number: str, otp: str, db: Session = Depends(get_db)):
    success, message = verify_otp(db, phone_number, otp)

    if not success:
        return {
            "success": False,
            "message": message
        }

    # 🔥 user logic
    user = get_user_by_phone(db, phone_number)

    if not user:
        user = create_user(db, phone_number)

    token = create_access_token({"sub": str(user.id)})

    return {
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer"
    }