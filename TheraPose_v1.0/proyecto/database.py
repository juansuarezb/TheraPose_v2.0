import sqlite3
from typing import List, Dict

def init_db():
    """
    1. Crea la tabla 'instructor_patients' si no existe con los siguientes campos:
       - id: Identificador único autoincremental
       - instructor_id: ID del instructor (no nulo)
       - patient_id: ID del paciente (no nulo)
       - created_at: Fecha y hora de creación del registro
   
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS instructor_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructor_id TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(instructor_id, patient_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_patient_to_instructor(instructor_id: str, patient_id: str):
    """
    Añade una relación instructor-paciente a la base de datos:
    1. Establece una conexión con la base de datos
    2. Inserta un nuevo registro en la tabla instructor_patients con:
       - instructor_id: ID del instructor
       - patient_id: ID del paciente
    3. Guarda los cambios y cierra la conexión
    
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO instructor_patients 
        (instructor_id, patient_id) 
        VALUES (?, ?)
    ''', (instructor_id, patient_id))
    conn.commit()
    conn.close()

def get_instructor_patients(instructor_id: str) -> List[Dict]:
    """
    Obtiene la lista de pacientes asociados a un instructor:
    1. Establece una conexión con la base de datos
    2. Consulta todos los patient_id asociados al instructor_id proporcionado
    3. Cierra la conexión
    4. Retorna una lista con los IDs de los pacientes
    
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('SELECT patient_id FROM instructor_patients WHERE instructor_id = ?', (instructor_id,))
    patients = [row[0] for row in c.fetchall()]
    conn.close()
    return patients 