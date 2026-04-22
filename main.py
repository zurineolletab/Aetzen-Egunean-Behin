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
    # Cargamos intentando saltar el error de permisos
    try:
        df_pre = conn.read(worksheet="preguntas", ttl=0)
        df_pun = conn.read(worksheet="puntuaciones", ttl=0)
        df_pre.columns = [str(c).strip().lower() for c in df_pre.columns]
        df_pun.columns = [str(c).strip().lower() for c in df_pun.columns]
        return df_pre, df_pun
    except Exception as e:
        st.error("Error de conexión con Google Sheets. Revisa los permisos en Secrets.")
        return pd.DataFrame(), pd.DataFrame()

# 3. FECHA DE HOY
hoy_str = datetime.now().strftime("%Y-%m-%d")

# 4. PUEBLOS
PUEBLOS = ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", 
           "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", 
           "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"]

# 5. LÓGICA DE JUEGO
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
    st.write(f"👤 **{user['nombre']}** | 🏘️ **{user['pueblo']}**")
    
    df_preguntas, df_puntos = cargar_datos()
    
    if not df_preguntas.empty:
        # Limpieza de fechas
        df_preguntas['f_limpia'] = pd.to_datetime(df_preguntas['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # ¿Ya jugó?
        ya_jugo = False
        if not df_puntos.empty and 'usuario' in df_puntos.columns:
            df_puntos['f_limpia'] = pd.to_datetime(df_puntos['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
            ya_jugo = not df_puntos[(df_puntos['usuario'] == user['nombre']) & (df_puntos['f_limpia'] == hoy_str)].empty
        
        if ya_jugo:
            st.info(f"¡Hola! Ya has participado hoy.")
        else:
            pregunta_hoy = df_preguntas[df_preguntas['f_limpia'] == hoy_str]
            
            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.divider()
                st.subheader(p['pregunta'])
                
                opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                res = st.radio("Elige tu respuesta:", opciones)
                
                if st.button("Enviar Respuesta"):
                    # Verificación simple
                    correcta_idx = str(p['correcta']).strip().lower()
                    col_map = {'a': 'opcion_a', 'b': 'opcion_b', 'c': 'opcion_c'}
                    val_correcto = str(p.get(col_map.get(correcta_idx, 'opcion_a'), ''))
                    
                    es_correcta = (res == val_correcto)
                    puntos = 10 if es_correcta else 0
                    
                    # GUARDAR (Solo si hay permisos de edición)
                    try:
                        nueva_fila = pd.DataFrame([{"fecha": hoy_str, "usuario": user['nombre'], "pueblo": user['pueblo'], "puntos": puntos}])
                        df_actualizado = pd.concat([df_puntos, nueva_fila], ignore_index=True)
                        conn.update(worksheet="puntuaciones", data=df_actualizado)
                        
                        if es_correcta:
                            st.success(f"¡Correcto! +10 puntos. {p['explicacion']}")
                            st.balloons()
                        else:
                            st.error(f"¡Vaya! No es correcto. {p['explicacion']}")
                        time_lib.sleep(2)
                        st.rerun()
                    except:
                        st.error("Error al guardar puntuación. Contacta con el admin.")
            else:
                st.write(f"⌛ No hay pregunta para hoy ({hoy_str}).")

# 6. RANKINGS
st.divider()
st.subheader("🏆 Rankings")
try:
    if not df_puntos.empty:
        st.table(df_puntos.groupby('pueblo')['puntos'].sum().sort_values(ascending=False))
except:
    pass
