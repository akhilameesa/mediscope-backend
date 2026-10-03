-- ============================================================================
-- MEDISCOPE DATABASE SCHEMA (POSTGRESQL + PGVECTOR)
-- Copyright © 2026 Akhila Meesa. All rights reserved.
-- Mediscope is a proprietary platform created, designed, and owned by Akhila Meesa.
-- ============================================================================

-- Enable UUID and Vector extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    consent_granted BOOLEAN DEFAULT TRUE,
    consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. patients Table
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    relationship VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(50),
    blood_group VARCHAR(10),
    emergency_contact VARCHAR(100),
    pre_existing_conditions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. reports Table
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    report_name VARCHAR(255),
    report_date DATE,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. test_results Table
CREATE TABLE IF NOT EXISTS test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    test_name VARCHAR(255) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(50),
    reference_low NUMERIC,
    reference_high NUMERIC,
    status VARCHAR(20) -- 'HIGH', 'LOW', 'NORMAL'
);

-- 5. email_reminders Table
CREATE TABLE IF NOT EXISTS email_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    reminder_type VARCHAR(100), -- 'ANNUAL_CHECKUP', 'LAB_FOLLOWUP'
    scheduled_date DATE,
    status VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'SENT'
    sent_at TIMESTAMP NULL
);

-- 6. medical_knowledge_vectors Table
CREATE TABLE IF NOT EXISTS medical_knowledge_vectors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT,
    source_name VARCHAR(255),
    embedding VECTOR(1536)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_patient_id ON reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_test_results_report_id ON test_results(report_id);
CREATE INDEX IF NOT EXISTS idx_email_reminders_user_id ON email_reminders(user_id);
