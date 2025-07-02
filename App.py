import streamlit as st
import pandas as pd

# 🎨 CONFIGURACIÓN DE DISEÑO
st.set_page_config(page_title="Validación de Participación", page_icon="🎫", layout="centered")

LOGO_URL = "https://raw.githubusercontent.com/certificados-ciec/ES/main/Logo.png"
COLOR_TITULO = "#f0b124"       # Dorado fuerte
COLOR_BOTON = "#f3d027"        # Dorado claro
COLOR_TEXTO = "#000000"        # Negro

# 🧾 URLs de las hojas públicas
URL_EVENTOS = "https://docs.google.com/spreadsheets/d/1jtnIcVBFCRX-lunJk3YCFtxOXMNbsarAemgOnBsvXDY/gviz/tq?tqx=out:csv"
URL_APROBADOS = "https://docs.google.com/spreadsheets/d/1_Kfc2LDo6kP9e0RgwZQVkRyuQz2_utElTbp5v7aRw-Q/gviz/tq?tqx=out:csv"

# 🖼️ ENCABEZADO CON LOGO
st.markdown(f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" width="800">
        <h1 style="color:{COLOR_TITULO}; margin-bottom:0;">Validación de Participación</h1>
        <p style="font-size:18px; color:{COLOR_TEXTO}; margin-top:5px;">
            Ingrese el curso, diplomado o evento, junto con su contraseña, para descargar su certificado.
        </p>
    </div>
""", unsafe_allow_html=True)

# 📊 Cargar datos
@st.cache_data
def cargar_datos():
    df_eventos = pd.read_csv(URL_EVENTOS, dtype=str).fillna("")
    df_aprobados = pd.read_csv(URL_APROBADOS, dtype=str).fillna("")
    return df_eventos, df_aprobados

try:
    df_eventos, df_aprobados = cargar_datos()
except:
    st.error("❌ No se pudo cargar la información. Verifique que las hojas estén públicas.")
    st.stop()

# 🧾 INTERFAZ
evento = st.selectbox("🗂️ Seleccione el nombre del curso, diplomado o evento", df_eventos["Nombre"].unique())
password = st.text_input("🔐 Contraseña", type="password")

# 🔎 Validar
if st.button("✅ Validar"):
    fila_evento = df_eventos[df_eventos["Nombre"] == evento]

    if fila_evento.empty:
        st.warning("⚠️ Evento no encontrado.")
    else:
        codigo = fila_evento.iloc[0]["Código"]
        nombre_archivo = f"{codigo}_{password}.pdf"
        fila_pdf = df_aprobados[df_aprobados["Nombre de Archivo"] == nombre_archivo]

        if not fila_pdf.empty:
            enlace = fila_pdf.iloc[0]["Enlace"]
            st.success("✅ Certificado encontrado.")
            st.markdown(f"""
                <div style="text-align:center; margin-top:20px;">
                    <a href="{enlace}" target="_blank">
                        <button style="background-color:{COLOR_BOTON}; color:{COLOR_TEXTO};
                            padding:10px 20px; border:none; border-radius:5px;
                            font-size:16px; font-weight:bold; cursor:pointer;">
                            📄 Descargar Certificado
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Contraseña inválida o revise si el evento es correcto.")

st.markdown(f"""
    <br>
    <div style="text-align:center; font-size:13px; color:{COLOR_TEXTO};">
        Los diplomas solo estarán disponibles hasta 1 año después de finalizado el evento, curso o diplomado.
    </div>
    <div style="text-align:center; font-size:13px; color:{COLOR_TEXTO};">
        En caso de presentarse problemas o no encontrar su certificado, comunicarse a ciec@uptc.edu.co
    </div>
    <br>
""", unsafe_allow_html=True)

# 📌 PIE DE PÁGINA
st.markdown(f"""
    <div style="border-top: 1px solid #dcdcda; margin-top: 40px; padding-top: 10px; text-align: center; font-size: 13px; color: {COLOR_TEXTO};">
        Aplicación desarrollada por el <strong>CIEC - Facultad de Ciencias UPTC</strong>.
    </div>
""", unsafe_allow_html=True)
