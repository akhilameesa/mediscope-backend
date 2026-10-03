import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Date, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    consent_granted = Column(Boolean, default=True)
    consent_timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    patients = relationship("Patient", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("EmailReminder", back_populates="user", cascade="all, delete-orphan")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    relationship_type = Column("relationship", String(100), nullable=False) # Self, Mother, Father, Spouse, Child, Sibling, Other
    date_of_birth = Column(String(50), nullable=False)
    gender = Column(String(50), nullable=True)
    blood_group = Column(String(10), nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    pre_existing_conditions = Column(Text, nullable=True)
    primary_physician = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="patients")
    reports = relationship("Report", back_populates="patient", cascade="all, delete-orphan")
    reminders = relationship("EmailReminder", back_populates="patient", cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    report_name = Column(String(255), nullable=False)
    report_date = Column(String(50), nullable=False)
    file_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="reports")
    test_results = relationship("TestResult", back_populates="report", cascade="all, delete-orphan")


class TestResult(Base):
    __tablename__ = "test_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    test_name = Column(String(255), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    reference_low = Column(Float, nullable=True)
    reference_high = Column(Float, nullable=True)
    status = Column(String(20), nullable=False) # 'HIGH', 'LOW', 'NORMAL'

    report = relationship("Report", back_populates="test_results")


class EmailReminder(Base):
    __tablename__ = "email_reminders"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    reminder_type = Column(String(100), default="ANNUAL_CHECKUP")
    scheduled_date = Column(String(50), nullable=False)
    frequency = Column(String(50), default="ANNUAL") # ANNUAL, SEMI_ANNUAL, QUARTERLY
    status = Column(String(20), default="PENDING") # 'PENDING', 'SENT'
    sent_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="reminders")
    patient = relationship("Patient", back_populates="reminders")


class MedicalKnowledgeVector(Base):
    __tablename__ = "medical_knowledge_vectors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    content = Column(Text, nullable=False)
    source_name = Column(String(255), nullable=False)
    embedding = Column(Text, nullable=True) # Serialized JSON vector representation for high-speed local inference
