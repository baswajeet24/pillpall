from fpdf import FPDF
import json
import os
from datetime import datetime

class PrescriptionPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def generate(self, prescription, doctor, patient):
        self.add_page()
        self.set_margins(10, 10, 10)
        
        page_width = self.w - 20
        
        self.set_fill_color(240, 248, 255)
        self.rect(0, 0, self.w, 25, 'F')
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.set_xy(10, 8)
        self.cell(page_width, 8, 'Top Sponsor Area - Your hospital sponsor / medical brand ad goes here.', 0, 1, 'C')
        
        self.ln(5)
        
        y_header = self.get_y()
        
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(0, 102, 153)
        hospital_name = doctor.hospital_name if doctor.hospital_name else "PILLPAL HEALTH"
        self.set_xy(10, y_header)
        self.cell(100, 10, hospital_name.upper(), 0, 0, 'L')
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(128, 128, 128)
        self.set_xy(10, y_header + 10)
        self.cell(100, 5, 'TREATING PATIENTS BETTER', 0, 0, 'L')
        
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', 'B', 12)
        self.set_xy(120, y_header)
        self.cell(80, 6, f"Dr. {doctor.name}", 0, 1, 'R')
        
        self.set_font('Helvetica', '', 9)
        self.set_text_color(80, 80, 80)
        
        specialization = doctor.specialization if doctor.specialization else "General Physician"
        self.set_xy(120, self.get_y())
        self.cell(80, 5, specialization, 0, 1, 'R')
        
        if doctor.address:
            address_lines = doctor.address.split('\n') if '\n' in doctor.address else [doctor.address]
            for line in address_lines[:2]:
                self.set_xy(120, self.get_y())
                self.cell(80, 4, line[:40], 0, 1, 'R')
        
        self.set_xy(120, self.get_y())
        self.cell(80, 4, doctor.phone, 0, 1, 'R')
        
        if doctor.email:
            self.set_xy(120, self.get_y())
            self.cell(80, 4, doctor.email, 0, 1, 'R')
        
        if doctor.website:
            self.set_xy(120, self.get_y())
            self.cell(80, 4, doctor.website, 0, 1, 'R')
        
        self.ln(5)
        
        y_strip = self.get_y()
        self.set_fill_color(245, 245, 245)
        self.rect(10, y_strip, page_width, 12, 'F')
        
        self.set_draw_color(200, 200, 200)
        self.line(10, y_strip, 10 + page_width, y_strip)
        self.line(10, y_strip + 12, 10 + page_width, y_strip + 12)
        
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', 'B', 10)
        self.set_xy(12, y_strip + 2)
        
        patient_info = f"MR. {patient.name.upper()}"
        self.cell(60, 4, patient_info, 0, 0, 'L')
        
        self.set_font('Helvetica', '', 9)
        age_gender = f"({patient.age}y, {patient.gender})"
        self.cell(25, 4, age_gender, 0, 0, 'L')
        
        self.set_font('Helvetica', '', 9)
        self.cell(5, 4, chr(149), 0, 0, 'C')
        self.cell(40, 4, f"+91-{patient.phone}", 0, 0, 'L')
        
        date_str = prescription.created_at.strftime('%d-%b-%Y')
        self.set_font('Helvetica', '', 9)
        self.set_xy(150, y_strip + 2)
        self.cell(48, 8, f"Date: ", 0, 0, 'R')
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 8, date_str, 0, 0, 'L')
        
        self.set_y(y_strip + 18)
        
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 102, 153)
        height_val = prescription.height if prescription.height else "N/A"
        self.cell(page_width, 6, f"Height: {height_val}", 0, 1, 'L')
        
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 102, 153)
        self.cell(20, 6, "Diagnosis: ", 0, 0, 'L')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        diagnosis = prescription.diagnosis if prescription.diagnosis else "N/A"
        self.multi_cell(page_width - 20, 6, diagnosis)
        
        self.ln(5)
        
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(0, 102, 153)
        self.cell(20, 15, 'Rx', 0, 1, 'L')
        
        self.ln(3)
        
        medicines = json.loads(prescription.content) if prescription.content else []
        
        if medicines:
            col_widths = [12, 75, 25, 40, 38]
            headers = ['#', 'Medicine', 'Dosage', 'Timing - Freq.', 'Duration / Notes']
            
            y_table_start = self.get_y()
            
            self.set_fill_color(250, 250, 250)
            self.rect(10, y_table_start, page_width, 8, 'F')
            
            self.set_draw_color(180, 180, 180)
            self.line(10, y_table_start, 10 + page_width, y_table_start)
            self.line(10, y_table_start + 8, 10 + page_width, y_table_start + 8)
            
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(60, 60, 60)
            x = 10
            for i, header in enumerate(headers):
                self.set_xy(x, y_table_start + 1)
                self.cell(col_widths[i], 6, header, 0, 0, 'L')
                x += col_widths[i]
            
            self.set_y(y_table_start + 10)
            
            for idx, med in enumerate(medicines):
                row_y = self.get_y()
                
                self.set_draw_color(220, 220, 220)
                self.line(10, row_y + 14, 10 + page_width, row_y + 14)
                
                x = 10
                
                self.set_font('Helvetica', '', 10)
                self.set_text_color(0, 0, 0)
                self.set_xy(x, row_y)
                self.cell(col_widths[0], 7, f"{idx + 1})", 0, 0, 'L')
                x += col_widths[0]
                
                self.set_xy(x, row_y)
                self.set_font('Helvetica', 'B', 10)
                med_name = med.get('name', 'Unknown')
                self.cell(col_widths[1], 6, med_name.upper(), 0, 0, 'L')
                
                self.set_font('Helvetica', '', 8)
                self.set_text_color(100, 100, 100)
                timing_instruction = f"Timing: {med.get('timing', 'As directed')}"
                self.set_xy(x, row_y + 6)
                self.cell(col_widths[1], 5, timing_instruction, 0, 0, 'L')
                self.set_text_color(0, 0, 0)
                x += col_widths[1]
                
                self.set_font('Helvetica', '', 10)
                self.set_xy(x, row_y)
                dosage = med.get('dosage', '1-0-1')
                self.cell(col_widths[2], 7, dosage, 0, 0, 'L')
                x += col_widths[2]
                
                self.set_xy(x, row_y)
                timing_freq = f"{med.get('timing', 'After Food')} - Daily"
                self.cell(col_widths[3], 7, timing_freq, 0, 0, 'L')
                x += col_widths[3]
                
                self.set_xy(x, row_y)
                duration = med.get('duration', '1 Week')
                self.cell(col_widths[4], 7, duration, 0, 0, 'L')
                
                self.set_y(row_y + 16)
        
        self.ln(15)
        
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.set_x(130)
        self.cell(70, 6, f"Dr. {doctor.name}", 0, 1, 'R')
        self.set_font('Helvetica', '', 9)
        self.set_x(130)
        specialization = doctor.specialization if doctor.specialization else "MBBS, MD"
        self.cell(70, 5, specialization, 0, 1, 'R')
        
        self.ln(10)
        
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(page_width, 6, 'Download our app to store and view your prescriptions online.', 0, 1, 'C')
        
        self.set_y(-30)
        self.set_fill_color(240, 248, 255)
        self.rect(0, self.get_y(), self.w, 30, 'F')
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.set_xy(10, self.get_y() + 8)
        self.cell(page_width, 5, 'Bottom Sponsor Area - Additional sponsors, terms & conditions, or app promotion text.', 0, 1, 'C')
        
        os.makedirs('prescriptions', exist_ok=True)
        filename = f"prescriptions/prescription_{prescription.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.output(filename)
        
        return filename
