import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time as time_lib
import os

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- ESTILO: FONDO VERDE, BOTONES LOGO Y CUADROS BLANCOS ---
st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; }
    h1, h2, h3 { color: #000000 !important; }
    
    /* --- MEJORA DE CONTRASTE: CUADROS BLANCOS --- */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div[role="button"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #bdbdbd !important;
    }
    .stTextInput label, .stSelectbox label {
        color: #000000 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN OFICIAL (Usa los Secrets con la llave JSON)
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_pestaña(nombre):
    try:
        df = conn.read(worksheet=nombre, ttl=0)
        # Limpiar nombres de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 3. LOGO
if os.path.exists("AKE.jpeg"):
    st.image("AKE.jpeg", width=140)

# Fecha de hoy
hoy_str = datetime.now().strftime("%Y-%m-%d")

# 4. ACCESO POR EMAIL
if 'user_email' not in st.session_state:
    with st.form("login"):
        st.write("### 🔑 Acceso al Challenge")
        email_input = st.text_input("Correo Electrónico").strip().lower()
        pueblo_input = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        
        if st.form_submit_button("Entrar a jugar"):
            if "@" in email_input and "." in email_input:
                # Comprobamos si ya jugó hoy buscando en el Excel
                df_puntos = cargar_pestaña("puntuaciones")
                ya_jugo = False
                
                if not df_puntos.empty and 'usuario' in df_puntos.columns:
                    # Convertir fechas del excel a texto limpio para comparar
                    df_puntos['f_check'] = pd.to_datetime(df_puntos['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
                    check = df_puntos[(df_puntos['usuario'] == email_input) & (df_puntos['f_check'] == hoy_str)]
                    if not check.empty:
                        ya_jugo = True
                
                if ya_jugo:
                    st.error("⚠️ Ya has participado hoy con este correo.")
                else:
                    st.session_state.user_email = email_input
                    st.session_state.user_pueblo = pueblo_input
                    st.rerun()
            else:
                st.error("Introduce un email válido.")
else:
    # CABECERA USUARIO
    st.write(f"📧 **{st.session_state.user_email}** | 🏘️ **{st.session_state.user_pueblo}**")
    if st.button("⬅️ Cerrar Sesión"):
        del st.session_state.user_email
        st.rerun()

    st.divider()

    # 5. CARGAR PREGUNTA
    df_preguntas = cargar_pestaña("preguntas")
    if not df_preguntas.empty and 'fecha' in df_preguntas.columns:
        df_preguntas['fecha_dt'] = pd.to_datetime(df_preguntas['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
        p_hoy = df_preguntas[df_preguntas['fecha_dt'] == hoy_str]

        if not p_hoy.empty:
            p = p_hoy.iloc[0]
            st.subheader(p['pregunta'])
            
            opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
            res = st.radio("Selecciona tu respuesta:", opciones, index=None)
            
            if st.button("Enviar Respuesta"):
                if res:
                    correcta_letra = str(p['correcta']).strip().lower()
                    mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                    
                    puntos = 10 if res == mapa.get(correcta_letra) else 0
                    
                    # --- GUARDAR EN GOOGLE SHEETS ---
                    try:
                        df_actual = cargar_pestaña("puntuaciones")
                        nueva_fila = pd.DataFrame([{
                            "fecha": hoy_str, 
                            "usuario": st.session_state.user_email, 
                            "pueblo": st.session_state.user_pueblo, 
                            "puntos": puntos
                        }])
                        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                        
                        # Actualizamos la hoja de puntuaciones
                        conn.update(worksheet="puntuaciones", data=df_final)
                        
                        if puntos == 10:
                            st.success(f"¡CORRECTO! 🥳 {p.get('explicacion', '')}")
                            st.balloons()
                        else:
                            st.error(f"¡Incorrecto! La respuesta era: {mapa.get(correcta_letra)}")
                        
                        time_lib.sleep(3)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar puntos: {e}")
                else:
                    st.warning("Selecciona una opción.")
        else:
            st.warning(f"⌛ No hay pregunta para hoy ({hoy_str}).")
    else:
        st.error("No se pudo acceder a las preguntas.")

# 6. RANKING REAL
st.divider()
st.subheader("🏆 Ranking por Pueblos")
df_rank = cargar_pestaña("puntuaciones")
if not df_rank.empty and 'pueblo' in df_rank.columns:
    try:
        # Agrupamos los puntos por pueblo
        puntos_por_pueblo = df_rank.groupby('pueblo')['puntos'].sum().sort_values(ascending=False)
        st.bar_chart(puntos_por_pueblo)
        st.table(puntos_por_pueblo)
    except:
        st.write("Calculando resultados...")
else:
    st.write("Aún no hay puntuaciones registradas.")
