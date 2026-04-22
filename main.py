import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os

# 1. CONFIGURACIÓN Y ESTÉTICA (Aetzen Egunean Behin)
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- DISEÑO DE COLORES (Fondo verde clarito y botones logo) ---
st.markdown("""
    <style>
    /* Fondo de la app verde clarito */
    .stApp {
        background-color: #e8f5e9; 
    }
    
    /* Títulos en negro */
    h1, h2, h3 {
        color: #000000 !important;
    }
    
    /* Botones con el verde del logo */
    .stButton>button {
        background-color: #5d9e35; 
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #4a8029;
        color: white;
    }
    
    /* Tarjetas de mensajes */
    .stAlert {
        border-radius: 10px;
        background-color: #c8e6c9 !important;
        color: #1b5e20 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO (Nombre corregido a AKE.jpeg) ---
nombre_logo = "AKE.jpeg"

if os.path.exists(nombre_logo):
    st.image(nombre_logo, width=280)
else:
    st.title("Aetzen Egunean Behin")
    st.info(f"Subiendo logo... (Asegúrate de que el archivo se llame {nombre_logo} en GitHub)")

# 2. CARGAR DATOS
def cargar_datos():
    try:
        url = st.secrets["public_gsheets_url"]
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# 3. VARIABLES DE ESTADO
hoy_str = datetime.now().strftime("%Y-%m-%d")

if 'respondido_hoy' not in st.session_state:
    st.session_state.respondido_hoy = False

# 4. LÓGICA DE NAVEGACIÓN Y JUEGO
if 'user_auth' not in st.session_state:
    with st.form("registro"):
        st.write("### Registro de Participante")
        nombre = st.text_input("Nombre / Alias")
        pueblo = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        if st.form_submit_button("Entrar a jugar"):
            if nombre:
                st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                st.rerun()
            else:
                st.error("Introduce un nombre.")
else:
    # Cab
