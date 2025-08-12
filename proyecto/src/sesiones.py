# Importaciones necesarias para el módulo de gestión de sesiones de yoga terapéutico
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from .auth import get_user_info_from_token  # Función para validar autenticación
from typing import Optional
from .database import (  # Funciones de base de datos para sesiones y series
    get_serie_activa,
    get_posturas_by_serie,
    create_sesion,
    get_series_by_patient
)

# Configuración del router para las rutas de sesiones
router = APIRouter()
# Configuración de plantillas para renderizar páginas HTML
templates = Jinja2Templates(directory="proyecto/templates")

# Niveles de intensidad de dolor/malestar para evaluación del paciente
NIVELES_INTENSIDAD = [
    "Sin dolor",      # Nivel 0
    "Leve",          # Nivel 1
    "Moderado",      # Nivel 2
    "Intenso",       # Nivel 3
    "Máximo dolor"   # Nivel 4
]

# Página de inicio de sesión terapéutica - Vista GET
@router.get("/patient/iniciar-sesion/{id_serie}", response_class=HTMLResponse)
def iniciar_sesion_page(request: Request, id_serie: int):
    """
    Renderiza la página de preparación para iniciar una nueva sesión de yoga terapéutico.
    Valida que la serie no esté completa antes de permitir iniciar la sesión.
    
    Args:
        request (Request): Objeto de petición HTTP
        id_serie (int): ID único de la serie terapéutica a realizar
        
    Returns:
        RedirectResponse: Redirección al login si no está autenticado
        TemplateResponse: Página de error si la serie está completa
        TemplateResponse: Página de inicio de sesión con formulario de intensidad inicial
    """
    # Verificar autenticación del paciente
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Verificar si la serie ya está completa para prevenir sesiones adicionales
    patient_id = user_info.get("sub")
    series = get_series_by_patient(patient_id)
    
    for serie in series:
        if serie[0] == id_serie:  # Encontrar la serie por ID
            if serie[5] == 1:  # Verificar si serie_completa es True
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Esta serie ya ha sido completada. No se pueden iniciar más sesiones."
                })
    
    # Renderizar página de inicio de sesión con niveles de intensidad
    return templates.TemplateResponse("iniciar_sesion.html", {
        "request": request,
        "user": user_info,
        "id_serie": id_serie,
        "niveles_intensidad": NIVELES_INTENSIDAD
    })

# Inicio de sesión terapéutica - Vista POST
@router.post("/patient/iniciar-sesion/{id_serie}")
def iniciar_sesion(request: Request, id_serie: int, intensidad_inicio: int = Form(...)):
    """
    Procesa el inicio de una sesión de yoga terapéutico después de registrar la intensidad inicial.
    Carga las posturas de la serie y presenta la interfaz de sesión activa.
    
    Args:
        request (Request): Objeto de petición HTTP
        id_serie (int): ID único de la serie terapéutica
        intensidad_inicio (int): Nivel de intensidad inicial del dolor/malestar (0-4)
        
    Returns:
        RedirectResponse: Redirección al login si no está autenticado
        TemplateResponse: Página de error si la serie está completa
        TemplateResponse: Página de sesión en curso con posturas y controles
    """
    # Verificar autenticación del paciente
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Verificar nuevamente si la serie está completa antes de iniciar
    patient_id = user_info.get("sub")
    series = get_series_by_patient(patient_id)
    for serie in series:
        if serie[0] == id_serie:  # Encontrar la serie por ID
            if serie[5] == 1:  # Verificar si serie_completa es True
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Esta serie ya ha sido completada. No se pueden iniciar más sesiones."
                })
    
    # Obtener todas las posturas de la serie ordenadas según la configuración
    posturas = get_posturas_by_serie(id_serie)
    
    # Renderizar página de sesión en curso con toda la información necesaria
    return templates.TemplateResponse("sesion_en_curso.html", {
        "request": request,
        "user": user_info,
        "id_serie": id_serie,
        "posturas": posturas,  # Lista ordenada de posturas con duraciones
        "intensidad_inicio": intensidad_inicio,
        "niveles_intensidad": NIVELES_INTENSIDAD
    })

# API para obtener posturas de una sesión (uso interno)
@router.get("/api/posturas-sesion/{id_serie}")
def get_posturas_sesion(id_serie: int):
    """
    API endpoint para obtener las posturas de una serie específica.
    Utilizado por JavaScript durante la sesión para cargar dinámicamente las posturas.
    
    Args:
        id_serie (int): ID único de la serie terapéutica
        
    Returns:
        JSONResponse: Lista de posturas con orden y duración en formato JSON
    """
    # Obtener posturas de la serie ordenadas según configuración
    posturas = get_posturas_by_serie(id_serie)
    return JSONResponse(content={"posturas": posturas})

# Finalización de sesión terapéutica - Vista POST
@router.post("/patient/finalizar-sesion/{id_serie}")
def finalizar_sesion(
    request: Request,
    id_serie: int,
    intensidad_inicio: int = Form(...),
    intensidad_final: int = Form(...),
    comentario: str = Form(...),
    hora_inicio: Optional[str] = Form(None),
    hora_fin: Optional[str] = Form(None)
):
    """
    Procesa la finalización de una sesión de yoga terapéutico y guarda los resultados.
    Registra la evolución del paciente y actualiza el progreso de la serie.
    
    Args:
        request (Request): Objeto de petición HTTP
        id_serie (int): ID único de la serie terapéutica
        intensidad_inicio (int): Nivel de intensidad al inicio de la sesión (0-4)
        intensidad_final (int): Nivel de intensidad al final de la sesión (0-4)
        comentario (str): Comentarios del paciente sobre la sesión
        hora_inicio (str, optional): Hora de inicio en formato HH:MM:SS
        hora_fin (str, optional): Hora de finalización en formato HH:MM:SS
        
    Returns:
        RedirectResponse: Redirección al dashboard del paciente si es exitoso
        TemplateResponse: Página de error si ocurre algún problema
    """
    try:
        # Verificar autenticación del paciente
        user_info = get_user_info_from_token(request)
        if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
        # Convertir strings a enteros para validación
        intensidad_inicio = int(intensidad_inicio)
        intensidad_final = int(intensidad_final)
        
        # Validar formato de hora recibido desde el frontend
        try:
            datetime.strptime(hora_inicio, '%H:%M:%S')
            datetime.strptime(hora_fin, '%H:%M:%S')
        except ValueError:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Formato de hora inválido. Use HH:MM:SS"
            })
        
        # Crear registro de la sesión completada en la base de datos
        create_sesion(
            id_serie=id_serie,
            fecha=datetime.now().date(),           # Fecha actual
            hora_inicio=hora_inicio,               # Hora registrada por JavaScript
            hora_fin=hora_fin,                     # Hora registrada por JavaScript
            intensidad_inicio=intensidad_inicio,   # Evaluación inicial del paciente
            intensidad_final=intensidad_final,     # Evaluación final del paciente
            comentario=comentario                  # Reflexiones del paciente
        )
        
        # Redireccionar al dashboard tras completar la sesión exitosamente
        return RedirectResponse(url="/patient/dashboard", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        # Logging detallado para debugging de errores
        import traceback
        print("Error en finalizar_sesion:", str(e))
        print(traceback.format_exc())
        
        # Mostrar página de error con información específica
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": f"Error al finalizar la sesión: {str(e)}"
        }) 