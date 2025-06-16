import pandas as pd
import fitz  # PyMuPDF
import docx


def read_excel(path):
    """Lee contenido de un archivo Excel y lo convierte a texto plano"""
    try:
        df = pd.read_excel(path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error leyendo Excel: {e}"


def read_pdf(path):
    """Lee todo el texto de un archivo PDF usando PyMuPDF"""
    try:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Error leyendo PDF: {e}"

def read_docx(path):
    """Lee contenido de un archivo Word .docx"""
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"Error leyendo DOCX: {e}"
