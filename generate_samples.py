import os
import pymupdf

os.makedirs("sample_reports", exist_ok=True)

def create_sample_pdf(filename, title, patient_name, tests):
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842) # A4
    
    # Header
    page.draw_rect(pymupdf.Rect(40, 40, 555, 100), color=(0.24, 0.32, 0.63), fill=(0.24, 0.32, 0.63))
    page.insert_text(pymupdf.Point(60, 75), "METROPOLITAN CLINICAL LABORATORIES", fontsize=16, color=(1, 1, 1))
    page.insert_text(pymupdf.Point(60, 92), "ACCORD DIAGNOSTIC HEALTH NETWORK • ISO 15189 ACCREDITED", fontsize=10, color=(0.9, 0.9, 0.95))

    # Patient Details Box
    page.draw_rect(pymupdf.Rect(40, 115, 555, 195), color=(0.68, 0.73, 0.85), width=1)
    page.insert_text(pymupdf.Point(55, 135), f"Patient Name: {patient_name}", fontsize=11, color=(0.1, 0.1, 0.2))
    page.insert_text(pymupdf.Point(320, 135), "Report Type: Comprehensive Bio-Panel", fontsize=11, color=(0.1, 0.1, 0.2))
    page.insert_text(pymupdf.Point(55, 155), "Sample Collected: 2026-09-15 08:30 AM", fontsize=10, color=(0.3, 0.3, 0.4))
    page.insert_text(pymupdf.Point(320, 155), "Report Verified: 2026-09-15 02:45 PM", fontsize=10, color=(0.3, 0.3, 0.4))
    page.insert_text(pymupdf.Point(55, 175), "Referring Physician: Dr. Marcus Vance, MD", fontsize=10, color=(0.3, 0.3, 0.4))
    page.insert_text(pymupdf.Point(320, 175), "Specimen: Fasting Venous Serum", fontsize=10, color=(0.3, 0.3, 0.4))

    # Section Title
    page.insert_text(pymupdf.Point(40, 225), title, fontsize=13, color=(0.24, 0.32, 0.63))

    # Table Header
    page.draw_rect(pymupdf.Rect(40, 235, 555, 255), color=(0.93, 0.91, 0.96), fill=(0.93, 0.91, 0.96))
    page.insert_text(pymupdf.Point(50, 249), "TEST / BIOMARKER", fontsize=9, color=(0.24, 0.32, 0.63))
    page.insert_text(pymupdf.Point(230, 249), "RESULT", fontsize=9, color=(0.24, 0.32, 0.63))
    page.insert_text(pymupdf.Point(320, 249), "UNITS", fontsize=9, color=(0.24, 0.32, 0.63))
    page.insert_text(pymupdf.Point(420, 249), "REFERENCE RANGE", fontsize=9, color=(0.24, 0.32, 0.63))

    # Rows
    y = 275
    for test in tests:
        name, val, unit, ref = test
        page.insert_text(pymupdf.Point(50, y), name, fontsize=9.5, color=(0.15, 0.15, 0.2))
        page.insert_text(pymupdf.Point(230, y), str(val), fontsize=10, color=(0.1, 0.1, 0.3))
        page.insert_text(pymupdf.Point(320, y), unit, fontsize=9, color=(0.4, 0.4, 0.5))
        page.insert_text(pymupdf.Point(420, y), ref, fontsize=9, color=(0.4, 0.4, 0.5))
        page.draw_line(pymupdf.Point(40, y + 6), pymupdf.Point(555, y + 6), color=(0.85, 0.85, 0.9), width=0.5)
        y += 24

    # Footer Disclaimer & Copyright
    page.draw_line(pymupdf.Point(40, 750), pymupdf.Point(555, 750), color=(0.68, 0.73, 0.85), width=1)
    page.insert_text(
        pymupdf.Point(40, 770),
        "Safety Notice: Mediscope is an educational health report companion, NOT a diagnostic platform or medical decision system.",
        fontsize=7.5,
        color=(0.5, 0.5, 0.6)
    )
    page.insert_text(
        pymupdf.Point(40, 785),
        "Copyright (C) 2026 Akhila Meesa. All rights reserved. Mediscope is a proprietary platform created, designed, and owned by Akhila Meesa.",
        fontsize=7.5,
        color=(0.24, 0.32, 0.63)
    )

    doc.save(filename)
    doc.close()
    print(f"Created {filename}")

# Panel 1: Comprehensive Metabolic & Lipid
tests_1 = [
    ("Fasting Blood Glucose", 128.0, "mg/dL", "70.0 - 99.0"),
    ("HbA1c (Glycated Hemoglobin)", 6.9, "%", "4.0 - 5.6"),
    ("Total Cholesterol", 235.0, "mg/dL", "125.0 - 200.0"),
    ("LDL Cholesterol", 142.0, "mg/dL", "50.0 - 100.0"),
    ("HDL Cholesterol", 44.0, "mg/dL", "40.0 - 60.0"),
    ("Triglycerides", 195.0, "mg/dL", "50.0 - 150.0"),
    ("Serum Creatinine", 1.05, "mg/dL", "0.70 - 1.30"),
    ("Blood Urea Nitrogen (BUN)", 18.0, "mg/dL", "7.0 - 20.0"),
    ("Thyroid Stimulating Hormone (TSH)", 2.45, "uIU/mL", "0.40 - 4.00"),
    ("Vitamin D (25-OH)", 21.0, "ng/mL", "30.0 - 100.0")
]
create_sample_pdf("sample_reports/sample_metabolic_report.pdf", "COMPREHENSIVE METABOLIC & LIPID PROFILE", "Alexander Meesa", tests_1)

# Panel 2: Followup Improved (showing delta drop!)
tests_2 = [
    ("Fasting Blood Glucose", 115.0, "mg/dL", "70.0 - 99.0"),
    ("HbA1c (Glycated Hemoglobin)", 6.2, "%", "4.0 - 5.6"),
    ("Total Cholesterol", 198.0, "mg/dL", "125.0 - 200.0"),
    ("LDL Cholesterol", 112.0, "mg/dL", "50.0 - 100.0"),
    ("HDL Cholesterol", 52.0, "mg/dL", "40.0 - 60.0"),
    ("Triglycerides", 148.0, "mg/dL", "50.0 - 150.0"),
    ("Serum Creatinine", 0.95, "mg/dL", "0.70 - 1.30"),
    ("Blood Urea Nitrogen (BUN)", 15.0, "mg/dL", "7.0 - 20.0"),
    ("Thyroid Stimulating Hormone (TSH)", 2.10, "uIU/mL", "0.40 - 4.00"),
    ("Vitamin D (25-OH)", 34.0, "ng/mL", "30.0 - 100.0")
]
create_sample_pdf("sample_reports/sample_followup_report.pdf", "FOLLOW-UP COMPARATIVE LAB EVALUATION", "Alexander Meesa", tests_2)
