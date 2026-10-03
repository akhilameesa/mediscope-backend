from typing import List, Dict, Any
from datetime import datetime

CURRENT_OUTBREAK_DATA: List[Dict[str, Any]] = [
    {
        "id": "inf-1",
        "name": "Influenza A (H3N2 Clade 2a.3a.1)",
        "type": "Respiratory Viral Pathogen",
        "risk_level": "High",
        "regional_hotspots": "North America, Western Europe, East Asia",
        "spread_trend": "Surging (+18.4% weekly)",
        "transmission_vector": "Airborne respiratory droplets & contaminated fomites",
        "primary_symptoms": [
            "Sudden high fever (>102°F / 38.9°C)",
            "Severe myalgia and generalized arthralgia",
            "Non-productive hacking cough",
            "Extreme fatigue and cephalalgia"
        ],
        "clinical_precaution_guidelines": [
            "Annual seasonal quadrivalent influenza immunization strongly advised.",
            "High-efficiency particulate air (HEPA) filtration in indoor shared spaces.",
            "Early initiation of neuraminidase inhibitors (e.g., Oseltamivir) within 48h of symptom onset for high-risk patients."
        ],
        "last_updated": "2026-10-03"
    },
    {
        "id": "inf-2",
        "name": "Dengue Virus (DENV-2 & DENV-3 Serotypes)",
        "type": "Vector-Borne Arbovirus",
        "risk_level": "High",
        "regional_hotspots": "South Asia, Southeast Asia, Central & South America",
        "spread_trend": "Elevated (+12.1% season-on-season)",
        "transmission_vector": "Bite of infected female Aedes aegypti / Aedes albopictus mosquitoes",
        "primary_symptoms": [
            "Biphasic high fever",
            "Severe retro-orbital pain (pain behind the eyes)",
            "Maculopapular petechial skin rash",
            "Thrombocytopenia (sudden platelet drop) & plasma leakage signs"
        ],
        "clinical_precaution_guidelines": [
            "Eliminate standing water reservoirs around living quarters weekly.",
            "Apply EPA-approved DEET (20-30%) or Picaridin mosquito repellents.",
            "Strictly avoid Aspirin or NSAIDs (due to hemorrhage risk); use acetaminophen under medical guidance."
        ],
        "last_updated": "2026-10-03"
    },
    {
        "id": "inf-3",
        "name": "Respiratory Syncytial Virus (RSV Subtype B)",
        "type": "Pneumovirus (Lower Respiratory)",
        "risk_level": "Moderate",
        "regional_hotspots": "Suburban Pediatric & Geriatric Communities",
        "spread_trend": "Moderate / Plateauing (+3.2% weekly)",
        "transmission_vector": "Direct contact with oral secretions and aerosol inhalation",
        "primary_symptoms": [
            "Wheezing and tachypnea (rapid breathing)",
            "Persistent intercostal chest retractions in infants",
            "Copious rhinorrhea and lethargy",
            "Hypoxemia in adults over 65 with cardiopulmonary comorbidity"
        ],
        "clinical_precaution_guidelines": [
            "RSV bivalent prefusion F vaccine recommended for adults 60+ and pregnant women in weeks 32-36.",
            "Monoclonal antibody prophylaxis (Nirsevimab) for eligible neonates and infants.",
            "Rigorous hand hygiene with alcohol-based sanitizers."
        ],
        "last_updated": "2026-10-03"
    },
    {
        "id": "inf-4",
        "name": "SARS-CoV-2 (Omicron KP.3.1.1 Sub-lineage)",
        "type": "Coronaviridae Respiratory Virus",
        "risk_level": "Moderate",
        "regional_hotspots": "Global surveillance / Urban transportation hubs",
        "spread_trend": "Active transmission (+6.7% positivity)",
        "transmission_vector": "Aerosolized micro-droplet inhalation in enclosed settings",
        "primary_symptoms": [
            "Sore throat with razor-blade sensation",
            "Mild-to-moderate fever and chills",
            "Sinus congestion and loss of taste/smell (transient)",
            "Gastrointestinal upset in 15% of clinical presentations"
        ],
        "clinical_precaution_guidelines": [
            "Maintain updated updated seasonal mRNA booster coverage.",
            "Wear well-fitted N95/KF94 masks during high-density indoor public transits.",
            "Isolate upon positive antigen test; oral antivirals (Paxlovid) for qualified high-risk individuals."
        ],
        "last_updated": "2026-10-03"
    },
    {
        "id": "inf-5",
        "name": "Norovirus (GII.4 Sydney Strain)",
        "type": "Enteric Calicivirus",
        "risk_level": "Moderate",
        "regional_hotspots": "Educational Institutions, Cruise lines, Food-service facilities",
        "spread_trend": "Clustered Outbreaks",
        "transmission_vector": "Fecal-oral route, ingestion of contaminated water/food, contact with fomites",
        "primary_symptoms": [
            "Acute projectile vomiting",
            "Watery non-bloody diarrhea",
            "Abdominal cramping and mild fever",
            "Rapid dehydration risk"
        ],
        "clinical_precaution_guidelines": [
            "Wash hands thoroughly with warm water and soap for 20 seconds (alcohol sanitizers are ineffective against non-enveloped virions).",
            "Disinfect contaminated surfaces using chlorine bleach solutions (1,000 to 5,000 ppm).",
            "Aggressive oral rehydration salts (ORS) maintenance."
        ],
        "last_updated": "2026-10-03"
    }
]

def get_outbreak_statistics() -> Dict[str, Any]:
    """Returns current active infections, viral trends, and regional risk levels."""
    return {
        "status": "success",
        "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        "total_tracked_pathogens": len(CURRENT_OUTBREAK_DATA),
        "high_risk_count": sum(1 for item in CURRENT_OUTBREAK_DATA if item["risk_level"] == "High"),
        "moderate_risk_count": sum(1 for item in CURRENT_OUTBREAK_DATA if item["risk_level"] == "Moderate"),
        "infections": CURRENT_OUTBREAK_DATA,
        "global_alert_summary": "Surveillance indicates heightened co-circulation of Influenza A (H3N2) and vector-borne Dengue arbovirus in tropical and temperate transition corridors. Adhere to clinical vaccination schedules and vector barrier controls."
    }
