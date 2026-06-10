document.addEventListener('DOMContentLoaded', () => {
    // Seleccionar los enlaces y las secciones
    const links = {
        inicio: document.getElementById('enlace-inicio'),
        productos: document.getElementById('enlace-productos'),
        contacto: document.getElementById('enlace-contacto'),
        admin: document.getElementById('enlace-admin')
    };

    const vistas = {
        inicio: document.getElementById('vista-inicio'),
        productos: document.getElementById('vista-productos'),
        admin: document.getElementById('vista-admin')
    };

    // Función para ocultar todo
    function ocultarTodo() {
        Object.values(vistas).forEach(vista => vista.classList.add('oculto'));
    }

    // Eventos para cambiar de vista
    links.inicio.addEventListener('click', () => {
        ocultarTodo();
        vistas.inicio.classList.remove('oculto');
    });

    links.productos.addEventListener('click', () => {
        ocultarTodo();
        vistas.productos.classList.remove('oculto');
    });

    links.admin.addEventListener('click', () => {
        ocultarTodo();
        vistas.admin.classList.remove('oculto');
    });

    links.contacto.addEventListener('click', () => {
        ocultarTodo();
        vistas.inicio.classList.remove('oculto');
        // Desplazamiento suave hacia contacto (asumiendo que tiene un ID en la sección)
        document.getElementById('vista-inicio').scrollIntoView({ behavior: 'smooth' });
    });
});