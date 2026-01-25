import streamlit as st
import requests
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# 1. Configuración
load_dotenv()
URL_BACKEND = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="FIA AgroPredictor", page_icon="🛰️", layout="wide")

# Estilos CSS Futuristas
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #E0E0E0; }
    div[data-testid="stMetricValue"] { color: #00F2FF; font-family: 'Courier New', monospace; }
    .stButton>button {
        width: 100%; background-color: transparent; color: #00F2FF;
        border: 2px solid #00F2FF; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #00F2FF; color: black; box-shadow: 0 0 15px #00F2FF; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar con el Formulario Correcto
mapa_meses = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
    "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}

with st.sidebar:
    st.header("🛰️ Terminal de Control")
    st.markdown("---")
    with st.form("form_prediccion"):
        st.subheader("Variables Térmicas")
        temp_max = st.number_input("Temp. Máxima (°C)", value=18.0, step=0.1)
        temp_min = st.number_input("Temp. Mínima (°C)", value=8.0, step=0.1)
        
        st.subheader("Condiciones Atmosféricas")
        lluvia = st.number_input("Precipitación (mm)", value=5.0, step=0.1)
        humedad = st.slider("Humedad (%)", 0, 100, 60)
        nombre_mes = st.selectbox("Mes", list(mapa_meses.keys()))
        
        st.markdown("---")
        submit = st.form_submit_button("EJECUTAR PREDICCIÓN")

# 3. Lógica Principal
st.title("Sistema de Predicción Climática")
st.caption(f"Status: Conectado a {URL_BACKEND}")

# Inicializamos la variable para evitar el NameError
temp_final = 0.0 

if submit:
    mes_numero = mapa_meses[nombre_mes]
    endpoint = f"{URL_BACKEND}/api/v1/predecir-clima"
    
    payload = {
        "temp_max": temp_max,
        "temp_min": temp_min,
        "lluvia": lluvia,
        "humedad": humedad,
        "mes": mes_numero
    }

    with st.spinner("Procesando telemetría..."):
        try:
            response = requests.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                resultado = response.json()
                
                # 1. Primero entramos a la carpeta "resultado"
                datos_internos = resultado.get("resultado", {})
                
                # 2. Luego sacamos la temperatura exacta de ahí
                temp_final = datos_internos.get("temperatura_manana_estimada", 0.0)
                
                # 3. ¡Bonus! Saquemos también la descripción del riesgo
                descripcion_riesgo = datos_internos.get("riesgo_descripcion", "Sin datos")
                
                st.success(f"¡Cálculo Exitoso! Estado: {descripcion_riesgo}")
                # -----------------------
                
            else:
                st.error(f"Error del servidor: {response.status_code}")
                st.write(response.text)

        except Exception as e:
            st.error(f"Error de conexión: {e}")

    # 4. Visualización (Fuera del Try/Except para no romper el layout)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="TEMPERATURA PROYECTADA", value=f"{temp_final:.2f} °C", delta="Estimación IA")

    with col2:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = temp_final,
            title = {'text': "Predicción de Campo", 'font': {'color': "#00F2FF"}},
            gauge = {
                'axis': {'range': [None, 30], 'tickwidth': 1, 'tickcolor': "#00F2FF"},
                'bar': {'color': "#00F2FF"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "#444",
            }
        ))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#00F2FF"})
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Ingresa los datos en el panel izquierdo.")