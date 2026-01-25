import streamlit as st
import requests
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv
import time

# 1. Configuración
load_dotenv()
try:
    # Intenta obtener la URL de los secretos de Streamlit Cloud
    URL_BACKEND = st.secrets["API_URL"]
except FileNotFoundError:
    # Si falla (porque estamos en local), usa la variable de entorno o el default
    URL_BACKEND = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="FIA AgroPredictor Pro", page_icon="🛰️", layout="wide")

# 2. Estilos CSS Avanzados 
st.markdown("""
    <style>
    /* Fondo y textos generales */
    .stApp { background-color: #050505; color: #E0E0E0; }
    
    /* Métricas estilo HUD */
    div[data-testid="stMetricValue"] { 
        color: #00F2FF; 
        font-family: 'Courier New', monospace;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
    }
    div[data-testid="stMetricLabel"] { color: #888; }
    
    /* Botones Futuristas */
    .stButton>button {
        width: 100%; background-color: transparent; color: #00F2FF;
        border: 1px solid #00F2FF; border-radius: 0px;
        font-weight: bold; transition: 0.3s;
        text-transform: uppercase; letter-spacing: 2px;
    }
    .stButton>button:hover { 
        background-color: #00F2FF; color: black; 
        box-shadow: 0 0 20px #00F2FF; 
    }
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; white-space: pre-wrap; background-color: #111; border-radius: 4px 4px 0px 0px;
        gap: 1px; padding-top: 10px; padding-bottom: 10px; color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #00F2FF !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Helpers y Constantes
mapa_meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

# 4. Sidebar (Controles)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3222/3222691.png", width=60)
    st.title("COMANDO CENTRAL")
    st.markdown("---")
    
    with st.form("form_prediccion"):
        st.subheader("📡 Datos de Sensores")
        col_side_1, col_side_2 = st.columns(2)
        with col_side_1:
            temp_max = st.number_input("T. Máx (°C)", value=18.0, step=0.1)
            lluvia = st.number_input("Lluvia (mm)", value=5.0, step=0.1)
        with col_side_2:
            temp_min = st.number_input("T. Mín (°C)", value=8.0, step=0.1)
            humedad = st.number_input("Humedad (%)", value=60, step=1)
            
        nombre_mes = st.selectbox("Mes de Análisis", list(mapa_meses.keys()))
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("INICIAR ESCANEO CLIMÁTICO")

# 5. Cuerpo Principal
st.title("🛰️ Sistema de Predicción Climática | FIA")
st.markdown(f"**Conexión Activa:** `{URL_BACKEND}` | **Región:** Sierra Ecuatoriana")

# Variables de estado (para mantener datos si cambiamos de tab)
if 'temp_result' not in st.session_state:
    st.session_state['temp_result'] = None
if 'riesgo_result' not in st.session_state:
    st.session_state['riesgo_result'] = "En espera..."

# LÓGICA DE PREDICCIÓN
if submit:
    mes_numero = mapa_meses[nombre_mes]
    endpoint = f"{URL_BACKEND}/api/v1/predecir-clima"
    payload = {
        "temp_max": temp_max, "temp_min": temp_min,
        "lluvia": lluvia, "humedad": humedad, "mes": mes_numero
    }

    # Barra de progreso simulada para efecto "Processing"
    progress_text = "Calibrando modelos meteorológicos..."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    my_bar.empty()

    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            resultado_inner = data.get("resultado", {})
            
            # Guardar en sesión
            st.session_state['temp_result'] = resultado_inner.get("temperatura_manana_estimada", 0.0)
            st.session_state['riesgo_result'] = resultado_inner.get("riesgo_descripcion", "Normal")
            st.session_state['helada'] = resultado_inner.get("alerta_helada", False)
            
            st.toast('¡Cálculo finalizado con éxito!', icon='✅')
            if st.session_state['helada']:
                st.toast('ALERTA DE HELADA DETECTADA', icon='⚠️')
        else:
            st.error(f"Error del servidor: {response.status_code}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

# 6. VISUALIZACIÓN CON TABS
if st.session_state['temp_result'] is not None:
    tab1, tab2, tab3 = st.tabs(["📊 DASHBOARD", "📈 ANÁLISIS HISTÓRICO", "🚜 RECOMENDACIONES"])

    # TAB 1: EL RELOJ PRINCIPAL
    with tab1:
        col_metrics, col_gauge = st.columns([1, 2])
        
        with col_metrics:
            st.markdown("### Resumen Ejecutivo")
            st.metric(label="Temperatura Estimada", value=f"{st.session_state['temp_result']:.2f} °C", delta="Estable")
            st.metric(label="Nivel de Riesgo", value=st.session_state['riesgo_result'], delta_color="off")
            
            if st.session_state['helada']:
                st.error("🚨 ALERTA: Probabilidad de Helada")
            else:
                st.success("✅ Condiciones seguras para siembra")

        with col_gauge:
            val = st.session_state['temp_result']
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = val,
                title = {'text': "Termómetro Digital IA", 'font': {'size': 24, 'color': "#00F2FF"}},
                gauge = {
                    'axis': {'range': [None, 30], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#00F2FF"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'steps': [
                        {'range': [0, 5], 'color': "#ff3333"},
                        {'range': [5, 12], 'color': "#333"},
                    ],
                    'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': val}
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig, use_container_width=True)

    # TAB 2: GRÁFICA COMPARATIVA (PLOTLY)
    with tab2:
        st.subheader("Comparativa vs Histórico (Simulación)")
        
        # Generamos datos ficticios para que se vea bonito el gráfico
        # (En el futuro, esto vendría de tu Base de Datos)
        dias = ["Hace 3 días", "Hace 2 días", "Ayer", "HOY (Predicción)", "Mañana", "Pasado"]
        
        # Simulamos una curva suave alrededor de la predicción
        base_temp = st.session_state['temp_result']
        temps = [base_temp - 2, base_temp - 1.5, base_temp - 0.5, base_temp, base_temp + 0.5, base_temp + 1.2]
        
        df_chart = pd.DataFrame({"Día": dias, "Temperatura": temps})
        
        fig_line = px.line(df_chart, x="Día", y="Temperatura", markers=True, title="Tendencia Térmica Semanal")
        fig_line.update_traces(line_color='#00F2FF', line_width=4)
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(255,255,255,0.05)',
            font_color="white",
            yaxis_title="Grados Centígrados"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # TAB 3: CONSEJOS AGRÓNOMOS
    with tab3:
        st.subheader("💡 Asistente Agrónomo Inteligente")
        col_consejo_1, col_consejo_2 = st.columns(2)
        
        temp_val = st.session_state['temp_result']
        
        with col_consejo_1:
            st.info("💧 **Riego Sugerido**")
            if temp_val > 20:
                st.write("Alta evaporación detectada. Se recomienda riego abundante en la tarde.")
            else:
                st.write("Condiciones húmedas. Mantener riego moderado para evitar hongos.")
                
        with col_consejo_2:
            st.warning("🛡️ **Protección de Cultivos**")
            if temp_val < 8:
                st.write("¡Atención! Temperaturas bajas. Cubrir semilleros esta noche.")
            else:
                st.write("Condiciones óptimas para fertilización foliar.")

else:
    # Pantalla de bienvenida
    st.info("👈 Ingresa los datos en el panel lateral para calcular la predicción.")
    st.markdown("""
    ### Bienvenido al Sistema FIA
    Este sistema utiliza Inteligencia Artificial conectada a satélites virtuales para proteger tus cultivos.
    
    **Instrucciones:**
    1. Ajusta los parámetros de temperatura y humedad.
    2. Selecciona el mes.
    3. Presiona **INICIAR ESCANEO**.
    """)