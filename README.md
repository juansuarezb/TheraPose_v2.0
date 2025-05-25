[![Typing SVG](https://readme-typing-svg.demolab.com?font=Press+Start+2P&weight=900&size=28&pause=1000&color=003566&background=FFFFFF&center=true&vCenter=true&width=800&height=100&lines=CleanCoders;+Proyecto+calidad+v1.0)](https://git.io/typing-svg)
[![Typing SVG](https://readme-typing-svg.demolab.com?font=Press+Start+2P&weight=900&size=28&pause=1200&color=003566&background=FFFFFF&center=true&vCenter=true&width=800&height=100&lines=TheraPose+%F0%9F%A7%98%E2%80%8D%E2%99%80%EF%B8%8F)](https://git.io/typing-svg)

---

![version](https://img.shields.io/badge/version-1.0.0-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Status](https://img.shields.io/badge/status-en%20desarrollo-orange) ![Clean Code](https://img.shields.io/badge/code%20style-clean--code-brightgreen) ![Focus](https://img.shields.io/badge/yoga-terapéutico-blueviolet) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg) [![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/) [![Keycloak](https://img.shields.io/badge/Keycloak-2CA5E0?style=flat&logo=keycloak&logoColor=white)](https://www.keycloak.org/)

---

TheraPose es una plataforma de software para la gestión de clases de yoga terapéutico. El sistema permitirá a los instructores gestionar a sus pacientes, crear y asignar series terapéuticas, y realizar un seguimiento detallado del progreso de cada paciente en su práctica de yoga. Los pacientes podrán acceder a las sesiones asignadas y llevar un registro de su experiencia, incluyendo la intensidad del dolor o molestia durante las sesiones.

---

## Prerrequisitos
- <b>WSL 2</b> habilitado - Windows 10/11.
- Tener <b> Ubuntu </b> instalado desde la Microsoft Store
- <b> Docker </b> (Docker Desktop).
- Git (Clonar el repositorio).
- Python 3.11+. 

---

## Instalación 

### 1. Descargar imagen personalizada de Keycloak en el bash.

```bash
docker pull bryanhert/keycloak-yoga:26.1.3

```

<img src="images/paso1.avif" alt="paso1" width="600" height="auto">

### 2. Navega al directorio donde quieres descargar el proyecto y clona el repositorio en tu máquina local. Finalmente, dirígete al proyecto descargado.

```bash
git clone https://github.com/juansuarezb/TheraPose_v1.0.git
cd TheraPose_v1.0
```
<img src="images/paso2.webp" alt="paso2" width="600" height="auto">

### 3. Levantar los servicios con Docker Compose (dentro del proyecto descargado).

```bash
docker-compose up -d
```

<img src="images/paso3.webp" alt="paso3" width="600" height="auto">

> [!IMPORTANT] 
> Hasta este punto ya tenemos el entorno para el manejo de usuarios correctamente instalado.  
> Dirígete a [http://localhost:8080](http://localhost:8080) para acceder a la consola de administración de Keycloak.
> Ingresa con los credenciales "admin" y "admin" respectivamente y comprueba el acceso al keycloak.
> Ahora, se procederá a utilizar Ubuntu desde windows para la instalación del backend de la aplicación.

<img src="images/paso4.webp" alt="paso4" width="600" height="auto">

### 4. Dirígete al proyecto descargado y crea un entorno virtual luego, activalo. 
### Verás un (venv - Virtual Environment) en la línea de comandos que verifica la correcta creación del ambiente.

```bash
cd /mnt/d/EPN/2025-A/TheraPose_v1.0
python3 -m venv venv
source venv/bin/activate
```
<img src="images/paso5.avif" alt="paso5" width="600" height="auto">

### 5. Actualizar pip y herramientas básicas e instala las depedencias del proyecto.

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

<img src="images/paso6.avif" alt="paso6" width="600" height="auto">

### 6. Establecer el PYTHONPATH y ejecutar la app con recarga automática
### Dirígete a [http://localhost:8000](http://localhost:8000) para acceder al index de la página web.

```bash
PYTHONPATH=proyecto uvicorn src.main:app --reload
```
<img src="images/paso7.webp" alt="paso7" width="600" height="auto">
<img src="images/paso7.webp" alt="paso8" width="600" height="auto">
---

## Stack 

| Categoría       | Tecnologías                                                                                                                                                                                 |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Backend**     | ![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-informational?style=flat&logo=fastapi&logoColor=white&color=6aa6f8) ![Python](https://img.shields.io/badge/Python-3.11-informational?style=flat&logo=python&logoColor=white&color=6aa6f8)                                                                                           |
| **Frontend**    | ![Jinja2](https://img.shields.io/badge/Jinja2-3.1.2-informational?style=flat&logo=jinja&logoColor=white&color=6aa6f8) ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-informational?style=flat&logo=javascript&logoColor=white&color=6aa6f8) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-informational?style=flat&logo=bootstrap&logoColor=white&color=6aa6f8)                         |
| **Base de Datos** | ![SQLite](https://img.shields.io/badge/SQLite-3.42-informational?style=flat&logo=sqlite&logoColor=white&color=6aa6f8) ![SQLModel](https://img.shields.io/badge/SQLModel-0.0.14-informational?style=flat&logo=sqlalchemy&logoColor=white&color=6aa6f8) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-informational?style=flat&logo=sqlalchemy&logoColor=white&color=6aa6f8)                     |
| **Autenticación** | ![Keycloak](https://img.shields.io/badge/Keycloak-22.0.1-informational?style=flat&logo=keycloak&logoColor=white&color=6aa6f8)  
| **Autenticación** | ![Keycloak](https://img.shields.io/badge/Keycloak-22.0.1-informational?style=flat&logo=keycloak&logoColor=white&color=6aa6f8)                                                                                                                                                                                                               |
| **DevOps**      | ![Docker](https://img.shields.io/badge/Docker-24.0-informational?style=flat&logo=docker&logoColor=white&color=6aa6f8) ![Docker Compose](https://img.shields.io/badge/Docker_Compose-2.22-informational?style=flat&logo=docker&logoColor=white&color=6aa6f8)                                                                                  |

---

