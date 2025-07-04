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

    # Asegurar que las tablas estén actualizadas
    create_therapy_tables()
    update_serie_table()

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

# Definición de tablas para Series Terapéuticas y Posturas
def create_therapy_tables():
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    # Tabla Serie Terapéutica
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS serie_terapeutica (
            id_serie INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo_terapia TEXT NOT NULL,
            sesiones_recomendadas INTEGER NOT NULL,
            patient_id TEXT NOT NULL,
            activa BOOLEAN DEFAULT 1,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    # Tabla Postura
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postura (
            id_postura INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_es TEXT NOT NULL,
            nombre_sans TEXT,
            instrucciones TEXT,
            beneficios TEXT,
            precauciones TEXT,
            video TEXT,
            fotografia TEXT
        )
    ''')
    
    # Tabla de relación PosturaEnSerie
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postura_en_serie (
            id_serie INTEGER,
            id_postura INTEGER,
            orden INTEGER NOT NULL,
            duracion_min INTEGER NOT NULL,
            PRIMARY KEY (id_serie, id_postura),
            FOREIGN KEY (id_serie) REFERENCES serie_terapeutica(id_serie),
            FOREIGN KEY (id_postura) REFERENCES postura(id_postura)
        )
    ''')
    
    # Tabla Sesion
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sesion (
            id_sesion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_serie INTEGER,
            fecha DATE NOT NULL,
            hora_inicio TIME,
            hora_fin TIME,
            intensidad_inicio INTEGER,
            intensidad_final INTEGER,
            comentario TEXT,
            tiempo_efectivo REAL DEFAULT 0.0,
            FOREIGN KEY (id_serie) REFERENCES serie_terapeutica(id_serie)
        )
    ''')
    
    # Insertar posturas predefinidas si no existen
    posturas = [
        ("Cat Pose", "Marjaryasana"),
        ("Chair Pose", "Utkatasana"),
        ("Cobra Pose", "Bhujangasana"),
        ("Bound Angle Pose", "Baddha Konasana"),
        ("Dolphin Plank Pose", "Makara Adho Mukha Svanasana"),
        ("Downward Facing Dog", "Adho Mukha Svanasana"),
        ("Boat Pose", "Navasana"),
        ("Corpse Pose", "Savasana"),
        ("Easy Pose", "Sukhasana")
    ]
    
    cursor.execute("SELECT COUNT(*) FROM postura")
    if cursor.fetchone()[0] == 0:
        for nombre_es, nombre_sans in posturas:
            cursor.execute('''
                INSERT INTO postura (nombre_es, nombre_sans)
                VALUES (?, ?)
            ''', (nombre_es, nombre_sans))
    
    conn.commit()
    conn.close()
    
    # Insertar posturas adicionales para los nuevos tipos de terapia
    insert_additional_posturas()

def update_serie_table():
    """Actualiza la estructura de la tabla serie_terapeutica si es necesario"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    # Verificar si la columna activa existe
    cursor.execute("PRAGMA table_info(serie_terapeutica)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'activa' not in columns:
        cursor.execute('''
            ALTER TABLE serie_terapeutica
            ADD COLUMN activa BOOLEAN DEFAULT 1
        ''')
    
    conn.commit()
    conn.close()

# Funciones para manejar series terapéuticas
def get_posturas_by_tipo_terapia(tipo_terapia):
    posturas_por_tipo = {
        "Ansiedad": ["Bound Angle Pose", "Boat Pose", "Cobra Pose", "Cat Pose", "Corpse Pose", "Easy Pose", "Child's Pose", "Legs Up the Wall", "Seated Forward Bend", "Bridge Pose", "Camel Pose", "Lotus Pose"],
        "Depresión": ["Cat Pose", "Cobra Pose", "Boat Pose", "Bound Angle Pose", "Corpse Pose", "Easy Pose", "Child's Pose", "Legs Up the Wall", "Seated Forward Bend", "Bridge Pose", "Camel Pose", "Lotus Pose"],
        "Dolor de Espalda": ["Cat Pose", "Chair Pose", "Cobra Pose", "Bound Angle Pose", "Dolphin Plank Pose", "Downward Facing Dog", "Child's Pose", "Bridge Pose", "Locust Pose", "Camel Pose", "Seated Twist", "Supine Twist"],
        "Artritis": ["Easy Pose", "Child's Pose", "Cat Pose", "Cobra Pose", "Bound Angle Pose", "Seated Forward Bend", "Bridge Pose", "Legs Up the Wall", "Corpse Pose", "Seated Twist", "Supine Twist", "Lotus Pose"],
        "Dolor de Cabeza": ["Child's Pose", "Cat Pose", "Cobra Pose", "Easy Pose", "Seated Forward Bend", "Legs Up the Wall", "Corpse Pose", "Seated Twist", "Supine Twist", "Bridge Pose", "Camel Pose", "Lotus Pose"],
        "Insomnio": ["Child's Pose", "Legs Up the Wall", "Corpse Pose", "Easy Pose", "Seated Forward Bend", "Bound Angle Pose", "Bridge Pose", "Camel Pose", "Lotus Pose", "Seated Twist", "Supine Twist", "Cat Pose"],
        "Mala Postura": ["Cat Pose", "Cobra Pose", "Chair Pose", "Downward Facing Dog", "Child's Pose", "Bridge Pose", "Locust Pose", "Camel Pose", "Seated Twist", "Supine Twist", "Bound Angle Pose", "Seated Forward Bend"]
    }
    
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    posturas = cursor.execute('''
        SELECT id_postura, nombre_es, nombre_sans
        FROM postura
        WHERE nombre_es IN ({})
    '''.format(','.join('?' * len(posturas_por_tipo[tipo_terapia]))), 
    posturas_por_tipo[tipo_terapia]).fetchall()
    
    conn.close()
    return posturas

def insert_additional_posturas():
    """Inserta las posturas adicionales para los nuevos tipos de terapia"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    # Lista de posturas adicionales con sus nombres en sánscrito
    posturas_adicionales = [
        ("Child's Pose", "Balasana"),
        ("Legs Up the Wall", "Viparita Karani"),
        ("Seated Forward Bend", "Paschimottanasana"),
        ("Bridge Pose", "Setu Bandhasana"),
        ("Camel Pose", "Ustrasana"),
        ("Lotus Pose", "Padmasana"),
        ("Locust Pose", "Salabhasana"),
        ("Seated Twist", "Ardha Matsyendrasana"),
        ("Supine Twist", "Supta Matsyendrasana")
    ]
    
    # Verificar si las posturas ya existen
    for nombre_es, nombre_sans in posturas_adicionales:
        cursor.execute("SELECT COUNT(*) FROM postura WHERE nombre_es = ?", (nombre_es,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO postura (nombre_es, nombre_sans)
                VALUES (?, ?)
            ''', (nombre_es, nombre_sans))
    
    conn.commit()
    conn.close()

