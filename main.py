import streamlit as st
import pandas as pd
from datetime import datetime
import time as time_lib
import os

# 1. CONFIGURACIÓN Y ESTÉTICA (Aetzen Egunean Behin)
st.set_page_config(page_title="Aetzen Egunean Behin", page_icon="⛰️")

# --- DISEÑO: FONDO VERDE CLARITO, COLORES LOGO Y CONTRASTE MEJORADO ---
st.markdown("""
    <style>
    /* Fondo de la app verde clarito suave */
    .stApp {
        background-color: #e8f5e9; 
    }
    
    /* Títulos en negro */
    h1, h2, h3 {
        color: #000000 !important;
    }
    
    /* Botones con el verde del logo */
    .stButton>button {
        background-color: #5d9e35; 
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 25px;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #4a8029;
        color: white;
    }
    
    /* Tarjetas de mensajes info/success */
    .stAlert {
        border-radius: 10px;
        background-color: #c8e6c9 !important;
        color: #1b5e20 !important;
    }
    
    /* --- MEJORA DE CONTRASTE EN FORMULARIOS --- */
    /* Forzar fondo blanco en cuadros de texto y selectboxes */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > select,
    .stSelectbox > div > div > div[role="button"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #bdbdbd !important; /* Borde más visible */
        border-radius: 5px !important;
    }
    
    /* Asegurar contraste del texto en las etiquetas */
    .stTextInput label, .stSelectbox label {
        color: #000000 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO (Reducido a la mitad) ---
# Se busca el archivo AKE.jpeg en GitHub
nombre_logo = "AKE.jpeg"
if os.path.exists(nombre_logo):
    # Se reduce width de 280 a 140 para que sea la mitad de pequeño
    st.image(nombre_logo, width=140)
else:
    # Si no se encuentra, mostramos el título en texto
    st.title("Aetzen Egunean Behin")

# 2. CARGAR DATOS
def cargar_datos():
    try:
        url = st.secrets["public_gsheets_url"]
        df = pd.read_csv(url)
        # Limpiar nombres de columnas
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except:
        return None

# 3. VARIABLES DE ESTADO Y JUEGO
hoy_str = datetime.now().strftime("%Y-%m-%d")

# Inicializar si el usuario ya ha respondido en esta sesión
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
    # Cabecera de usuario y botón salir
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"👤 **{st.session_state.user_auth['nombre']}** | 🏘️ **{st.session_state.user_auth['pueblo']}**")
    with col2:
        if st.button("⬅️ Salir"):
            del st.session_state.user_auth
            st.session_state.respondido_hoy = False
            st.rerun()
    
    st.divider()

    if st.session_state.respondido_hoy:
        st.success("✅ ¡Gracias! Tu respuesta ha sido enviada correctamente.")
    else:
        df_preguntas = cargar_datos()
        if df_preguntas is not None:
            # Limpiar fecha del Excel
            df_preguntas['fecha'] = df_preguntas['fecha'].astype(str).str.strip()
            pregunta_hoy = df_preguntas[df_preguntas['fecha'] == hoy_str]

            if not pregunta_hoy.empty:
                p = pregunta_hoy.iloc[0]
                st.subheader(p['pregunta'])
                
                opciones = [str(p['opcion_a']), str(p['opcion_b']), str(p['opcion_c'])]
                # Asegurar contraste en el radio button
                res = st.radio("Elige tu respuesta:", opciones, index=None)
                
                if st.button("Enviar Respuesta"):
                    if res:
                        correcta_letra = str(p['correcta']).strip().lower()
                        # Mapa de respuestas correctas
                        mapa = {'a': str(p['opcion_a']), 'b': str(p['opcion_b']), 'c': str(p['opcion_c'])}
                        
                        if res == mapa.get(correcta_letra):
                            st.success(f"¡CORRECTO! 🥳 {p['explicacion']}")
                            st.balloons() # Globos al acertar
                        else:
                            st.error(f"No es correcto. La respuesta era la {correcta_letra.upper()}. {p['explicacion']}")
                        
                        # Bloquear respuesta por hoy
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
