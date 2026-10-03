from typing import Dict, Any, List

# Comprehensive medical knowledge base for clinical biomarkers
BIOMARKER_KNOWLEDGE_BASE = {
    "Fasting Blood Glucose": {
        "definition": "Measures the amount of sugar (glucose) in your bloodstream after an overnight fast (typically 8–12 hours).",
        "high_explanation": "Elevated levels may indicate prediabetes or diabetes mellitus, insulin resistance, or acute physiological stress. Cells are not absorbing circulating glucose efficiently.",
        "low_explanation": "Subnormal levels (hypoglycemia) may occur with prolonged starvation, medication side effects, or excessive insulin production.",
        "lifestyle_tips": "Focus on complex low-glycemic carbohydrates, lean proteins, regular physical exercise (e.g. 30 min daily brisk walking), and consistent meal timing.",
        "category": "Endocrinology & Metabolism"
    },
    "HbA1c (Glycated Hemoglobin)": {
        "definition": "Reflects your average blood sugar concentration over the past 2 to 3 months by measuring the percentage of hemoglobin bound to glucose.",
        "high_explanation": "Values at or above 5.7% indicate prediabetes; 6.5% or above indicates diabetes mellitus. Sustained elevation increases risk of microvascular complications.",
        "low_explanation": "Unusually low levels are rare and may relate to hemolytic anemia or recent severe blood loss with rapid red cell turnover.",
        "lifestyle_tips": "Adopt Mediterranean dietary patterns, minimize refined sugars and ultra-processed snacks, track post-meal glucose spikes, and maintain regular sleep hygiene.",
        "category": "Endocrinology & Metabolism"
    },
    "Total Cholesterol": {
        "definition": "The cumulative estimate of all circulating sterol lipids in your blood, including LDL, HDL, and VLDL particles.",
        "high_explanation": "Elevated levels contribute to plaque buildup (atherosclerosis) inside arterial walls, raising long-term cardiovascular event risks.",
        "low_explanation": "Extremely low levels can occasionally associate with malnutrition, hyperthyroidism, or chronic liver conditions.",
        "lifestyle_tips": "Replace saturated and trans fats with monounsaturated oils (extra virgin olive oil, avocado), boost soluble dietary fiber (oats, legumes), and avoid smoking.",
        "category": "Cardiovascular Health"
    },
    "LDL Cholesterol": {
        "definition": "Often termed 'bad cholesterol', Low-Density Lipoprotein carries cholesterol particles throughout your vascular tree.",
        "high_explanation": "Excess LDL oxidizes and deposits into arterial linings, forming atherosclerotic plaques and narrowing coronary and carotid arteries.",
        "low_explanation": "Generally considered favorable for cardiovascular protection; exceptionally low levels should be evaluated with your doctor.",
        "lifestyle_tips": "Increase plant sterols, soluble fiber (chia seeds, psyllium husk), and engage in regular aerobic conditioning.",
        "category": "Cardiovascular Health"
    },
    "HDL Cholesterol": {
        "definition": "Referred to as 'good cholesterol', High-Density Lipoprotein scavenges excess cholesterol from blood vessels and transports it to the liver for excretion.",
        "high_explanation": "Higher values (typically > 50-60 mg/dL) are generally cardioprotective against coronary artery disease.",
        "low_explanation": "Suboptimal HDL removes less arterial cholesterol, which independently correlates with higher atherosclerotic cardiovascular risk.",
        "lifestyle_tips": "Engage in moderate-to-vigorous resistance and aerobic exercise, incorporate omega-3 fatty acids (salmon, walnuts, flaxseed), and maintain healthy body weight.",
        "category": "Cardiovascular Health"
    },
    "Triglycerides": {
        "definition": "The most common form of stored fat in your body, synthesized from surplus dietary calories.",
        "high_explanation": "High levels contribute to hardening of arterial walls and, when markedly elevated (>500 mg/dL), increase the risk of acute pancreatitis.",
        "low_explanation": "Rarely of clinical concern; occasionally seen in severe malnutrition or malabsorption syndromes.",
        "lifestyle_tips": "Significantly restrict sugary beverages, alcohol intake, refined white flours, and simple syrups.",
        "category": "Cardiovascular Health"
    },
    "Serum Creatinine": {
        "definition": "A chemical waste byproduct produced by everyday muscle metabolism and eliminated exclusively by renal filtration.",
        "high_explanation": "Elevated creatinine implies decreased glomerular filtration rate (GFR) in the kidneys, indicating acute kidney stress or chronic renal impairment.",
        "low_explanation": "Low levels are commonly associated with reduced muscle mass, advanced age, or low dietary protein consumption.",
        "lifestyle_tips": "Maintain adequate daily hydration, avoid excessive unprescribed NSAID pain medications (ibuprofen, naproxen), and monitor blood pressure closely.",
        "category": "Nephrology & Renal Function"
    },
    "Blood Urea Nitrogen (BUN)": {
        "definition": "Measures the amount of nitrogen in your blood that comes from the waste product urea, produced during protein breakdown.",
        "high_explanation": "Elevated BUN can indicate dehydration, high protein intake, gastrointestinal bleeding, or impaired renal clearance.",
        "low_explanation": "May occur in low-protein diets, severe liver disease, or overhydration.",
        "lifestyle_tips": "Ensure consistent daily water intake and evaluate overall protein supplementation with a registered dietitian.",
        "category": "Nephrology & Renal Function"
    },
    "Hemoglobin": {
        "definition": "The iron-rich protein in red blood cells that binds oxygen in the lungs and delivers it to tissues throughout the body.",
        "high_explanation": "Elevated values can result from chronic dehydration, living at high altitudes, smoking, or myeloproliferative disorders like polycythemia vera.",
        "low_explanation": "Lower than normal values signify anemia (iron deficiency, chronic disease, or B12/folate deficiency), causing fatigue and shortness of breath.",
        "lifestyle_tips": "If low, explore dietary iron sources (spinach, lentils, lean poultry) paired with vitamin C for enhanced absorption.",
        "category": "Hematology"
    },
    "Thyroid Stimulating Hormone (TSH)": {
        "definition": "A pituitary hormone that signals your thyroid gland to produce thyroxine (T4) and triiodothyronine (T3).",
        "high_explanation": "Elevated TSH indicates an underactive thyroid (hypothyroidism). The pituitary produces extra TSH in an effort to stimulate thyroid output.",
        "low_explanation": "Low TSH signals an overactive thyroid gland (hyperthyroidism), leading to elevated metabolic rate, tremors, or palpitations.",
        "lifestyle_tips": "Avoid self-medicating with large doses of kelp/iodine; maintain steady micronutrient intake (selenium, zinc) and follow up with an endocrinologist.",
        "category": "Endocrinology & Thyroid"
    },
    "Vitamin D (25-OH)": {
        "definition": "A critical fat-soluble secosteroid involved in intestinal calcium absorption, immune function, and bone mineralization.",
        "high_explanation": "Excessive accumulation is rare and almost always due to extreme over-supplementation, potentially causing hypercalcemia.",
        "low_explanation": "Deficiency is widespread and can result in bone weakness (osteomalacia/osteoporosis), muscle aches, and depressed immune resilience.",
        "lifestyle_tips": "Get sensible sunlight exposure (15-20 mins midday), consume fortified foods, and consult your physician regarding vitamin D3/K2 supplementation.",
        "category": "Nutritional & Preventive Health"
    }
}

