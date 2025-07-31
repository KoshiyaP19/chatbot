from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Simulate ML model with rules
disease_rules = {
    'fever,cough,sore throat': ('Flu', 'Stay hydrated and rest.'),
    'headache,nausea,blurred vision': ('Migraine', 'Avoid bright lights. Take prescribed painkillers.'),
    'chest pain,shortness of breath': ('Heart Issue', 'Seek emergency care immediately.'),
    'rash,itching,swelling': ('Allergy', 'Use antihistamines. Avoid allergens.'),
    'stomach pain,diarrhea,vomiting': ('Food Poisoning', 'Stay hydrated. Eat light.'),
}

# Hospital suggestions
hospital_info = {
    'Flu': 'City General Hospital',
    'Migraine': 'NeuroCare Clinic',
    'Heart Issue': 'Apollo Heart Center',
    'Allergy': 'Skin & Allergy Clinic',
    'Food Poisoning': 'HealthPlus Hospital',
}

# Store user session symptoms
session_symptoms = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def message():
    global session_symptoms
    data = request.get_json()
    user_input = data.get("message", "").lower()

    # Reset logic
    if "reset" in user_input:
        session_symptoms = []
        return jsonify(response="Session reset. Please start by telling your first symptom.")

    # Add symptom
    session_symptoms.append(user_input)

    # Check if enough symptoms
    if len(session_symptoms) < 3:
        return jsonify(response=f"Do you have anyother symptom {len(session_symptoms)+1}.")

    # Try diagnosis
    combined = ",".join(session_symptoms)
    diagnosis = None
    for symptoms, (disease, advice) in disease_rules.items():
        required = symptoms.split(',')
        if all(symptom in combined for symptom in required):
            diagnosis = (disease, advice)
            break

    if diagnosis:
        disease, advice = diagnosis
        hospital = hospital_info[disease]
        log_diagnosis(disease, session_symptoms)
        session_symptoms = []  # Reset session after diagnosis
        response = (
            f"Based on your symptoms, you may have **{disease}**.\n"
            f"Advice: {advice}\n"
            f"Suggested Hospital: {hospital}"
        )
        return jsonify(response=response)
    else:
        return jsonify(response="Thanks. Please tell me more symptoms for accurate diagnosis.")

def log_diagnosis(disease, symptoms):
    with open("diagnosis_log.txt", "a") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - Disease: {disease}, Symptoms: {', '.join(symptoms)}\n")

if __name__ == "__main__":
    app.run(debug=True)
