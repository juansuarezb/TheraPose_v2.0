import time
from keycloak_config import keycloak_openid, keycloak_admin, KEYCLOAK_SERVER_URL, KEYCLOAK_ADMIN_USERNAME, KEYCLOAK_ADMIN_PASSWORD, KEYCLOAK_REALM
from keycloak.exceptions import KeycloakAuthenticationError
from keycloak import KeycloakAdmin

default_admin_tokens = {
    'access_token': None,
    'refresh_token': None,
    'expires_at': 0
}
admin_tokens = default_admin_tokens.copy()

def refresh_keycloak_admin_token():
    """
    Maneja el refresco del token de administrador:
    1. Crea una nueva instancia de KeycloakAdmin con las credenciales actuales
    2. Actualiza la instancia global de keycloak_admin
    """
    global keycloak_admin
    try:
        # Crear nueva instancia de KeycloakAdmin
        keycloak_admin = KeycloakAdmin(
            server_url=KEYCLOAK_SERVER_URL,
            username=KEYCLOAK_ADMIN_USERNAME,
            password=KEYCLOAK_ADMIN_PASSWORD,
            realm_name="master",
            verify=True
        )
        # Cambiar al realm de usuarios
        keycloak_admin.realm_name = KEYCLOAK_REALM
    except Exception as e:
        raise Exception(f"Error refreshing admin token: {str(e)}")

def keycloak_admin_call(method_name, *args, **kwargs):
    """
    Función auxiliar para llamadas seguras a la API de Keycloak:
    1. Intenta ejecutar el método solicitado
    2. Si falla por autenticación, refresca el token y reintenta una vez
    3. Propaga otros errores
    """
    global keycloak_admin
    method = getattr(keycloak_admin, method_name)
    try:
        return method(*args, **kwargs)
    except KeycloakAuthenticationError:
        # Si falla por autenticación, refrescar token y reintentar una vez
        refresh_keycloak_admin_token()
        method = getattr(keycloak_admin, method_name)
        return method(*args, **kwargs)
    except Exception as e:
        raise Exception(f"Error in keycloak_admin_call: {str(e)}") 