import sqlite3
from typing import List, Dict

def init_db():
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS instructor_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructor_id TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            fecha_nac TEXT,
            genero TEXT,
            celular TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(instructor_id, patient_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_patient_to_instructor(instructor_id: str, patient_id: str, fecha_nac: str = None, genero: str = None, celular: str = None):
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO instructor_patients 
        (instructor_id, patient_id, fecha_nac, genero, celular) 
        VALUES (?, ?, ?, ?, ?)
    ''', (instructor_id, patient_id, fecha_nac, genero, celular))
    conn.commit()
    conn.close()

def get_instructor_patients(instructor_id: str) -> List[Dict]:
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('SELECT patient_id FROM instructor_patients WHERE instructor_id = ?', (instructor_id,))
    patients = [row[0] for row in c.fetchall()]
    conn.close()
    return patients 