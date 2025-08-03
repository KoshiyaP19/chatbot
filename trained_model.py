import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Sample dataset
data = {
    'symptom_1': ['fever', 'headache', 'nausea'],
    'symptom_2': ['cough', 'vomiting', 'dizziness'],
    'symptom_3': ['sore throat', 'blurred vision', 'fatigue'],
    'disease': ['Flu', 'Migraine', 'Food Poisoning']
}
df = pd.DataFrame(data)

# Create a mapping from symptom to a unique integer
symptoms = list(set(df['symptom_1']) | set(df['symptom_2']) | set(df['symptom_3']))
symptom_map = {symptom: i for i, symptom in enumerate(symptoms)}

# Encode function
def encode(sym):
    return symptom_map.get(sym, -1)

# Encode symptoms using apply + map (future-proof)
X = df[['symptom_1', 'symptom_2', 'symptom_3']].apply(lambda col: col.map(encode))
y = df['disease']

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model and mapping
joblib.dump((model, symptom_map), 'model.joblib')
