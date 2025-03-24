import streamlit as st
import pandas as pd

st.set_page_config(page_title="Validación de Participación", page_icon="📄")

st.title("🎫 Validación de Participación en Eventos")
st.markdown("Seleccione su evento e ingrese su contraseña para descargar su certificado en PDF.")

# URLs de las hojas públicas
URL_EVENTOS = "https://docs.google.com/spreadsheets/d/1jtnIcVBFCRX-lunJk3YCFtxOXMNbsarAemgOnBsvXDY/gviz/tq?tqx=out:csv"
URL_APROBADOS = "https://docs.google.com/spreadsheets/d/1_Kfc2LDo6kP9e0RgwZQVkRyuQz2_utElTbp5v7aRw-Q/gviz/tq?tqx=out:csv"

@st.cache_data
def cargar_datos():
    df_eventos = pd.read_csv(URL_EVENTOS, dtype=str).fillna("")
    df_aprobados = pd.read_csv(URL_APROBADOS, dtype=str).fillna("")
    return df_eventos, df_aprobados

try:
    df_eventos, df_aprobados = cargar_datos()
except:
    st.error("❌ Error al cargar las hojas. Verifique que sean públicas.")
    st.stop()

# Selección de evento
evento = st.selectbox("🗂️ Seleccione el evento", df_eventos["Nombre del Curso o Diplomado"].unique())
password = st.text_input("🔐 Contraseña", type="password")

if st.button("✅ Validar"):
    fila_evento = df_eventos[df_eventos["Nombre del Curso o Diplomado"] == evento]
    
    if fila_evento.empty:
        st.error("❌ Evento no encontrado.")
    else:
        codigo = fila_evento.iloc[0]["Código"]
        nombre_archivo = f"{codigo}_{password}.pdf"

        fila_pdf = df_aprobados[df_aprobados["Nombre de Archivo"] == nombre_archivo]

        if not fila_pdf.empty:
            enlace = fila_pdf.iloc[0]["Enlace"]
            st.success("✅ Certificado encontrado.")
            st.markdown(f"[📄 Descargar certificado]({enlace})", unsafe_allow_html=True)
        else:
            st.error("❌ Contraseña inválida o revise si el evento es correcto.")
