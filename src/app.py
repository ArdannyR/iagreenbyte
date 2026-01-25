import streamlit as st
import requests
import os
from dotenv import load_dotenv # Importar librería

# 1. Cargar las variables del archivo .env
load_dotenv()

# 2. Leer la variable (Si no existe, usa una por defecto para no romper nada)
URL_BACKEND = os.getenv("API_URL")

st.title("Prueba de Conexión por Variables de Entorno")
st.write(f"Conectando a: `{URL_BACKEND}`") # Solo para depurar visualmente

if st.button("Probar Conexión"):
    try:
        # Usamos la variable en lugar de la URL fija
        respuesta = requests.get(f"{URL_BACKEND}/")
        st.success(f"Respuesta del servidor: {respuesta.json()}")
    except:
        st.error("Falló la conexión. Revisa que el puerto en el .env sea correcto.")