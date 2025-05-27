import os
from dotenv import load_dotenv
from keycloak import KeycloakOpenID, KeycloakAdmin

# Cargar variables de entorno
load_dotenv()

# Configuración de Keycloak
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://172.17.0.1:8081/")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "yoga-client")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "ZwdSdvqdylUikyYMdsGAOWnuIzl7B9Tl")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "yoga-realm")
KEYCLOAK_ADMIN_USERNAME = os.getenv("KEYCLOAK_ADMIN_USERNAME", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")

# Inicializar KeycloakOpenID
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET
)

# Inicializar KeycloakAdmin
keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_SERVER_URL,
    username=KEYCLOAK_ADMIN_USERNAME,
    password=KEYCLOAK_ADMIN_PASSWORD,
    realm_name="master",
    verify=True
)
# Cambiar al realm de usuarios después de la autenticación
keycloak_admin.realm_name = KEYCLOAK_REALM 