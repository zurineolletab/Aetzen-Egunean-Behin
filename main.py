import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div[role="button"] {
        background-color: #ffffff !important; border: 2px solid #bdbdbd !important;
    }
    h1, h2, h3 { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIONES DE CARGA (Usando URL directa para evitar HTTPError)
def cargar_csv(pestaña):
    try:
        # Convertimos la URL de edición en URL de exportación CSV
        base_url = st.secrets["public_gsheets_url"].replace("/edit", "")
        # Si es la pestaña puntuaciones, Google necesita el GID (normalmente 0 es la primera, pero buscamos por nombre)
        # Para simplificar, usamos el nombre de la hoja en la URL
        sheet_url = f"{base_url}/gviz/tq?tqx=out:csv&sheet={pestaña}"
        df = pd.read_csv(sheet_url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

# 3. LOGO
if os.path.exists("AKE.jpeg"):
    st.image("AKE.jpeg", width=140)
else:
    st.title("Aetzen Egunean Behin")

hoy_str = datetime.now().strftime("%Y-%m-%d")

# 4. LÓGICA DE JUEGO
if 'user_auth' not in st.session_state:
    with st.form("registro"):
        st.write("### Registro de Participante")
        nombre = st.text_input("Nombre / Alias").strip()
        pueblo = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        if st.form_submit_button("Entrar a jugar"):
            if nombre:
                # Comprobamos si el usuario ya existe en el ranking de hoy
                df_puntos = cargar_csv("puntuaciones")
                if not df_puntos.empty and 'usuario' in df_puntos.columns:
                    # Convertimos fechas a string para comparar bien
                    df_puntos['fecha'] = df_puntos['fecha'].astype(str)
                    ya_jugo = df_puntos[(df_puntos['usuario'].str.lower() == nombre.lower()) & (df_puntos['fecha'] == hoy_str)]
                    if not ya_jugo.empty:
                        st.error(f"⚠️ {nombre}, ya has participado hoy.")
                    else:
                        st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                        st.rerun()
                else:
                    st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                    st.rerun()
            else:
                st.error("Introduce un nombre.")
else:
    col1, col2 = st.columns([3, 1])
    with col1: st.write(f"👤 **{st.session_state.user_auth['nombre']}**")
    with col2: 
        if st.button("⬅️ Salir"):
            del st.session_state.user_auth
            st.rerun()
    
    st.divider()
    
    df_preguntas = cargar_csv("preguntas")
    if not df_preguntas.empty:
        df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
        p_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

        if not p_hoy.empty:
            p = p_hoy.iloc[0]
            st.subheader(p['pregunta'])
            opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
            res = st.radio("Elige tu respuesta:", opciones, index=None)
            
            if st.button("Enviar Respuesta"):
                if res:
                    correcta_letra = str(p['correcta']).strip().lower()
                    mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                    puntos = 10 if res == mapa.get(correcta_letra) else 0
                    
                    # --- AVISO SOBRE GUARDADO ---
                    if puntos == 10: st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                    else: st.error(f"Incorrecto. {p['explicacion']}")
                    
                    st.info("Nota: Para guardar puntos oficialmente, contacta con el administrador para habilitar permisos de escritura.")
                    time_lib.sleep(4)
                    st.rerun()
                else:
                    st.warning("Selecciona una opción.")
        else:
            st.write("⌛ No hay pregunta para hoy.")

# 5. RANKING
st.divider()
st.subheader("🏆 Ranking por Pueblos")
df_rank = cargar_csv("puntuaciones")
if not df_rank.empty and 'puntos' in df_rank.columns:
    try:
        ranking = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
        st.bar_chart(ranking)
    except:
        st.write("Cargando datos del ranking...")
else:
    st.write("Aún no hay puntuaciones registradas.")