def get_serie_activa(patient_id):
    """Obtiene la serie terapéutica activa de un paciente"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    serie = cursor.execute('''
        SELECT id_serie, nombre, tipo_terapia, sesiones_recomendadas
        FROM serie_terapeutica
        WHERE patient_id = ? AND activa = 1
    ''', (patient_id,)).fetchone()
    
    conn.close()
    return serie

def desactivar_series_anteriores(patient_id):
    """Desactiva todas las series anteriores de un paciente"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE serie_terapeutica
        SET activa = 0
        WHERE patient_id = ?
    ''', (patient_id,))
    
    conn.commit()
    conn.close()

def create_serie_terapeutica(nombre, tipo_terapia, sesiones_recomendadas, patient_id, posturas_orden):
    """Crea una nueva serie terapéutica"""
    serie_activa = get_serie_activa(patient_id)
    if serie_activa:
        raise ValueError("El paciente ya tiene una serie terapéutica activa.")
    
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    desactivar_series_anteriores(patient_id)
    
    cursor.execute('''
        INSERT INTO serie_terapeutica (nombre, tipo_terapia, sesiones_recomendadas, patient_id, activa)
        VALUES (?, ?, ?, ?, 1)
    ''', (nombre, tipo_terapia, sesiones_recomendadas, patient_id))
    
    id_serie = cursor.lastrowid
    
    for postura_id, orden, duracion in posturas_orden:
        cursor.execute('''
            INSERT INTO postura_en_serie (id_serie, id_postura, orden, duracion_min)
            VALUES (?, ?, ?, ?)
        ''', (id_serie, postura_id, orden, duracion))
    
    conn.commit()
    conn.close()
    return id_serie

def get_series_by_patient(patient_id):
    """Obtiene las series de un paciente"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    series = cursor.execute('''
        SELECT 
            st.id_serie, 
            st.nombre, 
            st.tipo_terapia, 
            st.sesiones_recomendadas,
            (SELECT COUNT(*) FROM sesion s WHERE s.id_serie = st.id_serie) as sesiones_completadas,
            CASE 
                WHEN (SELECT COUNT(*) FROM sesion s WHERE s.id_serie = st.id_serie) >= st.sesiones_recomendadas 
                THEN 1 
                ELSE 0 
            END as serie_completa
        FROM serie_terapeutica st
        WHERE st.patient_id = ? AND st.activa = 1
    ''', (patient_id,)).fetchall()
    
    conn.close()
    return series

def get_posturas_by_serie(id_serie):
    """Obtiene las posturas de una serie"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    posturas = cursor.execute('''
        SELECT p.id_postura, p.nombre_es, p.nombre_sans, pes.orden, pes.duracion_min
        FROM postura p
        JOIN postura_en_serie pes ON p.id_postura = pes.id_postura
        WHERE pes.id_serie = ?
        ORDER BY pes.orden
    ''', (id_serie,)).fetchall()
    
    conn.close()
    return posturas

def get_tiempo_efectivo_serie(id_serie):
    """Calcula el tiempo efectivo de una serie"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    tiempo_total = cursor.execute('''
        SELECT SUM(duracion_min)
        FROM postura_en_serie
        WHERE id_serie = ?
    ''', (id_serie,)).fetchone()[0] or 0
    
    conn.close()
    return tiempo_total

def create_sesion(id_serie, fecha, hora_inicio, hora_fin, intensidad_inicio, intensidad_final, comentario):
    """Crea un registro de sesión"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    try:
        tiempo_efectivo = get_tiempo_efectivo_serie(id_serie)
        
        cursor.execute('''
            INSERT INTO sesion (
                id_serie, fecha, hora_inicio, hora_fin,
                intensidad_inicio, intensidad_final, comentario,
                tiempo_efectivo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_serie, fecha.strftime('%Y-%m-%d'), hora_inicio, hora_fin, 
              intensidad_inicio, intensidad_final, comentario, tiempo_efectivo))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_sesiones_by_serie(id_serie):
    """Obtiene las sesiones de una serie"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    
    sesiones = cursor.execute('''
        SELECT id_sesion, fecha, hora_inicio, hora_fin, 
               intensidad_inicio, intensidad_final, comentario,
               tiempo_efectivo
        FROM sesion
        WHERE id_serie = ?
        ORDER BY fecha, hora_inicio
    ''', (id_serie,)).fetchall()
    
    columns = ['id_sesion', 'fecha', 'hora_inicio', 'hora_fin', 
              'intensidad_inicio', 'intensidad_final', 'comentario',
              'tiempo_efectivo']
    result = [dict(zip(columns, sesion)) for sesion in sesiones]
    
    conn.close()
    return result

def delete_serie(id_serie):
    """Elimina una serie y sus registros relacionados"""
    conn = sqlite3.connect('proyecto/instructor_patients.db')
    cursor = conn.cursor()
    success = False
    
    try:
        cursor.execute('BEGIN TRANSACTION')
        cursor.execute('DELETE FROM sesion WHERE id_serie = ?', (id_serie,))
        cursor.execute('DELETE FROM postura_en_serie WHERE id_serie = ?', (id_serie,))
        cursor.execute('DELETE FROM serie_terapeutica WHERE id_serie = ?', (id_serie,))
        conn.commit()
        success = True
    except Exception as e:
        conn.rollback()
        print("Error al eliminar serie:", str(e))
    finally:
        conn.close()
        return success 