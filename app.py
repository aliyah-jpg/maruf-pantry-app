from flask import Flask, render_template, request, jsonify
import json
import os
import uuid

app = Flask(__name__)

DATA_FILE = 'data.json'

PRE_RAMADAN_ITEMS_2027 = [
    {'id': 'p1', 'task': 'Masjid Table Outreach & Confirmations', 'lead': 'AjiFanta', 'target': '2026-10-13', 'status': 'Pending'},
    {'id': 'p2', 'task': 'Donation Drives Email Outreach', 'lead': 'AjiFanta', 'target': '2026-12-01', 'status': 'Pending'},
    {'id': 'p3', 'task': 'Identify Fitra & Giving Wall Recipients', 'lead': 'Aisha / Abdi', 'target': '2026-12-01', 'status': 'Pending'},
    {'id': 'p4', 'task': 'Ramadan Campaign Scripts & Messaging', 'lead': 'Muntaha', 'target': '2026-11-01', 'status': 'Pending'},
    {'id': 'p5', 'task': 'Donation Drives Graphic Newsletter & Socials', 'lead': 'Muntaha', 'target': '2026-11-15', 'status': 'Pending'},
    {'id': 'p6', 'task': 'Ramadan Intern Job Posting & Hiring', 'lead': 'Aliyah', 'target': '2026-10-15', 'status': 'In Progress'},
    {'id': 'p7', 'task': "Ma'ruf Ramadan Operations App", 'lead': 'Aliyah', 'target': '2026-10-20', 'status': 'In Progress'},
    {'id': 'p8', 'task': 'Website Revamp & Webpage Update', 'lead': 'Marwa', 'target': '2026-10-20', 'status': 'In Progress'},
    {'id': 'p9', 'task': 'LaunchGood Page & Community Campaign Setup', 'lead': 'Marwa', 'target': '2026-11-01', 'status': 'Pending'},
    {'id': 'p10', 'task': 'Digital Ads & Paid Media Schedule', 'lead': 'Marwa / Walid', 'target': '2026-11-05', 'status': 'Pending'},
    {'id': 'p11', 'task': 'Volunteer Communication Workflow', 'lead': 'Marwa / Raheeq', 'target': '2026-11-10', 'status': 'Pending'},
    {'id': 'p12', 'task': 'Social Media Content Calendar & Newsletters', 'lead': 'Marwa / Mahek', 'target': '2026-11-15', 'status': 'In Progress'},
    {'id': 'p13', 'task': 'Video Scripting, Recording & Editing', 'lead': 'Marwa', 'target': '2026-11-20', 'status': 'Pending'},
    {'id': 'p14', 'task': 'Donated & Internal Grocery Box Prep', 'lead': 'Marwa / Hikmatullah', 'target': '2026-11-25', 'status': 'In Progress'},
    {'id': 'p15', 'task': 'Toy Drives Coordination', 'lead': 'Raheeq', 'target': '2026-10-29', 'status': 'Pending'},
    {'id': 'p16', 'task': 'Iftar Sponsorships Coordination', 'lead': 'Fuad / Aisha', 'target': '2026-11-01', 'status': 'In Progress'},
    {'id': 'p17', 'task': 'Staff Iftar Planning & Logistics', 'lead': 'Fuad', 'target': '2026-11-15', 'status': 'Pending'},
    {'id': 'p18', 'task': 'Water Supply Logistics (Monty Outreach)', 'lead': 'Fuad', 'target': '2026-10-25', 'status': 'In Progress'},
    {'id': 'p19', 'task': 'Pita Bread Procurement (Mohammad Outreach)', 'lead': 'Abdi', 'target': '2026-10-25', 'status': 'In Progress'}
]

PRE_RAMADAN_SHOPPING_2027 = [
    {'item': 'White Packing Boxes (300 Target)', 'qty': '300 units', 'status': 'Needed'},
    {'item': 'Staff & Volunteer Shirts', 'qty': '150 shirts', 'status': 'Ordered'},
    {'item': 'Food Grade Gloves', 'qty': '20 boxes', 'status': 'In Stock'},
    {'item': 'Ziplock Bags (Quart Size)', 'qty': '50 packs', 'status': 'Needed'},
    {'item': 'Heavy Duty Packing Tape', 'qty': '30 rolls', 'status': 'In Stock'},
    {'item': 'Trash Bags (55 Gal)', 'qty': '15 rolls', 'status': 'In Stock'},
    {'item': 'Table Cloths (Navy / Cream)', 'qty': '25 cloths', 'status': 'Ordered'},
    {'item': 'Window Markers & Drive-thru Signage', 'qty': '10 sets', 'status': 'Needed'},
    {'item': 'Stop Signs for Distribution Control', 'qty': '4 units', 'status': 'In Stock'}
]

