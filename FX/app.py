import os
import json
import time
import webbrowser
from threading import Timer
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

# --- CONFIGURACIÓN Y PERSISTENCIA DE DATOS DE LA INFRAESTRUCTURA ---
DB_FILE = "config_computo.json"

DATA_POR_DEFECTO = {
    "usuario": {
        "saldo": 150.00
    },
    "caja": {
        "balance_total_recaudado": 0.00,
        "historial_tickets": []
    },
    "cabinas": {
        "promedio": {
            "clave": "promedio",
            "titulo": "Área Básica / Estudio",
            "tarifa": 2.00,
            "desc": "Terminales optimizadas para procesamiento de textos, desarrollo académico y navegación de alta velocidad.",
            "specs": [
                "Procesador: AMD Ryzen 3 3200G (4 núcleos / 4 hilos a 3.6 GHz)",
                "Memoria: 8 GB RAM DDR4 3200MHz de alta estabilidad",
                "Almacenamiento: Disco de Estado Sólido 480GB SSD Kingston",
                "Video: Gráficos Integrados Radeon Vega 8",
                "Pantalla: Monitor LED LG 19.5\" HD Pro Confort Eye"
            ],
            "beneficios": [
                "Entorno libre de ruido externo ideal para estudio",
                "Paquete Office completo instalado (Word, Excel, PowerPoint)",
                "Acceso directo a bibliotecas universitarias digitales",
                "Navegación fluida de alta velocidad vía fibra óptica"
            ]
        },
        "alto": {
            "clave": "alto",
            "titulo": "Área de Alto Rendimiento (Gamer)",
            "tarifa": 3.50,
            "desc": "Estaciones con aceleración gráfica por hardware dedicadas a renderizado, simulación y videojuegos competitivos.",
            "specs": [
                "Procesador: Intel Core i5-11400F (6 núcleos / 12 hilos hasta 4.4 GHz)",
                "Memoria: 16 GB RAM TeamGroup T-Force Vulcan (Dual Channel)",
                "Tarjeta Gráfica: NVIDIA GeForce RTX 3050 8GB GDDR6",
                "Almacenamiento: 1TB NVMe M.2 ultra rápido",
                "Pantalla: Monitor Gamer ASUS TUF 24\" Ultra-Smooth 144Hz IPS"
            ],
            "beneficios": [
                "Tasa de refresco ultra fluida de 144Hz sin retraso visual",
                "Periféricos mecánicos de alta respuesta incorporados",
                "Optimizado para software CAD, Suite Adobe y Gaming competitivo",
                "Aislamiento acústico con auriculares de diadema premium"
            ]
        }
    },
    "servicios": {
        "limpieza": {
            "clave": "limpieza", "tipo_item": "servicio", "titulo": "Limpieza Física Integral", "costo": 35.00,
            "desc": "Remoción total de micropartículas, mantenimiento a ventiladores y optimización del flujo interno del chasis.",
            "detalles": ["Desconexión dieléctrica y desarme completo.", "Soplado con compresor antiestático de alta presión.", "Limpieza estructural con alcohol isopropílico al 99%.", "Reensamblaje estructurado y verificación de temperaturas."],
            "personal": {"nombre": "Ing. Sergio Medina", "cargo": "Especialista en Infraestructura TI / Soporte Hardware"}
        },
        "pasta": {
            "clave": "pasta", "tipo_item": "servicio", "titulo": "Cambio de Pasta Térmica", "costo": 25.00,
            "desc": "Aplicación de compuestos de disipación de alta gama para mitigar degradación térmica en microprocesadores.",
            "detalles": ["Remoción calibrada del bloque disipador de calor.", "Limpieza química de excedentes de compuesto cristalizado.", "Aplicación uniforme de Arctic MX-4 de alta conductividad.", "Monitoreo mediante pruebas de estrés térmico continuo."],
            "personal": {"nombre": "Tec. Carlos Junes", "cargo": "Técnico Especialista en Enfriamiento Avanzado"}
        },
        "mouse": {
            "clave": "mouse", "tipo_item": "producto", "titulo": "Mouse Óptico Gamer", "costo": 65.00,
            "desc": "Periférico de alta precisión con switches ópticos, sensor calibrado de 16,000 DPI e iluminación RGB.",
            "detalles": ["Sensor de alta gama PMW3389.", "Vida útil estimada de 50 millones de clics.", "Cable paracord ultra flexible de baja fricción.", "Software de mapeo de macros dedicado."],
            "personal": {"nombre": "Área de Logística", "cargo": "Control de Inventario y Garantías"}
        },
        "teclado": {
            "clave": "teclado", "tipo_item": "producto", "titulo": "Teclado Mecánico RGB", "costo": 120.00,
            "desc": "Teclado de respuesta inmediata con switches mecánicos Blue de alta resistencia y distribución en español.",
            "detalles": ["Switches mecánicos Outemu Blue táctiles.", "Estructura reforzada de aluminio cepillado.", "Tecnología 100% Anti-Ghosting.", "Efectos de iluminación RGB preconfigurados."],
            "personal": {"nombre": "Área de Logística", "cargo": "Control de Inventario y Suministros"}
        }
    },
    "mapeo_red_pcs": [True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False],
    "estaciones_activas_tiempo": {} # Guarda id_pc -> timestamp_fin
}

def cargar_base_datos():
    if not os.path.exists(DB_FILE):
        guardar_base_datos(DATA_POR_DEFECTO)
        return DATA_POR_DEFECTO
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DATA_POR_DEFECTO

