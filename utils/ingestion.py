"""functions for reading different document formats"""
import pandas as pd
import fitz  # PyMuPDF
import docx


def read_excel(path):
    """
    Reads an Excel file from the specified path and returns its contents as a string.

    Parameters:
        path (str): The file path to the Excel document.

    Returns:
        str: The contents of the Excel file as a string, or an error message if reading fails.
    """
    try:
        df = pd.read_excel(path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error leyendo Excel: {e}"


def read_pdf(path):
    """Read all text from a PDF file using PyMuPDF.

    Args:
        path (str): The file path to the PDF document.

    Returns:
        str: The extracted text from the PDF, or an error message if reading fails.
    """
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
    """
    Reads a DOCX file from the specified path and returns its text content.

    This function extracts and concatenates the text from all paragraphs in the
    DOCX file, omitting any empty paragraphs. If an error occurs during the
    reading process, an error message is returned.

    Args:
        path (str): The file path to the DOCX document.

    Returns:
        str: The concatenated text of the document's paragraphs or an error message.
    """
    try:
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"Error leyendo DOCX: {e}"
