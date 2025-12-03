from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    unique_id = db.Column(db.String(20), unique=True, nullable=True)
    role = db.Column(db.String(20), nullable=False)  # Patient, Doctor, Pharmacist, Lab, Receptionist
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Doctor specific fields
    specialization = db.Column(db.String(100), nullable=True)
    hospital_name = db.Column(db.String(200), nullable=True)
    medical_license_id = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    
    # Patient specific fields
    raw_medical_history = db.Column(db.Text, nullable=True)
    ai_summary_history = db.Column(db.Text, nullable=True)
    
    # Relationships
    patient_appointments = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy='dynamic')
    doctor_appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id', backref='doctor', lazy='dynamic')
    patient_prescriptions = db.relationship('Prescription', foreign_keys='Prescription.patient_id', backref='patient', lazy='dynamic')
    doctor_prescriptions = db.relationship('Prescription', foreign_keys='Prescription.doctor_id', backref='doctor', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_patient_id(phone, name):
        """Generate unique_id: Last 4 digits of Phone + First 3 chars of Name"""
        phone_part = phone[-4:] if len(phone) >= 4 else phone.zfill(4)
        name_part = name[:3].upper() if len(name) >= 3 else name.upper().ljust(3, 'X')
        return f"{phone_part}{name_part}"


class MedicineInventory(db.Model):
    __tablename__ = 'medicine_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    stock_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='Waiting')  # Waiting, In-Consultation, Completed
    share_history = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=True)  # JSON: meds, dosage, timing, duration
    diagnosis = db.Column(db.Text, nullable=True)
    height = db.Column(db.String(20), nullable=True)
    vitals = db.Column(db.Text, nullable=True)
    pdf_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LabRequest(db.Model):
    __tablename__ = 'lab_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lab_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    test_name = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')  # Pending, Done
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_lab_requests')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_lab_requests')
    lab_user = db.relationship('User', foreign_keys=[lab_user_id], backref='lab_user_requests')
