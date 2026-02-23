import hashlib
import io
import re
import urllib.request
import zipfile

import pandas as pd
import streamlit as st

# Configuración general
st.set_page_config(page_title="Validación de Participación", page_icon="🎫", layout="centered")

LOGO_URL = "https://raw.githubusercontent.com/certificados-ciec/ES/main/Logo.png"
URL_EVENTOS = "https://docs.google.com/spreadsheets/d/1jtnIcVBFCRX-lunJk3YCFtxOXMNbsarAemgOnBsvXDY/gviz/tq?tqx=out:csv"
URL_APROBADOS = "https://docs.google.com/spreadsheets/d/1_Kfc2LDo6kP9e0RgwZQVkRyuQz2_utElTbp5v7aRw-Q/gviz/tq?tqx=out:csv"
URL_FORM_SOPORTE = "https://forms.gle/82rmSt65KNHQDfC4A"

COLOR_TITULO = "#f0b124"
COLOR_TEXTO = "#000000"

COLUMNAS_EVENTOS = {"Nombre", "Código"}
COLUMNAS_APROBADOS = {"Nombre de Archivo", "Enlace"}
PREFIJO_CHECK = "sel_archivo_"


def validar_columnas(df: pd.DataFrame, requeridas: set[str], nombre_df: str) -> None:
    faltantes = requeridas.difference(df.columns)
    if faltantes:
        faltantes_txt = ", ".join(sorted(faltantes))
        raise ValueError(f"En '{nombre_df}' faltan columnas requeridas: {faltantes_txt}")


@st.cache_data(show_spinner=False)
def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_eventos = pd.read_csv(URL_EVENTOS, dtype=str).fillna("")
    df_aprobados = pd.read_csv(URL_APROBADOS, dtype=str).fillna("")
    validar_columnas(df_eventos, COLUMNAS_EVENTOS, "Eventos")
    validar_columnas(df_aprobados, COLUMNAS_APROBADOS, "Aprobados")
    return df_eventos, df_aprobados


def limpiar_seleccion_archivos() -> None:
    for clave in list(st.session_state.keys()):
        if clave.startswith(PREFIJO_CHECK):
            del st.session_state[clave]


def generar_uid(nombre_archivo: str, enlace: str) -> str:
    huella = hashlib.md5(f"{nombre_archivo}|{enlace}".encode("utf-8")).hexdigest()
    return huella[:12]


def seleccionar_todos(df: pd.DataFrame, marcado: bool) -> None:
    for uid in df["uid"].tolist():
        st.session_state[f"{PREFIJO_CHECK}{uid}"] = marcado


def obtener_seleccion(df: pd.DataFrame) -> pd.DataFrame:
    uids = [
        uid
        for uid in df["uid"].tolist()
        if st.session_state.get(f"{PREFIJO_CHECK}{uid}", False)
    ]
    return df[df["uid"].isin(uids)].copy()


