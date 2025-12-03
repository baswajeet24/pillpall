from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from gemini_helper import summarize_medical_history

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user.role)
    
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(phone=phone, role=role).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect_to_dashboard(role)
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_to_dashboard(current_user.role)
    
    role = request.args.get('role', 'Patient')
    
    if request.method == 'POST':
        role = request.form.get('role')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(phone=phone, role=role).first()
        if existing_user:
            flash('An account with this phone number already exists for this role.', 'danger')
            return render_template('auth/register.html', role=role)
        
        user = User(name=name, phone=phone, role=role)
        user.set_password(password)
        
        if role == 'Patient':
            age = request.form.get('age')
            gender = request.form.get('gender')
            raw_medical_history = request.form.get('medical_history', '')
            
            user.age = int(age) if age else None
            user.gender = gender
            user.raw_medical_history = raw_medical_history
            
            user.unique_id = User.generate_patient_id(phone, name)
            
            if raw_medical_history:
                user.ai_summary_history = summarize_medical_history(raw_medical_history)
        
        elif role == 'Doctor':
            user.specialization = request.form.get('specialization')
            user.hospital_name = request.form.get('hospital_name')
            user.medical_license_id = request.form.get('license_id')
            user.address = request.form.get('address')
            user.website = request.form.get('website')
            user.email = request.form.get('email')
            user.unique_id = f"DR{phone[-4:]}"
        
        elif role in ['Pharmacist', 'Lab', 'Receptionist']:
            user.unique_id = f"{role[:3].upper()}{phone[-4:]}"
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Registration successful! Your ID is: {user.unique_id}', 'success')
        login_user(user)
        return redirect_to_dashboard(role)
    
    return render_template('auth/register.html', role=role)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))

def redirect_to_dashboard(role):
    if role == 'Patient':
        return redirect(url_for('patient.dashboard'))
    elif role == 'Doctor':
        return redirect(url_for('doctor.dashboard'))
    elif role == 'Pharmacist':
        return redirect(url_for('staff.pharmacist_dashboard'))
    elif role == 'Lab':
        return redirect(url_for('staff.lab_dashboard'))
    elif role == 'Receptionist':
        return redirect(url_for('staff.receptionist_dashboard'))
    return redirect(url_for('main.landing'))
