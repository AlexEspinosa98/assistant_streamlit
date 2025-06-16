# utils/chatbot.py
import os
from google import genai
from utils.ingestion import read_excel, read_pdf, read_docx

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def build_context():
    docs = []
    docs.append(read_excel("data/Horarios.xlsx"))
    docs.append(read_pdf("data/Suma_Gana.pdf"))
    docs.append(read_docx("data/Preguntas_frecuentes.docx"))
    return "\n".join(docs)

def get_response(message_history, context):

    system_prompt = f"""
Eres un asistente virtual para un supermercado. Tu tarea es interactuar con el cliente de manera natural y pedirle los siguientes datos si no los ha dado aún: 

historial del cliente, nombre, teléfono y correo electrónico. Asegúrate de validar los datos ingresados:
{message_history}

- Identificación (4 a 11 dígitos, única).
- Nombre completo (solo letras y tildes).
- Teléfono (exactamente 10 dígitos, inicia en 3 o 6).
- Correo electrónico (debe contener @).

Primero, identifica si es cliente nuevo o frecuente. Si es nuevo, solicita estos datos uno por uno de manera amable. Si es frecuente, pídele la identificación y da la bienvenida.

"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=system_prompt)
    return response.text.strip()  # Elimina espacios en blanco al inicio y final