DEFAULT_METRICS = {
    'base_raised': 185000,
    'raised': 185000,
    'goal': 250000,
    'foodBoxes': 2100,
    'mealsServed': 5400,
    'volunteersCount': 96
}

def recalculate_season_funds(data, season):
    entries = data[season].get('entries', [])
    total_tabling_funds = sum(float(e.get('funds', 0)) for e in entries if e.get('section') == 'tabling')
    
    if 'metrics' not in data[season]:
        data[season]['metrics'] = DEFAULT_METRICS.copy()
        
    base_raised = float(data[season]['metrics'].get('base_raised', 185000))
    data[season]['metrics']['raised'] = base_raised + total_tabling_funds

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if 'planning' not in data['ramadan'] or not data['ramadan']['planning']:
                data['ramadan']['planning'] = PRE_RAMADAN_ITEMS_2027
            if 'shopping' not in data['ramadan']:
                data['ramadan']['shopping'] = PRE_RAMADAN_SHOPPING_2027
            if 'metrics' not in data['ramadan']:
                data['ramadan']['metrics'] = DEFAULT_METRICS.copy()
            if 'metrics' not in data['dhulhijjah']:
                data['dhulhijjah']['metrics'] = DEFAULT_METRICS.copy()
            
            recalculate_season_funds(data, 'ramadan')
            recalculate_season_funds(data, 'dhulhijjah')
            return data
            
    data = {
        'ramadan': {
            'entries': [], 
            'tasks': [], 
            'planning': PRE_RAMADAN_ITEMS_2027, 
            'shopping': PRE_RAMADAN_SHOPPING_2027,
            'metrics': DEFAULT_METRICS.copy()
        },
        'dhulhijjah': {
            'entries': [], 
            'tasks': [], 
            'planning': [], 
            'shopping': [],
            'metrics': DEFAULT_METRICS.copy()
        }
    }
    return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/api/metrics', methods=['POST'])
def update_metrics():
    req = request.json
    season = req.get('season', 'ramadan')
    data = load_data()
    
    base_raised = float(req.get('raised', 0))
    data[season]['metrics']['base_raised'] = base_raised
    data[season]['metrics']['goal'] = float(req.get('goal', 0))
    data[season]['metrics']['foodBoxes'] = int(req.get('foodBoxes', 0))
    data[season]['metrics']['mealsServed'] = int(req.get('mealsServed', 0))
    data[season]['metrics']['volunteersCount'] = int(req.get('volunteersCount', 0))
    
    recalculate_season_funds(data, season)
    save_data(data)
    return jsonify({'success': True, 'data': data})

@app.route('/api/entries', methods=['POST'])
def add_entry():
    req = request.json
    season = req.get('season', 'ramadan')
    data = load_data()
    
    cash = float(req.get('cash', 0))
    check = float(req.get('check', 0))
    swiftgive = float(req.get('swiftgive', 0))
    total_funds = cash + check + swiftgive
    
    new_entry = {
        'id': str(uuid.uuid4())[:8],
        'section': req.get('section'),
        'title': req.get('title'),
        'creator': req.get('creator'),
        'date': req.get('date'),
        'location': req.get('location', ''),
        'contact_name': req.get('contact_name', ''),
        'contact_title': req.get('contact_title', ''),
        'contact_phone': req.get('contact_phone', ''),
        'drive_link': req.get('drive_link', ''),
        'cash': cash,
        'check': check,
        'swiftgive': swiftgive,
        'funds': total_funds,
        'swift_tag': req.get('swift_tag', ''),
        'item_description': req.get('item_description', ''),
        'item_qty': req.get('item_qty', ''),
        'donation_type': req.get('donation_type', ''),
        'itinerary': req.get('itinerary', ''),
        'vendor_name': req.get('vendor_name', ''),
        'vendor_phone': req.get('vendor_phone', ''),
        'notes': req.get('notes', '')
    }
    
    data[season]['entries'].append(new_entry)
    recalculate_season_funds(data, season)
    save_data(data)
    return jsonify({'success': True, 'data': data})

