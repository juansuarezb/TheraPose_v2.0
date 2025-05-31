from fastapi import APIRouter, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token
from .database import add_patient_to_instructor, get_instructor_patients, add_instructor, add_patient, update_patient, get_patient, delete_patient
from .admin import keycloak_admin_call, refresh_keycloak_admin_token
from keycloak_config import keycloak_admin
import sqlite3

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
        
        # Guardar instructor en la base de datos 
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
        
        # Guardar paciente en la base de datos 
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

# Página de registro de paciente por instructor 
@router.get("/instructor/create-patient", response_class=HTMLResponse)
def create_patient_page(request: Request):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("register_patient_instructor.html", {"request": request, "user": user_info})

@router.get("/partials/{section_name}", response_class=HTMLResponse)
def load_partial(request: Request, section_name: str):
    allowed = ["dashboard", "patients", "therapeutic-series", "settings", "help"]
    if section_name not in allowed:
        return HTMLResponse("<p>Sección no encontrada</p>", status_code=404)
    
    # Obtener info del usuario para filtrar datos 
    user_info = get_user_info_from_token(request)
    context = {"request": request}

    if section_name == "patients":
        if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
            return HTMLResponse("<p>No autorizado</p>", status_code=403)
        instructor_id = user_info.get("sub")
        patients = get_instructor_patients(instructor_id)
        context["patients"] = patients

    return templates.TemplateResponse(f"partials/{section_name}.html", context)

@router.get("/instructor/update-patient/{patient_id}", response_class=HTMLResponse)
def update_patient_page(request: Request, patient_id: str):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Obtener información del paciente
    patient = get_patient(patient_id)
    if not patient:
        return RedirectResponse(url="/instructor/dashboard", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("update_patient.html", {
        "request": request,
        "user": user_info,
        "patient": patient
    })

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
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    try:
        # Actualizar en Keycloak
        payload = {}
        if username is not None:
            payload["username"] = username
        if email is not None:
            payload["email"] = email
        if firstName is not None:
            payload["firstName"] = firstName
        if lastName is not None:
            payload["lastName"] = lastName
        
        # Actualizar atributos personalizados
        attributes = {}
        if fecha_nac is not None:
            attributes["fecha_nac"] = [fecha_nac]
        if genero is not None:
            attributes["genero"] = [genero]
        if celular is not None:
            attributes["celular"] = [celular]
        
        if attributes:
            payload["attributes"] = attributes
        
        if payload:
            refresh_keycloak_admin_token()
            keycloak_admin_call('update_user', user_id=patient_id, payload=payload)
        
        # Actualizar en SQLite
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
        # Renderizar la plantilla con mensaje de éxito
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
        error_message = str(e)
        if "User exists with same email" in error_message:
            error_message = "El correo electrónico ya está registrado. Por favor, usa otro correo electrónico."
        elif "User exists with same username" in error_message:
            error_message = "El nombre de usuario ya está en uso. Por favor, elige otro nombre de usuario."
        elif "401" in error_message:
            error_message = "Error de autenticación con el servidor. Por favor, intente nuevamente."
        
        # Obtener información del paciente
        patient = get_patient(patient_id)
        return templates.TemplateResponse("update_patient.html", {
            "request": request,
            "user": user_info,
            "patient": patient,
            "error": error_message
        })

@router.delete("/instructor/delete-patient/{patient_id}")
async def delete_patient_route(patient_id: str, request: Request):
    try:
        # Verificar que el usuario es un instructor
        user_info = get_user_info_from_token(request)
        if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
            raise HTTPException(status_code=403, detail="No autorizado")
            
        # Eliminar el paciente de la base de datos y obtener su keycloak_id
        keycloak_id, success = delete_patient(patient_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Eliminar el usuario de Keycloak usando keycloak_admin_call
        refresh_keycloak_admin_token()
        keycloak_admin_call('delete_user', user_id=keycloak_id)
        
        return JSONResponse(content={"message": "Paciente eliminado exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))