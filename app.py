from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import joblib
import datetime
import os
import requests
from flask_cors import CORS
from datetime import datetime


app = Flask(__name__)    # 👈 This defines 'app'
CORS(app)    


app.secret_key = 'your_secret_key'

model, symptom_map = joblib.load('model.joblib')

advice_map = {
    'Flu': 'Drink fluids and rest. Use a humidifier to ease congestion.',
    'Migraine': 'Stay in a dark, quiet room. Take prescribed medications.',
    'Food Poisoning': 'Stay hydrated and avoid solid food for a few hours.'
}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] and request.form['password']:
            session['username'] = request.form['username']
            return redirect('/chat')
        session['username'] = username

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return redirect('/login')
    return render_template('register.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        step = int(request.form['step'])
        chat_history = session.get('chat_history', [])

        message = request.form['message']
        chat_history.append(("Patient", message))

        if step == 1:
            session['symptom_1'] = message
            reply = "Please enter your second symptom:"
        elif step == 2:
            session['symptom_2'] = message
            reply = "Please enter your third symptom:"
        else:
            session['symptom_3'] = message
            s1 = symptom_map.get(session['symptom_1'], -1)
            s2 = symptom_map.get(session['symptom_2'], -1)
            s3 = symptom_map.get(session['symptom_3'], -1)
            prediction = model.predict([[s1, s2, s3]])[0]
            advice = advice_map.get(prediction, "Consult a nearby doctor.")
            
            reply = f"Based on your symptoms, you may have: {prediction}.\n Advice: {advice}"
            
            # ✅ Save to user-specific file
            username = session.get('username')
            if username:
                with open(f"history_{username}.txt", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {prediction}\n")

            # ✅ Clear session chat state
            session.pop('symptom_1', None)
            session.pop('symptom_2', None)
            session.pop('symptom_3', None)
            session.pop('chat_history', None)

        chat_history.append(("Bot", reply))
        session['chat_history'] = chat_history
        return render_template('chat.html', chat_history=chat_history, step=min(step+1, 3))

    # GET method
    session['chat_history'] = []
    return render_template('chat.html', chat_history=[], step=1)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route("/history")
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    history_file = f"history_{username}.txt"
    
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history_data = f.readlines()
    else:
        history_data = []

    return render_template("history.html", history=history_data, username=username)



@app.route('/find_hospitals', methods=['POST'])
def find_hospitals():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        lat = data.get('latitude')
        lon = data.get('longitude')

        if lat is None or lon is None:
            return jsonify({'error': 'Missing latitude or longitude'}), 400

        lat = float(lat)
        lon = float(lon)

        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'format': 'json',
            'q': 'hospital',
            'limit': 10,
            'bounded': 1,
            'viewbox': f"{lon - 0.1},{lat + 0.1},{lon + 0.1},{lat - 0.1}"
        }
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        results = response.json()
        hospitals = [{'name': r.get('display_name'), 'lat': r.get('lat'), 'lon': r.get('lon')} for r in results]

        return jsonify({'hospitals': hospitals})

    except Exception as e:
        import traceback
        print("Error fetching hospital data:", traceback.format_exc())
        return jsonify({'error': 'Failed to fetch hospital data'}), 500



if __name__ == '__main__':
    app.run(debug=True)
