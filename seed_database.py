from app import create_app, db
from models import MedicineInventory, User

def seed_medicines():
    """Add sample medicines to inventory"""
    medicines = [
        {'name': 'TELVAS 20MG TABLET', 'stock_quantity': 100},
        {'name': 'GTN SORBITRATE 2.6MG TABLET CR', 'stock_quantity': 50},
        {'name': 'PARACETAMOL 500MG', 'stock_quantity': 200},
        {'name': 'AMOXICILLIN 250MG CAPSULE', 'stock_quantity': 150},
        {'name': 'OMEPRAZOLE 20MG CAPSULE', 'stock_quantity': 80},
        {'name': 'METFORMIN 500MG TABLET', 'stock_quantity': 120},
        {'name': 'AMLODIPINE 5MG TABLET', 'stock_quantity': 90},
        {'name': 'ATORVASTATIN 10MG TABLET', 'stock_quantity': 75},
        {'name': 'CETIRIZINE 10MG TABLET', 'stock_quantity': 180},
        {'name': 'PANTOPRAZOLE 40MG TABLET', 'stock_quantity': 60}
    ]
    
    for med_data in medicines:
        existing = MedicineInventory.query.filter_by(name=med_data['name']).first()
        if not existing:
            medicine = MedicineInventory(**med_data)
            db.session.add(medicine)
            print(f"Added: {med_data['name']}")
        else:
            print(f"Already exists: {med_data['name']}")
    
    db.session.commit()
    print("\nMedicine inventory seeded successfully!")

def seed_sample_users():
    """Add sample users for testing"""
    
    doctor = User.query.filter_by(phone='9876543210', role='Doctor').first()
    if not doctor:
        doctor = User(
            name='Argha Chakraborty',
            phone='9876543210',
            role='Doctor',
            unique_id='DR3210',
            specialization='MBBS, MD',
            hospital_name='Best Health',
            address='6/165, Sector-2\nSahibabad, Ghaziabad, UP',
            email='doctor@besthealth.com',
            website='www.besthealth.com'
        )
        doctor.set_password('doctor123')
        db.session.add(doctor)
        print("Added sample doctor: Dr. Argha Chakraborty")
    
    pharmacist = User.query.filter_by(phone='9876543211', role='Pharmacist').first()
    if not pharmacist:
        pharmacist = User(
            name='John Pharmacist',
            phone='9876543211',
            role='Pharmacist',
            unique_id='PHA3211'
        )
        pharmacist.set_password('pharma123')
        db.session.add(pharmacist)
        print("Added sample pharmacist")
    
    lab_user = User.query.filter_by(phone='9876543212', role='Lab').first()
    if not lab_user:
        lab_user = User(
            name='Lab Technician',
            phone='9876543212',
            role='Lab',
            unique_id='LAB3212'
        )
        lab_user.set_password('lab123')
        db.session.add(lab_user)
        print("Added sample lab user")
    
    receptionist = User.query.filter_by(phone='9876543213', role='Receptionist').first()
    if not receptionist:
        receptionist = User(
            name='Reception Staff',
            phone='9876543213',
            role='Receptionist',
            unique_id='REC3213'
        )
        receptionist.set_password('reception123')
        db.session.add(receptionist)
        print("Added sample receptionist")
    
    db.session.commit()
    print("\nSample users seeded successfully!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_medicines()
        seed_sample_users()
        print("\n=== Database seeding complete! ===")
        print("\nSample Login Credentials:")
        print("Doctor: Phone: 9876543210, Password: doctor123")
        print("Pharmacist: Phone: 9876543211, Password: pharma123")
        print("Lab: Phone: 9876543212, Password: lab123")
        print("Receptionist: Phone: 9876543213, Password: reception123")
