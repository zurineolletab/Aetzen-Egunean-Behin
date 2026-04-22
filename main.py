import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Pirineo Cultural", page_icon="⛰️")
st.title("⛰️ Pirineo Navarro Challenge")

# 2. CONEXIÓN (Usando el Secret que acabamos de crear)
url = st.secrets["public_gsheets_url"]
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_todo():
    try:
        # Forzamos la lectura de la pestaña preguntas
        df = conn.read(spreadsheet=url, worksheet="preguntas", ttl=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error de permisos: {e}")
        return None

# 3. LÓGICA DE LA PREGUNTA
hoy = datetime.now().strftime("%Y-%m-%d")
df_preguntas = cargar_todo()

if df_preguntas is not None:
    # Aseguramos que la fecha se lea bien
    df_preguntas['f_limpia'] = pd.to_datetime(df_preguntas['fecha']).dt.strftime('%Y-%m-%d')
    pregunta_hoy = df_preguntas[df_preguntas['f_limpia'] == hoy]

    if not pregunta_hoy.empty:
        p = pregunta_hoy.iloc[0]
        st.info(f"Pregunta del día: {hoy}")
        st.subheader(p['pregunta'])
        
        opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
        res = st.radio("Elige tu respuesta:", opciones)
        
        if st.button("Enviar"):
            st.success(f"¡Respuesta enviada! Dato curioso: {p['explicacion']}")
            st.balloons()
    else:
        st.warning(f"No hay preguntas para hoy ({hoy}). Revisa la columna A de tu Excel.")
