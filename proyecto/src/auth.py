from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from keycloak_config import keycloak_openid

router = APIRouter()
templates = Jinja2Templates(directory="proyecto/templates")

# Función para obtener información del usuario desde el token
def get_user_info_from_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return keycloak_openid.userinfo(token)
    except Exception:
        return None

# Ruta de login - Maneja la autenticación de usuarios
@router.post("/login")
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
            return templates.TemplateResponse("index.html", {"request": request, "error": "Tu usuario no tiene un rol válido asignado."})

