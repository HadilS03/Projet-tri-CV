import os
from docx import Document # type: ignore
import fitz  # type: ignore # PyMuPDF
from sentence_transformers import SentenceTransformer, util # type: ignore

# Modèle SentenceTransformer pour calcul de similarité
model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file_path: str) -> str:
    """Extrait le texte d'un PDF avec PyMuPDF."""
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extrait le texte d'un fichier DOCX."""
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def process_cv(file_path: str, job_description: str, user_id=None, option1=None, option2=None) -> dict:
    ...

    """
    Traite un CV et renvoie les scores :
    - Similarité sémantique
    - Mots-clés (optionnel)
    - Expérience (optionnel)
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Format non supporté")

    # Similarité sémantique
    embedding_cv = model.encode(text, convert_to_tensor=True)
    embedding_job = model.encode(job_description, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding_cv, embedding_job).item() * 100
     # Pour l'instant on met des scores fictifs pour mots-clés et expérience
    keywords_score = 0
    experience_score = 0

    # Score global pondéré (à ajuster selon ton UI)
    score = 0.7*similarity + 0.2*keywords_score + 0.1*experience_score

    return {
        "score": round(score, 2),
        "similarity": round(similarity, 2),
        "keywords": round(keywords_score, 2),
        "experience": round(experience_score, 2)
    }