from flask import Flask, render_template, request, jsonify, redirect, url_for
import time
import random

app = Flask(__name__)

# Fixed admin credentials
admin_username = 'admin'
admin_password = 'adminpassword'

# Dummy user data
users = {}

# Track failed login attempts and lockout time
failed_attempts = {}
lockout_time = {}
LOCKOUT_LIMIT = 6
LOCKOUT_DURATION = 3 * 60  # 3 minutes in seconds

# Funny lockout messages
lockout_messages = [
    "🚫 Easy there, '{username}'! You've hit the login wall. Your account is now meditating for {wait} minute(s). Try again after enlightenment 🧘.",
    "🕵️‍♂️ Suspicious activity detected! '{username}', either you're a hacker or just really forgetful. Cool off for {wait} minute(s) and come back with better guesses.",
    "🐢 Slow down, '{username}'! You've tried too many times. Your account is taking a power nap for {wait} minute(s).",
    "🎯 Missed again, '{username}'! After 6 failed attempts, your account is now in timeout. Try again in {wait} minute(s) — maybe with snacks.",
    "🧠 Brain overload! '{username}', your password attempts have exhausted the server’s patience. Recharge for {wait} minute(s) and return smarter."
]

@app.route('/')
def home():
    return render_template("products.html")

@app.route('/login')
def loginpage():
    return redirect(url_for('login'))

@app.route('/loginpage', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    # Check if user is locked out
    if failed_attempts.get(username, 0) >= LOCKOUT_LIMIT:
        last_attempt_time = lockout_time.get(username, 0)
        time_since_lockout = time.time() - last_attempt_time

        if time_since_lockout < LOCKOUT_DURATION:
            wait_minutes = int((LOCKOUT_DURATION - time_since_lockout) / 60) + 1
            message_template = random.choice(lockout_messages)
            message = message_template.format(username=username, wait=wait_minutes)
            return jsonify({'message': message, 'status_code': 429}), 429
        else:
            # Cooldown expired — reset attempts
            failed_attempts[username] = 0
            lockout_time.pop(username, None)

    # Admin login
    if username == admin_username and password == admin_password:
        failed_attempts[username] = 0
        return redirect(url_for('dashboard', username=username)), 210
    elif username == admin_username and password != admin_password:
        failed_attempts[username] = failed_attempts.get(username, 0) + 1
        if failed_attempts[username] == LOCKOUT_LIMIT:
            lockout_time[username] = time.time()
        return jsonify({'message': 'Incorrect admin password'}), 220

    # Registered user login
    elif username in users:
        if users[username] == password:
            failed_attempts[username] = 0
            return render_template('login_success.html', username=username), 200
        else:
            failed_attempts[username] = failed_attempts.get(username, 0) + 1
            if failed_attempts[username] == LOCKOUT_LIMIT:
                lockout_time[username] = time.time()
            return jsonify({'message': 'Incorrect password. Please try again.'}), 406
    else:
        failed_attempts[username] = failed_attempts.get(username, 0) + 1
        if failed_attempts[username] == LOCKOUT_LIMIT:
            lockout_time[username] = time.time()
        return jsonify({'message': 'Incorrect username. Please try again.', 'status_code': 404}), 404

@app.route('/register', methods=['POST', 'GET'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users:
        return jsonify({'message': 'Username already exists. Please choose a different username.', 'status_code': 400}), 400
    else:
        users[username] = password
        return jsonify({'message': 'You have been successfully registered! Please login.', 'status_code': 201}), 201

@app.route('/dashboard')
def dashboard():
    username = request.args.get('username')
    if username:
        return render_template('dashboard.html', username=username), 200
    else:
        return jsonify({'message': 'You need to login first.', 'status_code': 401}), 401

@app.route('/logout')
def logout():
    username = request.args.get('username')
    if username:
        return jsonify({'message': 'You have been logged out.', 'status_code': 200}), 200
    else:
        return jsonify({'message': 'You are not logged in.', 'status_code': 401}), 401

if __name__ == '__main__':
    app.run(debug=True)