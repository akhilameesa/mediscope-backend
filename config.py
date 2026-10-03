import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Mediscope"
    OWNER_NAME: str = "Akhila Meesa"
    COPYRIGHT_STATEMENT: str = (
        "Copyright © 2026 Akhila Meesa. All rights reserved. "
        "Mediscope is a proprietary platform created, designed, and owned by Akhila Meesa."
    )
    SAFETY_DISCLAIMER: str = (
        "Mediscope is an educational health report companion, NOT a diagnostic platform or medical decision system. "
        "All outputs are intended for appointment preparation with a qualified healthcare provider."
    )
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mediscope-secret-key-akhila-meesa-2026-secure-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./mediscope.db")
    
    # SMTP Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "notifications@mediscope.health")
    
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

settings = Settings()
