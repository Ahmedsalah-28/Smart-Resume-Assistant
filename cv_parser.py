from pdfminer.high_level import extract_text
from docx import Document

def extract_text_from_pdf(file):
    return extract_text(file)

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])