def guardar_base_datos(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- RUTAS DE LA API REST (FLASK) ---

@app.route("/")
def index():
    return render_template_string(HTML_BASE)

@app.route("/api/get_data", methods=["GET"])
def get_data():
    data = cargar_base_datos()
    # Limpiar tiempos expirados antes de enviar la topología
    actual_ts = time.time()
    expirados = []
    for pc_id, ts_fin in data["estaciones_activas_tiempo"].items():
        if actual_ts >= ts_fin:
            expirados.append(pc_id)
            
    if expirados:
        for pc_id in expirados:
            del data["estaciones_activas_tiempo"][pc_id]
        guardar_base_datos(data)
        
    return jsonify(data)

@app.route("/api/recarga_saldo", methods=["POST"])
def recarga_saldo():
    req = request.get_json()
    monto = float(req.get("monto", 0))
    data = cargar_base_datos()
    data["usuario"]["saldo"] += monto
    guardar_base_datos(data)
    return jsonify({"status": "success", "nuevo_saldo": data["usuario"]["saldo"]})

@app.route("/api/actualizar_config", methods=["POST"])
def actualizar_config():
    req = request.get_json()
    data = cargar_base_datos()
    
    data["cabinas"]["promedio"]["titulo"] = req["c1_titulo"]
    data["cabinas"]["promedio"]["tarifa"] = float(req["c1_tarifa"])
    data["cabinas"]["promedio"]["desc"] = req["c1_desc"]
    data["cabinas"]["promedio"]["specs"] = [x.strip() for x in req["c1_specs"].split(",") if x.strip()]
    
    data["cabinas"]["alto"]["titulo"] = req["c2_titulo"]
    data["cabinas"]["alto"]["tarifa"] = float(req["c2_tarifa"])
    data["cabinas"]["alto"]["desc"] = req["c2_desc"]
    data["cabinas"]["alto"]["specs"] = [x.strip() for x in req["c2_specs"].split(",") if x.strip()]
    
    guardar_base_datos(data)
    return jsonify({"status": "success"})

@app.route("/api/toggle_pc", methods=["POST"])
def toggle_pc():
    req = request.get_json()
    pc_idx = int(req.get("pc_index"))
    estado = bool(req.get("estado"))
    data = cargar_base_datos()
    data["mapeo_red_pcs"][pc_idx] = estado
    # Si se apaga, quitar del monitoreo de renta activa
    pc_id_str = str(pc_idx + 1)
    if not estado and pc_id_str in data["estaciones_activas_tiempo"]:
        del data["estaciones_activas_tiempo"][pc_id_str]
    guardar_base_datos(data)
    return jsonify({"status": "success"})

@app.route("/api/procesar_pago", methods=["POST"])
def procesar_pago():
    req = request.get_json()
    items = req.get("items", [])
    total_orden = float(req.get("total", 0))
    
    data = cargar_base_datos()
    
    if data["usuario"]["saldo"] < total_orden:
        return jsonify({"status": "error", "message": "Saldo insuficiente en el monedero."}), 400
        
    # Descontar saldo y sumar a la caja del laboratorio
    data["usuario"]["saldo"] -= total_orden
    data["caja"]["balance_total_recaudado"] += total_orden
    
    ticket_id = int(time.time() * 100) % 1000000
    timestamp_formateado = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # Registrar tickets e inicializar contadores si son cabinas
    for item in items:
        data["caja"]["historial_tickets"].append({
            "ticket_id": f"TEC-{ticket_id}",
            "fecha": timestamp_formateado,
            "descripcion": item["descripcion"],
            "monto": item["monto"],
            "tag": item["tag"]
        })
        
        if item["tag"] == "CABINA":
            pc_id_str = str(item["pc_id"])
            horas = int(item["horas"])
            segundos_adquiridos = horas * 60 # 1 hora simulada equivale a 60 segundos reales para demostración fluida
            data["estaciones_activas_tiempo"][pc_id_str] = time.time() + segundos_adquiridos
            
    guardar_base_datos(data)
    return jsonify({
        "status": "success",
        "ticket_id": f"TEC-{ticket_id}",
        "fecha": timestamp_formateado,
        "nuevo_saldo": data["usuario"]["saldo"]
    })

# --- PLATILLA MAESTRA FRONTEND INTERACTIVO INTEGRAL ---
HTML_BASE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TECNO - Advanced Infrastructure Suite</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;800&family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-principal: #0d0e12;
            --bg-tarjeta: rgba(26, 29, 41, 0.75);
            --border-color: rgba(255, 255, 255, 0.08);
            --color-estudio: #328cc1;
            --color-gamer: #28a745;
            --color-admin: #ee6c4d;
            --color-manto: #ffc107;
            --text-principal: #f3f4f6;
            --text-secundario: #9ca3af;
            --fuente-global: 'Plus Jakarta Sans', sans-serif;
            --fuente-tech: 'Orbitron', sans-serif;
        }

        body {
            font-family: var(--fuente-global);
            margin: 0; padding: 0;
            background: radial-gradient(circle at 50% 0%, #16192b 0%, var(--bg-principal) 70%);
            color: var(--text-principal);
            overflow-x: hidden; min-height: 100vh;
        }

        .encabezado-principal {
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(11, 60, 93, 0.4); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            padding: 15px 40px; border-bottom: 1px solid var(--border-color);
            position: sticky; top: 0; z-index: 1000;
        }

        .marca-empresa { display: flex; align-items: center; gap: 12px; }
        .marca-empresa h1 {
            margin: 0; font-family: var(--fuente-tech); font-size: 1.8rem; font-weight: 800;
            letter-spacing: 2px; background: linear-gradient(90deg, #ffffff, var(--color-estudio));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .marca-empresa i { font-size: 1.6rem; color: var(--color-gamer); filter: drop-shadow(0 0 8px var(--color-gamer)); }

        .panel-navegacion ul { list-style: none; margin: 0; padding: 0; display: flex; align-items: center; gap: 8px; }
        .panel-navegacion ul li a {
            color: var(--text-secundario); text-decoration: none; font-weight: 600; font-size: 0.9rem;
            padding: 10px 18px; border-radius: 8px; transition: all 0.3s;
            display: inline-flex; align-items: center; gap: 10px; cursor: pointer; border: 1px solid transparent;
        }
        .panel-navegacion ul li a:hover { color: #fff; background: rgba(255, 255, 255, 0.05); }
        .panel-navegacion ul li a.activo {
            background: rgba(50, 140, 193, 0.15); color: #fff; border-color: rgba(50, 140, 193, 0.3);
            box-shadow: 0 0 15px rgba(50, 140, 193, 0.1);
        }
        .panel-navegacion ul li a.nav-admin { background: rgba(238, 108, 77, 0.05); color: var(--color-admin); border-color: rgba(238, 108, 77, 0.2); }
        .panel-navegacion ul li a.nav-admin:hover, .panel-navegacion ul li a.nav-admin.activo {
            background: var(--color-admin); color: #fff; border-color: var(--color-admin); box-shadow: 0 0 15px rgba(238, 108, 77, 0.4);
        }

        .widget-usuario-info { display: flex; align-items: center; gap: 15px; margin-left: 20px; border-left: 1px solid var(--border-color); padding-left: 20px; }
        .badge-saldo { background: rgba(40, 167, 69, 0.1); border: 1px solid rgba(40, 167, 69, 0.2); padding: 8px 14px; border-radius: 8px; font-family: var(--fuente-tech); color: #4cd16b; font-size: 0.9rem; }
        
        .btn-carrito-trigger {
            background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); color: #fff;
            padding: 8px 14px; border-radius: 8px; cursor: pointer; position: relative; font-size: 0.9rem; transition: all 0.2s;
        }
        .carrito-counter { position: absolute; top: -6px; right: -6px; background: var(--color-admin); color: #fff; font-size: 0.75rem; font-weight: bold; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; }

        .contenedor-cuerpo { padding: 40px; max-width: 1400px; margin: 0 auto; box-sizing: border-box; }
        .modulo-vista { display: none; animation: vistaFadeIn 0.4s ease forwards; }
        .modulo-vista.activo { display: block; }
        @keyframes vistaFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .hero-computo { text-align: center; padding: 60px 20px; background: radial-gradient(ellipse at center, rgba(11,60,93,0.2) 0%, transparent 70%); border-radius: 20px; }
        .hero-computo i.logo-grande { font-size: 5.5rem; color: var(--color-gamer); filter: drop-shadow(0 0 25px rgba(40, 167, 69, 0.4)); margin-bottom: 20px; }
        .hero-computo h2 { font-family: var(--fuente-tech); font-size: 3.5rem; margin: 0; letter-spacing: 4px; color: #fff; }
        .hero-computo p { max-width: 650px; margin: 20px auto 0 auto; color: var(--text-secundario); font-size: 1.1rem; line-height: 1.6; }

        .titulo-seccion { font-size: 2rem; font-weight: 800; margin: 0 0 8px 0; color: #fff; }
        .subtitulo-seccion { color: var(--text-secundario); margin: 0 0 35px 0; font-size: 1rem; }
        .bloque-subcategoria-titulo { font-size: 1.2rem; font-weight: 700; margin: 40px 0 20px 0; padding-bottom: 10px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; gap: 10px; }

        .grid-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px; }
        .tarjeta-premium { background: var(--bg-tarjeta); border: 1px solid var(--border-color); border-radius: 16px; padding: 30px; display: flex; flex-direction: column; position: relative; overflow: hidden; }
        .tarjeta-premium::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: transparent; }
        .tarjeta-premium.borde-estudio::before { background: var(--color-estudio); }
        .tarjeta-premium.borde-gamer::before { background: var(--color-gamer); }
        .tarjeta-premium.borde-manto::before { background: var(--color-manto); }
        .tarjeta-premium h3 { margin: 15px 0 10px 0; font-size: 1.4rem; color: #fff; }
        .tarjeta-premium p { font-size: 0.95rem; color: var(--text-secundario); line-height: 1.6; margin: 0 0 25px 0; flex-grow: 1; }

        .badge-categoria { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 6px 12px; border-radius: 30px; align-self: flex-start; }
        .badge-estudio { background: rgba(50, 140, 193, 0.12); color: #4fa3d1; border: 1px solid rgba(50, 140, 193, 0.25); }
        .badge-gamer { background: rgba(40, 167, 69, 0.12); color: #4cd16b; border: 1px solid rgba(40, 167, 69, 0.25); }

        .precio-tag { font-size: 1.3rem; font-weight: 800; color: #fff; margin-bottom: 20px; }
        .precio-tag span { font-size: 0.85rem; color: var(--text-secundario); font-weight: 400; }

        .btn-flex-group { display: grid; grid-template-columns: 1fr auto; gap: 10px; }
        .btn-accion-principal { background: #1f2438; color: #fff; border: 1px solid rgba(255,255,255,0.05); padding: 12px 20px; border-radius: 10px; cursor: pointer; font-weight: 600; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 10px; }
        .btn-accion-principal:hover { background: var(--color-estudio); box-shadow: 0 0 15px rgba(50, 140, 193, 0.4); border-color: var(--color-estudio); }
        .btn-gamer-style:hover { background: var(--color-gamer); box-shadow: 0 0 15px rgba(40, 167, 69, 0.4); border-color: var(--color-gamer); }

        .grid-estaciones { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
        .tarjeta-estacion-pc { background: rgba(20, 22, 33, 0.9); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; position: relative; display: flex; flex-direction: column; justify-content: space-between; min-height: 250px; }
        
        .estado-senal-dot { width: 10px; height: 10px; border-radius: 50%; position: absolute; top: 18px; right: 18px; }
        .dot-online { background: var(--color-gamer); box-shadow: 0 0 10px var(--color-gamer); }
        .dot-offline { background: #dc3545; box-shadow: 0 0 10px #dc3545; }
        .dot-rentado { background: #ffc107; box-shadow: 0 0 10px #ffc107; }

        .tarjeta-estacion-pc i.monitor-icon { font-size: 2.4rem; margin-bottom: 12px; }
        .estacion-meta-info { border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px; margin: 12px 0; font-size: 0.8rem; color: var(--text-secundario); line-height: 1.5; flex-grow: 1; }

        .progressbar-container { background: rgba(255,255,255,0.05); border-radius: 4px; height: 6px; width: 100%; margin-top: 8px; overflow: hidden; display: none; }
        .progressbar-fill { background: var(--color-manto); height: 100%; width: 0%; transition: width 1s linear; }

        .btn-rentar-pc { background: rgba(255,255,255,0.04); color: #fff; border: 1px solid rgba(255,255,255,0.08); padding: 10px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; cursor: pointer; width: 100%; display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
        .btn-rentar-pc.style-estudio:hover { background: var(--color-estudio); border-color: var(--color-estudio); }
        .btn-rentar-pc.style-gamer:hover { background: var(--color-gamer); border-color: var(--color-gamer); }
        .btn-rentar-pc:disabled { background: #15161c !important; color: #4b4e5c !important; border: 1px solid #1c1d24 !important; cursor: not-allowed; }

        .sidebar-hardware-panel { position: fixed; top: 0; right: -460px; width: 440px; height: 100vh; background: #11131c; box-shadow: -10px 0 40px rgba(0,0,0,0.7); border-left: 1px solid var(--border-color); transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1); z-index: 5000; padding: 35px; box-sizing: border-box; overflow-y: auto; }
        .sidebar-hardware-panel.abierto { right: 0; }
        .cerrar-sidebar-btn { position: absolute; top: 25px; right: 25px; font-size: 1.4rem; color: var(--text-secundario); cursor: pointer; }
        
        .precio-contenedor-sidebar { background: rgba(255,255,255,0.02); border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 18px; text-align: center; margin: 25px 0; }
        .componentes-lista-ul { list-style: none; padding: 0; margin: 15px 0 25px 0; }
        .componentes-lista-ul li { margin-bottom: 14px; display: flex; gap: 14px; font-size: 0.9rem; align-items: flex-start; }

        .overlay-modal-global { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(5, 6, 10, 0.8); backdrop-filter: blur(6px); z-index: 3000; display: none; align-items: center; justify-content: center; }
        .modal-contenedor-interno { background: #141622; border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; width: 480px; padding: 35px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); position: relative; max-height: 90vh; overflow-y: auto; }

        .selector-horas-digital { display: flex; align-items: center; justify-content: center; gap: 20px; margin: 25px 0; }
        .btn-circulo-control { width: 42px; height: 42px; border-radius: 50%; background: #1f2336; border: none; color: #fff; font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .display-tiempo { font-family: var(--fuente-tech); font-size: 2rem; font-weight: 800; min-width: 80px; text-align: center; }

        .resumen-recibo-box { background: rgba(0,0,0,0.25); border-radius: 10px; padding: 20px; border-left: 4px solid var(--color-gamer); margin-bottom: 25px; }
        .recibo-fila { display: flex; justify-content: space-between; font-size: 0.9rem; color: var(--text-secundario); margin-bottom: 10px; }
        .recibo-total { display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px; font-size: 1.25rem; font-weight: bold; color: #fff; }

        .lista-items-carrito { max-height: 240px; overflow-y: auto; margin: 15px 0; }
        .item-carrito-fila { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }

        .layout-panel-admin { display: grid; grid-template-columns: 1fr; gap: 30px; }
        .seccion-admin-card { background: rgba(18, 20, 31, 0.8); border: 1px solid var(--border-color); border-radius: 14px; padding: 30px; }
        .seccion-admin-card h3 { margin-top: 0; margin-bottom: 25px; font-family: var(--fuente-tech); color: var(--color-admin); font-size: 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 12px; display: flex; align-items: center; gap: 12px; }
        
        .inputs-columnas-flex { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .admin-campo { display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; }
        .admin-campo label { font-size: 0.8rem; font-weight: 700; color: var(--text-secundario); text-transform: uppercase; }
        .admin-campo input, .admin-campo textarea { background: #0b0c10; border: 1px solid rgba(255,255,255,0.1); padding: 12px; color: #fff; border-radius: 8px; font-family: var(--fuente-global); }

        .contenedor-switches-red { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; }
        .item-switch-estacion { display: flex; align-items: center; justify-content: space-between; background: #0b0c10; padding: 12px 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.04); }
        
        .switch-toggle-base { position: relative; display: inline-block; width: 48px; height: 24px; }
        .switch-toggle-base input { opacity: 0; width: 0; height: 0; }
        .switch-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #dc3545; transition: .3s; border-radius: 24px; }
        .switch-slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }
        input:checked + .switch-slider { background-color: var(--color-gamer); }
        input:checked + .switch-slider:before { transform: translateX(24px); }

        /* Estilos Tabla de Auditoría */
        .tabla-auditoria-box { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.85rem; }
        .tabla-auditoria-box th { background: #141724; color: #fff; text-align: left; padding: 12px; border-bottom: 2px solid var(--border-color); }
        .tabla-auditoria-box td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); color: var(--text-secundario); }
        .badge-ticket-tag { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
        .b-tag-cabina { background: rgba(50,140,193,0.15); color: #328cc1; }
        .b-tag-servicio { background: rgba(255,193,7,0.15); color: #ffc107; }
        .b-tag-producto { background: rgba(238,108,77,0.15); color: #ee6c4d; }
    </style>
</head>
<body>

    <header class="encabezado-principal">
        <div class="marca-empresa">
            <i class="fa-solid fa-microchip"></i>
            <h1>TECNO</h1>
        </div>
        <nav class="panel-navegacion">
            <ul>
                <li><a id="nav-inicio" class="activo" onclick="navegarAModulo('inicio')"><i class="fa-solid fa-house"></i> Inicio</a></li>
                <li><a id="nav-cabinas" onclick="navegarAModulo('cabinas')"><i class="fa-solid fa-gamepad"></i> Cabinas</a></li>
                <li><a id="nav-servicios" onclick="navegarAModulo('servicios')"><i class="fa-solid fa-box-open"></i> Servicios & Suministros</a></li>
                <li><a id="nav-monitoreo" onclick="navegarAModulo('monitoreo')"><i class="fa-solid fa-network-wired"></i> Monitoreo de Red</a></li>
                <li><a id="nav-administracion" class="nav-admin" onclick="navegarAModulo('administracion')"><i class="fa-solid fa-user-shield"></i> Panel Admin</a></li>
            </ul>
        </nav>
        <div class="widget-usuario-info">
            <div id="display-monedero-saldo" class="badge-saldo">Crédito: S/. 0.00</div>
            <button class="btn-carrito-trigger" onclick="desplegarModalCarrito()">
                <i class="fa-solid fa-basket-shopping"></i> Carrito
                <div id="carrito-badge-count" class="carrito-counter">0</div>
            </button>
        </div>
    </header>

    <div id="sidebar-hardware-id" class="sidebar-hardware-panel">
        <span class="cerrar-sidebar-btn" onclick="ocultarSidebar()"><i class="fa-solid fa-xmark"></i></span>
        <h3 id="sidebar-titulo-cabina" style="font-family:var(--fuente-tech); color:#fff; margin-top:20px;">Especificaciones</h3>
        <div class="precio-contenedor-sidebar">
            <span style="font-size: 0.8rem; text-transform: uppercase; color: var(--text-secundario);">Costo del Servicio</span>
            <div id="sidebar-monto-tarifa" style="font-size: 1.8rem; font-weight: 800; color: var(--color-estudio); margin-top: 5px;">S/. 0.00</div>
        </div>
        <h4 style="color: #fff; font-size: 0.95rem; margin-bottom: 10px; text-transform: uppercase;"><i class="fa-solid fa-gears" style="color:var(--color-estudio);"></i> Arquitectura Interna:</h4>
        <ul id="sidebar-lista-specs" class="componentes-lista-ul"></ul>
        <h4 style="color: #fff; font-size: 0.95rem; margin-bottom: 10px; text-transform: uppercase;"><i class="fa-solid fa-wand-magic-sparkles" style="color:var(--color-manto);"></i> Beneficios Incluidos:</h4>
        <ul id="sidebar-lista-beneficios" class="componentes-lista-ul"></ul>
        <button class="btn-accion-principal btn-gamer-style" style="width: 100%; margin-top: 15px;" onclick="redirigirAMonitoreo()">
            <i class="fa-solid fa-network-wired"></i> Consultar Terminales Disponibles
        </button>
    </div>

    <div id="modal-alquiler-id" class="overlay-modal-global">
        <div class="modal-contenedor-interno">
            <span class="cerrar-sidebar-btn" onclick="cerrarModalAlquiler()"><i class="fa-solid fa-xmark"></i></span>
            <div style="text-align: center; margin-bottom: 20px;">
                <i class="fa-solid fa-desktop" style="font-size: 2.2rem; color: var(--color-estudio);"></i>
                <h3 id="modal-estacion-nombre" style="margin:5px 0 0 0; font-family:var(--fuente-tech); color:#fff;">Estación XX</h3>
            </div>
            <div class="selector-horas-digital">
                <button class="btn-circulo-control" onclick="cambiarContadorHoras(-1)">-</button>
                <div id="modal-horas-contador" class="display-tiempo">1h</div>
                <button class="btn-circulo-control" onclick="cambiarContadorHoras(1)">+</button>
            </div>
            <div class="resumen-recibo-box">
                <div class="recibo-fila"><span>Tipo de Cabina:</span><span id="modal-estacion-tipo" style="color:#fff; font-weight:600;">-</span></div>
                <div class="recibo-fila"><span>Tarifa por Hora:</span><span id="modal-estacion-tarifa">S/. 0.00</span></div>
                <div class="recibo-total"><span>Total Estimado:</span><span id="modal-estacion-total">S/. 0.00</span></div>
            </div>
            <button class="btn-accion-principal btn-gamer-style" style="width: 100%; background: var(--color-estudio);" onclick="agregarCabinaAlCarrito()">
                <i class="fa-solid fa-cart-plus"></i> Añadir Renta al Carrito
            </button>
        </div>
    </div>

    <div id="modal-servicio-id" class="overlay-modal-global">
        <div class="modal-contenedor-interno" style="width: 520px;">
            <span class="cerrar-sidebar-btn" onclick="cerrarModalServicio()"><i class="fa-solid fa-xmark"></i></span>
            <div style="display: flex; align-items: center; gap: 15px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 15px; margin-bottom: 20px;">
                <i id="m-serv-icono" class="fa-solid fa-screwdriver-wrench" style="font-size: 1.8rem; color: var(--color-gamer);"></i>
                <h3 id="m-serv-titulo" style="margin:0; color:#fff;">Detalles del Ítem</h3>
            </div>
            <div style="font-size:0.8rem; font-weight:700; color:var(--color-estudio); text-transform:uppercase; margin-bottom:5px;">Descripción</div>
            <p id="m-serv-desc" style="font-size:0.9rem; color:var(--text-secundario); margin:0 0 20px 0; line-height:1.5;"></p>
            <div style="font-size:0.8rem; font-weight:700; color:var(--color-estudio); text-transform:uppercase; margin-bottom:8px;">Atributos / Suministro</div>
            <ul id="m-serv-detalles-lista" style="padding-left:20px; margin:0 0 25px 0; font-size:0.9rem; color:var(--text-secundario); line-height:1.5;"></ul>
            <div class="resumen-recibo-box" style="margin-bottom:20px;">
                <div class="recibo-total"><span>Precio Unitario:</span><span id="m-serv-precio" style="color:var(--color-gamer);">S/. 0.00</span></div>
            </div>
            <button id="btn-add-servicio-carrito" class="btn-accion-principal btn-gamer-style" style="width:100%;">
                <i class="fa-solid fa-cart-plus"></i> Añadir al Carrito de Compras
            </button>
        </div>
    </div>

    <div id="modal-carrito-id" class="overlay-modal-global">
        <div class="modal-contenedor-interno" style="width: 500px;">
            <span class="cerrar-sidebar-btn" onclick="cerrarModalCarrito()"><i class="fa-solid fa-xmark"></i></span>
            <div style="display: flex; align-items: center; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 15px; margin-bottom: 15px;">
                <i class="fa-solid fa-basket-shopping" style="color: var(--color-estudio); font-size: 1.6rem;"></i>
                <h3 style="margin:0; color:#fff; font-family: var(--fuente-tech);">Módulo de Facturación</h3>
            </div>
            <div id="carrito-vacio-mensaje" style="text-align:center; padding: 30px 0; color: var(--text-secundario);">
                <i class="fa-solid fa-folder-open" style="font-size:2.5rem; margin-bottom:10px; display:block; opacity:0.5;"></i> El carrito está vacío.
            </div>
            <div id="carrito-lista-contenedor" class="lista-items-carrito"></div>
            <div class="resumen-recibo-box" style="margin-top:15px; margin-bottom:20px;">
                <div class="recibo-fila"><span>Subtotal Base (Excl. IGV):</span><span id="cart-subtotal">S/. 0.00</span></div>
                <div class="recibo-fila"><span>IGV de Ley (18%):</span><span id="cart-igv">S/. 0.00</span></div>
                <div class="recibo-total"><span>Total a Liquidar:</span><span id="cart-total">S/. 0.00</span></div>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
                <button class="btn-accion-principal" style="background: rgba(220,53,69,0.1); border-color: rgba(220,53,69,0.2); color:#ff5c6c;" onclick="vaciarTodoElCarrito()">
                    <i class="fa-solid fa-trash-can"></i> Vaciar
                </button>
                <button id="btn-ejecutar-pago-final" class="btn-accion-principal btn-gamer-style" style="background: var(--color-gamer); border-color: var(--color-gamer);" onclick="procesarPagoOrdenServicio()">
                    <i class="fa-solid fa-receipt"></i> Liquidar y Pagar
                </button>
            </div>
        </div>
    </div>

    <main class="contenedor-cuerpo">
        
        <div id="vista-inicio" class="modulo-vista activo">
            <div class="hero-computo">
                <i class="fa-solid fa-terminal logo-grande"></i>
                <h2>TECNO OPERATIVE SUITE</h2>
                <p>Plataforma inteligente para el control de infraestructura de red, auditoría remota de terminales y gestión comercial de portafolio tecnológico.</p>
            </div>
        </div>

        <div id="vista-cabinas" class="modulo-vista">
            <h2 class="titulo-seccion">Módulos de Conectividad</h2>
            <p class="subtitulo-seccion">Seleccione la categoría de hardware requerida para el despliegue del entorno operativo.</p>
            <div class="grid-layout">
                <div class="tarjeta-premium borde-estudio">
                    <span class="badge-categoria badge-estudio">Productividad</span>
                    <h3 id="txt-cab-estudio-titulo">-</h3>
                    <p id="txt-cab-estudio-desc">-</p>
                    <div class="precio-tag" id="txt-cab-estudio-precio">-</div>
                    <div class="btn-flex-group">
                        <button class="btn-accion-principal" style="background-color: #328cc1;" onclick="desplegarDetallesHardware('promedio')">Specs Técnicas</button>
                        <button class="btn-accion-principal btn-gamer-style" style="background:var(--color-estudio);" onclick="redirigirAMonitoreo()"><i class="fa-solid fa-desktop"></i> Rentar en Red</button>
                    </div>
                </div>
                <div class="tarjeta-premium borde-gamer">
                    <span class="badge-categoria badge-gamer">High Performance</span>
                    <h3 id="txt-cab-gamer-titulo">-</h3>
                    <p id="txt-cab-gamer-desc">-</p>
                    <div class="precio-tag" id="txt-cab-gamer-precio">-</div>
                    <div class="btn-flex-group">
                        <button class="btn-accion-principal" style="background-color: #28a745;" onclick="desplegarDetallesHardware('alto')">Specs Técnicas</button>
                        <button class="btn-accion-principal btn-gamer-style" style="background:var(--color-gamer); border-color:var(--color-gamer);" onclick="redirigirAMonitoreo()"><i class="fa-solid fa-bolt"></i> Rentar en Red</button>
                    </div>
                </div>
            </div>
        </div>

        <div id="vista-servicios" class="modulo-vista">
            <h2 class="titulo-seccion">Servicios Especializados e Inventario</h2>
            <p class="subtitulo-seccion">Portafolio técnico de mantenimiento preventivo y suministros de hardware.</p>
            <div class="bloque-subcategoria-titulo" style="color:var(--color-gamer);"><i class="fa-solid fa-screwdriver-wrench"></i> Soporte Técnico</div>
            <div class="grid-layout">
                <div class="tarjeta-premium borde-manto">
                    <i class="fa-solid fa-wind" style="font-size:2rem; color:var(--color-estudio); margin-bottom:12px;"></i>
                    <h3 id="txt-s1-titulo">-</h3>
                    <p id="txt-s1-desc">-</p>
                    <button class="btn-accion-principal" onclick="desplegarModalServicio('limpieza')">Auditar Soporte</button>
                </div>
                <div class="tarjeta-premium borde-manto">
                    <i class="fa-solid fa-temperature-arrow-down" style="font-size:2rem; color:var(--color-estudio); margin-bottom:12px;"></i>
                    <h3 id="txt-s2-titulo">-</h3>
                    <p id="txt-s2-desc">-</p>
                    <button class="btn-accion-principal" onclick="desplegarModalServicio('pasta')">Auditar Soporte</button>
                </div>
            </div>
            <div class="bloque-subcategoria-titulo" style="color:var(--color-estudio);"><i class="fa-solid fa-shop"></i> Stock de Componentes</div>
            <div class="grid-layout">
                <div class="tarjeta-premium">
                    <i class="fa-solid fa-computer-mouse" style="font-size:2rem; color:var(--color-admin); margin-bottom:12px;"></i>
                    <h3 id="txt-p1-titulo">-</h3>
                    <p id="txt-p1-desc">-</p>
                    <button class="btn-accion-principal" onclick="desplegarModalServicio('mouse')">Ver Características</button>
                </div>
                <div class="tarjeta-premium">
                    <i class="fa-solid fa-keyboard" style="font-size:2rem; color:var(--color-admin); margin-bottom:12px;"></i>
                    <h3 id="txt-p2-titulo">-</h3>
                    <p id="txt-p2-desc">-</p>
                    <button class="btn-accion-principal" onclick="desplegarModalServicio('teclado')">Ver Características</button>
                </div>
            </div>
        </div>

        <div id="vista-monitoreo" class="modulo-vista">
            <h2 class="titulo-seccion">Topología de Red e Infraestructura</h2>
            <p class="subtitulo-seccion">Estado lógico e indicadores de tiempo de renta activa de las terminales del laboratorio.</p>
            <div class="bloque-subcategoria-titulo" style="color: var(--color-estudio);"><i class="fa-solid fa-graduation-cap"></i> SECCIÓN A: Terminales de Estudio (PCs 01 - 07)</div>
            <div class="grid-estaciones" id="grid-render-estudio" style="margin-bottom: 40px;"></div>
            <div class="bloque-subcategoria-titulo" style="color: var(--color-gamer);"><i class="fa-solid fa-headset"></i> SECCIÓN B: Terminales Gamer (PCs 08 - 14)</div>
            <div class="grid-estaciones" id="grid-render-gamer" style="margin-bottom: 40px;"></div>
            <div class="bloque-subcategoria-titulo" style="color: var(--color-manto);"><i class="fa-solid fa-network-wired"></i> SECCIÓN C: Terminales Asignadas a Mantenimiento (PCs 15 - 20)</div>
            <div class="grid-estaciones" id="grid-render-mantenimiento"></div>
        </div>

        <div id="vista-administracion" class="modulo-vista">
            <h2 class="titulo-seccion" style="color: var(--color-admin);"><i class="fa-solid fa-unlock-keyhole"></i> Consola Central de Administración</h2>
            <p class="subtitulo-seccion">Panel maestro del negocio, control de red y arqueo de caja con desglose de impuestos.</p>
            <div class="layout-panel-admin">
                
                <div class="seccion-admin-card">
                    <h3 style="color: var(--color-gamer);"><i class="fa-solid fa-wallet"></i> Pasarela de Fondos en Caja</h3>
                    <div style="display: flex; gap: 15px; align-items: flex-end;">
                        <div class="admin-campo" style="margin: 0; flex-grow: 1;">
                            <label>Monto a Inyectar al Monedero (S/.)</label>
                            <input type="number" id="form-admin-recarga-monto" value="50.00" min="1">
                        </div>
                        <button class="btn-accion-principal btn-gamer-style" style="background: var(--color-gamer); border-color: var(--color-gamer); height: 45px;" onclick="ejecutarRecargaSaldoAdmin()">
                            <i class="fa-solid fa-plus"></i> Cargar Saldo
                        </button>
                    </div>
                </div>

                <div class="seccion-admin-card">
                    <h3><i class="fa-solid fa-power-off"></i> Control de Flujo de Red (Switches de Habilitación Estructural)</h3>
                    <div class="contenedor-switches-red" id="admin-render-switches"></div>
                </div>

                <div class="seccion-admin-card">
                    <h3><i class="fa-solid fa-sliders"></i> Configuración Global de Tarifas</h3>
                    <div class="inputs-columnas-flex">
                        <div class="admin-campo"><label>Título Área Estudio</label><input type="text" id="form-c1-titulo"></div>
                        <div class="admin-campo"><label>Tarifa Estudio (S/.)</label><input type="number" step="0.5" id="form-c1-precio"></div>
                    </div>
                    <div class="admin-campo"><label>Descripción Área Estudio</label><textarea id="form-c1-desc" rows="2"></textarea></div>
                    <div class="admin-campo"><label>Componentes (Separados por comas)</label><input type="text" id="form-c1-specs"></div>

                    <div class="inputs-columnas-flex" style="margin-top: 25px;">
                        <div class="admin-campo"><label>Título Área Gamer</label><input type="text" id="form-c2-titulo"></div>
                        <div class="admin-campo"><label>Tarifa Gamer (S/.)</label><input type="number" step="0.5" id="form-c2-precio"></div>
                    </div>
                    <div class="admin-campo"><label>Descripción Área Gamer</label><textarea id="form-c2-desc" rows="2"></textarea></div>
                    <div class="admin-campo"><label>Componentes (Separados por comas)</label><input type="text" id="form-c2-specs"></div>
                    
                    <button class="btn-accion-principal" style="background: var(--color-admin); width: 100%; border-color: var(--color-admin); margin-top: 15px;" onclick="guardarConfiguracionGlobalAdmin()">
                        <i class="fa-solid fa-floppy-disk"></i> Guardar Cambios Estructura
                    </button>
                </div>

                <div class="seccion-admin-card">
                    <h3 style="color: #fff;"><i class="fa-solid fa-receipt"></i> Auditoría e Historial de Caja (Recaudación Real)</h3>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #fff; margin-bottom: 20px; font-family: var(--fuente-tech);">
                        Total en Caja Bruto: <span style="color: var(--color-gamer);" id="admin-caja-total">S/. 0.00</span>
                    </div>
                    <div style="overflow-x: auto;">
                        <table class="tabla-auditoria-box">
                            <thead>
                                <tr>
                                    <th>Operación</th>
                                    <th>Fecha / Hora</th>
                                    <th>Concepto Adquirido</th>
                                    <th>Tipo</th>
                                    <th>Monto</th>
                                </tr>
                            </thead>
                            <tbody id="admin-tabla-tickets-body"></tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>

    </main>

    <script>
        let BACKEND_DATA = {};
        let CARRITO_LOCAL = [];
        let temporal_horas = 1;
        let temporal_pc_id = 1;
        let temporal_categoria = 'promedio';

        // Sincronizar bucle de renderizado cada segundo para simular cronómetros perfectos
        window.onload = function() {
            sincronizarConServidorBackend(true);
            setInterval(sincronizarConServidorBackend, 1000);
        };

        function id(el) { return document.getElementById(el); }

        function navegarAModulo(modulo) {
            document.querySelectorAll('.modulo-vista').forEach(vista => vista.classList.remove('activo'));
            document.querySelectorAll('.panel-navegacion ul li a').forEach(link => link.classList.remove('activo'));
            id('vista-' + modulo).classList.add('activo');
            id('nav-' + modulo).classList.add('activo');
        }

        function sincronizarConServidorBackend(primeraVez = false) {
            fetch('/api/get_data')
                .then(res => res.json())
                .then(data => {
                    BACKEND_DATA = data;
                    renderizarComponentesDinamicos(primeraVez);
                });
        }

        function renderizarComponentesDinamicos(cargarInputsAdmin) {
            // Saldo y Contador Carrito
            id('display-monedero-saldo').innerText = "Crédito: S/. " + BACKEND_DATA.usuario.saldo.toFixed(2);
            id('carrito-badge-count').innerText = CARRITO_LOCAL.length;

            // Datos de las cabinas
            id('txt-cab-estudio-titulo').innerText = BACKEND_DATA.cabinas.promedio.titulo;
            id('txt-cab-estudio-desc').innerText = BACKEND_DATA.cabinas.promedio.desc;
            id('txt-cab-estudio-precio').innerHTML = "S/. " + BACKEND_DATA.cabinas.promedio.tarifa.toFixed(2) + " <span>/ hora</span>";

            id('txt-cab-gamer-titulo').innerText = BACKEND_DATA.cabinas.alto.titulo;
            id('txt-cab-gamer-desc').innerText = BACKEND_DATA.cabinas.alto.desc;
            id('txt-cab-gamer-precio').innerHTML = "S/. " + BACKEND_DATA.cabinas.alto.tarifa.toFixed(2) + " <span>/ hora</span>";

            // Datos de Servicios en Fichas
            id('txt-s1-titulo').innerText = BACKEND_DATA.servicios.limpieza.titulo;
            id('txt-s1-desc').innerText = BACKEND_DATA.servicios.limpieza.desc;
            id('txt-s2-titulo').innerText = BACKEND_DATA.servicios.pasta.titulo;
            id('txt-s2-desc').innerText = BACKEND_DATA.servicios.pasta.desc;
            id('txt-p1-titulo').innerText = BACKEND_DATA.servicios.mouse.titulo;
            id('txt-p1-desc').innerText = BACKEND_DATA.servicios.mouse.desc;
            id('txt-p2-titulo').innerText = BACKEND_DATA.servicios.teclado.titulo;
            id('txt-p2-desc').innerText = BACKEND_DATA.servicios.teclado.desc;

            // Inyectar datos en inputs de administración una sola vez
            if (cargarInputsAdmin) {
                id('form-c1-titulo').value = BACKEND_DATA.cabinas.promedio.titulo;
                id('form-c1-precio').value = BACKEND_DATA.cabinas.promedio.tarifa;
                id('form-c1-desc').value = BACKEND_DATA.cabinas.promedio.desc;
                id('form-c1-specs').value = BACKEND_DATA.cabinas.promedio.specs.join(', ');

                id('form-c2-titulo').value = BACKEND_DATA.cabinas.alto.titulo;
                id('form-c2-precio').value = BACKEND_DATA.cabinas.alto.tarifa;
                id('form-c2-desc').value = BACKEND_DATA.cabinas.alto.desc;
                id('form-c2-specs').value = BACKEND_DATA.cabinas.alto.specs.join(', ');
                
                // Cargar switches de red
                const switchesBox = id('admin-render-switches');
                switchesBox.innerHTML = "";
                BACKEND_DATA.mapeo_red_pcs.forEach((estado, idx) => {
                    switchesBox.innerHTML += `
                        <div class="item-switch-estacion">
                            <span>PC ${String(idx + 1).padStart(2, '0')}</span>
                            <label class="switch-toggle-base">
                                <input type="checkbox" ${estado ? 'checked' : ''} onchange="cambiarEstadoRedTerminal(${idx}, this.checked)">
                                <span class="switch-slider"></span>
                            </label>
                        </div>
                    `;
                });
            }

            // Actualizar pestaña de arqueo de caja e historial
            id('admin-caja-total').innerText = "S/. " + BACKEND_DATA.caja.balance_total_recaudado.toFixed(2);
            const tbody = id('admin-tabla-tickets-body');
            tbody.innerHTML = "";
            BACKEND_DATA.caja.historial_tickets.forEach(tk => {
                tbody.innerHTML += `
                    <tr>
                        <td style="font-weight:700; color:#fff;">${tk.ticket_id}</td>
                        <td>${tk.fecha}</td>
                        <td>${tk.descripcion}</td>
                        <td><span class="badge-ticket-tag b-tag-${tk.tag.toLowerCase()}">${tk.tag}</span></td>
                        <td style="font-weight:700; color:#fff;">S/. ${tk.monto.toFixed(2)}</td>
                    </tr>
                `;
            });

            // RENDER DE TOPOLOGÍA DE RED CON CRONÓMETROS ACTIVOS
            const areaEstudio = id('grid-render-estudio');
            const areaGamer = id('grid-render-gamer');
            const areaManto = id('grid-render-mantenimiento');
            
            areaEstudio.innerHTML = ""; areaGamer.innerHTML = ""; areaManto.innerHTML = "";

            const actualTS = Date.now() / 1000;

-.--------------for (let i = 1; i <= 20; i++) {
                let redHabilitada = BACKEND_DATA.mapeo_red_pcs[i - 1];
                let pcIdStr = String(i);
                let estaRentada = pcIdStr in BACKEND_DATA.estaciones_activas_tiempo;
                
                if (!redHabilitada) {
                    // PC Deshabilitada
                    let html = `
                        <div class="tarjeta-estacion-pc" style="border-color: rgba(220,53,69,0.3); background: rgba(20,12,14,0.95);">
                            <div>
                                <div class="estado-senal-dot dot-offline"></div>
                                <i class="fa-solid fa-triangle-exclamation monitor-icon" style="color: #dc3545;"></i>
                                <h4 style="margin:0; font-family:var(--fuente-tech); color:#fff;">Terminal ${String(i).padStart(2, '0')}</h4>
                                <div class="estacion-meta-info">
                                    <strong>Modo lógico:</strong> Desconectado<br>
                                    <strong>Tráfico IP:</strong> Bloqueado por Red
                                </div>
                            </div>
                            <button class="btn-rentar-pc" disabled><i class="fa-solid fa-ban"></i> Bloqueado</button>
                        </div>
                    `;
                    areaManto.innerHTML += html;
                } else if (estaRentada) {
                    // PC Activa / Ocupada con contador de tiempo real
                    let tsFin = BACKEND_DATA.estaciones_activas_tiempo[pcIdStr];
                    let tiempoRestante = Math.max(0, Math.round(tsFin - actualTS));
                    
                    let minutos = Math.floor(tiempoRestante / 60);
                    let segundos = tiempoRestante % 60;
                    let displayTiempo = `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
                    
                    // Cálculo de porcentaje para la barra de progreso
                    let totalSimulado = 60; // Ajustado a nuestra simulación de minutos
                    let pct = Math.min(100, (tiempoRestante / totalSimulado) * 100);

                    let html = `
                        <div class="tarjeta-estacion-pc" style="border-color: var(--color-manto);">
                            <div>
                                <div class="estado-senal-dot dot-rentado"></div>
                                <i class="fa-solid fa-hourglass-half monitor-icon" style="color: var(--color-manto); animation: fa-spin 10s linear infinite;"></i>
                                <h4 style="margin:0; font-family:var(--fuente-tech); color:#fff;">Terminal ${String(i).padStart(2, '0')}</h4>
                                <div class="estacion-meta-info">
                                    <strong>Estado:</strong> Sesión en Uso<br>
                                    <strong>Restan:</strong> <span style="color:#fff; font-family:var(--fuente-tech); font-weight:800;">${displayTiempo}</span>
                                    <div class="progressbar-container" style="display:block;"><div class="progressbar-fill" style="width:${pct}%;"></div></div>
                                </div>
                            </div>
                            <button class="btn-rentar-pc" disabled style="background:rgba(255,193,7,0.1); color:var(--color-manto); border-color:rgba(255,193,7,0.2);">
                                <i class="fa-solid fa-lock"></i> Terminal Ocupada
                            </button>
                        </div>
                    `;
                    if (i <= 7) areaEstudio.innerHTML += html;
                    else if (i <= 14) areaGamer.innerHTML += html;
                    else areaManto.innerHTML += html;
                } else {
                    // PC Disponible
                    let esGamer = i > 7 && i <= 14;
                    let catClave = esGamer ? 'alto' : 'promedio';
                    let estiloBoton = esGamer ? 'style-gamer' : 'style-estudio';
                    let icon = esGamer ? 'fa-gamepad' : 'fa-desktop';
                    let colorIcon = esGamer ? 'var(--color-gamer)' : 'var(--color-estudio)';

                    let html = `
                        <div class="tarjeta-estacion-pc">
                            <div>
                                <div class="estado-senal-dot dot-online"></div>
                                <i class="fa-solid ${icon} monitor-icon" style="color: ${colorIcon};"></i>
                                <h4 style="margin:0; font-family:var(--fuente-tech); color:#fff;">Terminal ${String(i).padStart(2, '0')}</h4>
                                <div class="estacion-meta-info">
                                    <strong>Módulo:</strong> ${BACKEND_DATA.cabinas[catClave].titulo}<br>
                                    <strong>Estado:</strong> Libre / Disponible
                                </div>
                            </div>
                            <button class="btn-rentar-pc ${estiloBoton}" onclick="abrirModalAsignacionHoras(${i}, '${catClave}')">
                                <i class="fa-solid fa-clock"></i> Asignar Renta
                            </button>
                        </div>
                    `;
                    if (i <= 7) areaEstudio.innerHTML += html;
                    else if (i <= 14) areaGamer.innerHTML += html;
                    else areaManto.innerHTML += html;
                }
            }
        }

        // --- MANEJO SIDEBAR DETALLES ---
        function desplegarDetallesHardware(categoria) {
            const cabina = BACKEND_DATA.cabinas[categoria];
            id('sidebar-titulo-cabina').innerText = cabina.titulo;
            id('sidebar-monto-tarifa').innerText = "S/. " + cabina.tarifa.toFixed(2) + " / h";
            
            id('sidebar-lista-specs').innerHTML = cabina.specs.map(s => `<li><i class="fa-solid fa-microchip" style="color:var(--color-estudio); margin-top:3px;"></i><div>${s}</div></li>`).join('');
            id('sidebar-lista-beneficios').innerHTML = cabina.beneficios.map(b => `<li><i class="fa-solid fa-circle-check" style="color:var(--color-gamer); margin-top:3px;"></i><div>${b}</div></li>`).join('');
            id('sidebar-hardware-id').classList.add('abierto');
        }
        function ocultarSidebar() { id('sidebar-hardware-id').classList.remove('abierto'); }
        function redirigirAMonitoreo() { navegarAModulo('monitoreo'); }

        // --- RESEVA CABINAS ---
        function abrirModalAsignacionHoras(pc_id, categoria) {
            temporal_horas = 1;
            temporal_pc_id = pc_id;
            temporal_categoria = categoria;
            
            id('modal-estacion-nombre').innerText = "Terminal " + String(pc_id).padStart(2, '0');
            id('modal-estacion-tipo').innerText = BACKEND_DATA.cabinas[categoria].titulo;
            id('modal-estacion-tarifa').innerText = "S/. " + BACKEND_DATA.cabinas[categoria].tarifa.toFixed(2) + " / hora";
            id('modal-horas-contador').innerText = "1h";
            recalcularMontoFactura();
            id('modal-alquiler-id').style.display = 'flex';
        }
        function cerrarModalAlquiler() { id('modal-alquiler-id').style.display = 'none'; }
        
        function cambiarContadorHoras(factor) {
            temporal_horas = Math.max(1, Math.min(12, temporal_horas + factor));
            id('modal-horas-contador').innerText = temporal_horas + "h";
            recalcularMontoFactura();
        }
        function recalcularMontoFactura() {
            let tarifa = BACKEND_DATA.cabinas[temporal_categoria].tarifa;
            id('modal-estacion-total').innerText = "S/. " + (temporal_horas * tarifa).toFixed(2);
        }

        function agregarCabinaAlCarrito() {
            let desc = `Renta Terminal ${String(temporal_pc_id).padStart(2, '0')} por ${temporal_horas}h`;
            let total = temporal_horas * BACKEND_DATA.cabinas[temporal_categoria].tarifa;
            
            CARRITO_LOCAL.push({
                descripcion: desc, monto: total, tag: "CABINA", pc_id: temporal_pc_id, horas: temporal_horas
            });
            cerrarModalAlquiler();
            renderizarCarritoEconómico();
            alert("Añadido al carrito con éxito.");
        }

        // --- MANEJO DE SUMINISTROS ---
        function desplegarModalServicio(clave) {
            const item = BACKEND_DATA.servicios[clave];
            id('m-serv-titulo').innerText = item.titulo;
            id('m-serv-desc').innerText = item.desc;
            id('m-serv-precio').innerText = "S/. " + item.costo.toFixed(2);
            id('m-serv-detalles-lista').innerHTML = item.detalles.map(d => `<li>${d}</li>`).join('');

            id('btn-add-servicio-carrito').onclick = function() {
                CARRITO_LOCAL.push({ descripcion: item.titulo, monto: item.costo, tag: item.tipo_item.toUpperCase() });
                cerrarModalServicio();
                renderizarCarritoEconómico();
                alert("Añadido al carrito con éxito.");
            };
            id('modal-servicio-id').style.display = 'flex';
        }
        function cerrarModalServicio() { id('modal-servicio-id').style.display = 'none'; }

        // --- CONTROL DEL CARRITO FLOTANTE Y LIQUIDACIÓN ---
        function desplegarModalCarrito() {
            renderizarCarritoEconómico();
            id('modal-carrito-id').style.display = 'flex';
        }
        function cerrarModalCarrito() { id('modal-carrito-id').style.display = 'none'; }
        function vaciarTodoElCarrito() { CARRITO_LOCAL = []; renderizarCarritoEconómico(); }

        function renderizarCarritoEconómico() {
            id('carrito-badge-count').innerText = CARRITO_LOCAL.length;
            const contenedor = id('carrito-lista-contenedor');
            
            if (CARRITO_LOCAL.length === 0) {
                id('carrito-vacio-mensaje').style.display = 'block';
                contenedor.style.display = 'none';
                id('cart-subtotal').innerText = "S/. 0.00";
                id('cart-igv').innerText = "S/. 0.00";
                id('cart-total').innerText = "S/. 0.00";
                id('btn-ejecutar-pago-final').disabled = true;
                return;
            }

            id('carrito-vacio-mensaje').style.display = 'none';
            contenedor.style.display = 'block';
            contenedor.innerHTML = "";

            let bruto = 0;
            CARRITO_LOCAL.forEach((item, index) => {
                bruto += item.monto;
                contenedor.innerHTML += `
                    <div class="item-carrito-fila">
                        <div>
                            <h5 style="margin:0; color:#fff;">${item.descripcion}</h5>
                            <span style="font-size:0.75rem; color:var(--text-secundario);">[${item.tag}]</span>
                        </div>
                        <span style="font-weight:700;">S/. ${item.monto.toFixed(2)}</span>
                    </div>
                `;
            });

            let subtotal = bruto / 1.18;
            let igv = bruto - subtotal;

            id('cart-subtotal').innerText = "S/. " + subtotal.toFixed(2);
            id('cart-igv').innerText = "S/. " + igv.toFixed(2);
            id('cart-total').innerText = "S/. " + bruto.toFixed(2);
            id('btn-ejecutar-pago-final').disabled = false;
        }

        function procesarPagoOrdenServicio() {
            let bruto = CARRITO_LOCAL.reduce((acc, el) => acc + el.monto, 0);
            
            fetch('/api/procesar_pago', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: CARRITO_LOCAL, total: bruto })
            })
            .then(res => {
                if (!res.ok) throw new Error("Fondos insuficientes");
                return res.json();
            })
            .then(res => {
                alert(`¡COMPROBANTE DE PAGO EMITIDO!\\n\\nTicket: ${res.ticket_id}\\nFecha: ${res.fecha}\\nTotal Cobrado: S/. ${bruto.toFixed(2)}\\n\\nLas terminales reservadas han sido habilitadas en la topología de red.`);
                CARRITO_LOCAL = [];
                cerrarModalCarrito();
                sincronizarConServidorBackend();
            })
            .catch(err => {
                alert("ERROR EN FACTURACIÓN: Fondos insuficientes en el crédito del usuario.");
            });
        }

        // --- BACKEND ACCIONES ADMIN ---
        function ejecutarRecargaSaldoAdmin() {
            let monto = parseFloat(id('form-admin-recarga-monto').value) || 0;
            if(monto <= 0) return;
            fetch('/api/recarga_saldo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ monto: monto })
            })
            .then(() => {
                alert("Abono procesado correctamente en la base de datos.");
                sincronizarConServidorBackend();
            });
        }

        function cambiarEstadoRedTerminal(idx, checked) {
            fetch('/api/toggle_pc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pc_index: idx, estado: checked })
            }).then(() => sincronizarConServidorBackend());
        }

        function guardarConfiguracionGlobalAdmin() {
            let payload = {
                c1_titulo: id('form-c1-titulo').value,
                c1_tarifa: id('form-c1-precio').value,
                c1_desc: id('form-c1-desc').value,
                c1_specs: id('form-c1-specs').value,
                c2_titulo: id('form-c2-titulo').value,
                c2_tarifa: id('form-c2-precio').value,
                c2_desc: id('form-c2-desc').value,
                c2_specs: id('form-c2-specs').value
            };

            fetch('/api/actualizar_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }).then(() => {
                alert("Configuración de infraestructura guardada permanentemente en JSON.");
                sincronizarConServidorBackend();
            });
        }
    </script>
</body>
</html>
"""

def arrancar_navegador():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    Timer(1.5, arrancar_navegador).start()
    app.run(debug=True, use_reloader=False)
