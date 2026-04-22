import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Pirineo Cultural", page_icon="⛰️")
st.title("⛰️ Pirineo Navarro Challenge")

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_pre = conn.read(worksheet="preguntas", ttl=0)
    df_pun = conn.read(worksheet="puntuaciones", ttl=0)
    df_pre.columns = [str(c).strip().lower() for c in df_pre.columns]
    df_pun.columns = [str(c).strip().lower() for c in df_pun.columns]
    return df_pre, df_pun

# 3. FECHA DE HOY (Forzamos la fecha de la app)
hoy_dt = datetime.now().date()
hoy_str = hoy_dt.strftime("%Y-%m-%d")

# 4. LISTA DE PUEBLOS
PUEBLOS = ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", 
           "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", 
           "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"]

# 5. LÓGICA DE JUEGO (Sin restricción de hora para probar)
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
    
    # Limpiamos las fechas del Excel para que coincidan sí o sí
    df_preguntas['fecha_limpia'] = pd.to_datetime(df_preguntas['fecha']).dt.strftime('%Y-%m-%d')
    
    # Verificar si ya ha jugado hoy
    ya_jugo = False
    if not df_puntos.empty and 'usuario' in df_puntos.columns:
        df_puntos['fecha_limpia'] = pd.to_datetime(df_puntos['fecha']).dt.strftime('%Y-%m-%d')
        ya_jugo = not df_puntos[(df_puntos['usuario'] == user['nombre']) & (df_puntos['fecha_limpia'] == hoy_str)].empty
    
    if ya_jugo:
        st.info(f"¡Hola {user['nombre']}! Ya has participado hoy.")
    else:
        pregunta_hoy = df_preguntas[df_preguntas['fecha_limpia'] == hoy_str]
        
        if not pregunta_hoy.empty:
            p = pregunta_hoy.iloc[0]
            st.divider()
            st.markdown(f"### {p['pregunta']}")
            
            opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
            res = st.radio("Elige tu respuesta:", opciones)
            
            if st.button("Enviar Respuesta"):
                col_correcta = f"opcion_{str(p['correcta']).strip().lower()}"
                es_correcta = (res == str(p[col_correcta]))
                puntos_ganados = 10 if es_correcta else 0
                
                nueva_fila = pd.DataFrame([{
                    "fecha": hoy_str, 
                    "usuario": user['nombre'], 
                    "pueblo": user['pueblo'], 
                    "puntos": puntos_ganados
                }])
                
                df_actualizado = pd.concat([df_puntos.drop(columns=['fecha_limpia'], errors='ignore'), nueva_fila], ignore_index=True)
                conn.update(worksheet="puntuaciones", data=df_actualizado)
                
                if es_correcta:
                    st.success(f"¡CORRECTO! 🥳 +10 puntos. {p['explicacion']}")
                    st.balloons()
                else:
                    st.error(f"¡Vaya! No es correcto. {p['explicacion']}")
                
                time_lib.sleep(3)
                st.rerun()
        else:
            st.write(f"⌛ No hay pregunta para la fecha {hoy_str} en el Excel.")

# 6. RANKINGS
st.divider()
st.subheader("🏆 Rankings en Tiempo Real")
try:
    _, df_rank = cargar_datos()
    if not df_rank.empty:
        t1, t2 = st.tabs(["Individual", "Por Pueblos"])
        with t1:
            r_ind = df_rank.groupby('usuario')['puntos'].sum().sort_values(ascending=False).reset_index()
            st.table(r_ind)
        with t2:
            r_pueblo = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
            st.bar_chart(r_pueblo)
    else:
        st.write("Esperando primeras puntuaciones...")
except:
    pass
