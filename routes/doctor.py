from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Appointment, Prescription, LabRequest, MedicineInventory
from pdf_generator import PrescriptionPDF
import json
import os

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Doctor':
            flash('Access denied. Doctor account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    waiting_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='Waiting'
    ).order_by(Appointment.created_at.asc()).all()
    
    in_consultation = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='In-Consultation'
    ).first()
    
    completed_today = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='Completed'
    ).order_by(Appointment.updated_at.desc()).limit(10).all()
    
    return render_template('doctor/dashboard.html', 
                         waiting_appointments=waiting_appointments,
                         in_consultation=in_consultation,
                         completed_today=completed_today)

@doctor_bp.route('/queue')
@login_required
@doctor_required
def get_queue():
    waiting = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='Waiting'
    ).order_by(Appointment.created_at.asc()).all()
    
    in_consultation = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='In-Consultation'
    ).first()
    
    queue_data = []
    for apt in waiting:
        queue_data.append({
            'id': apt.id,
            'patient_name': apt.patient.name,
            'patient_id': apt.patient.unique_id,
            'status': apt.status,
            'share_history': apt.share_history
        })
    
    current_patient = None
    if in_consultation:
        current_patient = {
            'id': in_consultation.id,
            'patient_name': in_consultation.patient.name,
            'patient_id': in_consultation.patient.unique_id,
            'age': in_consultation.patient.age,
            'gender': in_consultation.patient.gender,
            'phone': in_consultation.patient.phone,
            'share_history': in_consultation.share_history,
            'ai_summary': in_consultation.patient.ai_summary_history if in_consultation.share_history else None
        }
    
    return jsonify({
        'queue': queue_data,
        'current_patient': current_patient
    })

@doctor_bp.route('/start-consultation/<int:appointment_id>', methods=['POST'])
@login_required
@doctor_required
def start_consultation(appointment_id):
    current = Appointment.query.filter_by(
        doctor_id=current_user.id, 
        status='In-Consultation'
    ).first()
    
    if current:
        return jsonify({'success': False, 'message': 'Complete current consultation first'})
    
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Invalid appointment'})
    
    appointment.status = 'In-Consultation'
    db.session.commit()
    
    return jsonify({'success': True})

@doctor_bp.route('/consultation/<int:appointment_id>')
@login_required
@doctor_required
def consultation(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    medicines = MedicineInventory.query.filter(MedicineInventory.stock_quantity > 0).all()
    
    return render_template('doctor/consultation.html', 
                         appointment=appointment,
                         patient=appointment.patient,
                         medicines=medicines)

@doctor_bp.route('/available-medicines')
@login_required
@doctor_required
def available_medicines():
    medicines = MedicineInventory.query.filter(MedicineInventory.stock_quantity > 0).all()
    return jsonify([{'id': m.id, 'name': m.name, 'stock': m.stock_quantity} for m in medicines])

@doctor_bp.route('/create-prescription/<int:appointment_id>', methods=['POST'])
@login_required
@doctor_required
def create_prescription(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Invalid appointment'})
    
    data = request.get_json()
    
    diagnosis = data.get('diagnosis', '')
    height = data.get('height', '')
    vitals = data.get('vitals', '')
    medicines = data.get('medicines', [])
    
    for med in medicines:
        inventory = MedicineInventory.query.get(med['medicine_id'])
        if inventory:
            quantity_needed = 1
            if inventory.stock_quantity >= quantity_needed:
                inventory.stock_quantity -= quantity_needed
            else:
                return jsonify({'success': False, 'message': f'Insufficient stock for {inventory.name}'})
    
    prescription = Prescription(
        patient_id=appointment.patient_id,
        doctor_id=current_user.id,
        content=json.dumps(medicines),
        diagnosis=diagnosis,
        height=height,
        vitals=vitals
    )
    db.session.add(prescription)
    db.session.flush()
    
    pdf_generator = PrescriptionPDF()
    pdf_path = pdf_generator.generate(prescription, current_user, appointment.patient)
    prescription.pdf_path = pdf_path
    
    appointment.status = 'Completed'
    db.session.commit()
    
    return jsonify({'success': True, 'prescription_id': prescription.id})

@doctor_bp.route('/create-lab-request/<int:appointment_id>', methods=['POST'])
@login_required
@doctor_required
def create_lab_request(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Invalid appointment'})
    
    data = request.get_json()
    test_name = data.get('test_name', '')
    notes = data.get('notes', '')
    
    lab_request = LabRequest(
        patient_id=appointment.patient_id,
        doctor_id=current_user.id,
        test_name=test_name,
        notes=notes,
        status='Pending'
    )
    db.session.add(lab_request)
    db.session.commit()
    
    return jsonify({'success': True, 'lab_request_id': lab_request.id})

@doctor_bp.route('/complete-consultation/<int:appointment_id>', methods=['POST'])
@login_required
@doctor_required
def complete_consultation(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Invalid appointment'})
    
    appointment.status = 'Completed'
    db.session.commit()
    
    return jsonify({'success': True})
