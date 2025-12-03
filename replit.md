# PillPal - Healthcare Management System

## Overview
PillPal is a comprehensive healthcare management web application built with Flask, SQLAlchemy, and Bootstrap 5. It provides role-based portals for Patients, Doctors, Pharmacists, Lab Technicians, and Receptionists.

## Tech Stack
- **Backend**: Python Flask
- **Database**: SQLite (instance/pillpal.db)
- **ORM**: SQLAlchemy
- **Authentication**: flask-login
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **PDF Generation**: fpdf
- **AI Integration**: Google Gemini API (for medical history summarization)

## Project Structure
```
.
├── app.py              # Main Flask application factory
├── models.py           # Database models
├── gemini_helper.py    # Gemini AI integration
├── pdf_generator.py    # PDF prescription generator
├── seed_database.py    # Database seeding script
├── routes/
│   ├── auth.py         # Authentication routes
│   ├── main.py         # Landing page
│   ├── patient.py      # Patient portal routes
│   ├── doctor.py       # Doctor portal routes
│   └── staff.py        # Pharmacist, Lab, Receptionist routes
├── templates/          # Jinja2 HTML templates
├── static/             # CSS, JS, images
├── instance/           # SQLite database
└── prescriptions/      # Generated PDF files
```

## Database Models
1. **User**: Multi-role user model (Patient, Doctor, Pharmacist, Lab, Receptionist)
2. **MedicineInventory**: Medicine stock management
3. **Appointment**: Patient-Doctor appointments with status tracking
4. **Prescription**: Prescriptions with medicines, diagnosis, PDF path
5. **LabRequest**: Lab test requests and results

## Features

### Patient Portal
- Register with auto-generated unique ID (last 4 digits of phone + first 3 chars of name)
- AI-powered medical history summarization (Gemini)
- Check-in with doctor via QR code simulation
- View and download prescriptions (PDF)
- View lab test results

### Doctor Portal
- Consultation queue management
- View patient medical history (if shared)
- Create prescriptions with inventory-filtered medicines
- Generate PDF prescriptions matching reference style
- Order lab tests

### Pharmacist Portal
- Search patient by unique ID
- View latest prescription
- Manage medicine inventory (add/edit stock)

### Lab Portal
- View pending lab requests
- Mark requests as completed with results

### Receptionist Portal
- Real-time queue monitoring (3-second polling)
- View all doctors' patient queues

## Running the App
```bash
python app.py
```

## Sample Login Credentials
- **Doctor**: Phone: 9876543210, Password: doctor123
- **Pharmacist**: Phone: 9876543211, Password: pharma123
- **Lab**: Phone: 9876543212, Password: lab123
- **Receptionist**: Phone: 9876543213, Password: reception123

## Environment Variables
- `SESSION_SECRET`: Flask session secret key
- `GEMINI_API_KEY`: Google Gemini API key for AI summarization

## Recent Changes
- 2024-12-03: Initial implementation with all portals
- 2024-12-03: Added PDF generator matching reference style
- 2024-12-03: Added from_json template filter for prescription display
