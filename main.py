import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib

# 1. CONFIGURACIÓN Y ESTÉTICA
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- NUEVA PALETA DE COLORES COMBINADA CON EL LOGO ---
st.markdown("""
    <style>
    /* 1. Color de fondo principal (Un gris muy claro, casi blanco, para que el logo resalte) */
    .stApp {
        background-color: #f9fbf9;
    }
    
    /* 2. Color de los Títulos (Negro, como las letras grandes 'AE' y 'ZKOA') */
    h1, h2, h3 {
        color: #000000 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* 3. Estilo de los Botones (Verde hierba, como las letras 'elkartea' y la base del logo) */
    .stButton>button {
        background-color: #5d9e35; /* El verde exacto del logo */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    /* Efecto al pasar el ratón por encima del botón */
    .stButton>button:hover {
        background-color: #4a8029; /* Un verde un poco más oscuro */
        color: white;
        border: none;
        transform: scale(1.03); /* Se agranda un poquito */
    }
    
    /* 4. Estilo de las tarjetas de pregunta y mensajes info */
    .stAlert {
        border-radius: 10px;
        border: 1px solid #d1e7dd;
    }
    
    /* 5. Color del texto normal */
    .stMarkdown, .stRadio label {
        color: #212529;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO (Asegúrate de haber subido 'logo_aezkoa.jpeg' a GitHub) ---
try:
    # He centrado el logo y ajustado el tamaño para que sea el protagonista
    col_logo, _ = st.columns([2, 1])
    with col_logo:
        st.image("logo_aezkoa.jpeg", width=250)
except:
    st.write("🏛️ **Aetzen Egunean Behin**")

st.title("Aetzen Egunean Behin")

# 2. CARGAR DATOS
def cargar_datos():
    try:
        url = st.secrets["public_gsheets_url"]
        df = pd.read_csv(url)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# 3. VARIABLES DE ESTADO Y JUEGO
hoy_str = datetime.now().strftime("%Y-%m-%d")

if 'respondido_hoy' not in st.session_state:
    st.session_state.respondido_hoy = False

# 4. LÓGICA DE NAVEGACIÓN Y JUEGO
if 'user_auth' not in st.session_state:
    # --- PANTALLA INICIAL ---
    with st.form("registro"):
        st.write("### Registro de Participante")
        nombre = st.text_input("Nombre / Alias")
        pueblo = st.selectbox("Tu Pueblo", ["Orbaizta", "Orbara", "Aria", "Aribe", "Garralda", "Garaioa", "Hiriberri Aezkoa", "Abaurrepea", "Abaurregaina", "Auritz", "Luzaide", "Olaldea", "Oroz-Betelu", "Erroibar", "Zaraitzu", "Erronkari", "Agoitz", "Iparralde"])
        if st.form_submit_button("Entrar a jugar"):
            if nombre:
                st.session_state.user_auth = {"nombre": nombre, "pueblo": pueblo}
                st.rerun()
            else:
                st.error("Introduce un nombre.")
else:
    # --- CABECERA DE JUEGO (Con botones integrados en el diseño) ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"👤 **{st.session_state.user_auth['nombre']}** | 🏘️ **{st.session_state.user_auth['pueblo']}**")
    with col2:
        # Un botón de salir más discreto
        if st.button("⬅️ Salir"):
            del st.session_state.user_auth
            st.session_state.respondido_hoy = False
            st.rerun()
    
    st.divider()

    # --- LÓGICA DE PREGUNTA ---
    if st.session_state.respondido_hoy:
        st.success("✅ ¡Gracias! Tu respuesta ha sido enviada correctamente.")
        st.balloons() # Mostramos globos solo una vez al responder
    else:
        df_preguntas = cargar_datos()
        if df_preguntas is not None:
            df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
            pregunta_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                # Tarjeta visual para la pregunta
                with st.container():
                    st.subheader(p['pregunta'])
                    
                    opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                    res = st.radio("Elige tu respuesta:", opciones, index=None)
                    
                    if st.button("Enviar Respuesta"):
                        if res: # Aseguramos que haya elegido algo
                            correcta_letra = str(p['correcta']).strip().lower()
                            mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                            
                            if res == mapa.get(correcta_letra):
                                st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                            else:
                                st.error(f"No es correcto. La respuesta era la {correcta_letra.upper()}. {p['explicacion']}")
                            
                            st.session_state.respondido_hoy = True
                            time_lib.sleep(3)
                            st.rerun()
                        else:
                            st.warning("Por favor, selecciona una opción.")
            else:
                st.write(f"⌛ No hay pregunta para hoy ({hoy_str}).")

# 5. CLASIFICACIÓN
st.divider()
st.subheader("🏆 Clasificación por Pueblos")
st.write("Ranking disponible próximamente.")
