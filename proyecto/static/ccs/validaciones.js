// validaciones.js
// Validaciones de formularios para login, registro de instructor y paciente

document.addEventListener('DOMContentLoaded', function () {
    // Validación para formularios de registro de instructor
    const formInstructor = document.querySelector('form[action="/register-instructor"]');
    if (formInstructor) {
        formInstructor.addEventListener('submit', function (e) {
            let valid = true;
            let mensajes = [];
            // Usuario
            const username = formInstructor.username.value.trim();
            if (!username) {
                valid = false;
                mensajes.push('El nombre de usuario es obligatorio.');
            }
            // Email solo GMAIL
            const email = formInstructor.email.value.trim();
            if (!/^([a-zA-Z0-9_.+-])+@gmail\.com$/.test(email)) {
                valid = false;
                mensajes.push('El correo debe ser de Gmail y tener formato válido.');
            }
            // Nombre y Apellido
            if (!formInstructor.firstName.value.trim()) {
                valid = false;
                mensajes.push('El nombre es obligatorio.');
            }
            if (!formInstructor.lastName.value.trim()) {
                valid = false;
                mensajes.push('El apellido es obligatorio.');
            }
            // Contraseña
            if (formInstructor.password.value.length < 5) {
                valid = false;
                mensajes.push('La contraseña debe tener al menos 5 caracteres.');
            }
            // Fecha de nacimiento
            const fecha = formInstructor.fecha_nac.value;
            if (!fecha) {
                valid = false;
                mensajes.push('La fecha de nacimiento es obligatoria.');
            } else {
                const fechaNac = new Date(fecha);
                const hoy = new Date();
                if (fechaNac >= hoy) {
                    valid = false;
                    mensajes.push('La fecha de nacimiento debe ser anterior a hoy.');
                }
            }
            // Celular
            if (!/^\d{10}$/.test(formInstructor.celular.value)) {
                valid = false;
                mensajes.push('El celular debe tener 10 dígitos.');
            }
            // Mostrar errores
            mostrarErrores(formInstructor, mensajes);
            if (!valid) e.preventDefault();
        });
    }

    // Validación para registro de paciente
    const formPaciente = document.querySelector('form[action="/register-patient"]');
    if (formPaciente) {
        formPaciente.addEventListener('submit', function (e) {
            let valid = true;
            let mensajes = [];
            if (!formPaciente.username.value.trim()) {
                valid = false;
                mensajes.push('El nombre de usuario es obligatorio.');
            }
            if (!/^([a-zA-Z0-9_.+-])+@gmail\.com$/.test(formPaciente.email.value.trim())) {
                valid = false;
                mensajes.push('El correo debe ser de Gmail y tener formato válido.');
            }
            if (!formPaciente.firstName.value.trim()) {
                valid = false;
                mensajes.push('El nombre es obligatorio.');
            }
            if (!formPaciente.lastName.value.trim()) {
                valid = false;
                mensajes.push('El apellido es obligatorio.');
            }
            if (formPaciente.password.value.length < 5) {
                valid = false;
                mensajes.push('La contraseña debe tener al menos 5 caracteres.');
            }
            // Validar fecha de nacimiento
            const fecha = formPaciente.fecha_nac.value;
            if (!fecha) {
                valid = false;
                mensajes.push('La fecha de nacimiento es obligatoria.');
            } else {
                const fechaNac = new Date(fecha);
                const hoy = new Date();
                if (fechaNac >= hoy) {
                    valid = false;
                    mensajes.push('La fecha de nacimiento debe ser anterior a hoy.');
                }
            }
            mostrarErrores(formPaciente, mensajes);
            if (!valid) e.preventDefault();
        });
    }

    // Validación para login
    const formLogin = document.querySelector('form[action="/login"]');
    if (formLogin) {
        formLogin.addEventListener('submit', function (e) {
            let valid = true;
            let mensajes = [];
            if (!formLogin.username.value.trim()) {
                valid = false;
                mensajes.push('El usuario es obligatorio.');
            }
            if (formLogin.password.value.length < 5) {
                valid = false;
                mensajes.push('La contraseña debe tener al menos 5 caracteres.');
            }
            mostrarErrores(formLogin, mensajes);
            if (!valid) e.preventDefault();
        });
    }

    // Función para mostrar errores amigables
    function mostrarErrores(form, mensajes) {
        let errorDiv = form.querySelector('.errores-form');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'errores-form';
            errorDiv.style.color = 'red';
            errorDiv.style.margin = '10px 0';
            form.prepend(errorDiv);
        }
        errorDiv.innerHTML = mensajes.length ? mensajes.map(m => `<div>• ${m}</div>`).join('') : '';
    }
});
