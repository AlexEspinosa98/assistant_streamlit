import sqlite3
import os
import json

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
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversaciones (
            session_id TEXT PRIMARY KEY,
            mensajes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            step INTEGER DEFAULT 0
        )
        """)

        conn.commit()


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_client_by_id(identificacion):
    """
    Obtiene un cliente por su identificación.
    :param identificacion: ID del cliente.
    :return: Diccionario con los datos del cliente o None si no existe.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, correo FROM clientes WHERE id = ?", (identificacion,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nombre": row[1], "telefono": row[2], "correo": row[3]}
    return None


def save_client_by_id(identificacion, nombre, telefono, correo):
    """
    Guarda o actualiza un cliente en la base de datos.
    :param identificacion: ID del cliente.
    :param nombre: Nombre del cliente.
    :param telefono: Teléfono del cliente.
    :param correo: Correo electrónico del cliente.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO clientes (id, nombre, telefono, correo)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        nombre = excluded.nombre,
        telefono = excluded.telefono,
        correo = excluded.correo
    """, (identificacion, nombre, telefono, correo))
    conn.commit()
    conn.close()


def save_message_with_step(sesion_id, role, mensaje, step=0):
    conn = get_connection()
    cursor = conn.cursor()

    # Ver si ya existe una conversación con ese sesion_id
    cursor.execute("SELECT mensajes FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
    row = cursor.fetchone()

    new_message = {"role": role, "content": mensaje}

    if row:
        mensajes = json.loads(row[0])
        mensajes.append(new_message)
        cursor.execute("UPDATE conversaciones SET mensajes = ?, step = ? WHERE sesion_id = ?", (json.dumps(mensajes), step, sesion_id))
    else:
        mensajes = [new_message]
        cursor.execute("INSERT INTO conversaciones (sesion_id, mensajes, step) VALUES (?, ?, ?)", (sesion_id, json.dumps(mensajes), step))

    conn.commit()
    conn.close()


def save_message(sesion_id, role, mensaje):
    """
    Guarda un mensaje en la base de datos asociado a una sesión.
    Si la sesión ya existe, actualiza los mensajes; si no, crea una nueva entrada.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si ya existe una conversación con ese sesion_id
    cursor.execute("SELECT mensajes FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
    row = cursor.fetchone()

    new_message = {"role": role, "content": mensaje}

    if row:
        mensajes = json.loads(row[0])
        mensajes.append(new_message)
        cursor.execute("UPDATE conversaciones SET mensajes = ? WHERE sesion_id = ?", (json.dumps(mensajes), sesion_id))
    else:
        mensajes = [new_message]
        cursor.execute("INSERT INTO conversaciones (sesion_id, mensajes, step) VALUES (?, ?, ?)", (sesion_id, json.dumps(mensajes), 0))

    conn.commit()
    conn.close()


def get_messages(sesion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mensajes FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return []


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


def get_step(sesion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT step FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0

