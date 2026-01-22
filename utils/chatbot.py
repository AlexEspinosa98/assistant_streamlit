# utils/chatbot.py
import os
from google import genai
from utils.ingestion import read_excel, read_pdf, read_docx
from utils.models import ResponseModel, InformationModel, IntentUser
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.prompts import prompt_identify, prompt_greeting, prompt_information, prompt_rag
from utils.db import get_client_by_id, save_client_by_id


os.environ["GEMINI_API_KEY"] = "AIzaSyCh1DJvBclnSumrE7-Yy5bQ03kA3JRIOSI"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    client=client,
)


def get_response(message_history: list, context: str, step: int, session_id: str, rag_chain=None):
    """
    Generates a response for the user based on the message history, context, and current step.

    Args:
        message_history (list): A list of dictionaries containing the conversation history.
        context (str): The current user input or context.
        step (int): The current step in the conversation flow.
        session_id (str): The unique identifier for the session.
        rag_chain (optional): An optional RAG chain for retrieving additional context.

    Returns:
        dict: A dictionary containing the response message and the next step in the conversation.
    """
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
    if rag_chain:
        information_response = rag_chain.run(context)
    system_prompt = prompt_rag(information_response, context)
    structured_llm = llm.with_structured_output(ResponseModel)
    response = structured_llm.invoke(
        [
            ("system", system_prompt),
            ("human", context),
        ]
    )
    return {"response": response.response.strip(), "step": 1}


def get_context_user(user_input: str, last_question_assistant: str):
    """
    Identifies the user's intent based on their input and the last question from the assistant.
    Args:
        user_input (str): The user's input message.
        last_question_assistant (str): The last question asked by the assistant.
    Returns:
        IntentUser: An instance of IntentUser containing the identified intent.
    """
    structured_llm = llm.with_structured_output(IntentUser)
    response = structured_llm.invoke(
        [
            ("system", prompt_identify(last_question_assistant)),
            ("human", user_input),
        ]
    )
    return response
