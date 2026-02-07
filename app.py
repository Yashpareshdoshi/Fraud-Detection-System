from flask import Flask, render_template, request, redirect, session
import sqlite3, requests
from user_agents import parse
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fraud_secret"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("fraud.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY, user TEXT, amount REAL, risk REAL,
                  decision TEXT, ip TEXT, device TEXT, location TEXT,
                  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS alerts
                 (id INTEGER PRIMARY KEY, user TEXT, risk REAL, message TEXT,
                  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- LOCATION ----------------
def get_location_from_ip(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url).json()
        city = response.get("city", "Unknown")
        country = response.get("country", "Unknown")
        return f"{city}, {country}"
    except:
        return "Unknown"

# ---------------- ALERT ----------------
def create_alert(user, risk):
    conn = sqlite3.connect("fraud.db")
    message = f"⚠ Suspicious transaction! Risk Score: {risk}%"
    conn.execute("INSERT INTO alerts (user, risk, message) VALUES (?,?,?)",
                 (user, risk, message))
    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------
@app.route('/')
def login_page():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect("fraud.db")
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", (u,p,"user"))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    u = request.form['username']
    p = request.form['password']
    conn = sqlite3.connect("fraud.db")
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (u,p))
    data = cur.fetchone()
    conn.close()

    if data:
        session['user'] = u
        session['role'] = data[0]
        return redirect('/home')
    return "Login Failed"

@app.route('/home')
def home():
    return render_template("index.html")

# ---------------- TRANSFER + ML ----------------

def get_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return res.get("lat"), res.get("lon"), res.get("city") + ", " + res.get("country")
    except:
        return 0, 0, "Unknown"

@app.route('/transfer', methods=['POST'])
def transfer():

    user = session.get('user')
    receiver = request.form["receiver"]
    amount = float(request.form["amount"])

    # 🔹 USER DEVICE
    ua = parse(request.headers.get("User-Agent"))
    device = "Mobile" if ua.is_mobile else "PC"

    # 🔹 USER LOCATION FROM IP
    ip = request.remote_addr
    user_lat, user_lon, location = get_location(ip)

    # 🔹 MERCHANT LOCATION (dummy example)
    merchant_lat, merchant_lon = 40.7128, -74.0060  # Example: New York

    # 🔹 CURRENT TIME
    timestamp = datetime.now().isoformat()

    # 🔹 SEND TO ML API
    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json={
            "amount": amount,
            "user_lat": user_lat,
            "user_lon": user_lon,
            "merch_lat": merchant_lat,
            "merch_lon": merchant_lon,
            "timestamp": timestamp
        }
    )

    result = response.json()
    risk = result["fraud_probability"] * 100

    decision = "BLOCKED" if result["status"] == "Fraud" else "APPROVED"

    # 🔹 SAVE TRANSACTION
    conn = sqlite3.connect("fraud.db")
    conn.execute("""INSERT INTO transactions 
        (user, amount, risk, decision, ip, device, location)
        VALUES (?,?,?,?,?,?,?)""",
        (user, amount, risk, decision, ip, device, location))
    conn.commit()
    conn.close()

    # 🔹 ALERT
    if risk > 70:
        create_alert(user, risk)

    return render_template("result.html", result=result, risk=risk)

@app.route('/alerts')
def alerts():
    user = session['user']
    conn = sqlite3.connect("fraud.db")
    cur = conn.cursor()
    cur.execute("SELECT message,time FROM alerts WHERE user=? ORDER BY time DESC", (user,))
    data = cur.fetchall()
    conn.close()
    return render_template("alerts.html", alerts=data)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("fraud.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM transactions WHERE decision='BLOCKED'")
    frauds = cur.fetchone()[0]
    conn.close()
    return render_template("dashboard.html", total=total, frauds=frauds)

if __name__ == "__main__":
    app.run(debug=True)
