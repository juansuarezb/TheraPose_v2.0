# Importaciones necesarias para el módulo de autenticación
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from keycloak_config import keycloak_openid  # Configuración de conexión con Keycloak
from keycloak.exceptions import KeycloakAuthenticationError
from .admin import  keycloak_admin_call, keycloak_admin  # Funciones de administración de Keycloak

# Configuración del router para las rutas de autenticación
router = APIRouter()
# Configuración de plantillas Jinja2 para renderizar páginas HTML
templates = Jinja2Templates(directory="proyecto/templates")

# Función para obtener información del usuario desde el token
def get_user_info_from_token(request: Request):
    """
    Extrae y valida el token de acceso desde las cookies de la petición HTTP.
    
    Args:
        request (Request): Objeto de petición HTTP de FastAPI
        
    Returns:
        dict: Información del usuario si el token es válido, None en caso contrario
    """
    # Obtener el token de acceso desde las cookies
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Utilizar el token para obtener información del usuario desde Keycloak
        return keycloak_openid.userinfo(token)
    except Exception:
        # Si hay cualquier error al validar el token, retornar None
        return None

# Ruta de login - Maneja la autenticación de usuarios mediante POST
@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """
    Procesa el login de usuarios validando credenciales con Keycloak.
    Redirige al dashboard correspondiente según el rol del usuario.
    
    Args:
        request (Request): Objeto de petición HTTP
        username (str): Nombre de usuario del formulario
        password (str): Contraseña del formulario
        
    Returns:
        RedirectResponse: Redirección al dashboard correspondiente
        TemplateResponse: Página de login con error si las credenciales son inválidas
    """
    try:
        # Autenticar usuario con Keycloak usando credenciales
        token = keycloak_openid.token(username=username, password=password, grant_type="password")
        
        # Obtener información del usuario autenticado
        user_info = keycloak_openid.userinfo(token["access_token"])
        
        # Extraer roles del usuario desde la información de Keycloak
        roles = user_info.get("realm_access", {}).get("roles", [])
        
        # Determinar dashboard de destino basado en el rol del usuario
        if "instructor" in roles:
            dashboard_url = "/instructor/dashboard"
        elif "patient" in roles:
            dashboard_url = "/patient/dashboard"
        else:
            # Si el usuario no tiene rol válido, mostrar error
            return templates.TemplateResponse("index.html", {"request": request, "error": "Tu usuario no tiene un rol válido asignado."})
        
        # Crear respuesta de redirección al dashboard apropiado
        response = RedirectResponse(url=dashboard_url, status_code=status.HTTP_302_FOUND)
        
        # Guardar token de acceso en cookie segura (httponly=True)
        # max_age=7600 significa que la cookie expira en ~2 horas
        response.set_cookie(key="access_token", value=token["access_token"], httponly=True, max_age=7600)
        return response
    except Exception:
        # Si hay error en autenticación, mostrar mensaje de error en login
        return templates.TemplateResponse("index.html", {"request": request, "error": "Usuario o contraseña incorrectos"})

# Ruta GET para mostrar el formulario de login
@router.get("/login")   
def login_form(request: Request):
    """
    Muestra la página de formulario de login.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        TemplateResponse: Página HTML con el formulario de login
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta para manejar el logout de usuarios
@router.get("/logout")
def logout(request: Request):
    """
    Cierra la sesión del usuario eliminando las cookies de autenticación
    y redirigiendo a la página de login.
    
    Args:
        request (Request): Objeto de petición HTTP
        
    Returns:
        RedirectResponse: Redirección a la página de login
    """
    # Crear respuesta de redirección a login
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    # Eliminar cookies de autenticación para cerrar sesión
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    return response 