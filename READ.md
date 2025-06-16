# 🛒 MercaBot - Asistente Virtual para Supermercado

**MercaBot** es un asistente virtual desarrollado con Streamlit, diseñado para atender de forma amigable y automatizada a los clientes de un supermercado. Utiliza modelos de lenguaje y recuperación de información desde documentos para responder preguntas, registrar clientes y gestionar conversaciones inteligentes.

---

## 🚀 ¿Qué es Streamlit?

[Streamlit](https://streamlit.io/) es un framework de Python de código abierto para crear aplicaciones web interactivas de forma rápida, sencilla y sin necesidad de conocimientos avanzados de desarrollo frontend.

---

## 🧠 ¿Qué hace esta app?

- Registra clientes nuevos con validación de datos.
- Identifica y saluda a clientes frecuentes.
- Responde preguntas frecuentes usando RAG (Recovery-Augmented Generation).
- Utiliza Gemini (Google Generative AI) como motor de respuesta.
- Mantiene historial de conversación por sesión en SQLite.
- Usa Langchain para estructurar prompts y lógica inteligente.

---

## 📁 Estructura del Proyecto

📦 tu-proyecto/
├── main.py                  # Entrada principal de Streamlit  
├── requirements.txt         # Dependencias necesarias  
├── .streamlit/  
│   └── secrets.toml         # Variables de entorno (API keys)  
├── data/                    # Documentos fuente (PDF, DOCX, Excel)  
├── utils/  
│   ├── chatbot.py           # Lógica del chatbot y prompts  
│   ├── db.py                # Conexión y consultas con SQLite  
│   ├── ingestion.py         # Lectura de documentos    
│   ├── models.py            # modelos de pydantic para la extración
│   ├── prompts.py           # prompts implementados
│   └── rag.py               # Recuperacion de informacion
└── README.md                # Este archivo

---

