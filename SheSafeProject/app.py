from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'yoursecretkey'

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Load users from users.json
def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save users to users.json
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)

# ------------------ ROUTES ------------------ #
@app.route('/')
def home():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']
        users[username] = password
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/product')
def product():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template('product.html')

@app.route('/solutions')
def solutions():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template('solutions.html')

@app.route('/community')
def community():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template('community.html')

@app.route('/resources')
def resources():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template('resources.html')

@app.route('/contact')
def contact():
    if not session.get("user"):
        return redirect(url_for('login'))
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/buddy')
def buddy():
    return render_template('buddy.html')

# ----------------- TWILIO FEATURE ---------------- #
@app.route('/twilio', methods=['GET', 'POST'])
def twilio_page():
    if not session.get("user"):
        return redirect(url_for('login'))

    if request.method == 'POST':
        phone = request.form.get("user_number")
        lat = request.form.get("latitude")
        lon = request.form.get("longitude")

        location_link = f"https://maps.google.com/?q={lat},{lon}"
        sms_body = f"🚨 Emergency Alert!\nLive Location: {location_link}"

        try:
            # Send SMS
            client.messages.create(
                body=sms_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )

            # Voice call with simple alert
            client.calls.create(
                twiml='<Response><Say>This is an emergency alert from SheSafe. Please check your messages for live location.</Say></Response>',
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )

            return "🚨 Emergency alert sent successfully!"
        except Exception as e:
            return f"Error sending alert: {str(e)}"

    return render_template('twilio.html')

# -------------------------------------------- #
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    eligible = []

    with open('schemes.json', encoding='utf-8') as f:
        schemes = json.load(f)

    if request.method == 'POST':
        age = int(request.form['age'])
        income = int(request.form['income'])
        gender = request.form['gender']
        state = request.form['state']
        marital_status = request.form['marital_status']
        education_level = request.form['education_level']
        religion = request.form.get('religion', '').strip()
        pregnant = request.form.get('pregnant') == 'yes'

        for scheme in schemes:
            if scheme["state"] != ["All"] and state not in scheme["state"]:
                continue
            if "gender" in scheme and scheme["gender"] != gender:
                continue
            if "min_age" in scheme and age < scheme["min_age"]:
                continue
            if "max_age" in scheme and age > scheme["max_age"]:
                continue
            if "income_limit" in scheme and income > scheme["income_limit"]:
                continue
            if "marital_status" in scheme and scheme["marital_status"] != "any" and scheme["marital_status"] != marital_status:
                continue
            if "education_level" in scheme and scheme["education_level"] != "any" and scheme["education_level"] != education_level:
                continue
            if "pregnant_required" in scheme and scheme["pregnant_required"] and not pregnant:
                continue
            if "religion" in scheme and scheme["religion"] != "any" and scheme["religion"].lower() != religion.lower():
                continue

            eligible.append(scheme)

    return render_template('explore.html', eligible=eligible)
if __name__ == '__main__':
    app.run(debug=True)