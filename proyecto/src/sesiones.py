from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from .auth import get_user_info_from_token
from typing import Optional
from .database import (
    get_serie_activa,
    get_posturas_by_serie,
    create_sesion,
    get_series_by_patient
)

router = APIRouter()
templates = Jinja2Templates(directory="proyecto/templates")

NIVELES_INTENSIDAD = [
    "Sin dolor",
    "Leve",
    "Moderado",
    "Intenso",
    "Máximo dolor"
]

@router.get("/patient/iniciar-sesion/{id_serie}", response_class=HTMLResponse)
def iniciar_sesion_page(request: Request, id_serie: int):
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Verificar si la serie está completa
    patient_id = user_info.get("sub")
    series = get_series_by_patient(patient_id)
    for serie in series:
        if serie[0] == id_serie:  # id_serie coincide
            if serie[5] == 1:  # serie_completa es True
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Esta serie ya ha sido completada. No se pueden iniciar más sesiones."
                })
    
    return templates.TemplateResponse("iniciar_sesion.html", {
        "request": request,
        "user": user_info,
        "id_serie": id_serie,
        "niveles_intensidad": NIVELES_INTENSIDAD
    })

@router.post("/patient/iniciar-sesion/{id_serie}")
def iniciar_sesion(request: Request, id_serie: int, intensidad_inicio: int = Form(...)):
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    # Verificar si la serie está completa
    patient_id = user_info.get("sub")
    series = get_series_by_patient(patient_id)
    for serie in series:
        if serie[0] == id_serie:  # id_serie coincide
            if serie[5] == 1:  # serie_completa es True
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error": "Esta serie ya ha sido completada. No se pueden iniciar más sesiones."
                })
    
    posturas = get_posturas_by_serie(id_serie)
    
    return templates.TemplateResponse("sesion_en_curso.html", {
        "request": request,
        "user": user_info,
        "id_serie": id_serie,
        "posturas": posturas,
        "intensidad_inicio": intensidad_inicio,
        "niveles_intensidad": NIVELES_INTENSIDAD
    })

@router.get("/api/posturas-sesion/{id_serie}")
def get_posturas_sesion(id_serie: int):
    posturas = get_posturas_by_serie(id_serie)
    return JSONResponse(content={"posturas": posturas})

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
    try:
        user_info = get_user_info_from_token(request)
        if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        
        # Convertir strings a enteros
        intensidad_inicio = int(intensidad_inicio)
        intensidad_final = int(intensidad_final)
        
        # Validar formato de hora
        try:
            datetime.strptime(hora_inicio, '%H:%M:%S')
            datetime.strptime(hora_fin, '%H:%M:%S')
        except ValueError:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error": "Formato de hora inválido. Use HH:MM:SS"
            })
        
        # Crear registro de la sesión
        create_sesion(
            id_serie=id_serie,
            fecha=datetime.now().date(),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            intensidad_inicio=intensidad_inicio,
            intensidad_final=intensidad_final,
            comentario=comentario
        )
        
        return RedirectResponse(url="/patient/dashboard", status_code=status.HTTP_302_FOUND)
        
    except Exception as e:
        import traceback
        print("Error en finalizar_sesion:", str(e))
        print(traceback.format_exc())
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": f"Error al finalizar la sesión: {str(e)}"
        }) 