@app.route('/api/entries/edit', methods=['POST'])
def edit_entry():
    req = request.json
    season = req.get('season', 'ramadan')
    entry_id = req.get('id')
    data = load_data()
    
    cash = float(req.get('cash', 0))
    check = float(req.get('check', 0))
    swiftgive = float(req.get('swiftgive', 0))
    total_funds = cash + check + swiftgive
    
    for entry in data[season]['entries']:
        if entry['id'] == entry_id:
            entry['title'] = req.get('title')
            entry['creator'] = req.get('creator')
            entry['date'] = req.get('date')
            entry['location'] = req.get('location', '')
            entry['contact_name'] = req.get('contact_name', '')
            entry['contact_title'] = req.get('contact_title', '')
            entry['contact_phone'] = req.get('contact_phone', '')
            entry['drive_link'] = req.get('drive_link', '')
            entry['cash'] = cash
            entry['check'] = check
            entry['swiftgive'] = swiftgive
            entry['funds'] = total_funds
            entry['swift_tag'] = req.get('swift_tag', '')
            entry['item_description'] = req.get('item_description', '')
            entry['item_qty'] = req.get('item_qty', '')
            entry['donation_type'] = req.get('donation_type', '')
            entry['itinerary'] = req.get('itinerary', '')
            entry['vendor_name'] = req.get('vendor_name', '')
            entry['vendor_phone'] = req.get('vendor_phone', '')
            entry['notes'] = req.get('notes', '')
            break
            
    recalculate_season_funds(data, season)
    save_data(data)
    return jsonify({'success': True, 'data': data})

@app.route('/api/planning/add', methods=['POST'])
def add_planning_item():
    req = request.json
    season = req.get('season', 'ramadan')
    data = load_data()
    
    new_item = {
        'id': str(uuid.uuid4())[:8],
        'task': req.get('task'),
        'lead': req.get('lead'),
        'target': req.get('target', 'TBD'),
        'status': req.get('status', 'Pending')
    }
    
    data[season]['planning'].append(new_item)
    save_data(data)
    return jsonify({'success': True, 'data': data})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    req = request.json
    season = req.get('season', 'ramadan')
    data = load_data()
    
    new_task = {
        'id': str(uuid.uuid4())[:8],
        'entry_id': req.get('entry_id'),
        'entry_title': req.get('entry_title'),
        'section': req.get('section'),
        'task_name': req.get('task_name'),
        'assignee': req.get('assignee'),
        'due_date': req.get('due_date'),
        'due_time': req.get('due_time', ''),
        'details': req.get('details', ''),
        'status': 'Pending'
    }
    
    data[season]['tasks'].append(new_task)
    save_data(data)
    return jsonify({'success': True, 'data': data})

@app.route('/api/tasks/status', methods=['POST'])
def update_task_status():
    req = request.json
    season = req.get('season', 'ramadan')
    task_id = req.get('task_id')
    new_status = req.get('status')
    
    data = load_data()
    for task in data[season]['tasks']:
        if task['id'] == task_id:
            task['status'] = new_status
            break
            
    save_data(data)
    return jsonify({'success': True, 'data': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)# ==========================================
# Task Notes & Automated Email Dispatch
# ==========================================
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace these with your operational Gmail/Google Workspace credentials
SENDER_EMAIL = "your-pantry-email@gmail.com"  
SENDER_PASSWORD = "your-app-password"          

def send_email_notification(to_email, staff_name, task_title, note_text):
    try:
        subject = f"[Ma'ruf Ops Hub] New Note on Task: {task_title}"
        body = f"""Assalamu Alaikum {staff_name},

A new note was added to your task "{task_title}" on the Ma'ruf Dallas Ops Hub:

--------------------------------------------------
"{note_text}"
--------------------------------------------------

Please log in to the dashboard to view or update your task status.

BarakAllahu Feekum,
Ma'ruf Dallas Operations Team
"""
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/api/add-note', methods=['POST'])
def add_note():
    data = request.json
    staff_name = data.get('staffName', 'Team Member')
    task_title = data.get('taskTitle', 'Assigned Task')
    note_text = data.get('note', '')
    
    clean_name = staff_name.split()[0].lower()
    recipient_email = f"{clean_name}@marufdallas.org"

    email_sent = send_email_notification(recipient_email, staff_name, task_title, note_text)
    
    if email_sent:
        return jsonify({"status": "success", "message": "Note published and emailed!"})
    else:
        return jsonify({"status": "partial_success", "message": "Note saved, but email dispatch failed. Check SMTP credentials."}), 500
