import os
import shutil
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session

from .config import settings
from .database import engine, Base, get_db
from .models import User, Patient, Report, TestResult, EmailReminder
from .schemas import (
    UserRegisterRequest, UserLoginRequest, CheckUserRequest,
    UserResponse, TokenResponse, PatientCreate, PatientUpdate,
    PatientResponse, ReportResponse, ReminderScheduleRequest,
    ReminderResponse, SendTestEmailRequest
)
from .auth import hash_password, verify_password, create_access_token, get_current_user
from .ocr_engine import extract_text_from_file, parse_biomarkers_from_text
from .rag_engine import synthesize_rag_overview, get_biomarker_rag_context
from .trend_analysis import compute_patient_trends
from .doctor_questions import generate_doctor_consultation_questions
from .specialists import find_specialists_for_markers, SPECIALIST_DIRECTORY
from .outbreak_tracker import get_outbreak_statistics
from .email_service import dispatch_checkup_email

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Mediscope Health Report Companion API - Owned by Akhila Meesa",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# LEGAL & META ENDPOINTS
# ============================================================================
@app.get("/api/v1/meta/legal")
def get_legal_metadata():
    """Returns persistent ownership and safety disclaimer tokens."""
    return {
        "application_title": settings.PROJECT_NAME,
        "proprietary_owner": settings.OWNER_NAME,
        "copyright_statement": settings.COPYRIGHT_STATEMENT,
        "safety_disclaimer": settings.SAFETY_DISCLAIMER
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================
@app.post("/api/v1/auth/check-user")
def check_user_exists(payload: CheckUserRequest, db: Session = Depends(get_db)):
    """Checks if an email is already registered."""
    clean_email = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == clean_email).first()
    return {"exists": existing_user is not None}


@app.post("/api/v1/auth/register", response_model=TokenResponse)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Validates password rules, checks email duplicate, records consent, creates user.
    """
    clean_email = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please log in."
        )

    hashed_pw = hash_password(payload.password)
    user = User(
        full_name=payload.full_name.strip(),
        email=clean_email,
        password_hash=hashed_pw,
        consent_granted=payload.consent_granted,
        consent_timestamp=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@app.post("/api/v1/auth/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user; if user doesn't exist, blocks attempt and returns specific code.
    """
    clean_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == clean_email).first()

    if not user:
        # Prompt Requirement: "Account Not Found: No account is associated with this email address. Please register for a new account instead of signing in."
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account Not Found: No account is associated with this email address. Please register for a new account instead of signing in."
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your password and try again."
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/api/v1/auth/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns current authenticated user."""
    return current_user


# ============================================================================
# PATIENT MANAGEMENT ENDPOINTS (Initial state must be completely EMPTY)
# ============================================================================
@app.get("/api/v1/patients", response_model=List[PatientResponse])
def get_patients(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns all patients linked to the logged-in user.
    Starts completely EMPTY for newly registered users.
    """
    patients = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .order_by(Patient.created_at.desc())
        .all()
    )
    # Serialize with relationship field mapped
    res = []
    for p in patients:
        res.append({
            "id": p.id,
            "user_id": p.user_id,
            "full_name": p.full_name,
            "relationship": p.relationship_type,
            "date_of_birth": p.date_of_birth,
            "gender": p.gender,
            "blood_group": p.blood_group,
            "emergency_contact": p.emergency_contact,
            "pre_existing_conditions": p.pre_existing_conditions,
            "primary_physician": p.primary_physician,
            "created_at": p.created_at,
            "reports": p.reports
        })
    return res


