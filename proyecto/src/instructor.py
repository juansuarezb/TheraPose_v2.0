# Importaciones necesarias para el módulo de funcionalidades del instructor
from fastapi import APIRouter, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token  # Función para validar autenticación
from .database import add_patient_to_instructor, get_instructor_patients, add_instructor, add_patient, update_patient, get_patient, delete_patient  # Operaciones de base de datos
from .admin import keycloak_admin_call, refresh_keycloak_admin_token  # Funciones de administración de Keycloak
from keycloak_config import keycloak_admin  # Configuración de Keycloak
import sqlite3
import datetime

# Configuración del router para las rutas del instructor
router = APIRouter()
# Configuración de plantillas para renderizar páginas HTML
templates = Jinja2Templates(directory="proyecto/templates")

# Página de registro para instructores - Vista GET
@router.get("/register-instructor", response_class=HTMLResponse)
def register_instructor_page(request: Request):
    """
    Renderiza la página de registro para nuevos instructores.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        TemplateResponse: Página HTML con formulario de registro de instructor
    """
    return templates.TemplateResponse("register_instructor.html", {"request": request})

# Proceso de registro de instructores - Vista POST
@router.post("/register-instructor")
def register_instructor(
    username: str = Form(...),
    email: str = Form(...),
    firstName: str = Form(...),
    lastName: str = Form(...),
    password: str = Form(...),
    fecha_nac: str = Form(...),
    genero: str = Form(...),
    celular: str = Form(...)
):
    """
    Procesa el registro de un nuevo instructor en Keycloak y base de datos.
    
    Args:
        username (str): Nombre de usuario único
        email (str): Correo electrónico del instructor
        firstName (str): Nombre del instructor
        lastName (str): Apellido del instructor
        password (str): Contraseña para la cuenta
        fecha_nac (str): Fecha de nacimiento
        genero (str): Género del instructor
        celular (str): Número de teléfono celular
        
    Returns:
        RedirectResponse: Redirección al login si es exitoso
        TemplateResponse: Página de registro con error si falla
    """
    try:
        # Configurar payload para crear usuario en Keycloak
        payload = {
            "username": username,
            "email": email,
            "firstName": firstName,
            "lastName": lastName,
            "enabled": True,  # Usuario habilitado desde el inicio
            "attributes": {   # Atributos personalizados
                "fecha_nac": [fecha_nac],
                "genero": [genero],
                "celular": [celular]
            },
            "credentials": [{  # Configuración de contraseña
                "type": "password",
                "value": password,
                "temporary": False  # Contraseña permanente (no temporal)
            }]
        }
        
        # Crear usuario en Keycloak
        user_id = keycloak_admin_call("create_user", payload)
        
        # Obtener y asignar el rol de instructor
        role = keycloak_admin_call("get_realm_role", "instructor")
        keycloak_admin_call("assign_realm_roles", user_id=user_id, roles=[role])
        
        # Guardar instructor en la base de datos local SQLite
        add_instructor(
            instructor_id=user_id,
            username=username,
            email=email,
            first_name=firstName,
            last_name=lastName,
            fecha_nac=fecha_nac,
            genero=genero,
            celular=celular
        )
        
        # Redireccionar al login tras registro exitoso
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        # Manejo de errores específicos con mensajes amigables
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        return templates.TemplateResponse("register_instructor.html", {"request": {}, "error": error_message})

# Dashboard principal del instructor
@router.get("/instructor/dashboard", response_class=HTMLResponse)
def instructor_dashboard(request: Request):
    """
    Renderiza el dashboard principal del instructor con sus pacientes asignados.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        RedirectResponse: Redirección al login si no está autenticado
        TemplateResponse: Dashboard del instructor con lista de pacientes
    """
    # Verificar autenticación y rol de instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Obtener ID del instructor y sus pacientes asignados
    instructor_id = user_info.get("sub")
    patients = get_instructor_patients(instructor_id)
    
    return templates.TemplateResponse("instructor_dashboard.html", {
        "request": request,
        "user": user_info,
        "patients": patients
    })

