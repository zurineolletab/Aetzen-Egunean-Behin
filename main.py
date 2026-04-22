import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- ESTILO MEJORADO ---
st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; }
    .stTextInput > div > div > input { background-color: #ffffff !important; border: 2px solid #bdbdbd !important; }
    h1, h2, h3 { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIONES DE LECTURA SEGURA (Sin usar conectores complejos que fallan)
def cargar_datos_csv(pestaña):
    try:
        # Convertimos la URL de edición en una de exportación CSV directa
        base_url = st.secrets["public_gsheets_url"].split("/edit")[0]
        sheet_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        df = pd.read_csv(sheet_url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error cargando {pestaña}: {e}")
        return pd.DataFrame()

# 3. LOGO
if os.path.exists("AKE.jpeg"):
    st.image("AKE.jpeg", width=140)

hoy_str = datetime.now().strftime("%Y-%m-%d")

# 4. LÓGICA DE ACCESO POR EMAIL
if 'user_email' not in st.session_state:
    with st.form("login"):
        st.write("### 🔑 Acceso al Challenge")
        email_input = st.text_input("Introduce tu Correo Electrónico").strip().lower()
        pueblo_input = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        
        if st.form_submit_button("Entrar a jugar"):
            if "@" in email_input and "." in email_input:
                # Verificamos si ya jugó hoy leyendo el CSV
                df_puntos = cargar_datos_csv("puntuaciones")
                ya_jugo = False
                
                if not df_puntos.empty and 'usuario' in df_puntos.columns:
                    df_puntos['fecha'] = df_puntos['fecha'].astype(str)
                    check = df_puntos[(df_puntos['usuario'] == email_input) & (df_puntos['fecha'] == hoy_str)]
                    if not check.empty:
                        ya_jugo = True
                
                if ya_jugo:
                    st.error("⚠️ Este correo ya ha participado hoy.")
                else:
                    st.session_state.user_email = email_input
                    st.session_state.user_pueblo = pueblo_input
                    st.rerun()
            else:
                st.error("Introduce un email válido.")
else:
    # PANTALLA DE PREGUNTA
    st.write(f"📧 Jugador: **{st.session_state.user_email}** | 🏘️ **{st.session_state.user_pueblo}**")
    if st.button("Cerrar Sesión"):
        del st.session_state.user_email
        st.rerun()

    st.divider()

    # Cargar pregunta de hoy
    df_preguntas = cargar_datos_csv("preguntas")
    if not df_preguntas.empty:
        df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
        p_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

        if not p_hoy.empty:
            p = p_hoy.iloc[0]
            st.subheader(p['pregunta'])
            
            # Limpiar opciones de posibles valores nulos
            opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
            res = st.radio("Selecciona tu respuesta:", opciones, index=None)
            
            if st.button("Enviar Respuesta"):
                if res:
                    correcta_letra = str(p['correcta']).strip().lower()
                    mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                    
                    if res == mapa.get(correcta_letra):
                        st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                        st.balloons()
                    else:
                        st.error(f"¡Incorrecto! La respuesta era la {correcta_letra.upper()}.")
                    
                    st.info("Para que tus puntos se guarden en el ranking oficial, envía un pantallazo a la organización.")
                    # Nota: La escritura automática requiere cuenta de servicio. 
                    time_lib.sleep(5)
                else:
                    st.warning("Selecciona una opción antes de enviar.")
        else:
            st.warning(f"⌛ No hay pregunta registrada para hoy ({hoy_str}).")

# 5. RANKING (Solo lectura)
st.divider()
st.subheader("🏆 Ranking por Pueblos")
df_rank = cargar_datos_csv("puntuaciones")
if not df_rank.empty and 'pueblo' in df_rank.columns:
    try:
        # Agrupar puntos por pueblo
        ranking = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
        st.bar_chart(ranking)
    except Exception as e:
        st.write("Actualizando ranking...")
else:
    st.write("Aún no hay datos en la tabla de puntuaciones.")
