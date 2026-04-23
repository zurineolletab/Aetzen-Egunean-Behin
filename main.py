import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import time as time_lib
import os

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

st.markdown("""
    <style>
    .stApp { background-color: #e8f5e9; }
    .stButton>button { background-color: #5d9e35; color: white; font-weight: bold; border-radius: 8px; }
    h1, h2, h3 { color: #000000 !important; }
    
    /* CUADROS DE TEXTO BLANCOS */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div[role="button"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #bdbdbd !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_pestaña(nombre):
    try:
        df = conn.read(worksheet=nombre, ttl=0)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# 3. LOGO
if os.path.exists("AKE.jpeg"):
    st.image("AKE.jpeg", width=140)

hoy = datetime.now().strftime("%Y-%m-%d")

# 4. ACCESO
if 'user_email' not in st.session_state:
    with st.form("login"):
        st.write("### 🔑 Saioa hasi")
        email_in = st.text_input("Posta elektronikoa").strip().lower()
        nombre_in = st.text_input("Izena / Ezizena").strip()
        pueblo_in = st.selectbox("Herria", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        
        if st.form_submit_button("Aurrera"):
            if "@" in email_in and nombre_in:
                df_pts = cargar_pestaña("puntuaciones")
                ya_jugo = False
                if not df_pts.empty and 'usuario' in df_pts.columns:
                    df_pts['f_check'] = pd.to_datetime(df_pts['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
                    if not df_pts[(df_pts['usuario'] == email_in) & (df_pts['f_check'] == hoy)].empty:
                        ya_jugo = True
                
                if ya_jugo:
                    st.error("⚠️ Ya has participado hoy.")
                else:
                    st.session_state.user_email = email_in
                    st.session_state.user_nombre = nombre_in
                    st.session_state.user_pueblo = pueblo_in
                    st.rerun()
            else:
                st.error("Rellena todos los campos.")
else:
    # CABECERA
    st.write(f"👤 **{st.session_state.get('user_nombre', 'Jugador')}** | 🏘️ **{st.session_state.get('user_pueblo', 'Aezkoa')}**")
    if st.button("⬅️ Saioa itxi"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

    st.divider()

    # 5. PREGUNTA Y RESPUESTA
    if 'respondido' not in st.session_state:
        st.session_state.respondido = False

    df_preg = cargar_pestaña("preguntas")
    if not df_preg.empty:
        df_preg['f_dt'] = pd.to_datetime(df_preg['fecha'], errors='coerce').dt.strftime('%Y-%m-%d')
        p_hoy = df_preg[df_preg['f_dt'] == hoy]

        if not p_hoy.empty:
            p = p_hoy.iloc[0]
            
            # Si NO ha respondido, mostramos la pregunta
            if not st.session_state.respondido:
                st.subheader(p['pregunta'])
                opts = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                res = st.radio("Respuesta:", opts, index=None)
                
                if st.button("Enviar"):
                    if res:
                        corr_letra = str(p['correcta']).strip().lower()
                        mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                        puntos = 1 if res == mapa.get(corr_letra) else 0
                        
                        # GUARDAR EN EXCEL
                        df_act = cargar_pestaña("puntuaciones")
                        nueva = pd.DataFrame([{"fecha": hoy, "usuario": st.session_state.user_email, "nombre": st.session_state.user_nombre, "pueblo": st.session_state.user_pueblo, "puntos": puntos}])
                        df_fin = pd.concat([df_act, nueva], ignore_index=True)
                        conn.update(worksheet="puntuaciones", data=df_fin)
                        
                        # Marcamos como respondido para mostrar la explicación
                        st.session_state.respondido = True
                        st.session_state.puntos_obtenidos = puntos
                        st.session_state.respuesta_correcta = mapa.get(corr_letra)
                        st.session_state.explicacion_hoy = p.get('explicacion', '¡Gracias por participar!')
                        st.rerun()
                    else:
                        st.warning("Selecciona una opción.")
            
            # Si YA ha respondido, mostramos el resultado y la explicación
            else:
                if st.session_state.puntos_obtenidos == 1:
                    st.success("¡ERANTZUN ZUZENA! 🥳")
                    st.balloons()
                else:
                    st.error(f"ERANTZUN OKERRA. Erantzun zuzena hau zen: {st.session_state.respuesta_correcta}")
                
                st.info(f"💡 **Azalpena:** {st.session_state.explicacion_hoy}")
                st.write("Hemen azpian ikusgai dituzu ranking-ak 👇")

        else:
            st.warning("Gaur ez dago galderarik.")

# 6. RANKINGS (Siempre visibles al final)
st.divider()
df_rk = cargar_pestaña("puntuaciones")
if not df_rk.empty:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Herriak")
        st.bar_chart(df_rk.groupby('pueblo')['puntos'].sum())
    with c2:
        st.subheader("🥇 Top 10 partaideak")
        st.table(df_rk.groupby('nombre')['puntos'].sum().sort_values(ascending=False).head(10))
