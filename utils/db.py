import sqlite3
import os
import json

DB_PATH = os.path.join("chatbot.db")


def init_db():
    """
    Initializes the database by creating necessary tables if they do not exist.

    This function connects to the SQLite database specified by DB_PATH and
    creates two tables: 'clientes' and 'conversaciones'. The 'clientes' table
    stores client information with fields for ID, name, phone, and email. The
    'conversaciones' table stores conversation data with fields for session ID,
    messages, timestamp, and step. Both tables are created only if they do not
    already exist.
    """
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
    """
    Establishes and returns a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database specified by DB_PATH.
    """
        
    return sqlite3.connect(DB_PATH)


def get_client_by_id(identificacion):
    """
    Retrieves a client's details from the database by their ID.

    Args:
        identificacion (int): The ID of the client to retrieve.

    Returns:
        dict or None: A dictionary containing the client's id, nombre, telefono, and correo if found; otherwise, None.
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
    Inserts or updates a client's information in the database based on the provided ID.

    If a client with the given ID already exists, their information is updated.
    Otherwise, a new client record is created.

    Args:
        identificacion (int): The unique identifier for the client.
        nombre (str): The name of the client.
        telefono (str): The phone number of the client.
        correo (str): The email address of the client.
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
    """
    Saves a message to the database associated with a given session ID.

    If a conversation with the specified session ID already exists, the message
    is appended to the existing messages and the step is updated. Otherwise, a
    new conversation record is created with the provided message and step.

    Args:
        sesion_id (str): The unique identifier for the session.
        role (str): The role of the message sender.
        mensaje (str): The content of the message.
        step (int, optional): The step number to associate with the message. Defaults to 0.
    """
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
    Saves a message to the database for a given session ID.

    This function checks if a conversation with the specified session ID
    already exists in the database. If it does, the new message is appended
    to the existing conversation. If not, a new conversation entry is created
    with the message. The message is stored as a JSON object with a role and
    content.

    Args:
        sesion_id (str): The unique identifier for the session.
        role (str): The role associated with the message (e.g., user, system).
        mensaje (str): The content of the message to be saved.
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
    """
    Retrieves messages from the database for a given session ID.

    Args:
        sesion_id (str): The ID of the session to retrieve messages for.

    Returns:
        list: A list of messages for the specified session. Returns an empty list if no messages are found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT mensajes FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return []


def save_or_update_cliente(cliente):
    """
    Inserts or updates a client in the database.
    This function checks if a client with the given ID already exists in the
    database. If it exists, it updates the client's information; otherwise,
    it inserts a new client record.
    Args:
        cliente (dict): A dictionary containing client information with keys 'id', 'nombre', 'telefono', and 'correo'.
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
    """, (cliente['id'], cliente['nombre'], cliente['telefono'], cliente['correo']))
    conn.commit()
    conn.close()


def get_cliente_by_id(identificacion):
    """
    Retrieves a client's information from the database by their ID.
    Args:
        identificacion (str): The ID of the client to retrieve.
    Returns:
        dict or None: A dictionary containing the client's id, nombre, telefono, and correo if found; otherwise, None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, correo FROM clientes WHERE id = ?", (identificacion,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nombre": row[1], "telefono": row[2], "correo": row[3]}
    return None


def get_step(sesion_id):
    """
    Retrieves the current step of a conversation from the database by session ID.
    Args:
        sesion_id (str): The ID of the session to retrieve the step for.
    Returns:
        int: The current step of the conversation. Returns 0 if no step is found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT step FROM conversaciones WHERE sesion_id = ?", (sesion_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0
