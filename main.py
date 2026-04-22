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

# 3. FECHA Y PUEBLOS
hoy_str = datetime.now().strftime("%Y-%m-%d")
PUEBLOS = ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", 
           "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", 
           "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"]

# 4. LÓGICA DE JUEGO
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
    user = st.session_state.user_auth
    st.write(f"👤 **{user['nombre']}** | 🏘️ **{user['pueblo']}**")
    
    try:
        # Cargamos solo la pestaña de preguntas primero
        df_preguntas = conn.read(worksheet="preguntas", ttl=0)
        df_preguntas.columns = [str(c).strip().lower() for c in df_preguntas.columns]
        df_preguntas['f_limpia'] = pd.to_datetime(df_preguntas['fecha']).dt.strftime('%Y-%m-%d')
        
        pregunta_hoy = df_preguntas[df_preguntas['f_limpia'] == hoy_str]
        
        if not pregunta_hoy.empty:
            p = pregunta_hoy.iloc[0]
            st.divider()
            st.subheader(p['pregunta'])
            
            opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
            res = st.radio("Elige tu respuesta:", opciones)
            
            if st.button("Enviar Respuesta"):
                # Comprobación de respuesta
                correcta_idx = str(p['correcta']).strip().lower()
                col_map = {'a': 'opcion_a', 'b': 'opcion_b', 'c': 'opcion_c'}
                val_correcto = str(p[col_map.get(correcta_idx, 'opcion_a')])
                
                if res == val_correcto:
                    st.success(f"¡Correcto! 🥳 {p['explicacion']}")
                    st.balloons()
                else:
                    st.error(f"¡Vaya! {p['explicacion']}")
                
                # Intentamos guardar la puntuación (si falla, al menos el usuario ve si acertó)
                try:
                    df_puntos = conn.read(worksheet="puntuaciones", ttl=0)
                    nueva_fila = pd.DataFrame([{"fecha": hoy_str, "usuario": user['nombre'], "pueblo": user['pueblo'], "puntos": 10 if res == val_correcto else 0}])
                    df_act = pd.concat([df_puntos, nueva_fila], ignore_index=True)
                    conn.update(worksheet="puntuaciones", data=df_act)
                except:
                    st.warning("Puntuación no guardada (error de permisos), ¡pero has respondido!")
                
                time_lib.sleep(3)
                st.rerun()
        else:
            st.write(f"⌛ No hay pregunta para hoy ({hoy_str}).")
    except Exception as e:
        st.error("No puedo leer el Excel. Revisa que el link en Secrets sea el correcto.")

# 5. RANKINGS
st.divider()
st.subheader("🏆 Rankings")
try:
    df_rank = conn.read(worksheet="puntuaciones", ttl=0)
    if not df_rank.empty:
        st.table(df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False))
except:
    pass