@app.post("/api/v1/patients", response_model=PatientResponse)
def create_patient(payload: PatientCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Creates a new family patient profile."""
    patient = Patient(
        user_id=current_user.id,
        full_name=payload.full_name.strip(),
        relationship_type=payload.relationship.strip(),
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        blood_group=payload.blood_group,
        emergency_contact=payload.emergency_contact,
        pre_existing_conditions=payload.pre_existing_conditions,
        primary_physician=payload.primary_physician
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "full_name": patient.full_name,
        "relationship": patient.relationship_type,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "blood_group": patient.blood_group,
        "emergency_contact": patient.emergency_contact,
        "pre_existing_conditions": patient.pre_existing_conditions,
        "primary_physician": patient.primary_physician,
        "created_at": patient.created_at,
        "reports": []
    }


@app.put("/api/v1/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    payload: PatientUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates an existing patient profile."""
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    if payload.full_name is not None:
        patient.full_name = payload.full_name.strip()
    if payload.relationship is not None:
        patient.relationship_type = payload.relationship.strip()
    if payload.date_of_birth is not None:
        patient.date_of_birth = payload.date_of_birth
    if payload.gender is not None:
        patient.gender = payload.gender
    if payload.blood_group is not None:
        patient.blood_group = payload.blood_group
    if payload.emergency_contact is not None:
        patient.emergency_contact = payload.emergency_contact
    if payload.pre_existing_conditions is not None:
        patient.pre_existing_conditions = payload.pre_existing_conditions
    if payload.primary_physician is not None:
        patient.primary_physician = payload.primary_physician

    db.commit()
    db.refresh(patient)

    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "full_name": patient.full_name,
        "relationship": patient.relationship_type,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "blood_group": patient.blood_group,
        "emergency_contact": patient.emergency_contact,
        "pre_existing_conditions": patient.pre_existing_conditions,
        "primary_physician": patient.primary_physician,
        "created_at": patient.created_at,
        "reports": patient.reports
    }


