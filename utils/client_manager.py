# utils/client_manager.py
import re

registered_clients = {}


def is_valid_id(identificacion):
    return re.fullmatch(r'\d{4,11}', identificacion) and identificacion not in registered_clients


def is_valid_name(nombre):
    return re.fullmatch(r"[A-Za-zÀ-ÿñÑ\s]{1,100}", nombre)


def is_valid_phone(telefono):
    return re.fullmatch(r'[63]\d{9}', telefono)


def is_valid_email(email):
    return '@' in email


def register_client(id, nombre, telefono, email):
    registered_clients[id] = {
        "nombre": nombre, "telefono": telefono, "email": email
    }
