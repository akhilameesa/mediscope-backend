import re
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

class UserRegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str
    consent_granted: bool = True

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Email must be in a valid format (e.g. user@domain.com)")
        domain = v.split("@")[-1]
        if "." not in domain or len(domain.split(".")[-1]) < 2:
            raise ValueError("Email must contain a valid domain (e.g., @gmail.com)")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter (A-Z)")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least 1 lowercase letter (a-z)")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least 1 numeric digit (0-9)")
        if not re.search(r"[@#$%!&*^()\-_=+\[\]{}|;:'\",.<>/?]", v):
            raise ValueError("Password must contain at least 1 special character (@, #, $, %, !, &, *, etc.)")
        return v

    @field_validator("consent_granted")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Consent is mandatory to create a Mediscope account.")
        return v


class UserLoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        return v.strip().lower()


class CheckUserRequest(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    consent_granted: bool
    consent_timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PatientCreate(BaseModel):
    full_name: str
    relationship: str # Self, Mother, Father, Spouse, Child, Sibling, Other
    date_of_birth: str
    gender: Optional[str] = "Unspecified"
    blood_group: Optional[str] = "Unknown"
    emergency_contact: Optional[str] = ""
    pre_existing_conditions: Optional[str] = ""
    primary_physician: Optional[str] = ""


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    relationship: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None
    pre_existing_conditions: Optional[str] = None
    primary_physician: Optional[str] = None


class TestResultResponse(BaseModel):
    id: str
    test_name: str
    value: float
    unit: Optional[str]
    reference_low: Optional[float]
    reference_high: Optional[float]
    status: str # 'HIGH', 'LOW', 'NORMAL'

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: str
    patient_id: str
    report_name: str
    report_date: str
    file_url: Optional[str]
    created_at: Optional[datetime]
    test_results: List[TestResultResponse] = []

    class Config:
        from_attributes = True


class PatientResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    relationship: str
    date_of_birth: str
    gender: Optional[str]
    blood_group: Optional[str]
    emergency_contact: Optional[str]
    pre_existing_conditions: Optional[str]
    primary_physician: Optional[str]
    created_at: Optional[datetime]
    reports: List[ReportResponse] = []

    class Config:
        from_attributes = True


class ReminderScheduleRequest(BaseModel):
    patient_id: str
    reminder_type: str = "ANNUAL_CHECKUP"
    scheduled_date: str
    frequency: str = "ANNUAL" # ANNUAL, SEMI_ANNUAL, QUARTERLY


class ReminderResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: Optional[str] = None
    reminder_type: str
    scheduled_date: str
    frequency: str
    status: str
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SendTestEmailRequest(BaseModel):
    patient_id: Optional[str] = None
    custom_recipient_email: Optional[str] = None
    reminder_type: str = "ANNUAL_CHECKUP"
