# 🎫 Generador para Eventos – Validación de Certificados

Aplicación en Streamlit para la validación y descarga de certificados de participación en eventos organizados por el CIEC.

---

## 🚀 ¿Qué hace esta app?

- Muestra una lista desplegable con los eventos disponibles.
- Permite ingresar una contraseña individual.
- Valida si el certificado PDF correspondiente (`{Código}_{Contraseña}.pdf`) existe.
- Si existe, permite descargarlo.
- Si no existe, muestra un mensaje de error.

---

## 📁 Estructura del sistema

El sistema se basa en dos hojas de cálculo de Google:

### 1. **Lista de eventos**
Contiene:
- `Nombre del Curso o Diplomado`
- `Código`
- `Fecha`

📄 [Ver hoja de eventos](https://docs.google.com/spreadsheets/d/1jtnIcVBFCRX-lunJk3YCFtxOXMNbsarAemgOnBsvXDY)

---

### 2. **Aprobados**
Contiene:
- `Nombre de Archivo` → Ej: `E-01_123456789.pdf`
- `Enlace` → URL pública del certificado PDF

📄 [Ver hoja de aprobados](https://docs.google.com/spreadsheets/d/1_Kfc2LDo6kP9e0RgwZQVkRyuQz2_utElTbp5v7aRw-Q)

---

## 🖼️ Diseño institucional

- Logo oficial del CIEC en el encabezado.
- Colores institucionales: dorado y negro.
- Botón de descarga estilizado.

---

## 📦 Requisitos

Incluye un archivo `requirements.txt` con:

streamlit pandas
---

## ▶️ Despliegue en Streamlit Cloud

1. Clona o sube este repositorio a tu cuenta.
2. Ve a [https://streamlit.io/cloud](https://streamlit.io/cloud) y conecta tu repositorio.
3. Establece como archivo principal: `app_eventos.py`

---

## 🙌 Créditos

Aplicación desarrollada para el **CIEC – Facultad de Ciencias de la Universidad Pedagógica y Tecnológica de Colombia**, como sistema automatizado de validación de participación en eventos y actividades académicas.

---
