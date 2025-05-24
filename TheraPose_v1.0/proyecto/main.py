from fastapi import FastAPI, Request, Form, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from keycloak_config import keycloak_openid, keycloak_admin
from dotenv import load_dotenv
import os
from keycloak.exceptions import KeycloakAuthenticationError
from proyecto.database import init_db, add_patient_to_instructor, get_instructor_patients
import time

load_dotenv()

app = FastAPI()

# Inicializar la base de datos al arrancar la aplicación
init_db()
admin_tokens = {
    'access_token': None,
    'refresh_token': None,
    'expires_at': 0
}

app.mount("/static", StaticFiles(directory="proyecto/static"), name="static")
templates = Jinja2Templates(directory="proyecto/templates")

# --- Funciones auxiliares ---

# Función para obtener información del usuario desde el token
def get_user_info_from_token(request: Request):
    """
    Extrae y valida la información del usuario desde el token de acceso
    Retorna None si no hay token o si es inválido
    """
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return keycloak_openid.userinfo(token)
    except Exception:
        return None

# --- Rutas de autenticación ---

# Ruta principal - Página de inicio
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Renderiza la página de inicio con el formulario de login
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta de login - Maneja la autenticación de usuarios
@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Proceso de login:
    1. Intenta autenticar al usuario con Keycloak
    2. Obtiene los roles del usuario
    3. Redirige al dashboard de l paciente o instructor correspondiente según el rol
    4. Establece la cookie con el token de acceso
    """
    try:
        token = keycloak_openid.token(username=username, password=password, grant_type="password")
        user_info = keycloak_openid.userinfo(token["access_token"])
        roles = user_info.get("realm_access", {}).get("roles", [])
        if "instructor" in roles:
            dashboard_url = "/instructor/dashboard"
        elif "patient" in roles:
            dashboard_url = "/patient/dashboard"
        else:
            return templates.TemplateResponse("index.html", {"request": request, "error": "Tu usuario no tiene un rol válido asignado."})
        response = RedirectResponse(url=dashboard_url, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=token["access_token"], httponly=True, max_age=7600)
        return response
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Usuario o contraseña incorrectos"})

# --- Rutas de registro ---

# Página de registro para instructores
@app.get("/register-instructor", response_class=HTMLResponse)
def register_instructor_page(request: Request):
    """
    Renderiza la página de registro para instructores
    """
    return templates.TemplateResponse("register_instructor.html", {"request": request})

# Proceso de registro de instructores
@app.post("/register-instructor")
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
    Proceso de registro de instructores:
    1. Crea el payload con la información del usuario
    2. Crea el usuario en Keycloak
    3. Asigna el rol de instructor
    4. Redirige a la página de inicio
    """
    try:
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
        user_id = keycloak_admin_call("create_user", payload)
        role = keycloak_admin_call("get_realm_role", "instructor")
        keycloak_admin_call("assign_realm_roles", user_id=user_id, roles=[role])
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        return templates.TemplateResponse("register_instructor.html", {"request": {}, "error": error_message})

# --- Funciones de administración de Keycloak ---

def refresh_keycloak_admin_token():
    """
    Maneja el refresco del token de administrador:
    1. Verifica si el token actual es válido
    2. Intenta refrescar el token si existe uno
    3. Si no hay token o el refresh falla, realiza autenticación completa
    4. Actualiza los tokens en el diccionario global
    """
    global keycloak_admin, admin_tokens
    from keycloak_config import KEYCLOAK_SERVER_URL, KEYCLOAK_ADMIN_USERNAME, KEYCLOAK_ADMIN_PASSWORD, KEYCLOAK_REALM
    from keycloak import KeycloakAdmin
    
    current_time = time.time()
    
    if admin_tokens['access_token'] and current_time < admin_tokens['expires_at']:
        keycloak_admin.token = admin_tokens['access_token']
        return
    
    try:
        if admin_tokens['refresh_token']:
            try:
                tokens = keycloak_admin.refresh_token(admin_tokens['refresh_token'])
                admin_tokens['access_token'] = tokens['access_token']
                admin_tokens['refresh_token'] = tokens['refresh_token']
                admin_tokens['expires_at'] = current_time + tokens['expires_in']
                keycloak_admin.token = admin_tokens['access_token']
                return
            except KeycloakAuthenticationError:
                pass
        
        keycloak_admin = KeycloakAdmin(
            server_url=KEYCLOAK_SERVER_URL,
            username=KEYCLOAK_ADMIN_USERNAME,
            password=KEYCLOAK_ADMIN_PASSWORD,
            realm_name="master",
            verify=True
        )
        keycloak_admin.realm_name = KEYCLOAK_REALM
        
        admin_tokens['access_token'] = keycloak_admin.token
        admin_tokens['refresh_token'] = keycloak_admin.refresh_token
        admin_tokens['expires_at'] = current_time + 300
        
    except Exception as e:
        raise Exception(f"Error refreshing admin token: {str(e)}")

