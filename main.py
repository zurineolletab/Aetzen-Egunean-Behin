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
    # Usamos un truco para forzar a que no use datos viejos
    df_pre = conn.read(worksheet="preguntas", ttl="0s")
    df_pun = conn.read(worksheet="puntuaciones", ttl="0s")
    df_pre.columns = [str(c).strip().lower() for c in df_pre.columns]
    df_pun.columns = [str(c).strip().lower() for c in df_pun.columns]
    return df_pre, df_pun

# 3. FECHA DE HOY
hoy_dt = datetime.now().date()
hoy_str = hoy_dt.strftime("%Y-%m-%d")

# 4. PUEBLOS
PUEBLOS = ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", 
           "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", 
           "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"]

# 5. LÓGICA
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
    st.write(f"👤 Jugador: **{user['nombre']}** | 🏘️ Pueblo: **{user['pueblo']}**")
    
    try:
        df_preguntas, df_puntos = cargar_datos()
        
        # Limpieza de fechas para comparar
        df_preguntas['f_limpia'] = pd.to_datetime(df_preguntas['fecha']).dt.strftime('%Y-%m-%d')
        
        # ¿Ya jugó hoy?
        ya_jugo = False
        if not df_puntos.empty and 'usuario' in df_puntos.columns:
            df_puntos['f_limpia'] = pd.to_datetime(df_puntos['fecha']).dt.strftime('%Y-%m-%d')
            ya_jugo = not df_puntos[(df_puntos['usuario'] == user['nombre']) & (df_puntos['f_limpia'] == hoy_str)].empty
        
        if ya_jugo:
            st.info(f"¡Hola {user['nombre']}! Ya has participado hoy. Mira los rankings abajo.")
        else:
            pregunta_hoy = df_preguntas[df_preguntas['f_limpia'] == hoy_str]
            
            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.divider()
                st.subheader(p['pregunta'])
                
                opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                res = st.radio("Elige tu respuesta:", opciones)
                
                if st.button("Enviar Respuesta"):
                    # Lógica de corrección
                    correcta_idx = str(p['correcta']).strip().lower()
                    col_map = {'a': 'opcion_a', 'b': 'opcion_b', 'c': 'opcion_c'}
                    val_correcto = str(p[col_map.get(correcta_idx, 'opcion_a')])
                    
                    es_correcta = (res == val_correcto)
                    puntos = 10 if es_correcta else 0
                    
                    # GUARDAR DATOS
                    nueva_fila = pd.DataFrame([{"fecha": hoy_str, "usuario": user['nombre'], "pueblo": user['pueblo'], "puntos": puntos}])
                    # Solo guardamos las columnas que necesitamos para no ensuciar el Excel
                    df_guardar = pd.concat([df_puntos[['fecha', 'usuario', 'pueblo', 'puntos']], nueva_fila], ignore_index=True)
                    
                    conn.update(worksheet="puntuaciones", data=df_guardar)
                    
                    if es_correcta:
                        st.success(f"¡CORRECTO! 🥳 +10 puntos. {p['explicacion']}")
                        st.balloons()
                    else:
                        st.error(f"¡Vaya! No es correcto. {p['explicacion']}")
                    
                    time_lib.sleep(2)
                    st.rerun()
            else:
                st.write(f"⌛ No hay pregunta para hoy ({hoy_str}).")
    except Exception as e:
        st.error("Error al conectar con los datos. Revisa que el Excel sea 'Editor' para todos.")

# 6. RANKINGS
st.divider()
st.subheader("🏆 Rankings")
try:
    _, df_rank = cargar_datos()
    if not df_rank.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Top Individual**")
            st.table(df_rank.groupby('usuario')['puntos'].sum().sort_values(ascending=False).head(10))
        with col2:
            st.write("**Top Pueblos**")
            st.bar_chart(df_rank.groupby('pueblo')['puntos'].sum())
except:
    pass
