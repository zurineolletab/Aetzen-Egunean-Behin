import streamlit as st
import pandas as pd
from datetime import date

# Configuración visual de la App
st.set_page_config(page_title="Pirineo Navarro Challenge", page_icon="⛰️")

st.title("⛰️ Pirineo Navarro Challenge")
st.subheader("Cultura y Tradición en el Pirineo")

# 1. Registro de usuario (Solo se pide la primera vez)
if 'user_name' not in st.session_state:
    with st.form("registro"):
        st.info("¡Bienvenido! Regístrate para participar en el ranking.")
        nombre = st.text_input("Tu Nombre o Alias")
        pueblo = st.selectbox("Tu Pueblo", ["Isaba", "Ochagavía", "Burguete", "Roncal", "Elizondo", "Roncesvalles", "Otro"])
        submit = st.form_submit_button("Empezar a jugar")
        if submit and nombre:
            st.session_state.user_name = nombre
            st.session_state.pueblo = pueblo
            st.rerun()
else:
    st.write(f"Jugador: **{st.session_state.user_name}** | Pueblo: **{st.session_state.pueblo}**")
    
    # 2. Lógica del Juego
    # Nota: Aquí conectaríamos con vuestro Google Sheets. 
    # De momento, pongo una pregunta de ejemplo para que veas cómo luce:
    hoy = date.today().strftime("%d/%m/%Y")
    
    st.divider()
    st.markdown(f"### Pregunta del día ({hoy})")
    st.write("¿Cuál es el baile típico de los valles del Pirineo que se danza en honor a la Virgen?")
    
    respuesta = st.radio("Selecciona una opción:", ["La Era", "Tunante", "Paloteado"])
    
    if st.button("Enviar respuesta"):
        if respuesta == "Tunante": # Aquí la IA validaría contra el Excel
            st.success("¡Correcto! Has sumado 10 puntos para tu ranking y para tu pueblo.")
            st.balloons()
        else:
            st.error("¡Casi! La respuesta correcta era Tunante.")

    # 3. Sección de Rankings
    st.divider()
    st.markdown("### 🏆 Clasificación")
    tab1, tab2 = st.tabs(["Individual", "Por Pueblos"])
    
    with tab1:
        # Ejemplo de datos de ranking
        df_ind = pd.DataFrame({'Jugador': ['Mikel', 'Ane'], 'Puntos': [50, 40]})
        st.table(df_ind)
        
    with tab2:
        # Ejemplo de ranking por pueblos
        df_pueblo = pd.DataFrame({'Pueblo': ['Ochagavía', 'Isaba'], 'Total': [120, 95]})
        st.bar_chart(data=df_pueblo, x='Pueblo', y='Total')
