import sqlite3

# Clasificacion de urgencias
URGENCIAS = {
    "emergencia": {"nombre": "Emergencia", "tipo": "Prioritaria", "minutos": 40},
    "urgente": {"nombre": "Urgente", "tipo": "Prioritaria", "minutos": 30},
    "leve": {"nombre": "Leve", "tipo": "General", "minutos": 20},
    "rutina": {"nombre": "Rutina", "tipo": "General", "minutos": 15},
}


class Hospital:
    def __init__(self):
        self.crear_tabla()

    # Base de datos
    def ejecutar(self, sql, datos=()):
        conexion = sqlite3.connect("hospital.db")
        cursor = conexion.execute(sql, datos)
        conexion.commit()
        ultimo_id = cursor.lastrowid
        conexion.close()
        return ultimo_id

    def consultar(self, sql, datos=()):
        conexion = sqlite3.connect("hospital.db")
        conexion.row_factory = sqlite3.Row
        filas = conexion.execute(sql, datos).fetchall()
        conexion.close()
        return filas

    def crear_tabla(self):
        self.ejecutar("""
            CREATE TABLE IF NOT EXISTS pacientes (
                turno INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                edad INTEGER,
                motivo TEXT,
                urgencia TEXT,
                tipo TEXT,
                tiempo_estimado INTEGER,
                estado TEXT DEFAULT 'espera'
            )
        """)

    # Registrar paciente
    def registrar(self, nombre, edad, motivo, urgencia):
        datos = URGENCIAS[urgencia]
        turno = self.ejecutar(
            "INSERT INTO pacientes (nombre, edad, motivo, urgencia, tipo, tiempo_estimado) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, edad, motivo, datos["nombre"], datos["tipo"], datos["minutos"]),
        )
        return turno

    # Filas de espera (el turno mas chico llego primero)
    def fila(self, tipo):
        return self.consultar(
            "SELECT * FROM pacientes WHERE estado = 'espera' AND tipo = ? ORDER BY turno", (tipo,)
        )

    def atendidos(self):
        return self.consultar("SELECT * FROM pacientes WHERE estado = 'atendido' ORDER BY turno")

    def en_consulta(self):
        pacientes = self.consultar("SELECT * FROM pacientes WHERE estado = 'consulta'")
        if len(pacientes) > 0:
            return pacientes[0]
        return None

    # Llamar al siguiente paciente
    def llamar_siguiente(self):
        siguientes = self.fila("Prioritaria")
        if len(siguientes) == 0:
            siguientes = self.fila("General")
        if len(siguientes) == 0:
            return None
        turno = siguientes[0]["turno"]
        self.ejecutar("UPDATE pacientes SET estado = 'consulta' WHERE turno = ?", (turno,))
        return turno

    # Finalizar consulta
    def finalizar_consulta(self):
        self.ejecutar("UPDATE pacientes SET estado = 'atendido' WHERE estado = 'consulta'")

    # Estadisticas
    def estadisticas(self):
        atendidos = self.atendidos()
        prioritarios = 0
        total_minutos = 0
        for p in atendidos:
            total_minutos += p["tiempo_estimado"]
            if p["tipo"] == "Prioritaria":
                prioritarios += 1

        promedio = 0
        if len(atendidos) > 0:
            promedio = round(total_minutos / len(atendidos), 1)

        return {
            "registrados": len(self.consultar("SELECT turno FROM pacientes")),
            "en_espera": len(self.fila("Prioritaria")) + len(self.fila("General")),
            "atendidos": len(atendidos),
            "prioritarios": prioritarios,
            "generales": len(atendidos) - prioritarios,
            "promedio": promedio,
        }