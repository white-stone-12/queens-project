from flask import Flask, render_template, jsonify, request, redirect, session
import razorpay
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# 🔑 USE ENV VARIABLES (IMPORTANT FOR RENDER)
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id TEXT,
        amount INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= ROUTES =================

@app.route('/')
def home():
    return render_template("index.html")

# CREATE ORDER
@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.get_json()
    amount = int(data['amount']) * 100

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    return jsonify(order)

# SAVE PAYMENT
@app.route('/payment', methods=['POST'])
def payment():
    data = request.get_json()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO payments(payment_id, amount) VALUES (?, ?)",
        (data['payment_id'], int(data['amount']))
    )

    conn.commit()
    conn.close()

    return "OK"

# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if request.form['username'] == "admin" and request.form['password'] == "1234":
            session['admin'] = True
            return redirect('/admin')
    return render_template("login.html")

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/login')

# ADMIN PANEL
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM payments ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()

    return render_template("admin.html", data=data)

# ================= LEGAL PAGES =================

@app.route('/privacy')
def privacy():
    return render_template("privacy.html")

@app.route('/terms')
def terms():
    return render_template("terms.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)