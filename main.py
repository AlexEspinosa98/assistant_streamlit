import streamlit as st
import uuid
from utils.db import init_db, save_message, get_messages, save_message_with_step, get_step
from utils.chatbot import build_context, get_response

st.set_page_config(page_title="Asistente Virtual")
st.title("🛒 Chatbot Supermercado")

# Inicializar la base de datos SQLite
init_db()

# Generar una nueva sesión por usuario si no existe
if "sesion_id" not in st.session_state:
    st.session_state.sesion_id = str(uuid.uuid4())
    # st.session_state.context = build_context()
    st.session_state.history = get_messages(st.session_state.sesion_id)
    st.session_state.messages = st.session_state.history.copy()


# Mostrar el historial completo en pantalla
def show_chat():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# Mostrar historial al cargar
show_chat()

# Entrada de usuario
user_input = st.chat_input("Escribe tu mensaje aquí...")
if user_input:
    # Guardar mensaje del usuario
    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_message(st.session_state.sesion_id, "user", user_input)

    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_input)

    # Obtener respuesta de Gemini con contexto y historial
    step = get_step(st.session_state.sesion_id)
    response = get_response(st.session_state.history, user_input, step, st.session_state.sesion_id)

    # Guardar respuesta del modelo
    st.session_state.history.append({"role": "model", "content": response["response"]})
    st.session_state.messages.append({"role": "model", "content": response["response"]})
    save_message_with_step(st.session_state.sesion_id, "model", response["response"], step=response["step"])

    # Mostrar respuesta en la interfaz
    with st.chat_message("model"):
        st.markdown(response["response"])