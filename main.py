import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- DISEÑO: FONDO VERDE CLARITO Y COLORES LOGO ---
st.markdown("""
    <style>
    .stApp {
        background-color: #e8f5e9; 
    }
    h1, h2, h3 {
        color: #000000 !important;
    }
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
    .stAlert {
        border-radius: 10px;
        background-color: #c8e6c9 !important;
        color: #1b5e20 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO ---
nombre_logo = "AKE.jpeg"
if os.path.exists(nombre_logo):
    st.image(nombre_logo, width=280)
else:
    st.title("Aetzen Egunean Behin")

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
    # Mostrar datos de usuario y botón salir
    col_u, col_s = st.columns([3, 1])
    with col_u:
        st.write(f"👤 **{st.session_state.user_auth['nombre']}** | 🏘️ **{st.session_state.user_auth['pueblo']}**")
    with col_s:
        if st.button("⬅️ Salir"):
            del st.session_state.user_auth
            st.session_state.respondido_hoy = False
            st.rerun()
    
    st.divider()

    if st.session_state.respondido_hoy:
        st.success("✅ ¡Gracias! Tu respuesta ha sido enviada correctamente.")
    else:
        df_preguntas = cargar_datos()
        if df_preguntas is not None:
            df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
            pregunta_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.subheader(p['pregunta'])
                
                opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                res = st.radio("Elige tu respuesta:", opciones, index=None)
                
                if st.button("Enviar Respuesta"):
                    if res:
                        correcta_letra = str(p['correcta']).strip().lower()
                        mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                        
                        if res == mapa.get(correcta_letra):
                            st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                            st.balloons()
                        else:
                            st.error(f"No es correcto. {p['explicacion']}")
                        
                        st.session_state.respondido_hoy = True
                        time_lib.sleep(3)
                        st.rerun()
                    else:
                        st.warning("Por favor, selecciona una opción.")
            else:
                st.write(f"⌛ No hay pregunta para hoy ({hoy_str}).")

# 5. CLASIFICACIÓN
st.divider()
st.subheader("🏆 Clasificación")
st.write("Ranking disponible próximamente.")
