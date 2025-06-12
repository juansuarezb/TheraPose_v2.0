from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token
from .database import (
    get_posturas_by_tipo_terapia,
    create_serie_terapeutica,
    get_series_by_patient,
    get_instructor_patients,
    get_sesiones_by_serie,
    delete_serie
)

router = APIRouter()
templates = Jinja2Templates(directory="proyecto/templates")

@router.get("/instructor/create-serie", response_class=HTMLResponse)
def create_serie_page(request: Request):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    instructor_id = user_info.get("sub")
    patients = get_instructor_patients(instructor_id)
    
    return templates.TemplateResponse("create_serie.html", {
        "request": request,
        "user": user_info,
        "patients": patients,
        "tipos_terapia": ["Ansiedad", "Depresión", "Dolor de Espalda"]
    })

@router.get("/api/posturas/{tipo_terapia}")
def get_posturas(tipo_terapia: str):
    posturas = get_posturas_by_tipo_terapia(tipo_terapia)
    return JSONResponse(content={"posturas": posturas})

@router.post("/instructor/create-serie")
def create_serie(
    request: Request,
    patient_id: str = Form(...),
    nombre: str = Form(...),
    tipo_terapia: str = Form(...),
    sesiones_recomendadas: int = Form(...),
    posturas: str = Form(...)  # JSON string con el orden y duración de cada postura
):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    try:
        import json
        posturas_orden = json.loads(posturas)  # Lista de [id_postura, orden, duracion]
        
        id_serie = create_serie_terapeutica(
            nombre=nombre,
            tipo_terapia=tipo_terapia,
            sesiones_recomendadas=sesiones_recomendadas,
            patient_id=patient_id,
            posturas_orden=posturas_orden
        )
        
        return RedirectResponse(
            url=f"/instructor/dashboard",
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        instructor_id = user_info.get("sub")
        patients = get_instructor_patients(instructor_id)
        return templates.TemplateResponse("create_serie.html", {
            "request": request,
            "user": user_info,
            "patients": patients,
            "tipos_terapia": ["Ansiedad", "Depresión", "Dolor de Espalda"],
            "error": str(e)
        })

@router.get("/instructor/gestionar-series", response_class=HTMLResponse)
def gestionar_series_page(request: Request):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    instructor_id = user_info.get("sub")
    patients = get_instructor_patients(instructor_id)
    
    return templates.TemplateResponse("gestionar_series.html", {
        "request": request,
        "user": user_info,
        "patients": patients
    })

@router.get("/api/series-paciente/{patient_id}")
def get_series_paciente(request: Request, patient_id: str):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    series = get_series_by_patient(patient_id)
    series_data = []
    for serie in series:
        series_data.append({
            'id_serie': serie[0],
            'nombre': serie[1],
            'tipo_terapia': serie[2],
            'sesiones_recomendadas': serie[3],
            'sesiones_completadas': serie[4] if len(serie) > 4 else 0,
            'serie_completa': serie[5] if len(serie) > 5 else 0
        })
    
    return JSONResponse(content={"series": series_data})

@router.get("/api/sesiones-serie/{id_serie}")
def get_sesiones(request: Request, id_serie: int):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    sesiones = get_sesiones_by_serie(id_serie)
    # Formatear la duración para cada sesión
    for sesion in sesiones:
        minutos = int(sesion['tiempo_efectivo'])
        segundos = round((sesion['tiempo_efectivo'] - minutos) * 60)
        sesion['duracion_formateada'] = f"{minutos} min{' ' + str(segundos) + ' seg' if segundos > 0 else ''}"
    
    return JSONResponse(content={"sesiones": sesiones})

@router.delete("/api/eliminar-serie/{id_serie}")
def eliminar_serie(request: Request, id_serie: int):
    user_info = get_user_info_from_token(request)
    if not user_info or "instructor" not in user_info.get("realm_access", {}).get("roles", []):
        return JSONResponse(content={"error": "No autorizado"}, status_code=401)
    
    if delete_serie(id_serie):
        return JSONResponse(content={"message": "Serie eliminada correctamente"})
    else:
        return JSONResponse(content={"error": "Error al eliminar la serie"}, status_code=500) 