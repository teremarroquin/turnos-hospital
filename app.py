from html import escape
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import sistema


# Partes de la pagina
def hacer_filas(pacientes):
    if not pacientes:
        return '<tr><td colspan="7">Sin pacientes</td></tr>'

    filas = ""
    for p in pacientes:
        filas += "<tr>"
        filas += "<td>#" + str(p["id"]) + "</td>"
        filas += "<td>" + escape(p["nombre"]) + "</td>"
        filas += "<td>" + str(p["edad"]) + "</td>"
        filas += "<td>" + escape(p["motivo"]) + "</td>"
        filas += "<td>" + p["urgencia"] + "</td>"
        filas += "<td>" + p["tipo_atencion"] + "</td>"
        filas += "<td>" + str(p["tiempo_estimado"]) + " min</td>"
        filas += "</tr>"
    return filas


def hacer_cuadro(paciente, texto_vacio):
    if not paciente:
        return "<p>" + texto_vacio + "</p>"

    texto = "<p>"
    texto += "<strong>Turno:</strong> #" + str(paciente["id"]) + "<br>"
    texto += "<strong>Nombre:</strong> " + escape(paciente["nombre"]) + "<br>"
    texto += "<strong>Urgencia:</strong> " + paciente["urgencia"] + " (" + paciente["tipo_atencion"] + ")"
    texto += "</p>"
    return texto


def armar_pagina():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    stats = sistema.obtener_estadisticas()

    html = html.replace("{{en_consulta}}", hacer_cuadro(sistema.obtener_paciente_en_consulta(), "El médico está disponible."))
    html = html.replace("{{siguiente}}", hacer_cuadro(sistema.obtener_siguiente_paciente(), "No hay pacientes en espera."))
    html = html.replace("{{fila_prioritaria}}", hacer_filas(sistema.obtener_fila("Prioritaria")))
    html = html.replace("{{fila_general}}", hacer_filas(sistema.obtener_fila("General")))
    html = html.replace("{{tabla_atendidos}}", hacer_filas(sistema.obtener_atendidos()))
    html = html.replace("{{registrados}}", str(stats["registrados"]))
    html = html.replace("{{en_espera}}", str(stats["en_espera"]))
    html = html.replace("{{atendidos}}", str(stats["atendidos"]))
    html = html.replace("{{prioritarios}}", str(stats["prioritarios"]))
    html = html.replace("{{generales}}", str(stats["generales"]))
    html = html.replace("{{promedio}}", str(stats["promedio"]))
    return html


# Servidor
class HospitalHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.responder(200, "text/html; charset=utf-8", armar_pagina().encode("utf-8"))
        elif self.path == "/static/styles.css":
            with open("static/styles.css", "rb") as f:
                self.responder(200, "text/css", f.read())
        else:
            self.responder(404, "text/plain", b"No encontrado")

    def do_POST(self):
        largo = int(self.headers["Content-Length"])
        cuerpo = self.rfile.read(largo).decode("utf-8")
        datos = parse_qs(cuerpo, keep_blank_values=True)

        if self.path == "/registrar":
            nombre = datos.get("nombre", [""])[0].strip()
            edad = datos.get("edad", [""])[0].strip()
            motivo = datos.get("motivo", [""])[0].strip()
            urgencia = datos.get("urgencia", [""])[0]

            if nombre and motivo and edad.isdigit() and int(edad) <= 120 and urgencia in sistema.URGENCIAS:
                sistema.registrar_paciente(nombre, int(edad), motivo, urgencia)
        elif self.path == "/llamar":
            sistema.llamar_siguiente_paciente()
        elif self.path == "/finalizar":
            sistema.finalizar_consulta()

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def responder(self, codigo, tipo, contenido):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.end_headers()
        self.wfile.write(contenido)


# Iniciar el sistema
if __name__ == "__main__":
    sistema.inicializar_db()
    servidor = HTTPServer(("localhost", 8000), HospitalHandler)
    print("Servidor corriendo en http://localhost:8000")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido.")