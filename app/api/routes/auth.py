from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.otp_service import create_otp, verify_otp

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

    return {
        "success": success,
        "message": message
    }