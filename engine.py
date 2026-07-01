import os
import requests
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN DE LA API
RAPIDAPI_KEY = "3b6eabe8d7e5hchC8f6l8b8efd6f80b1p9c29j5n5r9Y41339e3ed"
RAPIDAPI_HOST = "pdf-to-excel-converter-api1.p.rapidapi.com"

def procesar_pdf(pdf_path, base_dir=None):
    """
    Convierte un PDF a Excel usando la API de RapidAPI.
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # 1. Subir el PDF a la API
    url = f"https://{RAPIDAPI_HOST}/convert"
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY
    }
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {"single_sheet": "true"}
        response = requests.post(url, headers=headers, files=files, data=data)

    # 2. Verificar respuesta
    if response.status_code != 200:
        raise Exception(f"Error en API: {response.status_code} - {response.text}")

    # 3. Guardar el Excel devuelto por la API
    excel_path = os.path.join(base_dir, "resultado_real.xlsx")
    with open(excel_path, "wb") as f:
        f.write(response.content)

    # 4. Preparar resultado
    resultado = {
        "nombre_archivo": os.path.basename(pdf_path),
        "fecha_procesamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "texto_completo": "PDF convertido a Excel exitosamente",
        "excel_generado": excel_path,
        "datos": {
            "nombre": "Cliente",
            "email": "cliente@email.com",
            "habilidades": "Extraído de PDF",
            "perfil": "Datos extraídos automáticamente"
        }
    }
    return resultado

def guardar_en_db(datos, archivo, texto):
    import sqlite3
    conn = sqlite3.connect("cvs.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cvs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, email TEXT, habilidades TEXT,
        fecha_procesamiento TEXT, nombre_archivo TEXT
    )''')
    c.execute('''INSERT INTO cvs (nombre, email, habilidades, fecha_procesamiento, nombre_archivo)
        VALUES (?,?,?,?,?)''', (
        datos.get('nombre',''), datos.get('email',''), datos.get('habilidades',''),
        archivo.get('fecha_procesamiento',''), archivo.get('nombre_archivo','')
    ))
    conn.commit()
    conn.close()