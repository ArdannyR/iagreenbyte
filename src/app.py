import streamlit as st
import requests
import os
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import base64

# 1. CONFIGURACIÓN INICIAL
load_dotenv()
try:
    URL_BACKEND = st.secrets["API_URL"]
except FileNotFoundError:
    URL_BACKEND = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="AgreenPrediction", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ESTILOS CSS (SpaceX)
st.markdown("""
    <style>
    /* Reset básico para evitar conflictos de color */
    .stApp { background-color: #050505; color: #E0E0E0; }
    
    /* Status Badge */
    .status-badge { padding: 5px 10px; border-radius: 5px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .online { background-color: #00ff41; color: black; border: 1px solid #00ff41; box-shadow: 0 0 10px #00ff41; }
    .offline { background-color: #ff3333; color: white; border: 1px solid #ff3333; }
    
    /* Métricas */
    div[data-testid="stMetricValue"] { 
        color: #00F2FF; font-family: 'Courier New', monospace; 
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); 
    }
    
    /* Botones */
    .stButton>button { width: 100%; background-color: transparent; color: #00F2FF; border: 1px solid #00F2FF; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #00F2FF; color: black; box-shadow: 0 0 15px #00F2FF; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIONES AUXILIARES
def check_server_status():
    """Verifica salud del sistema en la raíz /"""
    try:
        r = requests.get(f"{URL_BACKEND}/", timeout=3)
        if r.status_code == 200:
            return True, "SISTEMA ONLINE 🟢"
        return False, f"ERROR {r.status_code} 🔴"
    except Exception:
        return False, "SISTEMA OFFLINE 🔴"

def get_video_html(video_path, fallback_url):
    """Intenta cargar video local, si falla usa URL"""
    try:
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            video_b64 = base64.b64encode(video_bytes).decode()
            return f"data:video/mp4;base64,{video_b64}"
    except FileNotFoundError:
        return fallback_url

# 4. BARRA LATERAL
status_bool, status_msg = check_server_status()
css_class = "online" if status_bool else "offline"

with st.sidebar:
    st.markdown(f'<div class="status-badge {css_class}">{status_msg}</div>', unsafe_allow_html=True)
    st.title("🎛️ PANEL DE CONTROL")
    st.markdown("---")
    
    st.subheader("Simulación Manual")
    with st.form("form_manual"):
        t_max = st.number_input("T. Máxima (°C)", min_value=-5.0, max_value=50.0, value=18.0, step=0.1)
        t_min = st.number_input("T. Mínima (°C)", min_value=-5.0, max_value=30.0, value=8.0, step=0.1)
        lluvia = st.number_input("Lluvia (mm)", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
        mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        
        btn_manual = st.form_submit_button("CALCULAR PREDICCIÓN")

    st.markdown("---")
    st.subheader("🚨 Monitor Auto")
    btn_auto = st.button("VERIFICAR RIESGO HELADA")

# 5. LÓGICA PRINCIPAL
st.title("Sistema de Predicción Climática")
mapa_meses = {"Enero":1, "Febrero":2, "Marzo":3, "Abril":4, "Mayo":5, "Junio":6, 
            "Julio":7, "Agosto":8, "Septiembre":9, "Octubre":10, "Noviembre":11, "Diciembre":12}

# --- LÓGICA 1: BOTÓN MANUAL ---
if btn_manual:
    if t_min > t_max:
        st.error("⛔ ERROR FÍSICO: La Temperatura Mínima no puede ser mayor que la Máxima.")
    else:
        endpoint = f"{URL_BACKEND}/api/v1/prediccion/temperatura"
        payload = {
            "temp_max": t_max, "temp_min": t_min,
            "lluvia": lluvia, "mes": mapa_meses[mes]
        }
        
        with st.spinner("Procesando datos..."):
            try:
                r = requests.post(endpoint, json=payload, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    val_pred = data.get("prediccion_temperatura", 0.0)
                    unidad = data.get("unidad", "°C")
                    
                    col_res, col_graph = st.columns([1, 2])
                    with col_res:
                        st.success("✅ Cálculo Exitoso")
                        st.metric("Temperatura Estimada", f"{val_pred:.2f} {unidad}", "Modelo IA")
                    
                    with col_graph:
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number", value = val_pred,
                            title = {'text': "Termómetro Digital", 'font': {'color': "#00F2FF"}},
                            gauge = {'axis': {'range': [None, 30]}, 'bar': {'color': "#00F2FF"},
                                    'steps': [{'range': [0, 5], 'color': "#330000"}]}
                        ))
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=450)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Error {r.status_code}: {r.text}")
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# --- LÓGICA 2: BOTÓN AUTO (HELADA) ---
if btn_auto:
    endpoint_auto = f"{URL_BACKEND}/api/v1/prediccion/helada-automatica"
    with st.spinner("Escaneando sensores satelitales..."):
        try:
            r = requests.get(endpoint_auto, timeout=10)
            if r.status_code == 200:
                data = r.json()
                ubicacion = data.get("ubicacion", "Latacunga")
                cond = data.get("condiciones_hoy", {})
                es_helada = data.get("alerta_helada", False)
                mensaje = data.get("mensaje", "Sin datos")
                
                st.markdown(f"### 📍 Reporte: **{ubicacion}**")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Máxima", f"{cond.get('max',0)}°C")
                c2.metric("Mínima", f"{cond.get('min',0)}°C")
                c3.metric("Lluvia", f"{cond.get('lluvia',0)}mm")
                
                st.divider()
                if es_helada:
                    st.error(f"🚨 **ALERTA:** {mensaje}")
                else:
                    st.success(f"✅ **ESTADO:** {mensaje}")
            else:
                st.warning("No se pudo conectar con la estación.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- LÓGICA 3: PANTALLA DE INICIO (VIDEO) ---
# Se muestra SOLO si no se ha presionado ningún botón
if not btn_manual and not btn_auto:
    
    # Configuración de Video (Local o Fallback)
    local_path = "assets/background.mp4"
    web_url = "https://upload.wikimedia.org/wikipedia/commons/transcoded/2/22/Earth_Western_Hemisphere_-_Transparent_Background.webm/Earth_Western_Hemisphere_-_Transparent_Background.webm.480p.vp9.webm"
    
    video_src = get_video_html(local_path, web_url)

    st.markdown(f"""
    <style>
    .hero-container {{
        position: relative; height: 500px; width: 100%; overflow: hidden;
        border-radius: 15px; border: 1px solid #333; background-color: black;
        box-shadow: 0 0 40px rgba(0, 242, 255, 0.1); margin-top: 10px;
    }}
    .hero-video {{
        position: absolute; top: 50%; left: 50%; min-width: 100%; min-height: 100%;
        transform: translateX(-50%) translateY(-50%); object-fit: cover; opacity: 0.7; z-index: 0;
    }}
    .hero-content {{
        position: relative; z-index: 2; padding: 50px; height: 100%;
        display: flex; flex-direction: column; justify-content: center; max-width: 600px;
    }}
    .hero-title {{ 
        color: #fff; font-size: 3rem; font-weight: 800; text-transform: uppercase;
        text-shadow: 0 0 20px rgba(0, 242, 255, 0.8); margin: 0;
    }}
    .hero-subtitle {{ color: #ccc; font-size: 1.2rem; margin-top: 10px; border-left: 3px solid #00F2FF; padding-left: 10px; }}
    </style>

    <div class="hero-container">
        <video class="hero-video" autoplay loop muted playsinline>
            <source src="{video_src}">
        </video>
        <div class="hero-content">
            <div class="hero-title">AGREEN<span style="color:#00F2FF">-PREDICTION</span></div>
            <div class="hero-subtitle">Inteligencia Artificial para la Seguridad Alimentaria</div>
            <p style="color: #aaa; margin-top: 20px;">
                Monitoreo satelital y predicción de heladas en tiempo real para la Sierra Ecuatoriana.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    