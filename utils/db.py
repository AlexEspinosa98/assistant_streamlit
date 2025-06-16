import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chatbot.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id TEXT PRIMARY KEY,
            nombre TEXT,
            telefono TEXT,
            correo TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sesion_id TEXT,
            rol TEXT CHECK(rol IN ('user', 'model')),
            mensaje TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def get_connection():
    return sqlite3.connect(DB_PATH)

def save_message(sesion_id, role, mensaje):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversaciones (sesion_id, rol, mensaje) VALUES (?, ?, ?)",
        (sesion_id, role, mensaje)
    )
    conn.commit()
    conn.close()

def get_messages(sesion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT rol, mensaje FROM conversaciones WHERE sesion_id = ? ORDER BY timestamp",
        (sesion_id,)
    )
    results = cursor.fetchall()
    conn.close()
    return [{"role": r, "content": m} for r, m in results]

def save_or_update_cliente(cliente):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO clientes (id, nombre, telefono, correo)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        nombre = excluded.nombre,
        telefono = excluded.telefono,
        correo = excluded.correo
    """, (cliente['id'], cliente['nombre'], cliente['telefono'], cliente['correo']))
    conn.commit()
    conn.close()

def get_cliente_by_id(identificacion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, correo FROM clientes WHERE id = ?", (identificacion,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nombre": row[1], "telefono": row[2], "correo": row[3]}
    return None
