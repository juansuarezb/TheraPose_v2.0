# Importaciones necesarias para el módulo de gestión de series terapéuticas
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token  # Función para validar autenticación
from .database import (  # Funciones de base de datos para series y posturas
    get_posturas_by_tipo_terapia,
    create_serie_terapeutica,
    get_series_by_patient,
    get_instructor_patients,
    get_sesiones_by_serie,
    delete_serie
)

# Configuración del router para las rutas de series terapéuticas
router = APIRouter()
# Configuración de plantillas para renderizar páginas HTML
templates = Jinja2Templates(directory="proyecto/templates")

# Página de creación de serie terapéutica - Vista GET
@router.get("/instructor/create-serie", response_class=HTMLResponse)
def create_serie_page(request: Request):
    """
    Renderiza la página de formulario para crear una nueva serie terapéutica.
    Incluye la lista de pacientes del instructor y tipos de terapia disponibles.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        RedirectResponse: Redirección al login si no está autenticado
        TemplateResponse: Página con formulario de creación de serie
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Obtener pacientes asignados al instructor actual
    instructor_id = user_info.get("sub")
    patients = get_instructor_patients(instructor_id)
    
    return templates.TemplateResponse("create_serie.html", {
        "request": request,
        "user": user_info,
        "patients": patients,
        # Lista de tipos de terapia disponibles en el sistema
        "tipos_terapia": ["Ansiedad", "Depresión", "Dolor de Espalda", "Artritis", "Dolor de Cabeza", "Insomnio", "Mala Postura"]
    })

# API para obtener posturas por tipo de terapia
@router.get("/api/posturas/{tipo_terapia}")
def get_posturas(tipo_terapia: str):
    """
    API endpoint para obtener todas las posturas disponibles para un tipo específico de terapia.
    Utilizado por JavaScript para cargar dinámicamente las posturas en el formulario.
    
    Args:
        tipo_terapia (str): Tipo de terapia (ej: "Ansiedad", "Dolor de Espalda")
        
    Returns:
        JSONResponse: Lista de posturas en formato JSON
    """
    # Obtener posturas desde la base de datos filtradas por tipo de terapia
    posturas = get_posturas_by_tipo_terapia(tipo_terapia)
    return JSONResponse(content={"posturas": posturas})

# Creación de nueva serie terapéutica - Vista POST
@router.post("/instructor/create-serie")
def create_serie(
    request: Request,
    patient_id: str = Form(...),
    nombre: str = Form(...),
    tipo_terapia: str = Form(...),
    sesiones_recomendadas: int = Form(...),
    posturas: str = Form(...)  # JSON string con el orden y duración de cada postura
):
    """
    Procesa la creación de una nueva serie terapéutica personalizada para un paciente.
    
    Args:
        request (Request): Objeto de petición HTTP
        patient_id (str): ID del paciente al que se asigna la serie
        nombre (str): Nombre descriptivo de la serie
        tipo_terapia (str): Tipo de terapia de la serie
        sesiones_recomendadas (int): Número de sesiones recomendadas para completar la serie
        posturas (str): String JSON con información de posturas [id_postura, orden, duracion]
        
    Returns:
        RedirectResponse: Redirección al dashboard si es exitoso
        TemplateResponse: Página de creación con error si falla
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    try:
        import json
        # Parsear el JSON de posturas que contiene [id_postura, orden, duracion]
        posturas_orden = json.loads(posturas)
        
        # Crear la serie terapéutica en la base de datos
        id_serie = create_serie_terapeutica(
            nombre=nombre,
            tipo_terapia=tipo_terapia,
            sesiones_recomendadas=sesiones_recomendadas,
            patient_id=patient_id,
            posturas_orden=posturas_orden
        )
        
        # Redireccionar al dashboard tras creación exitosa
        return RedirectResponse(
            url=f"/instructor/dashboard",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        # En caso de error, volver a mostrar el formulario con mensaje de error
        instructor_id = user_info.get("sub")
        patients = get_instructor_patients(instructor_id)
        return templates.TemplateResponse("create_serie.html", {
            "request": request,
            "user": user_info,
            "patients": patients,
            "tipos_terapia": ["Ansiedad", "Depresión", "Dolor de Espalda", "Artritis", "Dolor de Cabeza", "Insomnio", "Mala Postura"],
            "error": str(e)
        })

# Página de gestión de series terapéuticas - Vista GET
@router.get("/instructor/gestionar-series", response_class=HTMLResponse)
def gestionar_series_page(request: Request):
    """
    Renderiza la página para gestionar (ver, editar, eliminar) series terapéuticas existentes.
    Permite al instructor visualizar el progreso y sesiones de sus pacientes.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        RedirectResponse: Redirección al login si no está autenticado
        TemplateResponse: Página de gestión de series con lista de pacientes
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Obtener lista de pacientes del instructor para el selector
    instructor_id = user_info.get("sub")
    patients = get_instructor_patients(instructor_id)
    
    return templates.TemplateResponse("gestionar_series.html", {
        "request": request,
        "user": user_info,
        "patients": patients
    })

# API para obtener series de un paciente específico
@router.get("/api/series-paciente/{patient_id}")
def get_series_paciente(request: Request, patient_id: str):
    """
    API endpoint para obtener todas las series terapéuticas asignadas a un paciente específico.
    Incluye información de progreso y estado de completitud.
    
    Args:
        request (Request): Objeto de petición HTTP para verificar autenticación
        patient_id (str): ID único del paciente
        
    Returns:
        JSONResponse: Lista de series con información de progreso en formato JSON
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    # Obtener series del paciente desde la base de datos
    series = get_series_by_patient(patient_id)
    series_data = []
    
    # Formatear datos de series para respuesta JSON
    for serie in series:
        series_data.append({
            'id_serie': serie[0],
            'nombre': serie[1],
            'tipo_terapia': serie[2],
            'sesiones_recomendadas': serie[3],
            'sesiones_completadas': serie[4] if len(serie) > 4 else 0,  # Valor por defecto si no existe
            'serie_completa': serie[5] if len(serie) > 5 else 0         # Valor por defecto si no existe
        })
    
    return JSONResponse(content={"series": series_data})

# API para obtener sesiones de una serie específica
@router.get("/api/sesiones-serie/{id_serie}")
def get_sesiones(request: Request, id_serie: int):
    """
    API endpoint para obtener todas las sesiones completadas de una serie terapéutica.
    Incluye información detallada de cada sesión y duración formateada.
    
    Args:
        request (Request): Objeto de petición HTTP para verificar autenticación
        id_serie (int): ID único de la serie terapéutica
        
    Returns:
        JSONResponse: Lista de sesiones con duración formateada en formato JSON
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    # Obtener sesiones de la serie desde la base de datos
    sesiones = get_sesiones_by_serie(id_serie)
    
    # Formatear la duración de cada sesión para presentación amigable
    for sesion in sesiones:
        # Convertir tiempo decimal a minutos y segundos
        minutos = int(sesion['tiempo_efectivo'])
        segundos = round((sesion['tiempo_efectivo'] - minutos) * 60)
        # Crear string formateado de duración
        sesion['duracion_formateada'] = f"{minutos} min{' ' + str(segundos) + ' seg' if segundos > 0 else ''}"
    
    return JSONResponse(content={"sesiones": sesiones})

# API para eliminar una serie terapéutica
@router.delete("/api/eliminar-serie/{id_serie}")
def eliminar_serie(request: Request, id_serie: int):
    """
    API endpoint para eliminar permanentemente una serie terapéutica del sistema.
    Esta operación es irreversible y elimina también todas las sesiones asociadas.
    
    Args:
        request (Request): Objeto de petición HTTP para verificar autenticación
        id_serie (int): ID único de la serie a eliminar
        
    Returns:
        JSONResponse: Mensaje de confirmación o error en formato JSON
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    # Intentar eliminar la serie de la base de datos
    if delete_serie(id_serie):
        return JSONResponse(content={"message": "Serie eliminada correctamente"})
    else:
        return JSONResponse(content={"error": "Error al eliminar la serie"}, status_code=500) 