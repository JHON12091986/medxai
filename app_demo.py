import os
import sys
import traceback
from flask import Flask, request, render_template_string, send_file

# ===== CONFIGURACIÓN =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Procesador de CVs</title>
<style>
body { font-family: Arial; padding: 20px; background: #f0f4f8; }
.upload { border: 2px dashed #4A90D9; padding: 30px; text-align: center; background: white; border-radius: 10px; max-width: 600px; margin: auto; }
.upload input { margin: 10px; }
.upload input[type="submit"] { background: #4A90D9; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
table { border-collapse: collapse; width: 100%; margin-top: 20px; background: white; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background: #4A90D9; color: white; }
h1 { color: #2C3E50; text-align: center; }
</style>
</head>
<body>
<h1>🐯 Procesador de CVs</h1>
<div class="upload">
    <h3>Sube un PDF para procesar</h3>
    <form method="post" enctype="multipart/form-data" action="/upload">
        <input type="file" name="pdf" accept=".pdf" required>
        <input type="submit" value="Procesar">
    </form>
</div>
<div>
    <h3>📊 CVs procesados</h3>
    <table>
        <tr><th>Nombre</th><th>Email</th><th>Habilidades</th><th>Fecha</th></tr>
        {% for row in data %}
        <tr><td>{{ row.nombre }}</td><td>{{ row.email }}</td><td>{{ row.habilidades[:50] }}</td><td>{{ row.fecha_procesamiento }}</td></tr>
        {% endfor %}
    </table>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    import sqlite3
    import pandas as pd
    db_path = os.path.join(BASE_DIR, "cvs.db")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT nombre, email, habilidades, fecha_procesamiento FROM cvs ORDER BY id DESC", conn)
        data = df.to_dict('records')
    except:
        data = []
    conn.close()
    return render_template_string(HTML, data=data)

@app.route('/upload', methods=['POST'])
def upload():
    # --- CAPTURA GLOBAL DE ERRORES ---
    try:
        # 1. Importar dentro de la función
        from cv_engine import procesar_pdf, guardar_en_db

        # 2. Validar archivo
        if 'pdf' not in request.files:
            return "No file", 400
        file = request.files['pdf']
        if file.filename == '':
            return "No file selected", 400

        # 3. Guardar PDF
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        # 4. Procesar
        resultado = procesar_pdf(pdf_path, base_dir=BASE_DIR)

        # 5. Guardar en DB
        if resultado["datos"]:
            guardar_en_db(resultado["datos"], resultado, resultado["texto_completo"])

        # 6. Verificar Excel
        excel_file = resultado.get("excel_generado", "")
        if not excel_file or not os.path.exists(excel_file):
            return "Error: No se generó el Excel.", 500

        # 7. Respuesta exitosa
        dashboard_file = resultado.get("dashboard_html", "")
        if dashboard_file and not os.path.exists(dashboard_file):
            dashboard_file = ""

        return f"""
        ✅ Procesado. <a href='/'>Volver</a><br>
        📄 Excel: <a href='/download/{os.path.basename(excel_file)}'>Descargar</a><br>
        📊 Dashboard: <a href='/download/{os.path.basename(dashboard_file) if dashboard_file else ""}'>Descargar</a>
        """

    except Exception as e:
        # --- Captura CUALQUIER error y lo muestra en el navegador ---
        error_detalle = traceback.format_exc()
        return f"""
        <h2>❌ Error interno</h2>
        <pre style="background:#f4f4f4;padding:15px;border:1px solid #ccc;overflow:auto;">
        {error_detalle}
        </pre>
        <p><a href='/'>Volver al inicio</a></p>
        """, 500

@app.route('/download/<filename>')
def download(filename):
    posibles_rutas = [
        os.path.join(BASE_DIR, filename),
        os.path.join(UPLOAD_FOLDER, filename)
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return send_file(ruta, as_attachment=True)
    return "Archivo no encontrado", 404

if __name__ == '__main__':
    print("🚀 Servidor DEMO en http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080, debug=True)