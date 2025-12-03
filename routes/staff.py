from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Appointment, Prescription, LabRequest, MedicineInventory
import json

staff_bp = Blueprint('staff', __name__)

def pharmacist_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Pharmacist':
            flash('Access denied. Pharmacist account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def lab_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Lab':
            flash('Access denied. Lab account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def receptionist_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Receptionist':
            flash('Access denied. Receptionist account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Pharmacist Routes
@staff_bp.route('/pharmacist')
@login_required
@pharmacist_required
def pharmacist_dashboard():
    inventory = MedicineInventory.query.order_by(MedicineInventory.name).all()
    return render_template('staff/pharmacist.html', inventory=inventory)

@staff_bp.route('/pharmacist/search-patient', methods=['POST'])
@login_required
@pharmacist_required
def search_patient():
    patient_id = request.form.get('patient_id')
    patient = User.query.filter_by(unique_id=patient_id, role='Patient').first()
    
    if not patient:
        return jsonify({'success': False, 'message': 'Patient not found'})
    
    prescription = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.created_at.desc()).first()
    
    if not prescription:
        return jsonify({'success': False, 'message': 'No prescriptions found for this patient'})
    
    medicines = json.loads(prescription.content) if prescription.content else []
    doctor = User.query.get(prescription.doctor_id)
    
    return jsonify({
        'success': True,
        'patient': {
            'name': patient.name,
            'unique_id': patient.unique_id,
            'age': patient.age,
            'gender': patient.gender
        },
        'prescription': {
            'id': prescription.id,
            'diagnosis': prescription.diagnosis,
            'date': prescription.created_at.strftime('%d-%b-%Y'),
            'doctor': doctor.name if doctor else 'Unknown',
            'medicines': medicines
        }
    })

@staff_bp.route('/pharmacist/inventory/add', methods=['POST'])
@login_required
@pharmacist_required
def add_medicine():
    data = request.get_json()
    name = data.get('name')
    quantity = data.get('quantity', 0)
    
    existing = MedicineInventory.query.filter_by(name=name).first()
    if existing:
        existing.stock_quantity += int(quantity)
    else:
        medicine = MedicineInventory(name=name, stock_quantity=int(quantity))
        db.session.add(medicine)
    
    db.session.commit()
    return jsonify({'success': True})

@staff_bp.route('/pharmacist/inventory/update/<int:medicine_id>', methods=['POST'])
@login_required
@pharmacist_required
def update_medicine(medicine_id):
    data = request.get_json()
    medicine = MedicineInventory.query.get_or_404(medicine_id)
    
    if 'name' in data:
        medicine.name = data['name']
    if 'quantity' in data:
        medicine.stock_quantity = int(data['quantity'])
    
    db.session.commit()
    return jsonify({'success': True})

@staff_bp.route('/pharmacist/inventory')
@login_required
@pharmacist_required
def get_inventory():
    inventory = MedicineInventory.query.order_by(MedicineInventory.name).all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'stock': m.stock_quantity
    } for m in inventory])

# Lab Routes
@staff_bp.route('/lab')
@login_required
@lab_required
def lab_dashboard():
    pending_requests = LabRequest.query.filter_by(status='Pending').order_by(LabRequest.created_at.asc()).all()
    completed_requests = LabRequest.query.filter_by(status='Done').order_by(LabRequest.updated_at.desc()).limit(20).all()
    return render_template('staff/lab.html', 
                         pending_requests=pending_requests,
                         completed_requests=completed_requests)

@staff_bp.route('/lab/pending')
@login_required
@lab_required
def get_pending_requests():
    requests = LabRequest.query.filter_by(status='Pending').order_by(LabRequest.created_at.asc()).all()
    return jsonify([{
        'id': r.id,
        'patient_name': r.patient.name,
        'patient_id': r.patient.unique_id,
        'test_name': r.test_name,
        'notes': r.notes,
        'doctor_name': r.doctor.name,
        'date': r.created_at.strftime('%d-%b-%Y %H:%M')
    } for r in requests])

@staff_bp.route('/lab/complete/<int:request_id>', methods=['POST'])
@login_required
@lab_required
def complete_lab_request(request_id):
    lab_request = LabRequest.query.get_or_404(request_id)
    data = request.get_json()
    
    lab_request.status = 'Done'
    lab_request.result = data.get('result', '')
    lab_request.lab_user_id = current_user.id
    
    db.session.commit()
    return jsonify({'success': True})

# Receptionist Routes
@staff_bp.route('/receptionist')
@login_required
@receptionist_required
def receptionist_dashboard():
    doctors = User.query.filter_by(role='Doctor').all()
    return render_template('staff/receptionist.html', doctors=doctors)

@staff_bp.route('/receptionist/queue/<int:doctor_id>')
@login_required
@receptionist_required
def get_doctor_queue(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    
    waiting = Appointment.query.filter_by(
        doctor_id=doctor_id, 
        status='Waiting'
    ).order_by(Appointment.created_at.asc()).all()
    
    in_consultation = Appointment.query.filter_by(
        doctor_id=doctor_id, 
        status='In-Consultation'
    ).first()
    
    queue_data = []
    for apt in waiting:
        queue_data.append({
            'id': apt.id,
            'patient_name': apt.patient.name,
            'patient_id': apt.patient.unique_id,
            'status': apt.status,
            'time': apt.created_at.strftime('%H:%M')
        })
    
    current_patient = None
    if in_consultation:
        current_patient = {
            'patient_name': in_consultation.patient.name,
            'patient_id': in_consultation.patient.unique_id,
            'status': 'In-Consultation'
        }
    
    return jsonify({
        'doctor_name': doctor.name,
        'queue': queue_data,
        'current_patient': current_patient,
        'waiting_count': len(queue_data)
    })
