"""
scripts/populate_knowledge_base.py
Populate CARE-RAG knowledge base with medical information
Run this once to initialize the knowledge base
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.care_rag import get_care_rag

def populate_diagnostic_knowledge():
    """Add diagnostic criteria and symptoms"""
    rag = get_care_rag()
    
    documents = [
        # Diabetes
        "Type 2 Diabetes symptoms: frequent urination (polyuria), excessive thirst (polydipsia), unexplained weight loss, increased hunger, blurred vision, slow-healing sores, frequent infections, tingling in hands or feet",
        "WHO diagnostic criteria for diabetes: Fasting plasma glucose ≥126 mg/dL (7.0 mmol/L), OR 2-hour plasma glucose ≥200 mg/dL (11.1 mmol/L) during OGTT, OR HbA1c ≥6.5%, OR random plasma glucose ≥200 mg/dL with classic symptoms",
        "Prediabetes: Fasting glucose 100-125 mg/dL, HbA1c 5.7-6.4%. High risk for developing diabetes",
        
        # Hypertension
        "Hypertension symptoms: often asymptomatic (silent killer), severe headache, fatigue, vision problems, chest pain, difficulty breathing, irregular heartbeat, blood in urine",
        "Blood pressure classification: Normal <120/80, Elevated 120-129/<80, Stage 1 HTN 130-139/80-89, Stage 2 HTN ≥140/90",
        
        # Common infections
        "Malaria symptoms: fever with chills, sweating, headache, nausea, vomiting, body aches. Fever pattern: every 48-72 hours depending on species",
        "Typhoid fever: sustained high fever (103-104°F), weakness, stomach pain, headache, loss of appetite, rose spots on trunk",
        "Dengue fever: high fever, severe headache, pain behind eyes, joint and muscle pain, rash, mild bleeding (nose/gums)",
        
        # Maternal health
        "Pregnancy danger signs: vaginal bleeding, severe abdominal pain, severe headache with blurred vision, high fever, baby not moving, swelling of face/hands, convulsions",
        "Normal pregnancy symptoms: morning sickness, fatigue, frequent urination, breast tenderness, mood swings, food cravings/aversions",
    ]
    
    metadatas = [
        {"condition": "diabetes", "type": "symptoms"},
        {"condition": "diabetes", "type": "diagnostic_criteria"},
        {"condition": "prediabetes", "type": "diagnostic_criteria"},
        {"condition": "hypertension", "type": "symptoms"},
        {"condition": "hypertension", "type": "classification"},
        {"condition": "malaria", "type": "symptoms"},
        {"condition": "typhoid", "type": "symptoms"},
        {"condition": "dengue", "type": "symptoms"},
        {"condition": "pregnancy", "type": "danger_signs"},
        {"condition": "pregnancy", "type": "normal_symptoms"},
    ]
    
    rag.add_knowledge("diagnostic", documents, metadatas)
    print(f"✅ Added {len(documents)} diagnostic documents")


def populate_treatment_knowledge():
    """Add treatment protocols"""
    rag = get_care_rag()
    
    documents = [
        # Diabetes treatment
        "Type 2 Diabetes first-line treatment: Metformin 500mg twice daily with meals, gradually increase to 1000mg twice daily. Lifestyle modifications essential: diet control, regular exercise (150 min/week)",
        "Diabetes lifestyle management: Low glycemic index diet, avoid refined sugars, eat more fiber (vegetables, whole grains), portion control, regular meal timing",
        "Insulin therapy indications: HbA1c >9% despite oral medications, symptomatic hyperglycemia, pregnancy, acute illness, contraindications to oral drugs",
        
        # Hypertension treatment
        "Stage 1 Hypertension: Lifestyle modifications for 3-6 months. If BP remains elevated, start single antihypertensive (ACE inhibitor, ARB, CCB, or thiazide diuretic)",
        "Hypertension lifestyle: DASH diet (low sodium <2g/day, high potassium), weight loss if overweight, regular exercise, limit alcohol, stress management",
        
        # Common infections
        "Malaria treatment: Artemisinin-based combination therapy (ACT). For P. falciparum: Artemether-lumefantrine. Complete full course even if feeling better",
        "Typhoid treatment: Azithromycin 500mg daily for 7 days OR Ceftriaxone 2g IV daily. Fluoroquinolones if sensitive. Supportive care: hydration, rest",
        "Dengue management: No specific antiviral. Supportive care: adequate hydration (ORS), paracetamol for fever (avoid NSAIDs/aspirin), monitor for warning signs",
        
        # Maternal care
        "Antenatal care: Minimum 4 visits (1st trimester, 24-28 weeks, 32 weeks, 36 weeks). Iron-folic acid supplementation, tetanus toxoid vaccination, screening for complications",
        "Postpartum care: Rest, nutritious diet, exclusive breastfeeding for 6 months, family planning counseling, watch for danger signs (fever, heavy bleeding, foul discharge)",
    ]
    
    metadatas = [
        {"condition": "diabetes", "type": "medication"},
        {"condition": "diabetes", "type": "lifestyle"},
        {"condition": "diabetes", "type": "advanced_treatment"},
        {"condition": "hypertension", "type": "medication"},
        {"condition": "hypertension", "type": "lifestyle"},
        {"condition": "malaria", "type": "medication"},
        {"condition": "typhoid", "type": "medication"},
        {"condition": "dengue", "type": "supportive_care"},
        {"condition": "pregnancy", "type": "antenatal_care"},
        {"condition": "pregnancy", "type": "postpartum_care"},
    ]
    
    rag.add_knowledge("treatment", documents, metadatas)
    print(f"✅ Added {len(documents)} treatment documents")


def populate_preventive_knowledge():
    """Add preventive care information"""
    rag = get_care_rag()
    
    documents = [
        # Diabetes prevention
        "Diabetes prevention: Maintain healthy weight (BMI 18.5-24.9), regular physical activity (30 min/day), balanced diet (high fiber, low refined carbs), avoid tobacco, limit alcohol",
        "Prediabetes reversal: Weight loss of 5-7% body weight, 150 minutes moderate exercise per week, Mediterranean or DASH diet, regular monitoring",
        
        # Cardiovascular health
        "Heart disease prevention: Control blood pressure, manage cholesterol, don't smoke, maintain healthy weight, exercise regularly, manage stress, limit alcohol",
        "Stroke prevention: Control hypertension, manage diabetes, quit smoking, treat atrial fibrillation, healthy diet, regular exercise",
        
        # Infectious disease prevention
        "Malaria prevention: Sleep under insecticide-treated bed nets, use mosquito repellent, wear long sleeves/pants in evening, eliminate standing water",
        "Dengue prevention: Remove mosquito breeding sites (empty containers, clean water storage), use mosquito repellent, wear protective clothing",
        "Typhoid prevention: Drink safe water (boiled/filtered), eat properly cooked food, wash hands before eating, typhoid vaccination for high-risk areas",
        
        # General health
        "Vaccination schedule India: BCG, Hepatitis B, OPV, DPT, Hib, Pneumococcal, Rotavirus, Measles, Rubella, Japanese Encephalitis (as per UIP)",
        "Healthy diet basics: Eat variety of foods, more fruits and vegetables, whole grains, lean proteins, limit salt/sugar/saturated fats, adequate water intake",
        "Exercise recommendations: Adults 150 min moderate OR 75 min vigorous activity per week, muscle strengthening 2 days/week, reduce sedentary time",
    ]
    
    metadatas = [
        {"topic": "diabetes", "type": "prevention"},
        {"topic": "prediabetes", "type": "reversal"},
        {"topic": "heart_disease", "type": "prevention"},
        {"topic": "stroke", "type": "prevention"},
        {"topic": "malaria", "type": "prevention"},
        {"topic": "dengue", "type": "prevention"},
        {"topic": "typhoid", "type": "prevention"},
        {"topic": "vaccination", "type": "schedule"},
        {"topic": "nutrition", "type": "general"},
        {"topic": "exercise", "type": "recommendations"},
    ]
    
    rag.add_knowledge("preventive", documents, metadatas)
    print(f"✅ Added {len(documents)} preventive documents")


def populate_emergency_knowledge():
    """Add emergency protocols"""
    rag = get_care_rag()
    
    documents = [
        # Emergency recognition
        "Call 108 immediately for: chest pain/pressure, difficulty breathing, sudden severe headache, sudden weakness/numbness, loss of consciousness, severe bleeding, severe burns, poisoning, severe allergic reaction",
        "Stroke signs (FAST): Face drooping, Arm weakness, Speech difficulty, Time to call 108. Also: sudden confusion, trouble seeing, severe headache, loss of balance",
        "Heart attack signs: Chest pain/discomfort (pressure, squeezing), pain in arms/back/neck/jaw/stomach, shortness of breath, cold sweat, nausea, lightheadedness",
        
        # Maternal emergencies
        "Pregnancy emergencies requiring immediate hospital: Heavy vaginal bleeding, severe abdominal pain, severe headache with vision changes, high fever with chills, baby not moving, water breaks before 37 weeks, convulsions",
        "Postpartum danger signs: Heavy bleeding (soaking pad in 1 hour), severe abdominal pain, high fever, foul-smelling discharge, severe headache, chest pain, difficulty breathing",
        
        # Pediatric emergencies
        "Child emergency signs (IMNCI): Unable to drink/breastfeed, vomits everything, convulsions, lethargic/unconscious, chest indrawing, stridor in calm child",
        "Dehydration danger signs in children: Sunken eyes, skin pinch goes back slowly, lethargic, drinking poorly, no tears when crying, no urine for 6+ hours",
        
        # Common emergencies
        "Severe hypoglycemia: Confusion, seizures, loss of consciousness. Give sugar/glucose immediately if conscious, call 108 if unconscious",
        "Severe allergic reaction (anaphylaxis): Difficulty breathing, swelling of face/throat, rapid pulse, dizziness, skin rash. Use epinephrine if available, call 108",
        "Snake bite: Keep calm, immobilize affected limb, remove jewelry, do NOT cut/suck wound, do NOT apply tourniquet, go to hospital immediately for anti-venom",
    ]
    
    metadatas = [
        {"type": "general_emergency", "action": "call_108"},
        {"type": "stroke", "action": "call_108"},
        {"type": "heart_attack", "action": "call_108"},
        {"type": "pregnancy_emergency", "action": "hospital"},
        {"type": "postpartum_emergency", "action": "hospital"},
        {"type": "pediatric_emergency", "action": "call_108"},
        {"type": "dehydration", "action": "hospital"},
        {"type": "hypoglycemia", "action": "immediate_treatment"},
        {"type": "anaphylaxis", "action": "call_108"},
        {"type": "snake_bite", "action": "hospital"},
    ]
    
    rag.add_knowledge("emergency", documents, metadatas)
    print(f"✅ Added {len(documents)} emergency documents")


if __name__ == "__main__":
    print("🚀 Populating CARE-RAG Knowledge Base...")
    print("=" * 60)
    
    try:
        populate_diagnostic_knowledge()
        populate_treatment_knowledge()
        populate_preventive_knowledge()
        populate_emergency_knowledge()
        
        print("=" * 60)
        print("✅ Knowledge base populated successfully!")
        print("\nCollections created:")
        print("  - diagnostic_kb: Symptoms and diagnostic criteria")
        print("  - treatment_kb: Treatment protocols and medications")
        print("  - preventive_kb: Prevention and lifestyle guidance")
        print("  - emergency_kb: Emergency protocols and danger signs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
