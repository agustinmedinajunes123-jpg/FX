from flask import Flask, render_template_string, request
from ffrom flask import Flask, request, render_template_string

app = Flask(__name__)

# --- BLOQUE DE DISEÑO HTML CON PANEL ADMINISTRATIVO CENTRADO ---
PAGINA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soporte Técnico y Ciberseguridad</title>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        /* --- CONFIGURACIÓN GENERAL (MODO OSCURO) --- */
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #121212; 
            color: #e0e0e0; 
        }
        header { 
            background-color: #0056b3; 
            color: white; 
            padding: 15px; 
            border-radius: 8px;
        }
        nav ul { list-style: none; padding: 0; margin: 0; }
        nav ul li { display: inline; margin: 0 10px; }
        nav ul li a { color: white; text-decoration: none; font-weight: bold; cursor: pointer; }
        nav ul li a:hover { text-decoration: underline; }
        
        /* --- VISIBILIDAD DE SECCIONES --- */
        .seccion-contenido { display: block; }
        .oculto { display: none !important; }

        /* --- TARJETAS DE SERVICIOS --- */
        .contenedor-tarjetas { display: flex; gap: 20px; margin-top: 20px; }
        .tarjeta { 
            background: #1e1e1e; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            flex: 1; 
        }
        .tarjeta h2 { color: #ffffff; margin-top: 0; font-size: 1.4rem; }
        .tarjeta p { color: #aaaaaa; font-size: 0.95rem; line-height: 1.4; }
        
        /* --- GALERÍA --- */
        .galeria { display: flex; gap: 15px; margin-top: 20px; justify-content: space-between; }
        .galeria img { width: 32%; height: 200px; border-radius: 8px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        
        /* --- CATÁLOGO DE PRODUCTOS --- */
        .titulo-seccion-productos { margin-top: 20px; color: #ffffff; text-align: center; }
        .catalogo-grid { display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap; }
        .producto-card { 
            background: #1e1e1e; 
            padding: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.2); 
            width: calc(33.333% - 14px); 
            box-sizing: border-box; 
            text-align: center; 
            min-width: 250px; 
        }
        .producto-card img { width: 100%; height: 160px; border-radius: 6px; object-fit: contain; background-color: #2d2d2d; }
        .producto-card h3 { font-size: 1.15rem; margin: 12px 0 6px 0; color: #fff; }
        .producto-card p { font-size: 0.9rem; color: #bbb; min-height: 45px; margin-bottom: 10px; }
        .precio { display: block; font-weight: bold; color: #28a745; font-size: 1.2rem; margin-bottom: 15px; }
        .btn-consultar { background-color: #0056b3; color: white; border: none; padding: 8px 15px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 0.9rem; width: 100%; box-sizing: border-box; }
        
        /* --- CONTACTO Y FORMULARIOS --- */
        .contacto-simple { margin-top: 40px; background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }
        .info-contacto { display: flex; gap: 30px; margin-bottom: 20px; font-size: 1.1rem; }
        .info-contacto i { color: #28a745; margin-right: 8px; }
        
        form label { font-weight: bold; display: block; margin-top: 10px; color: #ddd; }
        form input[type="text"], form input[type="password"], form textarea { 
            width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #444; background-color: #2d2d2d; color: #fff; border-radius: 4px; box-sizing: border-box; 
        }
        form input[type="submit"], .btn-crud { background-color: #0056b3; color: white; border: none; padding: 10px; margin-top: 15px; border-radius: 4px; cursor: pointer; font-size: 1rem; width: 100%; }
        form input[type="submit"]:hover, .btn-crud:hover { background-color: #004085; }
        
        /* --- PANEL DE ADMINISTRACIÓN CENTRADO --- */
        .contenedor-admin-centrado {
            display: flex;
            justify-content: center; 
            align-items: center;     
            min-height: 70vh;        
            width: 100%;
        }
        .tarjeta-admin-medio {
            background: #1e1e1e;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); 
            width: 100%;
            max-width: 450px; 
            box-sizing: border-box;
        }
        .tarjeta-admin-medio h2 {
            margin-top: 0; color: #ffffff; text-align: center; font-size: 1.5rem; border-bottom: 2px solid #2d2d2d; padding-bottom: 10px; margin-bottom: 20px;
        }
        
        .btn-contenedor { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; }
        .btn-crud { flex: 1; min-width: 100px; margin-top: 0; }
        .btn-eliminar { background-color: #dc3545; }
        .btn-eliminar:hover { background-color: #bd2130; }
        
        /* --- ALERTAS --- */
        .alerta { background-color: #1e4620; color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; border: 1px solid #28a745; }
        .alerta-error { background-color: #611a1a; color: #f8d7da; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; border: 1px solid #dc3545; }
        footer { text-align: center; color: #666; margin-top: 40px; }
    </style>
</head>
<body>
    <header style="display: flex; justify-content: space-between; align-items: center; background-color: #0056b3; padding: 20px 30px; color: white; border-radius: 8px;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <i class="fa-solid fa-user-shield" style="font-size: 3rem; color: #28a745;"></i>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: bold; letter-spacing: 0.5px; display: flex; align-items: center; gap: 15px;">
                Seguri<span style="color: #28a745;">ty</span>
                <span style="font-size: 1.8rem; font-weight: 400; color: #ffffff; opacity: 0.9; border-left: 2px solid rgba(255, 255, 255, 0.4); padding-left: 15px; margin-left: 5px;">
                    Servicio Técnico
                </span>
            </h1>
        </div>
        <nav>
            <ul>
                <li><a id="enlace-inicio">Inicio / Servicios</a></li>
                <li><a id="enlace-productos">Productos</a></li>
                <li><a id="enlace-contacto">Contacto</a></li>
                <li><a id="enlace-admin" style="background-color: #004085; padding: 8px 12px; border-radius: 4px;">Admin Panel</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <div id="vista-inicio" class="seccion-contenido">
            <section class="contenedor-tarjetas">
                <article class="tarjeta">
                    <h2>Limpieza de Celular</h2>
                    <p>Mantenimiento integral interno y externo para smartphones. Eliminamos residuos de polvo en puertos de carga, altavoces y ranuras.</p>
                </article>
                <article class="tarjeta">
                    <h2>Mantenimiento de PC y Laptops</h2>
                    <p>Limpieza profunda preventiva y correctiva de componentes para equipos de escritorio y portátiles. Incluye remoción de polvo en fuentes, ventiladores, cambio de pasta térmica y limpieza de pantallas.</p>
                </article>
                <article class="tarjeta">
                    <h2>Ciberseguridad y Software</h2>
                    <p>Eliminación de virus, malware y optimización del sistema operativo. Instalación de software esencial y configuración de respaldos de seguridad para proteger tus datos.</p>
                </article>
            </section>
            
            <section class="galeria">
                <img src="https://forjandoelfuturo.com.ar/wp-content/uploads/2021/12/celulares-768x512.jpg" alt="Limpieza de celular">
                <img src="https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=1000" alt="Limpieza de computadoras">
                <img src="https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1000" alt="Ciberseguridad y software">
            </section>
            
            <section id="seccion-contacto" class="contacto-simple">
                <h2>Contáctanos</h2>
                <div class="info-contacto">
                    <div><i class="fa-solid fa-phone"></i> <strong>Teléfono:</strong> +51 987 654 321</div>
                    <div><i class="fa-solid fa-envelope"></i> <strong>Correo:</strong> soporte@misitioweb.com</div>
                    <div><i class="fa-solid fa-location-dot"></i> <strong>Ubicación:</strong> San Juan de Lurigancho</div>
                </div>
                
                <form method="POST">
                    {% if mensaje_confirmacion %}
                        <div class="alerta">{{ mensaje_confirmacion }}</div>
                    {% endif %}
                    <label for="nombre">Nombre:</label>
                    <input type="text" id="nombre" name="nombre" required>
                    <label for="mensaje">Mensaje:</label>
                    <textarea id="mensaje" name="mensaje" rows="3" required></textarea>
                    <input type="submit" name="accion" value="Enviar Mensaje">
                </form>
            </section>
        </div>

        <div id="vista-productos" class="seccion-contenido oculto">
            <h2 class="titulo-seccion-productos">Nuestro Catálogo de Productos</h2>
            <p style="text-align:center; color:#aaa;">Encuentra las mejores herramientas y accesorios para el cuidado y protección de tus equipos.</p>
            
            <section class="catalogo-grid">
                <article class="producto-card">
                    <img src="https://tse2.mm.bing.net/th/id/OIP.HIjpv7qfuNAdy4eQDE-oewHaHa?r=0&cb=thfc1falcon&w=1600&h=1600&rs=1&pid=ImgDetMain&o=7&rm=3">
                    <h3>Kit de Limpieza Antiestático</h3>
                    <p>Líquido limpiador especializado + paño de microfibra premium para pantallas.</p>
                    <span class="precio">S/. 25.00</span>
                    <button type="button" class="btn-consultar">Consultar Stock</button>
                </article>
                
                <article class="producto-card">
                    <img src="https://m.media-amazon.com/images/I/61h4Ql69VlL._AC_SL1500_.jpg">
                    <h3>Aire Comprimido en Aerosol</h3>
                    <p>Remueve con fuerza el polvo acumulado en zonas difíciles como ventiladores.</p>
                    <span class="precio">S/. 30.00</span>
                    <button type="button" class="btn-consultar">Consultar Stock</button>
                </article>
                
                <article class="producto-card">
                    <img src="https://promart.vteximg.com.br/arquivos/ids/6896880-1000-1000/image-9493404ae58d4331a5ad49f49fd95141.jpg?v=638169076099400000">
                    <h3>Base Refrigerante para Laptop</h3>
                    <p>Soporte ergonómico con potentes ventiladores silenciosos.</p>
                    <span class="precio">S/. 65.00</span>
                    <button type="button" class="btn-consultar">Consultar Stock</button>
                </article>

                <article class="producto-card">
                    <img src="https://mmartec.pe/wp-content/uploads/2025/02/D_NQ_NP_756466-MLU75809034186_042024-O-1.webp">
                    <h3>Pasta Térmica de Alta Densidad</h3>
                    <p>Compuesto térmico de alta calidad para procesadores de PC y Laptops.</p>
                    <span class="precio">S/. 35.00</span>
                    <button type="button" class="btn-consultar">Consultar Stock</button>
                </article>

                <article class="producto-card">
                    <img src="https://images-na.ssl-images-amazon.com/images/I/615I4OBtVtL._AC_UL375_SR375,375_.jpg">
                    <h3>Kit de Cubiertas para Webcam (3 un.)</h3>
                    <p>Mini tapas deslizantes ultra delgadas para proteger tu privacidad.</p>
                    <span class="precio">S/. 15.00</span>
                    <button type="button" class="btn-consultar">Consultar Stock</button>
                </article>
            </section>
        </div>

        <div id="vista-admin" class="contenedor-admin-centrado {{ clase_vista_admin }}">
            <div class="tarjeta-admin-medio">
                {% if not autenticado %}
                    <h2>Acceso Interno</h2>
                    {% if mensaje_error %}
                        <div class="alerta-error">{{ mensaje_error }}</div>
                    {% endif %}
                    <form method="POST">
                        <label>Usuario:</label>
                        <input type="text" name="usuario" required>
                        <label>Contraseña:</label>
                        <input type="password" name="clave" required>
                        <input type="submit" name="accion" value="Ingresar">
                    </form>
                {% else %}
                    <h2>Mantenimiento</h2>
                    {% if mensaje_crud %}
                        <div class="alerta">{{ mensaje_crud }}</div>
                    {% endif %}
                    
                    <form method="POST">
                        Código de Producto:<br>
                        <input type="text" name="prod_codigo" value="{{ prod_codigo }}"><br>
                        Nombre del Producto:<br>
                        <input type="text" name="prod_nombre" value="{{ prod_nombre }}"><br>
                        Precio (S/.):<br>
                        <input type="text" name="prod_precio" value="{{ prod_precio }}"><br>

                        <div class="btn-contenedor">
                            <button type="submit" name="accion" value="guardar_prod" class="btn-crud">Guardar</button>
                            <button type="submit" name="accion" value="buscar_prod" class="btn-crud">Buscar</button>
                            <button type="submit" name="accion" value="modificar_prod" class="btn-crud">Modificar</button>
                            <button type="submit" name="accion" value="eliminar_prod" class="btn-crud btn-eliminar">Eliminar</button>
                            <button type="submit" name="accion" value="salir" class="btn-crud" style="background-color:#6c757d;">Salir</button>
                        </div>
                    </form>
                {% endif %}
            </div>
        </div>
    </main>
    
    <footer>
        <p>&copy; 2026 Mi sitio web. Todos los derechos reservados.</p>
    </footer>

    <script>
        const enlaceInicio = document.getElementById('enlace-inicio');
        const enlaceProductos = document.getElementById('enlace-productos');
        const enlaceContacto = document.getElementById('enlace-contacto');
        const enlaceAdmin = document.getElementById('enlace-admin');

        const vistaInicio = document.getElementById('vista-inicio');
        const vistaProductos = document.getElementById('vista-productos');
        const vistaAdmin = document.getElementById('vista-admin');

        function ocultarVistas() {
            vistaInicio.classList.add('oculto');
            vistaProductos.classList.add('oculto');
            vistaAdmin.classList.add('oculto');
            vistaAdmin.style.display = 'none';
        }

        enlaceInicio.addEventListener('click', function() {
            ocultarVistas();
            vistaInicio.classList.remove('oculto');
        });

        enlaceProductos.addEventListener('click', function() {
            ocultarVistas();
            vistaProductos.classList.remove('oculto');
        });

        enlaceContacto.addEventListener('click', function() {
            ocultarVistas();
            vistaInicio.classList.remove('oculto');
            document.getElementById('seccion-contacto').scrollIntoView({ behavior: 'smooth' });
        });

        enlaceAdmin.addEventListener('click', function() {
            ocultarVistas();
            vistaAdmin.classList.remove('oculto');
            vistaAdmin.style.display = 'flex';
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def inicio():
    mensaje_confirmacion = None
    mensaje_error = None
    mensaje_crud = None
    autenticado = False
    clase_vista_admin = "oculto"

    prod_codigo = ""
    prod_nombre = ""
    prod_precio = ""

    if request.method == "POST":
        accion = request.form.get("accion")
        clase_vista_admin = "" 

        if accion == "Enviar Mensaje":
            clase_vista_admin = "oculto"
            nombre_usuario = request.form["nombre"]
            mensaje_confirmacion = f"¡Gracias {nombre_usuario}! Hemos recibido tu mensaje."

        elif accion == "Ingresar":
            usuario = request.form["usuario"]
            clave = request.form["clave"]
            if usuario == "gustabo" and clave == "oño":
                autenticado = True
                mensaje_crud = "Sesión iniciada."
            else:
                autenticado = False
                mensaje_error = "Credenciales incorrectas."

        elif accion in ["guardar_prod", "buscar_prod", "modificar_prod", "eliminar_prod"]:
            autenticado = True
            prod_codigo = request.form["prod_codigo"]
            prod_nombre = request.form["prod_nombre"]
            prod_precio = request.form["prod_precio"]

            if accion == "guardar_prod":
                with open("productos.txt", "a", encoding="utf-8") as archivo:
                    archivo.write(f"{prod_codigo},{prod_nombre},{prod_precio}\n")
                mensaje_crud = "Registro guardado."
                prod_codigo, prod_nombre, prod_precio = "", "", ""

            elif accion == "buscar_prod":
                try:
                    with open("productos.txt", "r", encoding="utf-8") as archivo:
                        for linea in archivo:
                            datos = linea.strip().split(",")
                            if datos[0] == prod_codigo:
                                prod_nombre = datos[1]
                                prod_precio = datos[2]
                                mensaje_crud = "Registro encontrado."
                                break
                        else:
                            mensaje_crud = "Código no encontrado."
                except FileNotFoundError:
                    mensaje_crud = "Archivo no encontrado."

            elif accion == "modificar_prod":
                nuevas_lineas = []
                encontrado = False
                try:
                    with open("productos.txt", "r", encoding="utf-8") as archivo:
                        for linea in archivo:
                            datos = linea.strip().split(",")
                            if datos[0] == prod_codigo:
                                nuevas_lineas.append(f"{prod_codigo},{prod_nombre},{prod_precio}\n")
                                encontrado = True
                            else:
                                nuevas_lineas.append(linea)
                    with open("productos.txt", "w", encoding="utf-8") as archivo:
                        archivo.writelines(nuevas_lineas)
                    mensaje_crud = "Registro modificado." if encontrado else "Código no encontrado."
                except FileNotFoundError:
                    mensaje_crud = "Archivo no encontrado."

            elif accion == "eliminar_prod":
                nuevas_lineas = []
                encontrado = False
                try:
                    with open("productos.txt", "r", encoding="utf-8") as archivo:
                        for linea in archivo:
                            datos = linea.strip().split(",")
                            if datos[0] == prod_codigo:
                                encontrado = True
                            else:
                                nuevas_lineas.append(linea)
                    with open("productos.txt", "w", encoding="utf-8") as archivo:
                        archivo.writelines(nuevas_lineas)
                    mensaje_crud = "Registro eliminado." if encontrado else "Código no encontrado."
                    if encontrado:
                        prod_codigo, prod_nombre, prod_precio = "", "", ""
                except FileNotFoundError:
                    mensaje_crud = "Archivo no encontrado."

        elif accion == "salir":
            autenticado = False
            clase_vista_admin = "oculto"

    return render_template_string(
        PAGINA_HTML,
        mensaje_confirmacion=mensaje_confirmacion,
        mensaje_error=mensaje_error,
        mensaje_crud=mensaje_crud,
        autenticado=autenticado,
        clase_vista_admin=clase_vista_admin,
        prod_codigo=prod_codigo,
        prod_nombre=prod_nombre,
        prod_precio=prod_precio
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)