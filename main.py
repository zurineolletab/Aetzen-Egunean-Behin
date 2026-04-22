import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Pirineo Cultural", page_icon="⛰️")
st.title("⛰️ Pirineo Navarro Challenge")

# 2. FUNCIÓN PARA CARGAR DATOS (Lectura directa)
def cargar_datos():
    try:
        # Leemos el link que pusimos en Secrets
        url = st.secrets["public_gsheets_url"]
        df = pd.read_csv(url)
        # Limpiamos nombres de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"No se pudo cargar el Excel: {e}")
        return None

# 3. LÓGICA DE LA PREGUNTA
hoy_str = datetime.now().strftime("%Y-%m-%d")
df_preguntas = cargar_datos()

if df_preguntas is not None:
    # Convertimos la columna fecha a texto para comparar
    df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
    
    pregunta_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

    if not pregunta_hoy.empty:
        p = pregunta_hoy.iloc[0]
        st.info(f"📅 Pregunta de hoy: {hoy_str}")
        st.subheader(p['pregunta'])
        
        opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
        res = st.radio("Elige tu respuesta:", opciones)
        
        if st.button("Enviar"):
            # Comprobación rápida
            correcta_letra = str(p['correcta']).strip().lower()
            # Mapeamos a, b, c a los valores de las columnas
            mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
            
            if res == mapa.get(correcta_letra):
                st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                st.balloons()
            else:
                st.error(f"¡Vaya! La respuesta correcta era la {correcta_letra.upper()}. {p['explicacion']}")
    else:
        st.warning(f"No hay preguntas para hoy ({hoy_str}) en el Excel. Revisa que la fecha en la columna A esté escrita como AAAA-MM-DD.")
else:
    st.error("Error al conectar con el archivo. Asegúrate de haberlo 'Publicado en la Web' en Google Sheets.")
