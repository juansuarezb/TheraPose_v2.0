import sqlite3
from typing import List, Dict

def init_db():
    """
    Crea las tablas necesarias si no existen:
    1. instructor_patients: Relación entre instructores y pacientes
    2. instructors: Información de los instructores
    3. patients: Información de los pacientes
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    
    # Tabla de instructores
    c.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            fecha_nac TEXT,
            genero TEXT,
            celular TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de pacientes
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            fecha_nac TEXT,
            genero TEXT,
            celular TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de relación instructor-paciente
    c.execute('''
        CREATE TABLE IF NOT EXISTS instructor_patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructor_id TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(instructor_id, patient_id),
            FOREIGN KEY (instructor_id) REFERENCES instructors(id),
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_instructor(instructor_id: str, username: str, email: str, first_name: str, last_name: str, 
                  fecha_nac: str = None, genero: str = None, celular: str = None):
    """
    Añade un instructor a la base de datos
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO instructors 
        (id, username, email, first_name, last_name, fecha_nac, genero, celular) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (instructor_id, username, email, first_name, last_name, fecha_nac, genero, celular))
    conn.commit()
    conn.close()

def add_patient(patient_id: str, username: str, email: str, first_name: str, last_name: str,
                fecha_nac: str = None, genero: str = None, celular: str = None):
    """
    Añade un paciente a la base de datos
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO patients 
        (id, username, email, first_name, last_name, fecha_nac, genero, celular) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (patient_id, username, email, first_name, last_name, fecha_nac, genero, celular))
    conn.commit()
    conn.close()

def add_patient_to_instructor(instructor_id: str, patient_id: str):
    """
    Añade una relación instructor-paciente a la base de datos
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
    Obtiene la lista de pacientes asociados a un instructor
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('''
        SELECT p.* 
        FROM patients p
        JOIN instructor_patients ip ON p.id = ip.patient_id
        WHERE ip.instructor_id = ?
    ''', (instructor_id,))
    
    columns = [description[0] for description in c.description]
    patients = []
    for row in c.fetchall():
        patient = dict(zip(columns, row))
        patients.append(patient)
    
    conn.close()
    return patients

def get_instructor(instructor_id: str) -> Dict:
    """
    Obtiene la información de un instructor
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM instructors WHERE id = ?', (instructor_id,))
    
    columns = [description[0] for description in c.description]
    row = c.fetchone()
    instructor = dict(zip(columns, row)) if row else None
    
    conn.close()
    return instructor

def get_patient(patient_id: str) -> Dict:
    """
    Obtiene la información de un paciente
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    c.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    
    columns = [description[0] for description in c.description]
    row = c.fetchone()
    patient = dict(zip(columns, row)) if row else None
    
    conn.close()
    return patient

def update_patient(patient_id: str, username: str = None, email: str = None, 
                  first_name: str = None, last_name: str = None,
                  fecha_nac: str = None, genero: str = None, celular: str = None):
    """
    Actualiza la información de un paciente en la base de datos
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    c = conn.cursor()
    
    # Construir la consulta  basada en los campos proporcionados
    update_fields = []
    params = []
    
    if username is not None:
        update_fields.append("username = ?")
        params.append(username)
    if email is not None:
        update_fields.append("email = ?")
        params.append(email)
    if first_name is not None:
        update_fields.append("first_name = ?")
        params.append(first_name)
    if last_name is not None:
        update_fields.append("last_name = ?")
        params.append(last_name)
    if fecha_nac is not None:
        update_fields.append("fecha_nac = ?")
        params.append(fecha_nac)
    if genero is not None:
        update_fields.append("genero = ?")
        params.append(genero)
    if celular is not None:
        update_fields.append("celular = ?")
        params.append(celular)
    
    if not update_fields:
        return
    
    query = f"UPDATE patients SET {', '.join(update_fields)} WHERE id = ?"
    params.append(patient_id)
    
    c.execute(query, params)
    conn.commit()
    conn.close()

def delete_patient(patient_id: str):
    """
    Elimina un paciente de la base de datos SQLite.
    
    Args:
        patient_id (str): ID del paciente a eliminar
        
    Returns:
        tuple: (keycloak_id, success) - ID de Keycloak del paciente y si se eliminó correctamente
    """
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    try:
        # Obtener el keycloak_id antes de eliminar
        cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            return None, False
            
        # Primero eliminar la relación instructor-paciente
        cursor.execute("DELETE FROM instructor_patients WHERE patient_id = ?", (patient_id,))
        
        # Luego eliminar el paciente
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        
        conn.commit()
        return patient[0], True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close() 