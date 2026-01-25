import streamlit as st
import requests
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import time

# 1. CONFIGURACIÓN INICIAL
load_dotenv()
try:
    # Intenta leer de la nube, si falla usa local
    URL_BACKEND = st.secrets["API_URL"]
except FileNotFoundError:
    URL_BACKEND = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="FIA AgroSystem v3", page_icon="📡", layout="wide")

# 2. ESTILOS CSS (SpaceX Theme)
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    
    /* Status Badge en Sidebar */
    .status-badge {
        padding: 5px 10px; border-radius: 5px; font-weight: bold; text-align: center; margin-bottom: 20px;
    }
    .online { background-color: #00ff41; color: black; border: 1px solid #00ff41; box-shadow: 0 0 10px #00ff41; }
    .offline { background-color: #ff3333; color: white; border: 1px solid #ff3333; }
    
    /* Métricas */
    div[data-testid="stMetricValue"] { color: #00F2FF; font-family: 'Courier New', monospace; text-shadow: 0 0 10px rgba(0, 242, 255, 0.5); }
    
    /* Botones */
    .stButton>button {
        width: 100%; background-color: transparent; color: #00F2FF;
        border: 1px solid #00F2FF; border-radius: 0px; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00F2FF; color: black; box-shadow: 0 0 15px #00F2FF; }
    
    /* Botón de Emergencia (Helada) */
    .emergency-btn { border: 1px solid #ffaa00 !important; color: #ffaa00 !important; }
    .emergency-btn:hover { background-color: #ffaa00 !important; color: black !important; box-shadow: 0 0 15px #ffaa00 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIONES DE CONEXIÓN

def check_server_status():
    """Ruta 1: GET / - Verifica salud del sistema"""
    try:
        
        r = requests.get(f"{URL_BACKEND}/", timeout=5)
        
        if r.status_code == 200:
            return True, "SISTEMA ONLINE 🟢"
        else:
            return False, f"ERROR {r.status_code} 🔴"
            
    except Exception as e:
        return False, "SISTEMA OFFLINE 🔴"

# 4. BARRA LATERAL (CONTROLES)
status_bool, status_msg = check_server_status()
css_class = "online" if status_bool else "offline"

with st.sidebar:
    st.markdown(f'<div class="status-badge {css_class}">{status_msg}</div>', unsafe_allow_html=True)
    st.title("🎛️ PANEL DE CONTROL")
    st.markdown("---")
    
    # --- SECCIÓN 1: PREDICCIÓN MANUAL ---
    st.subheader("Simulación Manual")
    with st.form("form_manual"):
        col1, col2 = st.columns(2)
        with col1:
            t_max = st.number_input("T. Máx (°C)", 18.0)
            lluvia = st.number_input("Lluvia (mm)", 5.0)
        with col2:
            t_min = st.number_input("T. Mín (°C)", 8.0)
            hum = st.number_input("Humedad (%)", 60)
            
        mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        
        btn_manual = st.form_submit_button("CALCULAR PREDICCIÓN")

    st.markdown("---")
    
    # --- SECCIÓN 2: ALERTA AUTOMÁTICA (NUEVA RUTA) ---
    st.subheader("🚨 Monitor en Tiempo Real")
    st.info("Consulta sensores remotos para detectar heladas al instante.")
    btn_auto = st.button("VERIFICAR RIESGO DE HELADA (AUTO)")

# 5. LÓGICA PRINCIPAL
st.title("🛰️ Sistema de Predicción Climática | FIA")

# MAPEO DE MESES
mapa_meses = {"Enero":1, "Febrero":2, "Marzo":3, "Abril":4, "Mayo":5, "Junio":6, 
            "Julio":7, "Agosto":8, "Septiembre":9, "Octubre":10, "Noviembre":11, "Diciembre":12}

# --- CASO 1: PREDICCIÓN MANUAL (POST) ---
if btn_manual:
    endpoint = f"{URL_BACKEND}/api/v1/prediccion/temperatura"
    payload = {
        "temp_max": t_max, "temp_min": t_min, "lluvia": lluvia, 
        "humedad": hum, "mes": mapa_meses[mes]
    }
    
    with st.spinner("Procesando datos en el servidor..."):
        try:
            r = requests.post(endpoint, json=payload, timeout=10)
            if r.status_code == 200:
                data = r.json()

                val_pred = data.get("prediccion_temperatura", 0.0)
                
                unidad = data.get("unidad", "°C")

                # 3. Visualización
                col_res, col_graph = st.columns([1, 2])
                with col_res:
                    st.success("✅ Cálculo Exitoso")
                    
                    st.metric("Temperatura Estimada", f"{val_pred:.2f} {unidad}", "Predicción IA")
                
                with col_graph:
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number", value = val_pred,
                        title = {'text': "Termómetro IA", 'font': {'color': "#00F2FF"}},
                        gauge = {'axis': {'range': [None, 30]}, 'bar': {'color': "#00F2FF"}}
                    ))
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=250)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Error {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

# --- CASO 2: HELADA AUTOMÁTICA (GET) ---
if btn_auto:
    endpoint_auto = f"{URL_BACKEND}/api/v1/prediccion/helada-automatica" 
    
    with st.spinner("Conectando con estación meteorológica automática..."):
        try:
            
            r = requests.get(endpoint_auto, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                st.markdown("### 📡 Reporte Automático de Sensores")
                st.json(data) 
                
                
                mensaje = data.get("mensaje", "Datos recibidos")
                es_helada = data.get("hay_helada", False) 
                
                if es_helada:
                    st.error(f"⚠️ ¡ALERTA CRÍTICA! {mensaje}")
                    st.toast("Riesgo de Helada Detectado", icon="❄️")
                else:
                    st.success(f"✅ Zona Segura: {mensaje}")
                    
            else:
                st.warning(f"No se pudo obtener el reporte automático. Código: {r.status_code}")
        except Exception as e:
            st.error(f"Error al conectar con el servicio automático: {e}")


if not btn_manual and not btn_auto:
    st.info("👈 Usa el panel lateral para elegir entre **Simulación Manual** o **Escaneo Automático**.")