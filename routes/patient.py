from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db
from models import User, Appointment, Prescription, LabRequest
import os

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Patient':
            flash('Access denied. Patient account required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@patient_bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).order_by(Prescription.created_at.desc()).all()
    lab_requests = LabRequest.query.filter_by(patient_id=current_user.id).order_by(LabRequest.created_at.desc()).all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.created_at.desc()).all()
    
    return render_template('patient/dashboard.html', 
                         prescriptions=prescriptions, 
                         lab_requests=lab_requests,
                         appointments=appointments)

@patient_bp.route('/prescriptions')
@login_required
@patient_required
def prescriptions():
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).order_by(Prescription.created_at.desc()).all()
    return render_template('patient/prescriptions.html', prescriptions=prescriptions)

@patient_bp.route('/prescription/<int:prescription_id>/download')
@login_required
@patient_required
def download_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    if prescription.patient_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('patient.dashboard'))
    
    if prescription.pdf_path and os.path.exists(prescription.pdf_path):
        return send_file(prescription.pdf_path, as_attachment=True)
    else:
        flash('PDF not available.', 'warning')
        return redirect(url_for('patient.prescriptions'))

@patient_bp.route('/tests')
@login_required
@patient_required
def tests():
    lab_requests = LabRequest.query.filter_by(patient_id=current_user.id).order_by(LabRequest.created_at.desc()).all()
    return render_template('patient/tests.html', lab_requests=lab_requests)

@patient_bp.route('/scan-qr', methods=['GET', 'POST'])
@login_required
@patient_required
def scan_qr():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        doctor = User.query.filter_by(unique_id=doctor_id, role='Doctor').first()
        
        if doctor:
            return jsonify({
                'success': True,
                'doctor_id': doctor.id,
                'doctor_name': doctor.name,
                'hospital': doctor.hospital_name,
                'specialization': doctor.specialization
            })
        else:
            return jsonify({'success': False, 'message': 'Doctor not found'})
    
    return render_template('patient/scan_qr.html')

@patient_bp.route('/confirm-appointment', methods=['POST'])
@login_required
@patient_required
def confirm_appointment():
    doctor_id = request.form.get('doctor_id')
    share_history = request.form.get('share_history') == 'true'
    
    doctor = User.query.get(doctor_id)
    if not doctor or doctor.role != 'Doctor':
        return jsonify({'success': False, 'message': 'Invalid doctor'})
    
    existing = Appointment.query.filter_by(
        patient_id=current_user.id, 
        doctor_id=doctor_id,
        status='Waiting'
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': 'You already have an appointment waiting'})
    
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        status='Waiting',
        share_history=share_history
    )
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': f'Appointment created with Dr. {doctor.name}. Status: Waiting'
    })
