from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .models import Report, TestResult

def compute_patient_trends(patient_id: str, db: Session) -> Dict[str, Any]:
    """
    Computes exact longitudinal deltas between prior and current lab reports for a patient.
    E.g. Fasting Glucose: June 128 mg/dL -> Current 115 mg/dL | Delta: -13 mg/dL
    """
    reports = (
        db.query(Report)
        .filter(Report.patient_id == patient_id)
        .order_by(Report.report_date.desc(), Report.created_at.desc())
        .all()
    )

    if not reports or len(reports) < 2:
        # If user only has 1 report or none, provide current baseline or empty comparison
        current_report = reports[0] if reports else None
        current_tests = []
        if current_report:
            current_tests = [
                {
                    "test_name": t.test_name,
                    "current_value": t.value,
                    "previous_value": None,
                    "delta": 0.0,
                    "unit": t.unit or "",
                    "current_date": current_report.report_date,
                    "previous_date": None,
                    "status_current": t.status,
                    "status_previous": None,
                    "trend_direction": "BASELINE"
                }
                for t in current_report.test_results
            ]
        return {
            "has_historical_comparison": False,
            "message": "At least two reports are required to calculate historical deltas. Showing baseline values.",
            "comparisons": current_tests,
            "report_count": len(reports)
        }

    current_report = reports[0]
    previous_report = reports[1]

    # Map previous report results by test_name
    prev_map = {t.test_name: t for t in previous_report.test_results}
    comparisons = []

    for curr_test in current_report.test_results:
        t_name = curr_test.test_name
        prev_test = prev_map.get(t_name)

        if prev_test:
            delta = round(curr_test.value - prev_test.value, 2)
            
            # Clinical interpretation of delta direction
            # For markers where lower is better (Glucose, HbA1c, LDL, Triglycerides, Creatinine, etc.)
            lower_is_better = any(kw in t_name.lower() for kw in ["glucose", "hba1c", "cholesterol", "ldl", "triglycerides", "creatinine", "bun", "uric acid", "alt", "ast", "tsh"])
            higher_is_better = any(kw in t_name.lower() for kw in ["hdl", "vitamin d", "b12", "hemoglobin", "platelet"])
            
            trend_direction = "STABLE"
            if abs(delta) > 0.01:
                if lower_is_better:
                    if delta < 0:
                        trend_direction = "IMPROVED"
                    else:
                        trend_direction = "WORSENED"
                elif higher_is_better:
                    if delta > 0:
                        trend_direction = "IMPROVED"
                    else:
                        trend_direction = "WORSENED"
                else:
                    trend_direction = "CHANGED"

            comparisons.append({
                "test_name": t_name,
                "current_value": curr_test.value,
                "previous_value": prev_test.value,
                "delta": delta,
                "delta_formatted": f"{'+' if delta > 0 else ''}{delta} {curr_test.unit or ''}".strip(),
                "unit": curr_test.unit or "",
                "current_date": current_report.report_date,
                "previous_date": previous_report.report_date,
                "status_current": curr_test.status,
                "status_previous": prev_test.status,
                "trend_direction": trend_direction
            })
        else:
            # Test not present in prior report
            comparisons.append({
                "test_name": t_name,
                "current_value": curr_test.value,
                "previous_value": None,
                "delta": 0.0,
                "delta_formatted": "N/A",
                "unit": curr_test.unit or "",
                "current_date": current_report.report_date,
                "previous_date": None,
                "status_current": curr_test.status,
                "status_previous": None,
                "trend_direction": "NEW_BIOMARKER"
            })

    return {
        "has_historical_comparison": True,
        "current_report_name": current_report.report_name,
        "current_date": current_report.report_date,
        "previous_report_name": previous_report.report_name,
        "previous_date": previous_report.report_date,
        "comparisons": comparisons,
        "report_count": len(reports)
    }
