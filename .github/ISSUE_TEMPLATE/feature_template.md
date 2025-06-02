---
name: 🚀 Feature
about: Nueva funcionalidad para el sistema
title: "[Feature] "
labels: enhancement, feature
assignees: 
---

## 📌 Feature: Registro & Autenticación

**Como** usuario del sistema (instructor o paciente)  
**Quiero** poder registrarme en el sistema e ingresar con mis credenciales  
**Para** poder realizar mis actividades específicas de mi rol  

---

### ✅ Criterios de Aceptación
- [ ] El usuario puede registrarse con los campos obligatorios según su rol.
- [ ] El login está disponible desde la página principal.
- [ ] La autenticación se realiza mediante Keycloak y respeta los flujos de seguridad definidos.

---

### 🧪 Definición de Done
- [ ] Código implementado y commit con mensaje claro.
- [ ] Tests unitarios que cubren la lógica de autenticación.
- [ ] Tests de integración que verifican el flujo end-to-end con Keycloak.
- [ ] Documentación del flujo de autenticación actualizada (README o Wiki).
- [ ] Pull Request aprobado por al menos un revisor.
- [ ] Validado el funcionamiento en entorno Docker.

---

### ⏱️ Estimación
**Puntos de historia**: [1, 2, 3, 5, 8]

---

### 🧩 Componentes Afectados
- [ ] FastAPI Backend  
- [ ] Frontend/Templates  
- [ ] Base de datos SQLite  
- [ ] Keycloak Integration  

---

### 🔁 Contexto
(Agrega aquí cualquier información adicional sobre esta feature o su historia de desarrollo)