def keycloak_admin_call(method_name, *args, **kwargs):
    """
    Función auxiliar para llamadas seguras a la API de Keycloak:
    1. Intenta ejecutar el método solicitado
    2. Si falla por autenticación, refresca el token y reintenta
    3. Propaga otros errores
    """
    global keycloak_admin
    method = getattr(keycloak_admin, method_name)
    try:
        return method(*args, **kwargs)
    except KeycloakAuthenticationError as e:
        if '401' in str(e):
            refresh_keycloak_admin_token()
            method = getattr(keycloak_admin, method_name)
            return method(*args, **kwargs)
        else:
            raise

# --- Rutas de gestión de pacientes ---

@app.post("/instructor/create-patient")
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
    Proceso de creación de pacientes por instructores:
    1. Verifica que el usuario sea instructor
    2. Crea el usuario en Keycloak con rol de paciente
    3. Establece la relación instructor-paciente en la base de datos
    4. Redirige al dashboard del instructor
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    try:
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
        refresh_keycloak_admin_token()
        user_id = keycloak_admin_call('create_user', payload)
        role = keycloak_admin_call('get_realm_role', "patient")
        keycloak_admin_call('assign_realm_roles', user_id=user_id, roles=[role])
        
        instructor_id = user_info.get("sub")
        add_patient_to_instructor(instructor_id, user_id)
        
        return RedirectResponse(url="/instructor/dashboard", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        elif "401" in error_message:
            error_message = "Error de autenticación con el servidor. Por favor, intente nuevamente."
        patients = []
        return templates.TemplateResponse("instructor_dashboard.html", {"request": request, "user": user_info, "patients": patients, "error": error_message})

# --- Rutas de dashboards ---

@app.get("/patient/dashboard", response_class=HTMLResponse)
def patient_dashboard(request: Request):
    """
    Dashboard del paciente:
    1. Verifica que el usuario sea paciente
    2. Renderiza el dashboard con la información del usuario
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("patient_dashboard.html", {"request": request, "user": user_info}) 

@app.get("/instructor/dashboard", response_class=HTMLResponse)
def instructor_dashboard(request: Request):
    """
    Dashboard del instructor:
    1. Verifica que el usuario sea instructor
    2. Obtiene la lista de pacientes asociados
    3. Obtiene la información detallada de cada paciente
    4. Renderiza el dashboard con la información del instructor y sus pacientes
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    instructor_id = user_info.get("sub")
    patient_ids = get_instructor_patients(instructor_id)
    
    patients = []
    for patient_id in patient_ids:
        try:
            patient_info = keycloak_admin_call('get_user', user_id=patient_id)
            patients.append({
                "id": patient_id,
                "username": patient_info.get("username"),
                "email": patient_info.get("email"),
                "firstName": patient_info.get("firstName"),
                "lastName": patient_info.get("lastName"),
                "fecha_nac": patient_info.get("attributes", {}).get("fecha_nac", [""])[0],
                "genero": patient_info.get("attributes", {}).get("genero", [""])[0],
                "celular": patient_info.get("attributes", {}).get("celular", [""])[0]
            })
        except Exception:
            continue
    
    return templates.TemplateResponse("instructor_dashboard.html", {
        "request": request,
        "user": user_info,
        "patients": patients
    })
