from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
from .database import init_db
# Importar y registrar routers
from .auth import router as auth_router
from .instructor import router as instructor_router
from .patient import router as patient_router
from .series import router as series_router
from .sesiones import router as sesiones_router

# Cargar variables de entorno
load_dotenv()

app = FastAPI()

# Inicializar la base de datos
init_db()

# Montar archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="proyecto/static"), name="static")
templates = Jinja2Templates(directory="proyecto/templates")

# Incluir todos los routers
app.include_router(auth_router)
app.include_router(instructor_router)
app.include_router(patient_router)
app.include_router(series_router)
app.include_router(sesiones_router)

# Ruta principal - Página de inicio
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


