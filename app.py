import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = 'ramadan_master_ops.json'

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'aliyah@marufdallas.com')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD', '')

DEFAULT_TASKS = [
    {
        "taskId": "RAM-101",
        "phase": "Tabling & Outreach",
        "title": "VRIC & BHA Goodie Bag Drive",
        "desc": "Coordinate pickup of 600 Goodie Bags & Diapers from Yazan. Setup volunteer table schedule.",
        "assignee": "Aliyah",
        "email": "aliyah@marufdallas.com",
        "deadline": "2026-03-12",
        "priority": "High",
        "status": "In Progress"
    },
    {
        "taskId": "RAM-102",
        "phase": "Marketing & Communications",
        "title": "Swiftgive Ramadan Campaign Setup",
        "desc": "Set Iftar dates, funding caps, own form triggers, and CTAs: 'A Simple Meal, A Lifelong Blessing'.",
        "assignee": "Muntaha",
        "email": "muntaha@marufdallas.com",
        "deadline": "2026-03-01",
        "priority": "Urgent",
        "status": "In Progress"
    },
    {
        "taskId": "RAM-103",
        "phase": "Distributions & Inventory",
        "title": "Food Line & Registration System",
        "desc": "Setup sign-in software, client registration, police detail (3-office, 2-land), and volunteer shirts.",
        "assignee": "Fuad",
        "email": "fuad@marufdallas.com",
        "deadline": "2026-03-10",
        "priority": "High",
        "status": "Pending"
    },
    {
        "taskId": "RAM-104",
        "phase": "Dinners & Events",
        "title": "Iftar Event Logistics & Timeline",
        "desc": "Guest arrival 6:00pm, Program 6:30-7:42pm, Iftar 7:42pm, Maghrib 7:46pm. Venue table setup.",
        "assignee": "Mahek",
        "email": "mahek@marufdallas.com",
        "deadline": "2026-03-14",
        "priority": "Medium",
        "status": "Pending"
    }
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return DEFAULT_TASKS
    return DEFAULT_TASKS

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def send_task_email(task):
    if not SENDER_PASSWORD or '@' not in task.get('email', ''):
        return False

    subject = f"[RAMADAN OPS] Task Assignment: {task['phase']} - {task['title']}"
    body = f"""As-salamu alaykum {task['assignee']},

You have been assigned a critical task for Ma'ruf Dallas Ramadan Operations.

--------------------------------------------------
Phase: {task['phase']}
Task Title: {task['title']}
Details: {task['desc']}
Deadline: {task['deadline']}
Priority: {task['priority']}
Status: {task['status']}
--------------------------------------------------

Please access the Ma'ruf Operations Hub to update your progress.

Jazakallah Khair,
Ma'ruf Dallas Operations Management
"""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = task['email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'status': 'SUCCESS', 'tasks': load_data()})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json(force=True, silent=True) or {}
    tasks = load_data()
    
    new_task = {
        'taskId': f"RAM-{100 + len(tasks) + 1}",
        'phase': data.get('phase', 'Tabling & Outreach'),
        'title': data.get('title', 'New Operation Task'),
        'desc': data.get('desc', ''),
        'assignee': data.get('assignee', 'Unassigned'),
        'email': f"{data.get('assignee', 'unassigned').lower()}@marufdallas.com",
        'deadline': data.get('deadline', 'ASAP'),
        'priority': data.get('priority', 'Medium'),
        'status': 'Pending'
    }

    tasks.insert(0, new_task)
    save_data(tasks)
    send_task_email(new_task)

    return jsonify({'status': 'SUCCESS', 'task': new_task})

@app.route('/api/tasks/status', methods=['POST'])
def update_status():
    data = request.get_json(force=True, silent=True) or {}
    tasks = load_data()
    for t in tasks:
        if t['taskId'] == data.get('taskId'):
            t['status'] = data.get('status')
            break
    save_data(tasks)
    return jsonify({'status': 'SUCCESS'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)