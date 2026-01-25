import streamlit as st
import requests
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# 1. Configuración de Entorno y Página
load_dotenv()
URL_BACKEND = os.getenv("API_URL", "http://127.0.0.1:8000") # Fallback por seguridad

st.set_page_config(
    page_title="FIA AgroPredictor | Sierra",
    page_icon="🛰️",
    layout="wide"
)

# 2. Estilo Custom 
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    div[data-testid="stMetricValue"] { color: #00F2FF; font-family: 'Courier New', monospace; }
    .stButton>button {
        width: 100%;
        background-color: transparent;
        color: #00F2FF;
        border: 2px solid #00F2FF;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00F2FF;
        color: black;
        box-shadow: 0 0 15px #00F2FF;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar: Formulario de datos
with st.sidebar:
    st.header("🛰️ Terminal de Control")
    st.markdown("---")
    with st.form("form_prediccion"):
        temp_actual = st.number_input("Temp. Actual (°C)", value=12.0, step=0.1)
        humedad = st.slider("Humedad (%)", 0, 100, 60)
        mes = st.selectbox("Mes de Análisis", [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        
        st.markdown("---")
        submit = st.form_submit_button("EJECUTAR PREDICCIÓN")

# 4. Cuerpo Principal
st.title("Sistema de Predicción Climática")
st.caption(f"Status: Conectado a {URL_BACKEND}")

if submit:
    # Endpoint solicitado: /api/v1/predecir-temperatura
    endpoint = f"{URL_BACKEND}/api/v1/predecir-temperatura"
    payload = {
        "temperatura": temp_actual,
        "humedad": humedad,
        "mes": mes
    }

    with st.spinner("Procesando telemetría..."):
        try:
            # Petición POST al backend
            response = requests.post(endpoint, json=payload, timeout=5)
            response.raise_for_status()
            resultado = response.json()
            
            # Asumiendo que la API devuelve {"temperatura_predicha": 14.5}
            temp_final = resultado.get("temperatura_predicha", 0.0)
            
        except Exception as e:
            # Fallback amigable si el backend falla
            st.error(f"Error de enlace: El centro de control (Backend) no responde.")
            st.info("Mostrando simulación de datos locales:")
            temp_final = temp_actual + 1.2 # Simulación

        # 5. Visualización Impactante
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(label="TEMPERATURA PROYECTADA", value=f"{temp_final:.2f} °C", delta="Variación Estimada")
            st.write(f"**Parámetros:** {mes} | {humedad}% Hum.")

        with col2:
            # Gráfico de radar o indicador minimalista con Plotly
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = temp_final,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Predicción de Campo", 'font': {'color': "#00F2FF"}},
                gauge = {
                    'axis': {'range': [None, 30], 'tickwidth': 1, 'tickcolor': "#00F2FF"},
                    'bar': {'color': "#00F2FF"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "#444",
                }
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                font={'color': "#00F2FF", 'family': "Arial"}, height=300)
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Esperando parámetros en la terminal lateral para iniciar el cálculo.")
    
    st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000", 
                caption="Análisis Satelital FIA - Sierra Ecuatoriana")