[![Typing SVG](https://readme-typing-svg.demolab.com?font=Press+Start+2P&weight=900&size=28&pause=1000&color=003566&background=FFFFFF&center=true&vCenter=true&width=800&height=100&lines=CleanCoders;+Proyecto+calidad+v1.0)](https://git.io/typing-svg)
[![Typing SVG](https://readme-typing-svg.demolab.com?font=Press+Start+2P&weight=900&size=28&pause=1200&color=003566&background=FFFFFF&center=true&vCenter=true&width=800&height=100&lines=TheraPose+%F0%9F%A7%98%E2%80%8D%E2%99%80%EF%B8%8F)](https://git.io/typing-svg)

---

![version](https://img.shields.io/badge/version-1.0.0-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Status](https://img.shields.io/badge/status-en%20desarrollo-orange) ![Clean Code](https://img.shields.io/badge/code%20style-clean--code-brightgreen) ![Focus](https://img.shields.io/badge/yoga-terapéutico-blueviolet) ![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg) [![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/) [![Keycloak](https://img.shields.io/badge/Keycloak-2CA5E0?style=flat&logo=keycloak&logoColor=white)](https://www.keycloak.org/)

---

TheraPose es una plataforma de software para la gestión de clases de yoga terapéutico. El sistema permitirá a los instructores gestionar a sus pacientes, crear y asignar series terapéuticas, y realizar un seguimiento detallado del progreso de cada paciente en su práctica de yoga. Los pacientes podrán acceder a las sesiones asignadas y llevar un registro de su experiencia, incluyendo la intensidad del dolor o molestia durante las sesiones.

---

## Prerrequisitos

- Docker (Docker Desktop).
- Git (Clonar el repositorio).
- Python 3.11+  (Opcional pero recomendable)

---

<h1>Instalación</h1> 

<h2>1. Clona el repositorio en tu máquina local </h2>
<p>Y navega hasta la ubicación del proyecto</p>

```bash
    git clone -b Documentos https://github.com/juansuarezb/TheraPose_v1.0.git
    cd TheraPose_v1.0
```

<h2>2. Descargar la imagen personalizada de Keycloak</h2>

```bash
    docker pull bryanhert/keycloak-yoga:26.1.3
```


<h2>3. Levanta los contenedores </h2> 

```bash
    docker-compose up -d
```

---

## Stack 

| Categoría       | Tecnologías                                                                                                                                                                                                                                                                                                                                 |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Backend**     | ![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-informational?style=flat&logo=fastapi&logoColor=white&color=6aa6f8) ![Python](https://img.shields.io/badge/Python-3.11-informational?style=flat&logo=python&logoColor=white&color=6aa6f8)                                                                                           |
| **Frontend**    | ![Jinja2](https://img.shields.io/badge/Jinja2-3.1.2-informational?style=flat&logo=jinja&logoColor=white&color=6aa6f8) ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-informational?style=flat&logo=javascript&logoColor=white&color=6aa6f8) ![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-informational?style=flat&logo=bootstrap&logoColor=white&color=6aa6f8)                         |
| **Base de Datos** | ![SQLite](https://img.shields.io/badge/SQLite-3.42-informational?style=flat&logo=sqlite&logoColor=white&color=6aa6f8) ![SQLModel](https://img.shields.io/badge/SQLModel-0.0.14-informational?style=flat&logo=sqlalchemy&logoColor=white&color=6aa6f8) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-informational?style=flat&logo=sqlalchemy&logoColor=white&color=6aa6f8)                     |
| **Autenticación** | ![Keycloak](https://img.shields.io/badge/Keycloak-22.0.1-informational?style=flat&logo=keycloak&logoColor=white&color=6aa6f8)  