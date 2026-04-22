import streamlit as st
import pandas as pd
from datetime import datetime, time
import time as time_lib
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Pirineo Cultural", page_icon="⛰️")

# LOGO: Sustituye esta URL por la de vuestro logo real
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

# 4. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Leemos las pestañas con ttl=0 para tener siempre datos frescos
    df_pre = conn.read(worksheet="preguntas", ttl=0)
    df_pun = conn.read(worksheet="puntuaciones", ttl=0)
    
    # Limpiamos nombres de columnas: quitamos espacios y pasamos a minúsculas
    df_pre.columns = [str(c).strip().lower() for c in df_pre.columns]
    df_pun.columns = [str(c).strip().lower() for c in df_pun.columns]
    
    return df_pre, df_pun

# 5. CONTROL DE ACCESO Y JUEGO
if hora_actual < hora_apertura:
    st.warning("🕒 La pregunta de hoy todavía no está disponible. Vuelve a las 08:00h.")
elif hora_actual > hora_cierre:
    st.error("🌙 El tiempo para responder hoy ha terminado. ¡Te esperamos mañana!")
else:
    if 'user_auth' not in st.session_state:
        with st.form("registro"):
            st.write("### Registro de Participante")
            nombre = st.text_input("Nombre / Alias")
            pueblo = st.selectbox("Tu Pueblo", PUEBLOS)
            if st.form_submit_button("Entrar a jugar"):
                if nombre:
                    st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                    st.rerun()
                else:
                    st.error("Por favor, introduce un nombre.")
    else:
        user = st.session_state.user_auth
        st.write(f"Jugador: **{user['nombre']}** | Pueblo: **{user['pueblo']}**")
        
        df_preguntas, df_puntos = cargar_datos()
        
        # Fecha de hoy en formato texto para comparar (Asegúrate que en Excel sea igual)
        hoy_str = ahora.strftime("%Y-%m-%d")
        
        # Verificar si ya ha jugado hoy
        ya_jugo = False
        if not df_puntos.empty and 'usuario' in df_puntos.columns:
            ya_jugo = not df_puntos[(df_puntos['usuario'] == user['nombre']) & (df_puntos['fecha'].astype(str) == hoy_str)].empty
        
        if ya_jugo:
            st.info(f"¡Hola {user['nombre']}! Ya has participado hoy. Mira los rankings abajo.")
        else:
            # Buscar la pregunta de hoy
            pregunta_hoy = df_preguntas[df_preguntas['fecha'].astype(str) == hoy_str]
            
            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.divider()
                st.markdown(f"### {p['pregunta']}")
                
                opciones = [p['opcion_a'], p['opcion_b'], p['opcion_c']]
                res = st.radio("Elige tu respuesta:", opciones)
                
                if st.button("Enviar Respuesta"):
                    # Comprobamos la respuesta correcta (basada en la letra A, B o C en la columna 'correcta')
                    col_correcta = f"opcion_{p['correcta'].strip().lower()}"
                    es_correcta = (res == p[col_correcta])
                    puntos_ganados = 10 if es_correcta else 0
                    
                    # GUARDAR EN GOOGLE SHEETS
                    nueva_fila = pd.DataFrame([{
                        "fecha": hoy_str, 
                        "usuario": user['nombre'], 
                        "pueblo": user['pueblo'], 
                        "puntos": puntos_ganados
                    }])
                    
                    df_actualizado = pd.concat([df_puntos, nueva_fila], ignore_index=True)
                    conn.update(worksheet="puntuaciones", data=df_actualizado)
                    
                    if es_correcta:
                        st.success(f"¡CORRECTO! 🥳 +10 puntos. {p['explicacion']}")
                        st.balloons()
                    else:
                        st.error(f"¡Vaya! No es correcto. {p['explicacion']}")
                    
                    time_lib.sleep(3)
                    st.rerun()
            else:
                st.write("休 No hay pregunta programada para hoy. ¡Avisa a los administradores!")

# 6. RANKINGS
st.divider()
st.subheader("🏆 Rankings en Tiempo Real")
try:
    _, df_rank = cargar_datos()
    if not df_rank.empty:
        t1, t2 = st.tabs(["Clasificación Individual", "Clasificación por Pueblos"])
        with t1:
            r_ind = df_rank.groupby('usuario')['puntos'].sum().sort_values(ascending=False).reset_index()
            st.dataframe(r_ind, use_container_width=True)
        with t2:
            r_pueblo = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
            st.bar_chart(r_pueblo)
    else:
        st.write("Aún no hay puntuaciones registradas. ¡Sé el primero!")
except Exception as e:
    st.write("Cargando rankings...")