# Registro de paciente por instructor - Vista POST
@router.post("/instructor/create-patient")
def create_patient(request: Request,
    username: str = Form(...),
    email: str = Form(...),
    firstName: str = Form(...),
    lastName: str = Form(...),
    password: str = Form(...),
    fecha_nac: str = Form(...),
    genero: str = Form(...),
    celular: str = Form(...)):
    """
    Crea un nuevo paciente y lo asigna al instructor actual.
    
    Args:
        request (Request): Objeto de petición HTTP
        username (str): Nombre de usuario único para el paciente
        email (str): Correo electrónico del paciente
        firstName (str): Nombre del paciente
        lastName (str): Apellido del paciente
        password (str): Contraseña para la cuenta del paciente
        fecha_nac (str): Fecha de nacimiento
        genero (str): Género del paciente
        celular (str): Número de teléfono celular
        
    Returns:
        RedirectResponse: Redirección al dashboard si es exitoso
        TemplateResponse: Dashboard con error si falla
    """
    # Verificar autenticación del instructor
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    try:
        # Configurar payload para crear paciente en Keycloak
        payload = {
            "username": username,
            "email": email,
            "firstName": firstName,
            "lastName": lastName,
            "enabled": True,
            "attributes": {
                "fecha_nac": [fecha_nac],
                "genero": [genero],
                "celular": [celular]
            },
            "credentials": [{
                "type": "password",
                "value": password,
                "temporary": False
            }]
        }
        
        # Refrescar token de administrador para operaciones en Keycloak
        refresh_keycloak_admin_token()
        
        # Crear usuario paciente en Keycloak
        user_id = keycloak_admin_call('create_user', payload)
        
        # Obtener y asignar rol de paciente
        role = keycloak_admin_call('get_realm_role', "patient")
        keycloak_admin_call('assign_realm_roles', user_id=user_id, roles=[role])
        
        # Guardar paciente en la base de datos local
        add_patient(
            patient_id=user_id,
            username=username,
            email=email,
            first_name=firstName,
            last_name=lastName,
            fecha_nac=fecha_nac,
            genero=genero,
            celular=celular
        )
        
        # Asociar paciente con el instructor actual
        instructor_id = user_info.get("sub")
        add_patient_to_instructor(instructor_id, user_id)
        
        return RedirectResponse(url="/instructor/dashboard", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        # Manejo de errores con mensajes específicos
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        elif "401" in error_message:
            error_message = "Error de autenticación con el servidor. Por favor, intente nuevamente."
        
        patients = []
        return templates.TemplateResponse("instructor_dashboard.html", {"request": request, "user": user_info, "patients": patients, "error": error_message})

# Página de registro de paciente por instructor - Vista GET
@router.get("/instructor/create-patient", response_class=HTMLResponse)
def create_patient_page(request: Request):
    """
    Renderiza la página de formulario para crear un nuevo paciente.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        RedirectResponse: Redirección al login si no está autenticado
        TemplateResponse: Página con formulario de registro de paciente
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register_patient_instructor.html", {"request": request, "user": user_info})

# Carga de secciones parciales del dashboard (AJAX)
@router.get("/partials/{section_name}", response_class=HTMLResponse)
def load_partial(request: Request, section_name: str):
    """
    Carga secciones específicas del dashboard de forma dinámica.
    Utilizado para navegación AJAX sin recargar toda la página.
    
    Args:
        request (Request): Objeto de petición HTTP
        section_name (str): Nombre de la sección a cargar
        
    Returns:
        HTMLResponse: Contenido HTML de la sección solicitada
    """
    # Lista de secciones permitidas para prevenir acceso no autorizado
    allowed = ["dashboard", "patients", "therapeutic-series", "settings", "help"]
    if section_name not in allowed:
        return HTMLResponse("<p>Sección no encontrada</p>", status_code=404)
    
    # Obtener información del usuario para filtrar datos según el rol
    user_info = get_user_info_from_token(request)
    context = {"request": request}

    # Cargar datos específicos según la sección solicitada
    if section_name == "patients":
        # Verificar autorización para acceder a la lista de pacientes
        if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
            return HTMLResponse("<p>No autorizado</p>", status_code=403)
        
        # Obtener pacientes del instructor actual
        instructor_id = user_info.get("sub")
        patients = get_instructor_patients(instructor_id)
        context["patients"] = patients

    return templates.TemplateResponse(f"partials/{section_name}.html", context)

# Página de actualización de información del paciente - Vista GET
@router.get("/instructor/update-patient/{patient_id}", response_class=HTMLResponse)
def update_patient_page(request: Request, patient_id: str):
    """
    Renderiza la página de formulario para actualizar información de un paciente.
    
    Args:
        request (Request): Objeto de petición HTTP
        patient_id (str): ID único del paciente a actualizar
        
    Returns:
        RedirectResponse: Redirección si no está autenticado o paciente no existe
        TemplateResponse: Página con formulario de actualización de paciente
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Obtener información actual del paciente desde la base de datos
    patient = get_patient(patient_id)
    if not patient:
        return RedirectResponse(url="/instructor/dashboard", status_code=status.HTTP_302_FOUND)
    
    # Obtener fecha actual para campos de fecha en el formulario
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    return templates.TemplateResponse("update_patient.html", {
        "request": request,
        "user": user_info,
        "patient": patient,
        "now": now
    })

# Actualización de información del paciente - Vista POST
@router.post("/instructor/update-patient/{patient_id}")
def update_patient_info(
    request: Request,
    patient_id: str,
    username: str = Form(None),
    email: str = Form(None),
    firstName: str = Form(None),
    lastName: str = Form(None),
    fecha_nac: str = Form(None),
    genero: str = Form(None),
    celular: str = Form(None)
):
    """
    Procesa la actualización de información de un paciente en Keycloak y base de datos.
    
    Args:
        request (Request): Objeto de petición HTTP
        patient_id (str): ID único del paciente a actualizar
        username (str, optional): Nuevo nombre de usuario
        email (str, optional): Nuevo correo electrónico
        firstName (str, optional): Nuevo nombre
        lastName (str, optional): Nuevo apellido
        fecha_nac (str, optional): Nueva fecha de nacimiento
        genero (str, optional): Nuevo género
        celular (str, optional): Nuevo número de celular
        
    Returns:
        TemplateResponse: Página de actualización con mensaje de éxito o error
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    try:
        # Preparar payload para actualización en Keycloak (solo campos no nulos)
        payload = {}
        if username is not None:
            payload["username"] = username
        if email is not None:
            payload["email"] = email
        if firstName is not None:
            payload["firstName"] = firstName
        if lastName is not None:
            payload["lastName"] = lastName
        
        # Preparar atributos personalizados para actualización
        attributes = {}
        if fecha_nac is not None:
            attributes["fecha_nac"] = [fecha_nac]
        if genero is not None:
            attributes["genero"] = [genero]
        if celular is not None:
            attributes["celular"] = [celular]
        
        if attributes:
            payload["attributes"] = attributes
        
        # Actualizar en Keycloak si hay cambios
        if payload:
            refresh_keycloak_admin_token()
            keycloak_admin_call('update_user', user_id=patient_id, payload=payload)
        
        # Actualizar información en la base de datos local SQLite
        update_patient(
            patient_id=patient_id,
            username=username,
            email=email,
            first_name=firstName,
            last_name=lastName,
            fecha_nac=fecha_nac,
            genero=genero,
            celular=celular
        )
        
        # Obtener información actualizada del paciente y mostrar mensaje de éxito
        patient = get_patient(patient_id)
        return templates.TemplateResponse(
            "update_patient.html",
            {
                "request": request,
                "user": user_info,
                "patient": patient,
                "success": "¡Paciente actualizado exitosamente!"
            }
        )
    except Exception as e:
        # Manejo de errores con mensajes específicos para el usuario
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        elif "401" in error_message:
            error_message = "Error de autenticación con el servidor. Por favor, intente nuevamente."
        
        # Obtener información actual del paciente para mostrar en caso de error
        patient = get_patient(patient_id)
        return templates.TemplateResponse("update_patient.html", {
            "request": request,
            "user": user_info,
            "patient": patient,
            "error": error_message
        })

# Eliminación de paciente - Vista DELETE (API)
@router.delete("/instructor/delete-patient/{patient_id}")
async def delete_patient_route(patient_id: str, request: Request):
    """
    Elimina un paciente del sistema (tanto de Keycloak como de la base de datos).
    Esta es una operación permanente e irreversible.
    
    Args:
        patient_id (str): ID único del paciente a eliminar
        request (Request): Objeto de petición HTTP para verificar autenticación
        
    Returns:
        JSONResponse: Respuesta JSON con resultado de la operación
        
    Raises:
        HTTPException: Si no está autorizado, paciente no encontrado, o error del servidor
    """
    try:
        # Verificar que el usuario es un instructor autorizado
        user_info = get_user_info_from_token(request)
        if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
            raise HTTPException(status_code=403, detail="No autorizado")
            
        # Eliminar el paciente de la base de datos local y obtener su keycloak_id
        keycloak_id, success = delete_patient(patient_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Eliminar el usuario de Keycloak usando el keycloak_id obtenido
        refresh_keycloak_admin_token()
        keycloak_admin_call('delete_user', user_id=keycloak_id)
        
        return JSONResponse(content={"message": "Paciente eliminado exitosamente"})
    except Exception as e:
        # Propagar la excepción HTTP o crear una nueva si es otro tipo de error
        raise HTTPException(status_code=500, detail=str(e))