import streamlit as st
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

# ========================
# 1️⃣ CONFIGURACIÓN INICIAL
# ========================
st.set_page_config(page_title="🤖 Chat con tu PDF (Gemini + Mistral + FAISS)", layout="wide")

st.title("📘 Chat con tu PDF usando **Gemini + Mistral Embeddings + FAISS**")
st.caption("Sube un PDF, analiza su contenido y haz preguntas contextualizadas.")

# 🔑 Pega aquí directamente tus claves API
GOOGLE_API_KEY = "AIzaSyCTkBuFORIgSBt6COrK9fAw4Vx2dcI0RGE"  # <-- reemplaza con tu API key real

if not GOOGLE_API_KEY:
    st.error("❌ Debes configurar tu API key de Google Gemini en el código.")
    st.stop()


# ========================
# 2️⃣ FUNCIÓN: LECTURA DEL PDF
# ========================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# ========================
# 3️⃣ SUBIR ARCHIVO PDF
# ========================
uploaded_file = st.file_uploader("📂 Sube tu archivo PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("📄 Leyendo y procesando el documento..."):
        pdf_text = read_pdf(uploaded_file)

        # Dividir el texto en fragmentos
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        docs = splitter.create_documents([pdf_text])

        # ========================
        # 4️⃣ VECTORIZAR CON MISTRAL (Hugging Face)
        # ========================
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Crear vectorstore con FAISS
        vectorstore = FAISS.from_documents(docs, embeddings)

        st.session_state.vectorstore = vectorstore

    st.success("✅ Documento vectorizado correctamente con embeddings tipo Mistral (Hugging Face).")


# ========================
# 5️⃣ CONFIGURAR GEMINI (LLM)
# ========================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2,
)


# ========================
# 6️⃣ PROMPT DINÁMICO
# ========================
prompt_usuario = st.text_area(
    "✍️ Escribe un prompt personalizado (opcional)",
    value="Eres un asistente experto en análisis de documentos. Usa el contenido del PDF para responder con precisión.",
)


# ========================
# 7️⃣ INTERFAZ DE CHAT
# ========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial del chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada del usuario
if question := st.chat_input("💬 Escribe tu pregunta sobre el documento..."):
    if "vectorstore" not in st.session_state:
        st.warning("⚠️ Primero sube un PDF para analizar.")
    else:
        # Mostrar mensaje del usuario
        st.chat_message("user").markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        # Recuperador FAISS
        retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 3})

        # Crear cadena de recuperación con Gemini
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
        )

        # Combinar el prompt del usuario con la pregunta
        full_prompt = f"{prompt_usuario}\n\nPregunta: {question}"

        with st.spinner("🤖 Analizando con Gemini y Mistral embeddings..."):
            result = qa_chain.run(full_prompt)

        # Mostrar respuesta
        st.chat_message("assistant").markdown(result)
        st.session_state.messages.append({"role": "assistant", "content": result})
