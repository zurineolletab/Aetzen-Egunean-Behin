import streamlit as st
import pandas as pd
from datetime import datetime, time
import time as time_lib
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Pirineo Cultural", page_icon="⛰️")

st.title("⛰️ Pirineo Navarro Challenge")
# Esta línea nos ayuda a ver si la fecha coincide
hoy_dt = datetime.now().date()
st.info(f"📅 Fecha que busca la App: {hoy_dt}")

# 2. LÓGICA DE HORARIOS
ahora = datetime.now()
hora_actual = ahora.time()
hora_apertura = time(8, 0)
hora_cierre = time(23, 59)

# 3. LISTA DE PUEBLOS
PUEBLOS = ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", 
           "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", 
           "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"]

# 4. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    df_pre = conn.read(worksheet="preguntas", ttl=0)
    df_pun = conn.read(worksheet="puntuaciones", ttl=0)
    df_pre.columns = [str(c).strip().lower() for c in df_pre.columns]
    df_pun.columns = [str(c).strip().lower() for c in df_pun.columns]
    return df_pre, df_pun

# 5. JUEGO
if hora_actual < hora_apertura:
    st.warning("🕒 La pregunta de hoy todavía no está disponible. Vuelve a las 08:00h.")
elif hora_actual > hora_cierre:
    st.error("🌙 El tiempo para responder hoy ha terminado.")
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
                    st.error("Introduce un nombre.")
    else:
        user = st.session_state.user_auth
        st.write(f"Jugador: **{user['nombre']}** | Pueblo: **{user['pueblo']}**")
        
        df_preguntas, df_puntos = cargar_datos()
        
        # --- DIAGNÓSTICO: Esto nos dirá qué ve la app ---
        df_preguntas['fecha_dt'] = pd.to_datetime(df_preguntas['fecha'], errors='coerce').dt.date
        num_preguntas = len(df_preguntas)
        st.write(f"🔎 He encontrado {num_preguntas} filas en tu pestaña de preguntas.")
        
        # Verificar si ya jugó hoy
        ya_jugo = False
        if not df_puntos.empty and 'usuario' in df_puntos.columns:
            df_puntos['fecha_dt'] = pd.to_datetime(df_puntos['fecha'], errors='coerce').dt.date
            ya_jugo = not df_puntos[(df_puntos['usuario'] == user['nombre']) & (df_puntos['fecha_dt'] == hoy_dt)].empty
        
        if ya_jugo:
            st.info(f"¡Hola {user['nombre']}! Ya has participado hoy.")
        else:
            pregunta_hoy = df_preguntas[df_preguntas['fecha_dt'] == hoy_dt]
            
            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.divider()
                st.markdown(f"### {p['pregunta']}")
                
                # Aseguramos que las opciones existan
                op_a = str(p.get('opcion_a', 'Opción A no encontrada'))
                op_b = str(p.get('opcion_b', 'Opción B no encontrada'))
                op_c = str(p.get('opcion_c', 'Opción C no encontrada'))
                
                res = st.radio("Elige tu respuesta:", [op_a, op_b, op_c])
                
                if st.button("Enviar Respuesta"):
                    correcta_raw = str(p.get('correcta', 'a')).strip().lower()
                    es_correcta = False
                    
                    if correcta_raw == 'a': es_correcta = (res == op_a)
                    elif correcta_raw == 'b': es_correcta = (res == op_b)
                    elif correcta_raw == 'c': es_correcta = (res == op_c)
                    else: es_correcta = (res.lower() == correcta_raw.lower())

                    puntos_ganados = 10 if es_correcta else 0
                    
                    nueva_fila = pd.DataFrame([{
                        "fecha": hoy_dt.strftime("%Y-%m-%d"), 
                        "usuario": user['nombre'], 
                        "pueblo": user['pueblo'], 
                        "puntos": puntos_ganados
                    }])
                    
                    df_actualizado = pd.concat([df_puntos.drop(columns=['fecha_dt'], errors='ignore'), nueva_fila], ignore_index=True)
                    conn.update(worksheet="puntuaciones", data=df_actualizado)
                    
                    if es_correcta:
                        st.success(f"¡CORRECTO! 🥳 +10 puntos. {p.get('explicacion', '')}")
                        st.balloons()
                    else:
                        st.error(f"¡Vaya! No es correcto. {p.get('explicacion', '')}")
                    
                    time_lib.sleep(3)
                    st.rerun()
            else:
                st.write("⌛ No hay pregunta programada para hoy en el Excel.")

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
        st.write("Aún no hay puntuaciones.")
except:
    pass
