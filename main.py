import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
from streamlit_gsheets import GSheetsConnection
import os

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- ESTILO ---
st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; }
    .stTextInput > div > div > input, .stSelectbox > div > div > div[role="button"] {
        background-color: #ffffff !important; border: 2px solid #bdbdbd !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN Y CARGA
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_preguntas():
    df = conn.read(worksheet="preguntas", ttl=0)
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df

def cargar_puntuaciones():
    try:
        df = conn.read(worksheet="puntuaciones", ttl=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["fecha", "usuario", "pueblo", "puntos"])

# 3. LOGO Y TÍTULO
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
                # Verificar si ya existe este usuario hoy en el Excel
                df_puntos = cargar_puntuaciones()
                if not df_puntos.empty:
                    ya_existe = df_puntos[(df_puntos['usuario'].str.lower() == nombre.lower()) & (df_puntos['fecha'].astype(str) == hoy_str)]
                    if not ya_existe.empty:
                        st.error(f"⚠️ El usuario '{nombre}' ya ha participado hoy.")
                    else:
                        st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                        st.rerun()
                else:
                    st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                    st.rerun()
            else:
                st.error("Introduce un nombre.")
else:
    # Pantalla de juego
    col1, col2 = st.columns([3, 1])
    with col1: st.write(f"👤 **{st.session_state.user_auth['nombre']}**")
    with col2: 
        if st.button("⬅️ Salir"):
            del st.session_state.user_auth
            st.rerun()
    
    st.divider()
    
    df_preguntas = cargar_preguntas()
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
                
                # GUARDAR EN EXCEL
                df_actual = cargar_puntuaciones()
                nueva_fila = pd.DataFrame([{"fecha": hoy_str, "usuario": st.session_state.user_auth['nombre'], "pueblo": st.session_state.user_auth['pueblo'], "puntos": puntos}])
                df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                
                conn.update(worksheet="puntuaciones", data=df_final)
                
                if puntos == 10: st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                else: st.error(f"Incorrecto. {p['explicacion']}")
                
                time_lib.sleep(3)
                st.rerun()
            else:
                st.warning("Selecciona una opción.")
    else:
        st.write("⌛ No hay pregunta para hoy.")

# 5. RANKING REAL
st.divider()
st.subheader("🏆 Ranking por Pueblos")
df_rank = cargar_puntuaciones()
if not df_rank.empty:
    ranking = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
    st.bar_chart(ranking)
    st.table(ranking)
else:
    st.write("Aún no hay puntuaciones.")
