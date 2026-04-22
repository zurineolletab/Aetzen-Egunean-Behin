import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- ESTILO ---
st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; }
    h1, h2, h3 { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS MEJORADA
def cargar_datos_csv(pestaña):
    try:
        base_url = st.secrets["public_gsheets_url"].split("/edit")[0]
        sheet_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        df = pd.read_csv(sheet_url)
        # Limpiar nombres de columnas: quitar espacios y poner en minúsculas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. LOGO
if os.path.exists("AKE.jpeg"):
    st.image("AKE.jpeg", width=140)

# Fecha de hoy en formato estándar
hoy_dt = datetime.now()
hoy_str = hoy_dt.strftime("%Y-%m-%d")

# 4. ACCESO POR EMAIL
if 'user_email' not in st.session_state:
    with st.form("login"):
        st.write("### 🔑 Acceso al Challenge")
        email_input = st.text_input("Correo Electrónico").strip().lower()
        pueblo_input = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        
        if st.form_submit_button("Entrar a jugar"):
            if "@" in email_input and "." in email_input:
                df_puntos = cargar_datos_csv("puntuaciones")
                ya_jugo = False
                if not df_puntos.empty and 'usuario' in df_puntos.columns:
                    # Normalizar fechas del Excel para comparar
                    df_puntos['fecha_limpia'] = pd.to_datetime(df_puntos['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
                    check = df_puntos[(df_puntos['usuario'] == email_input) & (df_puntos['fecha_limpia'] == hoy_str)]
                    if not check.empty:
                        ya_jugo = True
                
                if ya_jugo:
                    st.error("⚠️ Ya has participado hoy con este correo.")
                else:
                    st.session_state.user_email = email_input
                    st.session_state.user_pueblo = pueblo_input
                    st.rerun()
            else:
                st.error("Introduce un email válido.")
else:
    st.write(f"📧 **{st.session_state.user_email}** | 🏘️ **{st.session_state.user_pueblo}**")
    if st.button("Cerrar Sesión"):
        del st.session_state.user_email
        st.rerun()

    st.divider()

    # --- CARGAR PREGUNTA ---
    df_preguntas = cargar_datos_csv("preguntas")
    if not df_preguntas.empty and 'fecha' in df_preguntas.columns:
        # Convertimos la columna fecha del excel a formato YYYY-MM-DD para comparar
        df_preguntas['fecha_dt'] = pd.to_datetime(df_preguntas['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
        p_hoy = df_preguntas[df_preguntas['fecha_dt'] == hoy_str]

        if not p_hoy.empty:
            p = p_hoy.iloc[0]
            st.subheader(p['pregunta'])
            
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
                        st.error(f"¡Incorrecto! La respuesta era: {mapa.get(correcta_letra)}")
                    
                    st.info("¡Gracias por participar! Los puntos se actualizarán en el ranking.")
                    time_lib.sleep(5)
                else:
                    st.warning("Elige una opción.")
        else:
            # Si no hay pregunta, mostramos un mensaje más amable y la fecha que busca
            st.warning(f"⌛ No hay pregunta para hoy ({hoy_str}). Revisa el formato de fecha en el Excel.")
    else:
        st.error("No se pudo acceder a la pestaña de preguntas.")

# 5. RANKING
st.divider()
st.subheader("🏆 Ranking por Pueblos")
df_rank = cargar_datos_csv("puntuaciones")
if not df_rank.empty and 'pueblo' in df_rank.columns:
    try:
        ranking = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
        st.bar_chart(ranking)
    except:
        st.write("Calculando resultados...")
else:
    st.write("Aún no hay puntuaciones.")
