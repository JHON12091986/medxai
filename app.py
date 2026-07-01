import os, traceback
from flask import Flask, request, send_file

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <h1>Servidor funcionando</h1>
    <form method="post" enctype="multipart/form-data" action="/upload">
        <input type="file" name="pdf" accept=".pdf" required>
        <input type="submit" value="Procesar">
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
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
    return f'''
    ✅ Procesado. <a href='/'>Volver</a><br>
    📄 Excel: <a href='/download/{os.path.basename(resultado["excel_generado"])}'>Descargar</a>
    '''

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(BASE_DIR, filename)
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("No encontrado", 404)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=False)