def get_biomarker_rag_context(test_name: str, status: str, value: float, unit: str) -> Dict[str, Any]:
    """Retrieve synthesized clinical RAG context for an individual biomarker."""
    info = BIOMARKER_KNOWLEDGE_BASE.get(test_name)
    if not info:
        # Generic fallback
        return {
            "test_name": test_name,
            "category": "General Clinical Biomarker",
            "summary": f"{test_name} measures an important physiological indicator. Current recorded value is {value} {unit} ({status}).",
            "clinical_significance": f"Status is {status}. Consult your physician to evaluate in context of your total metabolic profile.",
            "lifestyle_tips": "Maintain balanced hydration, whole foods nutrition, and regular restorative sleep."
        }
    
    explanation = info["high_explanation"] if status == "HIGH" else (info["low_explanation"] if status == "LOW" else "Your result falls squarely within the healthy physiological reference interval.")
    
    return {
        "test_name": test_name,
        "category": info["category"],
        "summary": info["definition"],
        "clinical_significance": explanation,
        "lifestyle_tips": info["lifestyle_tips"]
    }

def synthesize_rag_overview(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synthesize holistic educational guidance from a collection of lab tests."""
    high_count = sum(1 for t in test_results if t.get("status") == "HIGH")
    low_count = sum(1 for t in test_results if t.get("status") == "LOW")
    normal_count = sum(1 for t in test_results if t.get("status") == "NORMAL")
    total = len(test_results)

    out_of_range = [t for t in test_results if t.get("status") in ("HIGH", "LOW")]

    # Categorize out of range tests
    flagged_summaries = []
    for item in out_of_range:
        ctx = get_biomarker_rag_context(item["test_name"], item["status"], item["value"], item.get("unit", ""))
        flagged_summaries.append({
            "test_name": item["test_name"],
            "value": item["value"],
            "unit": item.get("unit", ""),
            "status": item["status"],
            "category": ctx["category"],
            "explanation": ctx["clinical_significance"],
            "guidance": ctx["lifestyle_tips"]
        })

    educational_briefing = (
        f"Mediscope has parsed {total} biomarkers from your laboratory documentation. "
        f"{normal_count} markers are within optimal ranges, while {len(out_of_range)} require clinical attention with your physician."
    )

    return {
        "total_analyzed": total,
        "normal_count": normal_count,
        "high_count": high_count,
        "low_count": low_count,
        "flagged_markers": flagged_summaries,
        "educational_briefing": educational_briefing,
        "disclaimer": "Mediscope is an educational health report companion, NOT a diagnostic platform or medical decision system."
    }