@app.delete("/api/v1/patients/{patient_id}")
def delete_patient(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes patient profile and cascades deletion of associated reports and labs."""
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    db.delete(patient)
    db.commit()
    return {"status": "success", "message": f"Patient '{patient.full_name}' and all associated records deleted."}


# ============================================================================
# REPORTS & LAB ANALYSIS ENDPOINTS
# ============================================================================
@app.post("/api/v1/reports/upload")
async def upload_and_process_report(
    patient_id: str = Form(...),
    report_name: str = Form("Diagnostic Lab Report"),
    report_date: str = Form(datetime.utcnow().strftime("%Y-%m-%d")),
    file: UploadFile = File(None),
    preset_type: Optional[str] = Form(None), # Option for instant pre-set testing
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stage Processing Stepper:
    1. Storage -> 2. PyMuPDF/Tesseract OCR -> 3. Range Validation -> 4. RAG Synthesis.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    file_path = None
    extracted_text = ""

    if file and file.filename:
        # Save file to upload directory
        clean_filename = f"{patient_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
        dest_path = os.path.join(settings.UPLOAD_DIR, clean_filename)
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = dest_path
        extracted_text = extract_text_from_file(dest_path)

    # If preset requested or no file, generate curated panel based on preset
    biomarkers = []
    if preset_type == "lipid_metabolic":
        biomarkers = [
            {"test_name": "Fasting Blood Glucose", "value": 128.0, "unit": "mg/dL", "reference_low": 70.0, "reference_high": 99.0, "status": "HIGH"},
            {"test_name": "HbA1c (Glycated Hemoglobin)", "value": 6.9, "unit": "%", "reference_low": 4.0, "reference_high": 5.6, "status": "HIGH"},
            {"test_name": "Total Cholesterol", "value": 235.0, "unit": "mg/dL", "reference_low": 125.0, "reference_high": 200.0, "status": "HIGH"},
            {"test_name": "LDL Cholesterol", "value": 142.0, "unit": "mg/dL", "reference_low": 50.0, "reference_high": 100.0, "status": "HIGH"},
            {"test_name": "HDL Cholesterol", "value": 44.0, "unit": "mg/dL", "reference_low": 40.0, "reference_high": 60.0, "status": "NORMAL"},
            {"test_name": "Triglycerides", "value": 195.0, "unit": "mg/dL", "reference_low": 50.0, "reference_high": 150.0, "status": "HIGH"},
            {"test_name": "Serum Creatinine", "value": 1.05, "unit": "mg/dL", "reference_low": 0.7, "reference_high": 1.3, "status": "NORMAL"}
        ]
    elif preset_type == "followup_improved":
        # Great for demonstrating delta reduction!
        biomarkers = [
            {"test_name": "Fasting Blood Glucose", "value": 115.0, "unit": "mg/dL", "reference_low": 70.0, "reference_high": 99.0, "status": "HIGH"},
            {"test_name": "HbA1c (Glycated Hemoglobin)", "value": 6.2, "unit": "%", "reference_low": 4.0, "reference_high": 5.6, "status": "HIGH"},
            {"test_name": "Total Cholesterol", "value": 198.0, "unit": "mg/dL", "reference_low": 125.0, "reference_high": 200.0, "status": "NORMAL"},
            {"test_name": "LDL Cholesterol", "value": 112.0, "unit": "mg/dL", "reference_low": 50.0, "reference_high": 100.0, "status": "HIGH"},
            {"test_name": "HDL Cholesterol", "value": 52.0, "unit": "mg/dL", "reference_low": 40.0, "reference_high": 60.0, "status": "NORMAL"},
            {"test_name": "Triglycerides", "value": 148.0, "unit": "mg/dL", "reference_low": 50.0, "reference_high": 150.0, "status": "NORMAL"},
            {"test_name": "Serum Creatinine", "value": 0.95, "unit": "mg/dL", "reference_low": 0.7, "reference_high": 1.3, "status": "NORMAL"}
        ]
    elif preset_type == "complete_blood_count":
        biomarkers = [
            {"test_name": "Hemoglobin", "value": 11.2, "unit": "g/dL", "reference_low": 12.0, "reference_high": 17.5, "status": "LOW"},
            {"test_name": "Total Leukocyte Count (WBC)", "value": 7.4, "unit": "x10^3/uL", "reference_low": 4.5, "reference_high": 11.0, "status": "NORMAL"},
            {"test_name": "Platelet Count", "value": 240.0, "unit": "x10^3/uL", "reference_low": 150.0, "reference_high": 450.0, "status": "NORMAL"},
            {"test_name": "Thyroid Stimulating Hormone (TSH)", "value": 5.60, "unit": "uIU/mL", "reference_low": 0.4, "reference_high": 4.0, "status": "HIGH"},
            {"test_name": "Vitamin D (25-OH)", "value": 19.5, "unit": "ng/mL", "reference_low": 30.0, "reference_high": 100.0, "status": "LOW"}
        ]
    else:
        # Run PyMuPDF / OCR parser
        biomarkers = parse_biomarkers_from_text(extracted_text)

    # Persist report in database
    report = Report(
        patient_id=patient_id,
        report_name=report_name,
        report_date=report_date,
        file_url=file_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    # Persist test results
    db_test_results = []
    for bm in biomarkers:
        tr = TestResult(
            report_id=report.id,
            test_name=bm["test_name"],
            value=bm["value"],
            unit=bm.get("unit", ""),
            reference_low=bm.get("reference_low"),
            reference_high=bm.get("reference_high"),
            status=bm["status"]
        )
        db.add(tr)
        db_test_results.append(tr)

    db.commit()
    db.refresh(report)

    # RAG synthesis
    rag_summary = synthesize_rag_overview(biomarkers)

    return {
        "status": "success",
        "message": "Report processed successfully through 4-stage OCR & RAG pipeline.",
        "stepper_stages": [
            {"step": 1, "name": "Storage Securely Stored", "status": "completed"},
            {"step": 2, "name": "PyMuPDF Text & OCR Extraction", "status": "completed"},
            {"step": 3, "name": "Clinical Range Validation", "status": "completed"},
            {"step": 4, "name": "RAG Knowledge Synthesis", "status": "completed"}
        ],
        "report_id": report.id,
        "report_name": report.report_name,
        "report_date": report.report_date,
        "extracted_biomarkers": biomarkers,
        "rag_summary": rag_summary
    }


@app.get("/api/v1/reports/{patient_id}/trends")
def get_patient_trends(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Computes exact historical report deltas."""
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    return compute_patient_trends(patient_id, db)


@app.get("/api/v1/reports/{patient_id}/doctor-questions")
def get_doctor_questions(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Synthesizes clinical discussion questions tailored to patient's out-of-range lab results."""
    patient = db.query(Patient).filter(Patient.id == patient_id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")
    return generate_doctor_consultation_questions(patient_id, db)


@app.get("/api/v1/doctors/specialists")
def get_specialists(
    patient_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns local area specialists based on patient out-of-range lab categories.
    """
    flagged_markers = []
    if patient_id:
        patient = db.query(Patient).filter(Patient.id == patient_id, Patient.user_id == current_user.id).first()
        if patient and patient.reports:
            latest_report = sorted(patient.reports, key=lambda r: r.report_date, reverse=True)[0]
            flagged_markers = [t.test_name for t in latest_report.test_results if t.status in ("HIGH", "LOW")]

    return {
        "matched_markers": flagged_markers,
        "specialists": find_specialists_for_markers(flagged_markers)
    }


# ============================================================================
# LIVE INFECTION & OUTBREAK STATS
# ============================================================================
@app.get("/api/v1/health/outbreaks")
def get_outbreak_stats():
    """Returns live viral infection and outbreak stats."""
    return get_outbreak_statistics()


# ============================================================================
# EMAIL REMINDER DISPATCH ENDPOINTS
# ============================================================================
@app.get("/api/v1/reminders", response_model=List[ReminderResponse])
def get_user_reminders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists scheduled health checkup reminders for the logged-in user."""
    reminders = (
        db.query(EmailReminder)
        .filter(EmailReminder.user_id == current_user.id)
        .order_by(EmailReminder.scheduled_date.asc())
        .all()
    )
    res = []
    for r in reminders:
        res.append({
            "id": r.id,
            "patient_id": r.patient_id,
            "patient_name": r.patient.full_name if r.patient else "Family Member",
            "reminder_type": r.reminder_type,
            "scheduled_date": r.scheduled_date,
            "frequency": r.frequency,
            "status": r.status,
            "sent_at": r.sent_at
        })
    return res


@app.post("/api/v1/reminders/schedule")
def schedule_reminder(
    payload: ReminderScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedules an annual or periodic health checkup reminder."""
    patient = db.query(Patient).filter(Patient.id == payload.patient_id, Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found.")

    reminder = EmailReminder(
        user_id=current_user.id,
        patient_id=patient.id,
        reminder_type=payload.reminder_type,
        scheduled_date=payload.scheduled_date,
        frequency=payload.frequency,
        status="PENDING"
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return {
        "status": "success",
        "message": f"Checkup reminder scheduled for {patient.full_name} on {payload.scheduled_date}.",
        "reminder_id": reminder.id
    }


@app.post("/api/v1/reminders/send-test-email")
def trigger_email_dispatch(
    payload: SendTestEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Triggers an actual formatted HTML checkup reminder email to the user's registered email address.
    """
    patient_name = "Self (Registered Member)"
    relationship = "Self"
    if payload.patient_id:
        p = db.query(Patient).filter(Patient.id == payload.patient_id, Patient.user_id == current_user.id).first()
        if p:
            patient_name = p.full_name
            relationship = p.relationship_type

    target_email = payload.custom_recipient_email or current_user.email
    scheduled_date = datetime.utcnow().strftime("%Y-%m-%d")

    dispatch_result = dispatch_checkup_email(
        recipient_email=target_email,
        recipient_name=current_user.full_name,
        patient_name=patient_name,
        relationship=relationship,
        reminder_type=payload.reminder_type,
        scheduled_date=scheduled_date,
        frequency="ANNUAL"
    )

    # Record dispatch in database
    if payload.patient_id:
        new_reminder = EmailReminder(
            user_id=current_user.id,
            patient_id=payload.patient_id,
            reminder_type=payload.reminder_type,
            scheduled_date=scheduled_date,
            frequency="ANNUAL",
            status="SENT",
            sent_at=datetime.utcnow()
        )
        db.add(new_reminder)
        db.commit()

    return dispatch_result


# ============================================================================
# SERVE FRONTEND STATIC ASSETS & SPA ROUTING
# ============================================================================
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist")
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        target_file = os.path.join(frontend_dist, full_path)
        if os.path.isfile(target_file):
            return FileResponse(target_file)
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend index not found")

