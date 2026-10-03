from typing import List, Dict, Any

SPECIALIST_DIRECTORY = [
    {
        "id": "spec-1",
        "name": "Dr. Sarah Jenkins, MD, FACE",
        "specialty": "Endocrinology, Diabetes & Metabolism",
        "hospital_clinic": "Metropolitan Endocrinology & Diabetes Institute",
        "address": "450 Lexington Medical Center, Suite 400",
        "phone": "+1 (555) 382-9100",
        "rating": 4.9,
        "review_count": 142,
        "matched_biomarkers": ["Fasting Blood Glucose", "HbA1c (Glycated Hemoglobin)", "Thyroid Stimulating Hormone (TSH)", "Free Thyroxine (FT4)"],
        "appointment_prep_tips": [
            "Bring your last 3 blood glucose logs and 6-month laboratory history.",
            "List all medications, vitamins, and supplements with exact daily dosages.",
            "Fast for 10 hours prior to your morning visit if repeat fasting panels are anticipated."
        ],
        "accepting_new_patients": True
    },
    {
        "id": "spec-2",
        "name": "Dr. Robert Chen, MD, FACC",
        "specialty": "Cardiovascular Medicine & Lipidology",
        "hospital_clinic": "Advanced Heart & Vascular Pavilion",
        "address": "720 University Health Parkway, Tower B",
        "phone": "+1 (555) 491-2300",
        "rating": 4.8,
        "review_count": 98,
        "matched_biomarkers": ["Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", "Triglycerides"],
        "appointment_prep_tips": [
            "Compile a detailed pedigree of early cardiovascular events in first-degree relatives.",
            "Bring recent resting ECG traces or home blood pressure monitoring logs.",
            "Wear comfortable clothing suitable for a brief ambulatory consultation or vitals check."
        ],
        "accepting_new_patients": True
    },
    {
        "id": "spec-3",
        "name": "Dr. Elena Rostova, MD, FASN",
        "specialty": "Nephrology & Renal Hypertension",
        "hospital_clinic": "Center for Kidney Care & Metabolic Health",
        "address": "1200 Riverside Medical Arts, Floor 3",
        "phone": "+1 (555) 723-4811",
        "rating": 4.9,
        "review_count": 84,
        "matched_biomarkers": ["Serum Creatinine", "Blood Urea Nitrogen (BUN)", "Serum Potassium", "Serum Sodium"],
        "appointment_prep_tips": [
            "Maintain your normal hydration routine—do not severely overhydrate or dehydrate before appointments.",
            "Bring records of any prescription or NSAID pain relievers taken in the past month.",
            "Be prepared to provide a fresh spot urine sample for microalbumin analysis."
        ],
        "accepting_new_patients": True
    },
    {
        "id": "spec-4",
        "name": "Dr. Marcus Vance, MD",
        "specialty": "Hematology & Internal Medicine",
        "hospital_clinic": "Regional Comprehensive Hematology Center",
        "address": "810 Commonwealth Ave, Suite 620",
        "phone": "+1 (555) 912-7400",
        "rating": 4.7,
        "review_count": 115,
        "matched_biomarkers": ["Hemoglobin", "Total Leukocyte Count (WBC)", "Platelet Count", "Vitamin B12"],
        "appointment_prep_tips": [
            "Note any unusual bleeding symptoms, unexplained bruising, or severe fatigue episodes.",
            "Bring all dietary supplement facts panels, particularly iron or multivitamin formulations.",
            "Arrive 15 minutes early for standard CBC blood draws."
        ],
        "accepting_new_patients": True
    },
    {
        "id": "spec-5",
        "name": "Dr. Angela Morales, MD",
        "specialty": "Gastroenterology & Hepatology",
        "hospital_clinic": "Digestive Disease & Liver Specialists",
        "address": "330 Medical Plaza West, Suite 210",
        "phone": "+1 (555) 634-1188",
        "rating": 4.8,
        "review_count": 130,
        "matched_biomarkers": ["Alanine Aminotransferase (ALT/SGPT)", "Aspartate Aminotransferase (AST/SGOT)", "Alkaline Phosphatase (ALP)"],
        "appointment_prep_tips": [
            "Log your daily dietary patterns and alcohol consumption over the past two weeks.",
            "List any herbal teas, bodybuilding powders, or naturopathic products ingested.",
            "Notify staff if you have had abdominal ultrasound or imaging performed elsewhere."
        ],
        "accepting_new_patients": True
    },
    {
        "id": "spec-6",
        "name": "Dr. David Kim, MD, FAAFP",
        "specialty": "Preventive Medicine & Integrative Primary Care",
        "hospital_clinic": "Apex Comprehensive Health & Wellness",
        "address": "500 Park Avenue, 2nd Floor",
        "phone": "+1 (555) 839-5500",
        "rating": 5.0,
        "review_count": 210,
        "matched_biomarkers": ["Vitamin D (25-OH)", "Serum Uric Acid", "Serum Calcium"],
        "appointment_prep_tips": [
            "Bring your Mediscope AI Doctor Question briefing sheet printed or on your smartphone.",
            "Write down your top 3 overall wellness goals for the year ahead.",
            "Prepare your questions on lifestyle and preventive nutrition."
        ],
        "accepting_new_patients": True
    }
]

def find_specialists_for_markers(flagged_marker_names: List[str]) -> List[Dict[str, Any]]:
    """
    Returns tailored specialist doctor recommendations prioritized by matching out-of-range lab markers.
    """
    flagged_lower = [m.lower() for m in flagged_marker_names]
    matched = []
    others = []

    for doc in SPECIALIST_DIRECTORY:
        # Check if doctor specializes in any flagged marker
        is_match = any(any(m in target.lower() for m in flagged_lower) for target in doc["matched_biomarkers"])
        if is_match:
            matched.append(doc)
        else:
            others.append(doc)

    # Return matched first, followed by others up to 5 recommendations
    results = matched + others
    return results[:6]
