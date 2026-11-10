import sqlite3

# Inicializar base de datos
def inicializar_db():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            tipo_atencion TEXT NOT NULL,
            tiempo_estimado INTEGER NOT NULL,
            estado TEXT DEFAULT 'En espera'
        )
    ''')
    conn.commit()
    conn.close()

# Registrar paciente
def registrar_paciente(nombre, edad, motivo, tipo_atencion, tiempo_estimado):
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO turnos (nombre, edad, motivo, tipo_atencion, tiempo_estimado)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, edad, motivo, tipo_atencion, tiempo_estimado))
    conn.commit()
    conn.close()

# Obtener pacientes en espera
def obtener_pacientes_espera():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nombre, edad, motivo, tipo_atencion, tiempo_estimado 
        FROM turnos 
        WHERE estado = 'En espera'
        ORDER BY CASE WHEN tipo_atencion = 'Prioritaria' THEN 1 ELSE 2 END, id ASC
    ''')
    pacientes = cursor.fetchall()
    conn.close()
    return pacientes

# Obtener solo el siguiente paciente
def obtener_siguiente_paciente():
    pacientes = obtener_pacientes_espera()
    return pacientes[0] if pacientes else None

# Atender paciente
def atender_siguiente_paciente():
    paciente = obtener_siguiente_paciente()
    if paciente:
        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE turnos SET estado = 'Atendido' WHERE id = ?", (paciente[0],))
        conn.commit()
        conn.close()
    return paciente

# Estadísticas
def obtener_estadisticas():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM turnos WHERE estado = 'En espera'")
    en_espera = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM turnos WHERE estado = 'Atendido'")
    atendidos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM turnos WHERE tipo_atencion = 'Prioritaria'")
    prioritarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM turnos WHERE tipo_atencion = 'General'")
    generales = cursor.fetchone()[0]
    conn.close()
    return {"en_espera": en_espera, "atendidos": atendidos, "prioritarios": prioritarios, "generales": generales}