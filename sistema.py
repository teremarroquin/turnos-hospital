import sqlite3

# Clasificacion de urgencias
URGENCIAS = {
    "emergencia": {"nombre": "Emergencia", "tipo": "Prioritaria", "minutos": 40},
    "urgente": {"nombre": "Urgente", "tipo": "Prioritaria", "minutos": 30},
    "leve": {"nombre": "Leve", "tipo": "General", "minutos": 20},
    "rutina": {"nombre": "Rutina", "tipo": "General", "minutos": 15},
}


# Base de datos
def conectar():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn


def consultar(sql, datos=()):
    conn = conectar()
    filas = conn.execute(sql, datos).fetchall()
    conn.close()
    return filas


def ejecutar(sql, datos=()):
    conn = conectar()
    conn.execute(sql, datos)
    conn.commit()
    conn.close()


def inicializar_db():
    ejecutar('''
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            urgencia TEXT NOT NULL,
            tipo_atencion TEXT NOT NULL,
            tiempo_estimado INTEGER NOT NULL,
            estado TEXT DEFAULT 'En espera'
        )
    ''')


# Registrar paciente
def registrar_paciente(nombre, edad, motivo, urgencia):
    datos = URGENCIAS[urgencia]
    ejecutar(
        "INSERT INTO turnos (nombre, edad, motivo, urgencia, tipo_atencion, tiempo_estimado) VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, edad, motivo, datos["nombre"], datos["tipo"], datos["minutos"]),
    )


# Consultar pacientes
def obtener_fila(tipo_atencion):
    return consultar(
        "SELECT * FROM turnos WHERE estado = 'En espera' AND tipo_atencion = ? ORDER BY id",
        (tipo_atencion,),
    )


def obtener_siguiente_paciente():
    pacientes = consultar('''
        SELECT * FROM turnos
        WHERE estado = 'En espera'
        ORDER BY CASE WHEN tipo_atencion = 'Prioritaria' THEN 1 ELSE 2 END, id
        LIMIT 1
    ''')
    if pacientes:
        return pacientes[0]
    return None


def obtener_paciente_en_consulta():
    pacientes = consultar("SELECT * FROM turnos WHERE estado = 'En consulta'")
    if pacientes:
        return pacientes[0]
    return None


def obtener_atendidos():
    return consultar("SELECT * FROM turnos WHERE estado = 'Atendido' ORDER BY id")


# Controlar consultas
def llamar_siguiente_paciente():
    if obtener_paciente_en_consulta():
        return
    siguiente = obtener_siguiente_paciente()
    if siguiente:
        ejecutar("UPDATE turnos SET estado = 'En consulta' WHERE id = ?", (siguiente["id"],))


def finalizar_consulta():
    ejecutar("UPDATE turnos SET estado = 'Atendido' WHERE estado = 'En consulta'")


# Estadisticas
def contar(sql):
    return consultar(sql)[0][0]


def obtener_estadisticas():
    promedio = contar("SELECT AVG(tiempo_estimado) FROM turnos WHERE estado = 'Atendido'")
    if promedio is None:
        promedio = 0
    return {
        "registrados": contar("SELECT COUNT(*) FROM turnos"),
        "en_espera": contar("SELECT COUNT(*) FROM turnos WHERE estado = 'En espera'"),
        "atendidos": contar("SELECT COUNT(*) FROM turnos WHERE estado = 'Atendido'"),
        "prioritarios": contar("SELECT COUNT(*) FROM turnos WHERE estado = 'Atendido' AND tipo_atencion = 'Prioritaria'"),
        "generales": contar("SELECT COUNT(*) FROM turnos WHERE estado = 'Atendido' AND tipo_atencion = 'General'"),
        "promedio": round(promedio, 1),
    }