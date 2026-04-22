import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; width: 100%; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div[role="button"] {
        background-color: #ffffff !important; border: 2px solid #bdbdbd !important;
    }
    h1, h2, h3 { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos(pestaña):
    try:
        # Usamos la conexión oficial para escribir/leer
        df = conn.read(worksheet=pestaña, ttl=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 3. LOGO
if os.path.exists("AKE.jpeg"):
    st.image("AKE.jpeg", width=140)

hoy_str = datetime.now().strftime("%Y-%m-%d")

# 4. LÓGICA DE ACCESO (EMAIL)
if 'user_email' not in st.session_state:
    with st.form("login"):
        st.write("### 🔑 Acceso al Challenge")
        email = st.text_input("Introduce tu Correo Electrónico").strip().lower()
        pueblo = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        
        if st.form_submit_button("Entrar a jugar"):
            if "@" in email and "." in email: # Validación básica de email
                # Comprobamos en el Excel si ya jugó hoy
                df_puntos = cargar_datos("puntuaciones")
                if not df_puntos.empty and 'usuario' in df_puntos.columns:
                    ya_jugo = df_puntos[(df_puntos['usuario'] == email) & (df_puntos['fecha'].astype(str) == hoy_str)]
                    if not ya_jugo.empty:
                        st.error("⚠️ Este correo ya ha participado hoy. ¡Vuelve mañana!")
                    else:
                        st.session_state.user_email = email
                        st.session_state.user_pueblo = pueblo
                        st.rerun()
                else:
                    st.session_state.user_email = email
                    st.session_state.user_pueblo = pueblo
                    st.rerun()
            else:
                st.error("Por favor, introduce un correo electrónico válido.")
else:
    # PANTALLA DE PREGUNTA
    st.write(f"📧 Jugador: **{st.session_state.user_email}**")
    if st.button("Cerrar Sesión"):
        del st.session_state.user_email
        st.rerun()

    st.divider()

    df_preguntas = cargar_datos("preguntas")
    if not df_preguntas.empty:
        df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
        p_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

        if not p_hoy.empty:
            p = p_hoy.iloc[0]
            st.subheader(p['pregunta'])
            opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
            res = st.radio("Selecciona tu respuesta:", opciones, index=None)
            
            if st.button("Enviar Respuesta"):
                if res:
                    # Lógica de puntos
                    correcta_letra = str(p['correcta']).strip().lower()
                    mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                    puntos = 10 if res == mapa.get(correcta_letra) else 0
                    
                    # GUARDAR EN EL EXCEL (Para que el bloqueo sea permanente)
                    try:
                        df_puntos_act = cargar_datos("puntuaciones")
                        nueva_fila = pd.DataFrame([{
                            "fecha": hoy_str, 
                            "usuario": st.session_state.user_email, 
                            "pueblo": st.session_state.user_pueblo, 
                            "puntos": puntos
                        }])
                        df_final = pd.concat([df_puntos_act, nueva_fila], ignore_index=True)
                        conn.update(worksheet="puntuaciones", data=df_final)
                        
                        if puntos == 10: st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                        else: st.error(f"¡Vaya! {p['explicacion']}")
                        
                        time_lib.sleep(3)
                        st.rerun()
                    except:
                        st.error("Hubo un problema al guardar. Revisa los permisos del Excel.")
                else:
                    st.warning("Selecciona una opción.")
        else:
            st.write("⌛ No hay pregunta para hoy.")

# RANKING POR PUEBLOS
st.divider()
st.subheader("🏆 Ranking por Pueblos")
df_rank = cargar_datos("puntuaciones")
if not df_rank.empty:
    ranking = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
    st.bar_chart(ranking)
