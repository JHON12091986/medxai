import os
import re
import sqlite3
from datetime import datetime

DB_NAME = "cvs.db"

def extraer_campos(texto):
    campos = {}
    lineas = [l for l in texto.split('\n') if l.strip() and not l.startswith('---')]
    campos['nombre'] = lineas[0].strip() if lineas else "No detectado"
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', texto)
    campos['email'] = email_match.group(0) if email_match else ""
    linkedin_match = re.search(r'linkedin\.com/in/[a-zA-Z0-9-]+', texto, re.IGNORECASE)
    campos['linkedin'] = linkedin_match.group(0) if linkedin_match else ""
    github_match = re.search(r'github\.com/[a-zA-Z0-9-]+', texto, re.IGNORECASE)
    campos['github'] = github_match.group(0) if github_match else ""
    web_match = re.search(r'https?://[a-zA-Z0-9.-]+\.netlify\.app', texto, re.IGNORECASE)
    campos['portafolio'] = web_match.group(0) if web_match else ""
    perfil_match = re.search(r'(Ingeniero Informático.*?)(?=Portafolio|Contacto|LinkedIn)', texto, re.DOTALL)
    campos['perfil'] = re.sub(r'\s+', ' ', perfil_match.group(1).strip()) if perfil_match else ""
    skills_keywords = ['Python', 'Java', 'C++', 'SQL', 'Oracle', 'Windows', 'Excel', 'PowerPoint',
                       'Git', 'GitHub', 'VS Code', 'IA', 'Inteligencia Artificial', 'Automatización',
                       'Soporte TI', 'Infraestructura', 'Redes', 'Ciberseguridad', 'Linux', 'Docker']
    skills_found = [s for s in skills_keywords if re.search(r'\b' + re.escape(s) + r'\b', texto, re.IGNORECASE)]
    campos['habilidades'] = ', '.join(skills_found)
    formacion_match = re.search(r'(Universidad.*?)(?=COLEGIATURA|COMPETENCIAS|Habilidades)', texto, re.DOTALL | re.IGNORECASE)
    campos['formacion'] = re.sub(r'\s+', ' ', formacion_match.group(1).strip())[:500] if formacion_match else ""
    exp_match = re.search(r'(Experiencia|Trayectoria).*?(?=Formación|Competencias|Habilidades)', texto, re.DOTALL | re.IGNORECASE)
    campos['experiencia'] = re.sub(r'\s+', ' ', exp_match.group(0).strip())[:500] if exp_match else ""
    tel_match = re.search(r'\b\d{9}\b', texto)
    campos['telefono'] = tel_match.group(0) if tel_match else ""
    return campos

def extraer_texto_local(pdf_path):
    import pdfplumber
    texto = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    texto += text + "\n"
        return texto
    except Exception as e:
        print(f"Error local: {e}")
        return None

def extraer_con_api(pdf_path):
    import requests
    import pandas as pd
    RAPIDAPI_KEY = "3b6eabe8d7e5hchC8f6l8b8efd6f80b1p9c29j5n5r9Y41339e3ed"
    RAPIDAPI_HOST = "pdf-to-excel-converter-api1.p.rapidapi.com"
    try:
        url = f"https://{RAPIDAPI_HOST}/convert"
        headers = {"X-RapidAPI-Host": RAPIDAPI_HOST, "X-RapidAPI-Key": RAPIDAPI_KEY}
        with open(pdf_path, "rb") as f:
            files = {"file": f}
            data = {"single_sheet": "true"}
            response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 200:
            temp_xlsx = pdf_path.replace('.pdf', '_api.xlsx')
            with open(temp_xlsx, 'wb') as f:
                f.write(response.content)
            df = pd.read_excel(temp_xlsx, header=None)
            texto = df.to_string(index=False, header=False)
            os.remove(temp_xlsx)
            return texto
        return None
    except Exception as e:
        print(f"API error: {e}")
        return None

def generar_dashboard(campos, output_path):
    habilidades = campos.get('habilidades', '').split(', ')
    habilidades = [h for h in habilidades if h]
    if not habilidades:
        habilidades = ["No detectadas"]
    html = f"""
    <html><head><meta charset="UTF-8"><title>Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head><body>
    <h1>📊 Habilidades</h1>
    <p><strong>Nombre:</strong> {campos.get('nombre', '')}</p>
    <p><strong>Email:</strong> {campos.get('email', '')}</p>
    <div style="width:600px;height:400px;"><canvas id="skillsChart"></canvas></div>
    <script>
    const ctx = document.getElementById('skillsChart').getContext('2d');
    new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: {habilidades},
            datasets: [{{
                label: 'Competencias',
                data: {[1]*len(habilidades)},
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }}]
        }},
        options: {{ scales: {{ y: {{ beginAtZero: true, max: 1, ticks: {{ stepSize: 1 }} }} }}, plugins: {{ legend: {{ display: false }} }} }}
    }});
    </script>
    </body></html>
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def procesar_pdf(pdf_path, base_dir=None):
    """
    VERSIÓN DE PRUEBA: Siempre devuelve un Excel de prueba.
    """
    if base_dir is None:
        base_dir = os.getcwd()
    resultado = {
        "nombre_archivo": os.path.basename(pdf_path),
        "fecha_procesamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "texto_completo": "Texto de prueba",
        "excel_generado": "",
        "dashboard_html": "",
        "datos": {
            "nombre": "Empresa de Prueba",
            "email": "prueba@empresa.com",
            "habilidades": "Python, Automatización",
            "perfil": "Perfil de prueba"
        }
    }
    try:
        import pandas as pd
        excel_path = os.path.join(base_dir, "resultado_prueba.xlsx")
        df = pd.DataFrame({"Dato": ["Prueba"]})
        df.to_excel(excel_path, index=False)
        resultado["excel_generado"] = excel_path
        print(f"✅ Excel guardado en: {excel_path}")
    except Exception as e:
        print(f"ERROR al generar Excel: {e}")
        resultado["excel_generado"] = ""
    return resultado

def guardar_en_db(datos, archivo, texto):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cvs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, email TEXT, linkedin TEXT, github TEXT,
        portafolio TEXT, perfil TEXT, habilidades TEXT,
        formacion TEXT, experiencia TEXT, telefono TEXT,
        fecha_procesamiento TEXT,
        nombre_archivo TEXT, ruta_archivo TEXT, num_paginas INTEGER,
        texto_completo TEXT
    )''')
    c.execute('''INSERT INTO cvs (
        nombre, email, linkedin, github, portafolio,
        perfil, habilidades, formacion, experiencia, telefono,
        fecha_procesamiento, nombre_archivo, ruta_archivo, num_paginas,
        texto_completo
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        datos.get('nombre',''), datos.get('email',''), datos.get('linkedin',''),
        datos.get('github',''), datos.get('portafolio',''), datos.get('perfil',''),
        datos.get('habilidades',''), datos.get('formacion',''), datos.get('experiencia',''),
        datos.get('telefono',''), archivo.get('fecha_procesamiento',''),
        archivo.get('nombre_archivo',''), archivo.get('ruta_archivo',''),
        archivo.get('num_paginas',0), texto
    ))
    conn.commit()
    conn.close()