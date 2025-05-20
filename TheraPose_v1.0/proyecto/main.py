from fastapi import FastAPI, Request, Form, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from keycloak_config import keycloak_openid, keycloak_admin
from dotenv import load_dotenv
import os
from keycloak.exceptions import KeycloakAuthenticationError
from proyecto.database import init_db, add_patient_to_instructor, get_instructor_patients

load_dotenv()

app = FastAPI()

# Inicializar la base de datos al arrancar la aplicación
init_db()

app.mount("/static", StaticFiles(directory="proyecto/static"), name="static")
templates = Jinja2Templates(directory="proyecto/templates")

# --- Helper para obtener info de usuario autenticado ---
def get_user_info_from_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return keycloak_openid.userinfo(token)
    except Exception:
        return None

# --- Login para ambos roles ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        token = keycloak_openid.token(username=username, password=password, grant_type="password")
        user_info = keycloak_openid.userinfo(token["access_token"])
        roles = user_info.get("realm_access", {}).get("roles", [])
        if "instructor" in roles:
            dashboard_url = "/instructor/dashboard"
        elif "patient" in roles:
            dashboard_url = "/patient/dashboard"
        else:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Tu usuario no tiene un rol válido asignado."})
        response = RedirectResponse(url=dashboard_url, status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=token["access_token"], httponly=True, max_age=3600)
        return response
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Usuario o contraseña incorrectos"})

# --- Registro solo para instructor ---
@app.get("/register-instructor", response_class=HTMLResponse)
def register_instructor_page(request: Request):
    return templates.TemplateResponse("register_instructor.html", {"request": request})

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

# --- Refresco de token admin y helper para llamadas seguras ---
def refresh_keycloak_admin_token():
    global keycloak_admin
    from keycloak_config import KEYCLOAK_SERVER_URL, KEYCLOAK_ADMIN_USERNAME, KEYCLOAK_ADMIN_PASSWORD, KEYCLOAK_REALM
    from keycloak import KeycloakAdmin
    keycloak_admin = KeycloakAdmin(
        server_url=KEYCLOAK_SERVER_URL,
        username=KEYCLOAK_ADMIN_USERNAME,
        password=KEYCLOAK_ADMIN_PASSWORD,
        realm_name="master",
        verify=True
    )
    keycloak_admin.realm_name = KEYCLOAK_REALM

def keycloak_admin_call(method_name, *args, **kwargs):
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

# --- Crear paciente (solo instructor) ---
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
        
        # Guardar la relación instructor-paciente
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

# --- Dashboard del paciente ---
@app.get("/patient/dashboard", response_class=HTMLResponse)
def patient_dashboard(request: Request):
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("patient_dashboard.html", {"request": request, "user": user_info}) 

# --- Dashboard del instructor ---
@app.get("/instructor/dashboard", response_class=HTMLResponse)
def instructor_dashboard(request: Request):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Obtener los pacientes del instructor
    instructor_id = user_info.get("sub")
    patient_ids = get_instructor_patients(instructor_id)
    
    # Obtener la información de cada paciente
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
