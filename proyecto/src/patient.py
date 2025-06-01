from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token
from .database import get_series_by_patient, get_posturas_by_serie

templates = Jinja2Templates(directory="proyecto/templates")
router = APIRouter()

@router.get("/patient/dashboard", response_class=HTMLResponse)
def patient_dashboard(request: Request):
    """
    Dashboard del paciente:
    1. Verifica que el usuario sea paciente
    2. Obtiene las series asignadas al paciente
    3. Renderiza el dashboard con la información del usuario y sus series
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=302)
    
    # Obtener las series del paciente
    patient_id = user_info.get("sub")
    print(f"Buscando series para el paciente: {patient_id}")  # Debug log
    series_data = get_series_by_patient(patient_id)
    print(f"Series encontradas: {series_data}")  # Debug log
    
    # Formatear los datos de las series
    series = []
    for serie in series_data:
        serie_dict = {
            "id_serie": serie[0],
            "nombre": serie[1],
            "tipo_terapia": serie[2],
            "sesiones_recomendadas": serie[3],
            "sesiones_completadas": serie[4],
            "serie_completa": serie[5] == 1,  # Convert to boolean
            "posturas": get_posturas_by_serie(serie[0])
        }
        series.append(serie_dict)
    
    print(f"Series formateadas: {series}")  # Debug log
    
    return templates.TemplateResponse(
        "patient_dashboard.html", 
        {
            "request": request, 
            "user": user_info,
            "series": series
        }
    ) 