def construir_zip(df: pd.DataFrame) -> tuple[bytes | None, list[str]]:
    if df.empty:
        return None, []

    buffer_zip = io.BytesIO()
    errores = []
    usados = {}

    with zipfile.ZipFile(buffer_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for _, fila in df.iterrows():
            nombre = fila["Nombre de Archivo"]
            enlace = fila["Enlace"]

            try:
                with urllib.request.urlopen(enlace, timeout=30) as resp:
                    contenido = resp.read()
            except Exception:
                errores.append(nombre)
                continue

            base, ext = (nombre.rsplit(".", 1) + [""])[:2] if "." in nombre else (nombre, "")
            contador = usados.get(nombre, 0)
            usados[nombre] = contador + 1
            nombre_zip = nombre if contador == 0 else f"{base}({contador}).{ext}" if ext else f"{base}({contador})"

            zf.writestr(nombre_zip, contenido)

    if buffer_zip.getbuffer().nbytes == 0:
        return None, errores

    return buffer_zip.getvalue(), errores


st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{LOGO_URL}" width="800">
        <h1 style="color:{COLOR_TITULO}; margin-bottom:0;">Validación de Participación</h1>
        <p style="font-size:18px; color:{COLOR_TEXTO}; margin-top:5px;">
            Ingrese su contraseña para buscar y descargar sus certificados.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

try:
    df_eventos, df_aprobados = cargar_datos()
except Exception as e:
    st.error("❌ No se pudo cargar la información. Verifique conectividad y estructura de las hojas.")
    with st.expander("Detalle técnico"):
        st.code(str(e))
    st.stop()

if "resultados_busqueda" not in st.session_state:
    st.session_state["resultados_busqueda"] = pd.DataFrame()
if "zip_bytes" not in st.session_state:
    st.session_state["zip_bytes"] = None
if "zip_nombre" not in st.session_state:
    st.session_state["zip_nombre"] = ""
if "zip_errores" not in st.session_state:
    st.session_state["zip_errores"] = []

password = st.text_input("🔐 Contraseña*", type="password")

if st.button("✅ Buscar certificados"):
    st.session_state["zip_bytes"] = None
    st.session_state["zip_nombre"] = ""
    st.session_state["zip_errores"] = []

    if not password.strip():
        st.warning("⚠️ Ingrese una contraseña para continuar.")
        st.session_state["resultados_busqueda"] = pd.DataFrame()
        limpiar_seleccion_archivos()
    else:
        patron = rf"^[^_]+_{re.escape(password.strip())}(?:\(\d+\))?\.pdf$"
        coincidencias = df_aprobados[
            df_aprobados["Nombre de Archivo"].str.match(patron, na=False, case=False)
        ].copy()

        if coincidencias.empty:
            st.error("❌ No se encontraron certificados para la contraseña ingresada.")
            st.session_state["resultados_busqueda"] = pd.DataFrame()
            limpiar_seleccion_archivos()
        else:
            mapa_eventos = df_eventos.set_index("Código")["Nombre"].to_dict()
            coincidencias["Código Evento"] = coincidencias["Nombre de Archivo"].str.split("_", n=1).str[0]
            coincidencias["Evento"] = coincidencias["Código Evento"].map(mapa_eventos).fillna("Evento no identificado")
            coincidencias["uid"] = coincidencias.apply(
                lambda fila: generar_uid(fila["Nombre de Archivo"], fila["Enlace"]),
                axis=1,
            )
            coincidencias = coincidencias.sort_values(["Evento", "Nombre de Archivo"]).reset_index(drop=True)

            st.session_state["resultados_busqueda"] = coincidencias
            limpiar_seleccion_archivos()
            seleccionar_todos(coincidencias, True)

resultados = st.session_state["resultados_busqueda"]

if not resultados.empty:
    st.success(f"✅ Se encontraron {len(resultados)} certificado(s).")

    resultados_vista = resultados.copy()
    with st.expander("🔎 Filtrar por evento o nombre de archivo (opcional)", expanded=False):
        tipo_filtro = st.radio(
            "Filtrar por",
            options=["Evento", "Nombre de archivo"],
            horizontal=True,
            key="tipo_filtro",
        )

        if tipo_filtro == "Evento":
            opciones_evento = sorted(resultados["Evento"].dropna().unique().tolist())
            evento_sel = st.selectbox(
                "Seleccione un evento",
                options=["(Todos)"] + opciones_evento,
                key="filtro_evento",
            )
            if evento_sel != "(Todos)":
                resultados_vista = resultados[resultados["Evento"] == evento_sel].copy()
        else:
            opciones_archivo = sorted(resultados["Nombre de Archivo"].dropna().unique().tolist())
            archivo_sel = st.selectbox(
                "Seleccione un archivo",
                options=["(Todos)"] + opciones_archivo,
                key="filtro_archivo",
            )
            if archivo_sel != "(Todos)":
                resultados_vista = resultados[resultados["Nombre de Archivo"] == archivo_sel].copy()

    if resultados_vista.empty:
        st.info("No hay resultados con ese filtro.")
    else:
        col1, col2 = st.columns(2)
        if col1.button("Marcar todos (vista)"):
            seleccionar_todos(resultados_vista, True)
            st.rerun()
        if col2.button("Desmarcar todos (vista)"):
            seleccionar_todos(resultados_vista, False)
            st.rerun()

        st.markdown("### Seleccione certificados por evento")

        for evento, grupo in resultados_vista.groupby("Evento", sort=False):
            evento_id = hashlib.md5(evento.encode("utf-8")).hexdigest()[:8]
            with st.container(border=True):
                st.markdown(f"**{evento} ({len(grupo)} certificado(s))**")
                if len(grupo) >= 2:
                    btn1, btn2 = st.columns(2)
                    if btn1.button("Marcar todo", key=f"marcar_{evento_id}"):
                        seleccionar_todos(grupo, True)
                        st.rerun()
                    if btn2.button("Desmarcar todo", key=f"desmarcar_{evento_id}"):
                        seleccionar_todos(grupo, False)
                        st.rerun()

                for _, fila in grupo.iterrows():
                    clave_check = f"{PREFIJO_CHECK}{fila['uid']}"
                    st.checkbox(fila["Nombre de Archivo"], key=clave_check)

    seleccionados = obtener_seleccion(resultados)
    st.caption(f"Seleccionados: {len(seleccionados)}")

    if st.button("🗜️ Preparar ZIP de seleccionados"):
        if seleccionados.empty:
            st.warning("⚠️ Seleccione al menos un certificado.")
        else:
            with st.spinner("Descargando archivos y creando ZIP..."):
                zip_bytes, errores = construir_zip(seleccionados)
            st.session_state["zip_bytes"] = zip_bytes
            st.session_state["zip_errores"] = errores
            st.session_state["zip_nombre"] = f"certificados_{password.strip()}.zip"

            if zip_bytes is None:
                st.error("❌ No se pudo generar el ZIP. Verifique enlaces y vuelva a intentar.")

    if st.session_state["zip_bytes"] is not None:
        st.download_button(
            label="⬇️ Descargar ZIP",
            data=st.session_state["zip_bytes"],
            file_name=st.session_state["zip_nombre"],
            mime="application/zip",
        )

    if st.session_state["zip_errores"]:
        st.warning("⚠️ Algunos archivos no pudieron incluirse en el ZIP:")
        for nombre in st.session_state["zip_errores"]:
            st.markdown(f"- {nombre}")

    with st.expander("Enlaces directos de seleccionados"):
        if seleccionados.empty:
            st.caption("No hay certificados seleccionados.")
        else:
            for _, fila in seleccionados.iterrows():
                st.markdown(f"- [{fila['Evento']} | {fila['Nombre de Archivo']}]({fila['Enlace']})")

st.markdown(
    f"""
    <br>
    <div style="text-align:center; font-size:11px; color:{COLOR_TEXTO};">
        *Los diplomas solo estarán disponibles hasta 1 año después de finalizado el evento, curso o diplomado.
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="text-align:center; margin-top:14px; font-size:14px;">
        ¿No encuentras tus certificados o la información está errada?
        Por favor, diligencia el siguiente
        <a href="{URL_FORM_SOPORTE}" target="_blank">formulario</a>.
    </div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div style="border-top: 1px solid #dcdcda; margin-top: 40px; padding-top: 10px; text-align: center; font-size: 13px; color: {COLOR_TEXTO};">
        Aplicación desarrollada por el <strong>CIEC - Facultad de Ciencias UPTC</strong>
    </div>
""",
    unsafe_allow_html=True,
)
