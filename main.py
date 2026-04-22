import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- LOGO CORREGIDO ---
# Este es el enlace directo a la imagen del logo
LOGO_URL = "https://aezkoa.org/wp-content/uploads/2020/07/logo-elkarteak.png" 
try:
    # He ajustado el tamaño para que se vea bien
    st.image(LOGO_URL, width=200)
except:
    st.write("🏛️ **Aezkoako Udala**")

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

# Inicializar si el usuario ya ha respondido en esta sesión
if 'respondido_hoy' not in st.session_state:
    st.session_state.respondido_hoy = False

# 4. LÓGICA DE NAVEGACIÓN Y JUEGO
if 'user_auth' not in st.session_state:
    # --- PANTALLA INICIAL ---
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
    # --- BOTÓN VOLVER ATRÁS ---
    if st.button("⬅️ Salir / Volver al Inicio"):
        del st.session_state.user_auth
        st.session_state.respondido_hoy = False
        st.rerun()

    user = st.session_state.user_auth
    st.write(f"👤 **{user['nombre']}** | 🏘️ **{user['pueblo']}**")
    
    # --- LIMITAR A UNA RESPUESTA POR SESIÓN ---
    if st.session_state.respondido_hoy:
        st.success("✅ ¡Gracias! Tu respuesta ha sido enviada.")
        st.info("Para volver a ver el ranking, pulsa el botón de 'Salir' arriba.")
    else:
        df_preguntas = cargar_datos()
        if df_preguntas is not None:
            df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
            pregunta_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.divider()
                st.subheader(p['pregunta'])
                
                opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                res = st.radio("Elige tu respuesta:", opciones)
                
                if st.button("Enviar Respuesta"):
                    correcta_letra = str(p['correcta']).strip().lower()
                    mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                    
                    if res == mapa.get(correcta_letra):
                        st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                        st.balloons()
                    else:
                        st.error(f"No es correcto. La respuesta era la {correcta_letra.upper()}. {p['explicacion']}")
                    
                    st.session_state.respondido_hoy = True
                    time_lib.sleep(3)
                    st.rerun()
            else:
                st.write(f"⌛ No hay pregunta para hoy ({hoy_str}).")

# 5. CLASIFICACIÓN
st.divider()
st.subheader("🏆 Clasificación por Pueblos")
try:
    # Intentamos cargar la segunda hoja para el ranking si existe
    # Por ahora mostramos un mensaje de espera hasta que tengamos datos reales
    st.write("El ranking se actualiza con los datos del formulario.")
except:
    pass
