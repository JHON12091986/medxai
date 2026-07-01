from flask import Flask, request, send_file
import os
import traceback

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <h1>🐯 Procesador de CVs - DEMO</h1>
    <p>Sube un PDF y te devolveré un Excel de prueba en segundos.</p>
    <form method="post" enctype="multipart/form-data" action="/upload">
        <input type="file" name="pdf" accept=".pdf" required>
        <input type="submit" value="Procesar">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    try:
        from engine import procesar_pdf, guardar_en_db
        if 'pdf' not in request.files:
            return "No file", 400
        file = request.files['pdf']
        if file.filename == '':
            return "No file selected", 400

        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)
        resultado = procesar_pdf(pdf_path, base_dir=BASE_DIR)
        guardar_en_db(resultado["datos"], resultado, resultado["texto_completo"])

        excel_file = resultado.get("excel_generado")
        if not excel_file or not os.path.exists(excel_file):
            return "Error: No se generó el Excel", 500

        return f'''
        ✅ Procesado. <a href='/'>Volver</a><br>
        📄 Excel: <a href='/download/{os.path.basename(excel_file)}'>Descargar</a>
        '''

    except Exception as e:
        return f"<pre>Error: {traceback.format_exc()}</pre>", 500

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "No encontrado", 404

if __name__ == '__main__':
    print("🚀 Servidor DEMO en http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)