# Validacion de Participacion - Certificados CIEC

Aplicacion en Streamlit para buscar, seleccionar y descargar certificados PDF de eventos del CIEC usando solo la contrasena del usuario.

## Que hace esta app

- Solicita unicamente la `Contrasena`.
- Busca coincidencias en `Nombre de Archivo` con el patron:
  - `CODIGO_contrasena.pdf`
  - `CODIGO_contrasena(1).pdf`
  - `CODIGO_contrasena(2).pdf`
- Agrupa resultados por `Evento`.
- Permite seleccionar certificados por evento con casillas.
- Incluye filtros opcionales por:
  - `Evento`
  - `Nombre de archivo`
- Permite:
  - Marcar/Desmarcar todos en la vista actual
  - Marcar/Desmarcar por evento (solo si ese evento tiene 2 o mas certificados)
- Genera un archivo ZIP con los certificados seleccionados.
- Muestra enlaces directos como respaldo.
- Incluye enlace de soporte para reportar errores de informacion.

## Fuente de datos

La app usa dos hojas publicas de Google Sheets:

1. Eventos
- Columnas requeridas: `Nombre`, `Codigo`
- URL: https://docs.google.com/spreadsheets/d/1jtnIcVBFCRX-lunJk3YCFtxOXMNbsarAemgOnBsvXDY

2. Aprobados
- Columnas requeridas: `Nombre de Archivo`, `Enlace`
- URL: https://docs.google.com/spreadsheets/d/1_Kfc2LDo6kP9e0RgwZQVkRyuQz2_utElTbp5v7aRw-Q

La app valida que estas columnas existan. Si falta alguna, muestra un error claro.

## Flujo de uso

1. Ingresar la contrasena.
2. Hacer clic en `Buscar certificados`.
3. (Opcional) Abrir el filtro y seleccionar evento o archivo.
4. Marcar los certificados a descargar.
5. Hacer clic en `Preparar ZIP de seleccionados`.
6. Descargar con `Descargar ZIP`.

## Soporte al usuario

Si no encuentra sus certificados o hay errores en la informacion, usar:

https://forms.gle/82rmSt65KNHQDfC4A

## Requisitos

El archivo `Requeriments.txt` incluye:

- `streamlit`
- `pandas`

Las librerias `io`, `zipfile`, `urllib`, `re` y `hashlib` son parte de la libreria estandar de Python.

## Ejecucion local

```bash
pip install -r Requeriments.txt
streamlit run App.py
```

## Despliegue en Streamlit Cloud

1. Subir el repositorio a GitHub.
2. Crear una app en Streamlit Cloud.
3. Seleccionar como archivo principal: `App.py`.
4. Verificar que `Requeriments.txt` este en la raiz del proyecto.

## Creditos

Aplicacion desarrollada para el CIEC - Facultad de Ciencias UPTC.
