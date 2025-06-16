# utils/chatbot.py
import os
from google import genai
from utils.ingestion import read_excel, read_pdf, read_docx
import json
from utils.models import ResponseModel, InformationModel, IntentUser
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.prompts import prompt_identify, prompt_greeting, prompt_information
from utils.db import get_client_by_id, save_client_by_id

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Define the desired structure


def build_context():
    docs = []
    docs.append(read_excel("data/Horarios.xlsx"))
    docs.append(read_pdf("data/Suma_Gana.pdf"))
    docs.append(read_docx("data/Preguntas_frecuentes.docx"))
    return "\n".join(docs)


def get_response(message_history, context, step, session_id):

    intent_user = get_context_user(context, message_history[-2]["content"] if len(message_history) > 1 else "")
    if intent_user.greeting:
        system_prompt = prompt_greeting,
        structured_llm = llm.with_structured_output(ResponseModel)
        response = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", context),
            ]
        )
        return {"response": response.response.strip(), "step": 1}
    elif intent_user.data_personal or step==2:
        system_prompt = prompt_information(message_history)
        structured_llm = llm.with_structured_output(InformationModel)
        response = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", context),
            ]
        )
        # save or update client information in the database
        if not response.is_new and response.identificacion:
            
            client_data = get_client_by_id(response.identificacion)
            if client_data:
                message_response = f"¡Hola {client_data['nombre']}! 😊 tu informacion ha sido confirmada, en que puedo ayudarte?"
                return {
                    "response": message_response,
                    "step": 0,
                }
            else:
                message_response = f"¡Hola! 😊 Tu identificación no se encuentra en nuestros registros. Por favor, verifica tu ID o proporciónanos tus datos para registrarte."
                return {
                    "response": message_response,
                    "step": 2,
                }
        if response.identificacion:
            save_client_by_id(
                response.identificacion,
                response.nombre,
                response.telefono,
                response.correo,
            )
        if response.is_complete:
            return {
                "response": response.response.strip(),
                "step": 0,
            }
        return {"response": response.response.strip(), "step": 2}
    if intent_user.ask_for_info:
        system_prompt = prompt_identify(message_history[-2]["content"] if len(message_history) > 1 else "")
        structured_llm = llm.with_structured_output(ResponseModel)
        response = structured_llm.invoke(
            [
                ("system", system_prompt),
                ("human", context),
            ]
        )
        return {"response": response.response.strip(), "step": 1}
    system_prompt = f"""
Eres un asistente virtual llamado **Mercabot**, diseñado para atender clientes de un supermercado.

Tu objetivo es recopilar los siguientes datos del cliente, uno por uno y de forma amable pero clara:

- Identificación: debe tener entre 4 y 11 dígitos. No debe repetirse.
- Nombre completo: solo letras, puede contener tildes o ñ.
- Teléfono: exactamente 10 dígitos, debe comenzar con 3 o 6.
- Correo electrónico: debe contener @ y un dominio válido.

### Reglas estrictas:

1. NO inventes datos si no se han mencionado.
2. NO uses emojis, lenguaje informal, técnico o de programación.
3. Si el cliente ya ha dado un dato válido, no vuelvas a pedirlo.
4. Si aún falta información, **no respondas preguntas del cliente**. Primero completa los datos.
5. Una vez se tenga toda la información, puedes responder preguntas frecuentes usando el contexto adicional que se te dará más adelante.

A continuación se encuentra el historial de conversación hasta ahora. Usa esto para razonar:

{message_history}
"""

    # response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=system_prompt)
    messages = [
        ("system", system_prompt),
        ("human", context),
    ]
    llm
    response = llm.invoke(
        messages
    )
    structured_llm = llm.with_structured_output(ResponseModel)
    response = structured_llm.invoke(
        messages
    )
    # if response in format only use last message ```json\n[\n    {\n        "role": "user",\n        "content": "23123123"\n    },\n    {\n        "role": "model",\n        "content": "¡Perfecto! Gracias. 😊 He encontrado tu historial. \\n\\nPara verificar que eres tú, ¿podrías confirmarme tu nombre completo, por favor? (Solo letras y tildes)"\n    }\n]\n```\n'
    if response.response.strip().startswith("[") and response.response.strip().endswith("]"):
        messages = json.loads(response.response.replace("'",'"').strip())
        response_user = messages[-1]["content"]
    else:
        response_user = response.response.strip()
    return {"response": response_user, "step": 2 if intent_user.data_personal else 1}


def get_context_user(user_input, last_question_assistant):
    """
    Extrae el contexto del usuario a partir de su entrada.
    """
    structured_llm = llm.with_structured_output(IntentUser)
    response = structured_llm.invoke(
        [
            ("system", prompt_identify(last_question_assistant)),
            ("human", user_input),
        ]
    )
    return response
