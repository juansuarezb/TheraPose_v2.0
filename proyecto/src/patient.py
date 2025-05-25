from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .auth import get_user_info_from_token

templates = Jinja2Templates(directory="proyecto/templates")
router = APIRouter()

@router.get("/patient/dashboard", response_class=HTMLResponse)
def patient_dashboard(request: Request):
    """
    Dashboard del paciente:
    1. Verifica que el usuario sea paciente
    2. Renderiza el dashboard con la información del usuario
    """
    user_info = get_user_info_from_token(request)
    if not user_info or "patient" not in user_info.get("realm_access", {}).get("roles", []):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("patient_dashboard.html", {"request": request, "user": user_info}) 