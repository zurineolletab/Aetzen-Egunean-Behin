import streamlit as st
import pandas as pd
from datetime import datetime, time
import time as time_lib

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Pirineo Cultural", page_icon="⛰️")

# LOGO: Sustituye esta URL por la de vuestro logo real (puedes subirlo a GitHub y usar el link)
LOGO_URL = "https://tu-asociacion.org/logo.png" 
st.image(LOGO_URL, width=150)

st.title("⛰️ Pirineo Navarro Challenge")

# 2. LÓGICA DE HORARIOS
ahora = datetime.now()
hora_actual = ahora.time()
hora_apertura = time(8, 0)
hora_cierre = time(23, 59)

# 3. LISTA DE PUEBLOS ACTUALIZADA
PUEBLOS = ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", 
           "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", 
           "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"]

# 4. CONEXIÓN A GOOGLE SHEETS (Base de Datos)
# Nota: Para que esto funcione, debes configurar "Secrets" en Streamlit Cloud
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    preguntas = conn.read(worksheet="preguntas")
    puntos = conn.read(worksheet="puntuaciones")
    return preguntas, puntos

# 5. CONTROL DE ACCESO Y JUEGO
if hora_actual < hora_apertura:
    st.warning("🕒 La pregunta de hoy todavía no está disponible. Vuelve a las 08:00h.")
elif hora_actual > hora_cierre:
    st.error("🌙 El tiempo para responder hoy ha terminado. ¡Te esperamos mañana!")
else:
    if 'user_auth' not in st.session_state:
        with st.form("registro"):
            nombre = st.text_input("Nombre / Alias")
            pueblo = st.selectbox("Tu Pueblo", PUEBLOS)
            if st.form_submit_button("Entrar"):
                st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                st.rerun()
    else:
        user = st.session_state.user_auth
        df_preguntas, df_puntos = cargar_datos()
        
        # Verificar si ya ha jugado hoy
        hoy_str = ahora.strftime("%Y-%m-%d")
        ya_jugo = not df_puntos[(df_puntos['usuario'] == user['nombre']) & (df_puntos['fecha'] == hoy_str)].empty
        
        if ya_jugo:
            st.info(f"Hola {user['nombre']}, ¡ya has participado hoy! Consulta los rankings abajo.")
        else:
            # Buscar la pregunta de hoy
            pregunta_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]
            
            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.markdown(f"### {p['pregunta']}")
                res = st.radio("Elige tu respuesta:", [p['opcion_a'], p['opcion_b'], p['opcion_c']])
                
                if st.button("Enviar Respuesta"):
                    es_correcta = (res == p[f"opcion_{p['correcta'].lower()}"])
                    puntos_ganados = 10 if es_correcta else 0
                    
                    # GUARDAR PERMANENTEMENTE EN GOOGLE SHEETS
                    nueva_fila = pd.DataFrame([{"fecha": hoy_str, "usuario": user['nombre'], "pueblo": user['pueblo'], "puntos": puntos_ganados}])
                    df_actualizado = pd.concat([df_puntos, nueva_fila], ignore_index=True)
                    conn.update(worksheet="puntuaciones", data=df_actualizado)
                    
                    if es_correcta:
                        st.success(f"¡Correcto! +10 puntos para {user['pueblo']}. {p['explicacion']}")
                        st.balloons()
                    else:
                        st.error(f"¡Vaya! No es correcto. La respuesta era la {p['correcta']}. {p['explicacion']}")
                    
                    time_lib.sleep(3)
                    st.rerun()
            else:
                st.write("No hay pregunta programada para hoy.")

# 6. RANKINGS (Se leen de la pestaña 'puntuaciones')
st.divider()
st.subheader("🏆 Rankings en Tiempo Real")
_, df_rank = cargar_datos()

t1, t2 = st.tabs(["Clasificación Individual", "Clasificación por Pueblos"])
with t1:
    ranking_ind = df_rank.groupby('usuario')['puntos'].sum().sort_values(ascending=False)
    st.table(ranking_ind)
with t2:
    ranking_pueblo = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
    st.bar_chart(ranking_pueblo)
