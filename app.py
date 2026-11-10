from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from sistema import Hospital

hospital = Hospital()
mensaje = ""


# Filas de las tablas
def hacer_filas(pacientes):
    filas = ""
    for p in pacientes:
        filas += "<tr>"
        filas += "<td>" + str(p["turno"]) + "</td>"
        filas += "<td>" + escape(p["nombre"]) + "</td>"
        filas += "<td>" + str(p["edad"]) + "</td>"
        filas += "<td>" + escape(p["motivo"]) + "</td>"
        filas += "<td>" + p["urgencia"] + "</td>"
        filas += "<td>" + p["tipo"] + "</td>"
        filas += "<td>" + str(p["tiempo_estimado"]) + " min</td>"
        filas += "</tr>"
    return filas


# Armar la pagina
def armar_pagina():
    archivo = open("templates/index.html", encoding="utf-8")
    pagina = archivo.read()
    archivo.close()

    actual = hospital.en_consulta()
    if actual:
        texto_consulta = "Turno " + str(actual["turno"]) + " - " + escape(actual["nombre"]) + " (" + escape(actual["motivo"]) + ")"
    else:
        texto_consulta = "El médico está disponible."

    estadisticas = hospital.estadisticas()

    pagina = pagina.replace("{{MENSAJE}}", escape(mensaje))
    pagina = pagina.replace("{{CONSULTA_ACTUAL}}", texto_consulta)
    pagina = pagina.replace("{{FILAS_PRIORITARIA}}", hacer_filas(hospital.fila("Prioritaria")))
    pagina = pagina.replace("{{FILAS_GENERAL}}", hacer_filas(hospital.fila("General")))
    pagina = pagina.replace("{{FILAS_ATENDIDOS}}", hacer_filas(hospital.atendidos()))
    pagina = pagina.replace("{{REGISTRADOS}}", str(estadisticas["registrados"]))
    pagina = pagina.replace("{{EN_ESPERA}}", str(estadisticas["en_espera"]))
    pagina = pagina.replace("{{ATENDIDOS}}", str(estadisticas["atendidos"]))
    pagina = pagina.replace("{{PRIORITARIOS}}", str(estadisticas["prioritarios"]))
    pagina = pagina.replace("{{GENERALES}}", str(estadisticas["generales"]))
    pagina = pagina.replace("{{PROMEDIO}}", str(estadisticas["promedio"]))
    return pagina


# Servidor
class Servidor(BaseHTTPRequestHandler):

    # Mostrar la pagina
    def do_GET(self):
        global mensaje
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        pagina = armar_pagina()
        mensaje = ""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(pagina.encode("utf-8"))

    # Recibir los botones y el formulario
    def do_POST(self):
        global mensaje
        largo = int(self.headers["Content-Length"])
        datos = parse_qs(self.rfile.read(largo).decode("utf-8"), keep_blank_values=True)

        # Registrar paciente
        if self.path == "/registrar":
            nombre = datos["nombre"][0].strip()
            edad = datos["edad"][0]
            motivo = datos["motivo"][0].strip()
            urgencia = datos["urgencia"][0]

            if nombre == "" or motivo == "" or not edad.isdigit():
                mensaje = "Revisa los datos: la edad debe ser un número."
            else:
                turno = hospital.registrar(nombre, int(edad), motivo, urgencia)
                mensaje = nombre + " quedó registrado con el turno " + str(turno) + "."

        # Llamar siguiente paciente
        elif self.path == "/llamar":
            if hospital.en_consulta():
                mensaje = "Primero finaliza la consulta actual."
            else:
                turno = hospital.llamar_siguiente()
                if turno:
                    mensaje = "Pasa el turno " + str(turno) + "."
                else:
                    mensaje = "No hay pacientes en espera."

        # Finalizar consulta
        elif self.path == "/finalizar":
            hospital.finalizar_consulta()
            mensaje = "Consulta finalizada."

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


# Iniciar el sistema
servidor = HTTPServer(("localhost", 8000), Servidor)
print("http://localhost:8000")
servidor.serve_forever()