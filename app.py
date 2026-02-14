from flask import Flask, render_template, request, redirect, session
import sqlite3, requests
from user_agents import parse
from datetime import datetime
from utils import haversine

app = Flask(__name__)
app.secret_key = "fraud_secret"

# ================== FRAUD ENGINE ==================
def calculate_final_fraud_decision(
    amount,
    distance,
    time_diff_hours,
    is_night,
    ml_probability
):

    MAX_TRANSACTION_LIMIT = 500000
    HIGH_AMOUNT_LIMIT = 300000
    MEDIUM_AMOUNT_LIMIT = 150000

    # HARD LIMIT
    if amount >= MAX_TRANSACTION_LIMIT:
        return {
            "risk_score": 100,
            "decision": "BLOCKED",
            "reason": "Exceeded maximum bank transaction limit"
        }

    risk_score = (ml_probability * 100) * 0.4
    reasons = []

    # Amount Risk
    if amount >= HIGH_AMOUNT_LIMIT:
        risk_score += 40
        reasons.append("Very high amount")

    elif amount >= MEDIUM_AMOUNT_LIMIT:
        risk_score += 25
        reasons.append("High amount")

    # Geo Velocity
    if time_diff_hours > 0:
        speed = distance / time_diff_hours
    else:
        speed = 0

    if speed > 900:
        risk_score += 50
        reasons.append("Impossible travel speed")

    elif speed > 500:
        risk_score += 30
        reasons.append("Suspicious travel speed")

    # Distance Risk
    if distance > 4000:
        risk_score += 30
        reasons.append("Very large location change")

    elif distance > 2000:
        risk_score += 20
        reasons.append("Large location change")

    # Night Risk
    if is_night:
        risk_score += 15
        reasons.append("Night transaction")

        if amount > 100000:
            risk_score += 15
            reasons.append("High amount at night")

    # Final Decision
    if risk_score >= 80:
        decision = "BLOCKED"
    elif risk_score >= 50:
        decision = "ALERT"
    else:
        decision = "APPROVED"

    return {
        "risk_score": round(min(risk_score, 100), 2),
        "decision": decision,
        "reason": ", ".join(reasons) if reasons else "Normal transaction"
    }


# ================== DATABASE ==================
def init_db():
    conn = sqlite3.connect("fraud.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY,
                  user TEXT,
                  amount REAL,
                  risk REAL,
                  decision TEXT,
                  ip TEXT,
                  device TEXT,
                  location TEXT,
                  latitude REAL,
                  longitude REAL,
                  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS alerts
                 (id INTEGER PRIMARY KEY,
                  user TEXT,
                  risk REAL,
                  message TEXT,
                  time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    conn.commit()
    conn.close()

init_db()


# ================== LOCATION ==================
def get_location(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        return (
            res.get("lat", 0),
            res.get("lon", 0),
            f"{res.get('city','Unknown')}, {res.get('country','Unknown')}"
        )
    except:
        return 0, 0, "Unknown"


# ================== ALERT ==================
def create_alert(user, risk):
    conn = sqlite3.connect("fraud.db")
    message = f"⚠ Suspicious transaction! Risk Score: {round(risk,2)}%"
    conn.execute("INSERT INTO alerts (user, risk, message) VALUES (?,?,?)",
                 (user, risk, message))
    conn.commit()
    conn.close()


# ================== ROUTES ==================
@app.route('/')
def login_page():
    return render_template("login.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect("fraud.db")
        conn.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                     (u, p, "user"))
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
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p))
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


# ================== TRANSFER ==================
@app.route('/transfer', methods=['POST'])
def transfer():

    user = session.get('user')
    receiver = request.form["receiver"]
    amount = float(request.form["amount"])

    ua = parse(request.headers.get("User-Agent"))
    device = "Mobile" if ua.is_mobile else "PC"

    ip = request.remote_addr
    user_lat, user_lon, location = get_location(ip)

    conn = sqlite3.connect("fraud.db")
    cur = conn.cursor()

    # Last transaction
    cur.execute("""
        SELECT latitude, longitude, time
        FROM transactions
        WHERE user=?
        ORDER BY time DESC
        LIMIT 1
    """, (user,))
    last_txn = cur.fetchone()

    if last_txn and last_txn[0] is not None:
        last_lat, last_lon = last_txn[0], last_txn[1]
        last_time = datetime.fromisoformat(last_txn[2])
        hours_diff = (datetime.now() - last_time).total_seconds() / 3600
        distance = haversine(last_lat, last_lon, user_lat, user_lon)
    else:
        distance = 0
        hours_diff = 1

    # Night Detection
    current_hour = datetime.now().hour
    is_night = 1 if (current_hour < 6 or current_hour > 22) else 0

    # -------- ML API CALL --------
    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json={
            "amount": amount,
            "user_lat": user_lat,
            "user_lon": user_lon,
            "merch_lat": user_lat,
            "merch_lon": user_lon,
            "timestamp": datetime.now().isoformat()
        }
    )

    result = response.json()
    ml_probability = result["fraud_probability"]

    # -------- FINAL BANKING ENGINE --------
    final_result = calculate_final_fraud_decision(
        amount,
        distance,
        hours_diff,
        is_night,
        ml_probability
    )

    risk = final_result["risk_score"]
    decision = final_result["decision"]

    # Save Transaction
    cur.execute("""
        INSERT INTO transactions
        (user, amount, risk, decision, ip, device, location, latitude, longitude)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (user, amount, risk, decision, ip, device, location, user_lat, user_lon))

    conn.commit()
    conn.close()

    if risk >= 50:
        create_alert(user, risk)

    return render_template(
        "result.html",
        risk=risk,
        decision=decision,
        reason=final_result["reason"]
    )


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
