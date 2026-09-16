import fitz  # pymupdf
from docx import Document

def extraire_texte(fichier, nom_fichier):
    extension = nom_fichier.lower().split('.')[-1]

    if extension == 'pdf':
        return extraire_pdf(fichier)
    elif extension == 'docx':
        return extraire_docx(fichier)
    else:
        raise ValueError("Format non supporte ! Utilisez PDF ou DOCX.")

def extraire_pdf(fichier):
    texte = ""
    doc = fitz.open(stream=fichier.read(), filetype="pdf")
    for page in doc:
        texte += page.get_text()
    return texte.strip()

def extraire_docx(fichier):
    texte = ""
    doc = Document(fichier)
    for paragraphe in doc.paragraphs:
        if paragraphe.text.strip():
            texte += paragraphe.text + "\n"
    return texte.strip()