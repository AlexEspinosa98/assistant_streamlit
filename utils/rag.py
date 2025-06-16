""" RAG (Retrieval-Augmented Generation) Chain for Google Gemini"""
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from utils.ingestion import read_excel, read_pdf, read_docx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os


def load_documents() -> list:
    """
    Loads and processes documents from specified file paths.

    This function reads content from an Excel, PDF, and DOCX file, splits the text
    into chunks using a recursive character text splitter, and returns a list of
    Document objects containing these chunks.

    Returns:
        list: A list of Document objects, each containing a chunk of text.
    """
    contents = [
        read_excel("data/Horarios.xlsx"),
        read_pdf("data/Suma_Gana.pdf"),
        read_docx("data/Preguntas_frecuentes.docx")
    ]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    for content in contents:
        for chunk in text_splitter.split_text(content):
            docs.append(Document(page_content=chunk))
    return docs


def build_rag_chain():
    """
    Builds a RAG chain using Google Generative AI and FAISS.

    This function constructs a Retrieval-Augmented Generation chain by loading
    documents, generating embeddings using Google Generative AI, and storing them
    in a FAISS vector store. It then initializes a language model and a retriever
    to create a RetrievalQA chain.

    Returns:
        RetrievalQA: A chain object for performing retrieval-augmented generation.
    """
    docs = load_documents()

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    vectorstore = FAISS.from_documents(docs, embeddings)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )

    retriever = vectorstore.as_retriever()
    return RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
