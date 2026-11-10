from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sistema

class HospitalHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            pacientes = sistema.obtener_pacientes_espera()
            siguiente = sistema.obtener_siguiente_paciente()
            stats = sistema.obtener_estadisticas()
            
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                html = f.read()
            
            # Construir filas de la tabla
            filas_html = ""
            for p in pacientes:
                filas_html += f"<tr><td>#{p[0]}</td><td>{p[1]}</td><td>{p[2]}</td><td>{p[3]}</td><td><strong>{p[4]}</strong></td><td>{p[5]} min</td></tr>"
            
            # Construir info del siguiente paciente
            if siguiente:
                siguiente_html = f"<p><strong>Turno:</strong> #{siguiente[0]}<br><strong>Nombre:</strong> {siguiente[1]}<br><strong>Tipo:</strong> {siguiente[4]}</p>"
            else:
                siguiente_html = "<p>No hay pacientes en espera.</p>"
            
            # Reemplazar variables en el HTML
            html = html.replace('{{tabla_pacientes}}', filas_html)
            html = html.replace('{{siguiente_paciente}}', siguiente_html)
            html = html.replace('{{en_espera}}', str(stats['en_espera']))
            html = html.replace('{{atendidos}}', str(stats['atendidos']))
            html = html.replace('{{prioritarios}}', str(stats['prioritarios']))
            html = html.replace('{{generales}}', str(stats['generales']))
            
            self.wfile.write(html.encode('utf-8'))

        elif self.path == '/static/styles.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('static/styles.css', 'rb') as f:
                self.wfile.write(f.read())

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')
        datos = urllib.parse.parse_qs(body)
        
        if self.path == '/registrar':
            sistema.registrar_paciente(
                datos['nombre'][0],
                int(datos['edad'][0]),
                datos['motivo'][0],
                datos['tipo_atencion'][0],
                int(datos['tiempo_estimado'][0])
            )
        elif self.path == '/atender':
            sistema.atender_siguiente_paciente()
            
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

if __name__ == '__main__':
    sistema.inicializar_db()
    server = HTTPServer(('localhost', 8000), HospitalHandler)
    print("Servidor corriendo en http://localhost:8000")
    server.serve_forever()