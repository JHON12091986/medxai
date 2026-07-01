import os
import pandas as pd
from datetime import datetime

def procesar_pdf(pdf_path, base_dir=None):
    if base_dir is None:
        base_dir = os.getcwd()

    # Datos de ejemplo
    datos = {
        "nombre_archivo": os.path.basename(pdf_path),
        "fecha_procesamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "texto_completo": "Procesado sin dependencias externas",
        "excel_generado": "",
        "datos": {
            "nombre": "Cliente de Prueba",
            "email": "cliente@demo.com",
            "habilidades": "Python, Automatización",
            "perfil": "Perfil de prueba"
        }
    }

    excel_path = os.path.join(base_dir, "resultado_minimo.xlsx")
    df = pd.DataFrame({
        "Campo": ["Nombre", "Email", "Habilidades", "Procesado"],
        "Valor": [
            "Cliente de Prueba",
            "cliente@demo.com",
            "Python, Automatización",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
    })
    df.to_excel(excel_path, index=False)
    datos["excel_generado"] = excel_path
    return datos

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