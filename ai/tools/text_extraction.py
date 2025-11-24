import fitz  # PyMuPDF
import docx
from typing import Tuple

def extract_text_from_pdf(file_stream: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf = fitz.open(stream=file_stream, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def extract_text_from_docx(file_stream: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        import io
        doc = docx.Document(io.BytesIO(file_stream))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")

def extract_text_from_file(file_stream: bytes, filename: str) -> str:
    """Extract text based on file extension"""
    ext = filename.lower()
    
    if ext.endswith('.pdf'):
        return extract_text_from_pdf(file_stream)
    elif ext.endswith('.docx'):
        return extract_text_from_docx(file_stream)
    else:
        raise ValueError("Unsupported file format. Only PDF or DOCX allowed.")