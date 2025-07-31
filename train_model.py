from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

# Sample data (symptom description mapped to disease)
data = {
    "fever cough sore throat body ache": "Flu",
    "headache sensitivity to light nausea": "Migraine",
    "chest pain shortness of breath fatigue": "Heart Disease",
    "itchy skin rashes redness swelling": "Skin Allergy",
    "runny nose sneezing mild fever": "Common Cold",
    "vomiting diarrhea stomach pain dehydration": "Food Poisoning",
    "high fever joint pain skin rash bleeding": "Dengue",
    "shortness of breath wheezing chest tightness": "Asthma",
    "fever dry cough tiredness loss of taste": "COVID-19",
    "prolonged fever weakness abdominal pain loss of appetite": "Typhoid"
}

# Training data
X = list(data.keys())
y = list(data.values())

# Create a pipeline: vectorizer + classifier
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', MultinomialNB())
])

# Train the model
model.fit(X, y)

# Save the model
joblib.dump(model, "model.joblib")

print("✅ Model trained and saved as model.joblib")
