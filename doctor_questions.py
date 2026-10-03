from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .models import Report, Patient

def generate_doctor_consultation_questions(patient_id: str, db: Session) -> Dict[str, Any]:
    """
    Synthesizes tailored, patient-centric consultation questions based on out-of-range
    and high-risk laboratory findings for upcoming doctor appointments.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return {"error": "Patient not found", "questions": []}

    latest_report = (
        db.query(Report)
        .filter(Report.patient_id == patient_id)
        .order_by(Report.report_date.desc(), Report.created_at.desc())
        .first()
    )

    if not latest_report:
        return {
            "patient_name": patient.full_name,
            "has_reports": False,
            "message": "No laboratory reports found for this patient. Add a report to generate personalized consultation questions.",
            "general_questions": [
                "What baseline wellness screening panels do you recommend for my age group and medical history?",
                "Are there any chronic condition risks given my family history that I should proactively monitor?",
                "How often should I schedule preventative routine blood work?"
            ],
            "categorized_questions": []
        }

    out_of_range = [t for t in latest_report.test_results if t.status in ("HIGH", "LOW")]
    
    questions = []

    for test in out_of_range:
        t_name = test.test_name
        status = test.status
        val = test.value
        unit = test.unit or ""

        if "glucose" in t_name.lower() or "hba1c" in t_name.lower():
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Metabolic & Glycemic Control",
                "question": f"My {t_name} is currently flagged as {status} at {val} {unit}. Does this indicate progressive insulin resistance or prediabetes, and what specific target range should we aim for over the next 90 days?",
                "context": "Helps clarify if dietary intervention alone is sufficient or if pharmaceutical support or continuous glucose monitoring is warranted."
            })
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Lifestyle & Nutrition",
                "question": f"Given my elevated blood sugar levels, should I consult a registered clinical dietitian, and are there specific glycemic index thresholds I should maintain?",
                "context": "Directs clinical discussion to evidence-based medical nutritional therapy."
            })

        elif "cholesterol" in t_name.lower() or "ldl" in t_name.lower() or "triglycerides" in t_name.lower():
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Cardiovascular Risk Management",
                "question": f"My {t_name} came back at {val} {unit} ({status}). Based on my overall cardiovascular risk score, should we consider advanced lipid fractionation (ApoB/Lp(a)) or a coronary artery calcium (CAC) scan?",
                "context": "Evaluates whether plaque formation risk necessitates lipid-lowering therapy or lifestyle protocol changes."
            })

        elif "creatinine" in t_name.lower() or "bun" in t_name.lower():
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Renal & Kidney Function",
                "question": f"My {t_name} is {status} at {val} {unit}. Could this be influenced by dehydration, protein intake, or medications, and should we evaluate my estimated GFR (eGFR) and urine albumin-to-creatinine ratio (uACR)?",
                "context": "Differentiates transient renal stress from chronic kidney disease."
            })

        elif "tsh" in t_name.lower() or "thyroxine" in t_name.lower():
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Thyroid & Endocrine Function",
                "question": f"With my {t_name} testing {status} at {val} {unit}, should we perform a full thyroid antibody panel (TPO antibodies) or thyroid ultrasound to investigate autoimmune thyroiditis?",
                "context": "Clarifies etiology of thyroid dysfunction."
            })

        elif "vitamin d" in t_name.lower():
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Nutritional Optimization",
                "question": f"My Vitamin D level is {status} at {val} {unit}. What weekly therapeutic dosing (e.g., 50,000 IU D3 vs daily 2,000–5,000 IU) do you recommend, and when should we recheck my levels?",
                "context": "Ensures appropriate therapeutic repletion protocol."
            })

        elif "hemoglobin" in t_name.lower() or "wbc" in t_name.lower() or "platelet" in t_name.lower():
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "Hematology & Immune Profile",
                "question": f"My {t_name} is {status} at {val} {unit}. Does this warrant an iron study (ferritin, transferrin saturation) or peripheral blood smear evaluation?",
                "context": "Investigates root cause of cellular variations."
            })

        else:
            questions.append({
                "biomarker": t_name,
                "finding": f"{status} ({val} {unit})",
                "category": "General Clinical Evaluation",
                "question": f"My report flags {t_name} as {status} at {val} {unit}. In the context of my overall health and current symptoms, what physiological mechanism could explain this variation?",
                "context": "Opens a collaborative dialogue with your healthcare provider."
            })

    # Add follow-up & retesting questions
    followup_questions = [
        "What is the recommended timeline to repeat this blood panel to observe if these values normalize?",
        "Are there any prescription medications or over-the-counter supplements I am taking that could interact with these biomarker results?",
        "Should I monitor any specific symptoms at home (e.g. blood pressure, energy changes, fluid retention) between now and our next appointment?"
    ]

    return {
        "patient_name": patient.full_name,
        "relationship": patient.relationship_type,
        "report_date": latest_report.report_date,
        "total_out_of_range": len(out_of_range),
        "categorized_questions": questions,
        "followup_questions": followup_questions,
        "safety_disclaimer": "Mediscope is an educational health report companion, NOT a diagnostic platform. Discuss these questions with your licensed physician."
    }
