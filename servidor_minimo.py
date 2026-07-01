import http.server
import socketserver

PORT = 5000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor mínimo corriendo en http://127.0.0.1:{PORT}")
    httpd.serve_forever()