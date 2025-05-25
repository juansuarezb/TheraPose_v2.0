from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token
from .database import add_patient_to_instructor, get_instructor_patients, add_instructor, add_patient
from .admin import keycloak_admin_call, refresh_keycloak_admin_token
from keycloak_config import keycloak_admin

router = APIRouter()
templates = Jinja2Templates(directory="proyecto/templates")

# Página de registro para instructores
@router.get("/register-instructor", response_class=HTMLResponse)
def register_instructor_page(request: Request):
    return templates.TemplateResponse("register_instructor.html", {"request": request})

# Proceso de registro de instructores
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
        
        # Guardar instructor en la base de datos SQLite
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
        
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        return templates.TemplateResponse("register_instructor.html", {"request": {}, "error": error_message})

# Dashboard del instructor
@router.get("/instructor/dashboard", response_class=HTMLResponse)
def instructor_dashboard(request: Request):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    instructor_id = user_info.get("sub")
    patients = get_instructor_patients(instructor_id)
    return templates.TemplateResponse("instructor_dashboard.html", {
        "request": request,
        "user": user_info,
        "patients": patients
    })

# Registro de paciente por instructor
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
        
        # Guardar paciente en la base de datos SQLite
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