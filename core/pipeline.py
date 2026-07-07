import os
import re
import unicodedata

import fitz  # type: ignore # PyMuPDF
from docx import Document  # type: ignore
from sentence_transformers import SentenceTransformer, util  # type: ignore

# Modèle d'embeddings retenu : multilingue, car les CV traités sont en français ;
# l'anglo-centré all-MiniLM-L6-v2 sous-performe hors anglais. Surchargeable via la
# variable d'environnement CV_MODEL (ex. pour tester un autre modèle).
NOM_MODELE = os.environ.get("CV_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

_model = None


def get_model():
    """Charge le modèle d'embeddings à la demande, puis le met en cache.

    Le chargement paresseux évite tout téléchargement à l'import du module :
    indispensable pour que les tests et la CI s'exécutent sans accès réseau.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer(NOM_MODELE)
    return _model

# Petite liste de mots vides français, ignorés lors de l'extraction de mots-clés.
MOTS_VIDES = {
    "avec", "pour", "dans", "les", "des", "une", "vous", "nous", "sur", "est",
    "sont", "aux", "par", "plus", "cette", "leur", "sera", "etre", "avoir",
    "notre", "nos", "vos", "ses", "que", "qui", "ans", "annees", "experience",
}


def _normaliser(texte: str) -> str:
    """Minuscule + suppression des accents, pour comparer des mots simplement."""
    texte = texte.lower()
    texte = unicodedata.normalize("NFD", texte)
    return "".join(c for c in texte if unicodedata.category(c) != "Mn")


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


def keywords_score(cv_text: str, job_description: str) -> float:
    """Pourcentage des mots significatifs de l'annonce présents dans le CV.

    Méthode simple et assumée : on extrait les mots de l'annonce, on les normalise
    (minuscule, sans accents), on garde ceux d'au moins 4 lettres hors mots vides,
    on déduplique, puis on mesure la part de ces mots retrouvés dans le CV (même
    normalisation). Renvoie 0 si l'annonce ne produit aucun mot-clé.
    """
    cv_norm = _normaliser(cv_text)
    mots_cles = set()
    for mot in re.findall(r"\w+", job_description):
        mot_norm = _normaliser(mot)
        if len(mot_norm) >= 4 and mot_norm not in MOTS_VIDES:
            mots_cles.add(mot_norm)

    if not mots_cles:
        return 0.0

    presents = sum(1 for mot in mots_cles if mot in cv_norm)
    return presents / len(mots_cles) * 100


def experience_score(cv_text: str) -> float:
    """Estime l'expérience (0-100) par deux heuristiques assumées, pas de magie.

    (a) mentions explicites du type « 5 ans d'experience » (regex) ;
    (b) amplitude des années calendaires citées (max - min), plafonnée à 30 ans.
    On prend le maximum des deux estimations, puis on mappe linéairement
    0 -> 10 ans d'expérience sur 0 -> 100 (au-delà de 10 ans : 100).
    """
    texte = _normaliser(cv_text)
    annees_exp = 0

    # (a) « X ans d'experience » / « X annees exp... »
    for m in re.finditer(r"(\d{1,2})\s*(ans|annees)\s*(d['e]\s*)?exp", texte):
        annees_exp = max(annees_exp, int(m.group(1)))

    # (b) amplitude des années calendaires détectées (1900-2099).
    annees = [int(a) for a in re.findall(r"(?:19|20)\d{2}", texte)]
    if annees:
        amplitude = min(max(annees) - min(annees), 30)
        annees_exp = max(annees_exp, amplitude)

    # Mapping linéaire : 10 ans (ou plus) -> 100.
    return min(annees_exp / 10 * 100, 100.0)


def process_cv(
    file_path: str,
    job_description: str,
    poids_similarite: float = 0.7,
    poids_mots_cles: float = 0.2,
    poids_experience: float = 0.1,
) -> dict:
    """Traite un CV et renvoie les trois sous-scores et le score global pondéré.

    Les poids sont normalisés par leur somme, afin que le score global reste dans
    [0, 100] et que 100 reste atteignable quelle que soit la pondération choisie.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Format non supporté")

    # Similarité sémantique, bornée à [0, 100] (la similarité cosinus peut être
    # théoriquement négative).
    modele = get_model()
    embedding_cv = modele.encode(text, convert_to_tensor=True)
    embedding_job = modele.encode(job_description, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding_cv, embedding_job).item() * 100
    similarity = max(0.0, min(100.0, similarity))

    mots_cles = keywords_score(text, job_description)
    experience = experience_score(text)

    # Normalisation des poids : garantit un score global dans [0, 100].
    somme = poids_similarite + poids_mots_cles + poids_experience
    if somme <= 0:
        somme = 1.0
    score = (
        poids_similarite * similarity
        + poids_mots_cles * mots_cles
        + poids_experience * experience
    ) / somme

    return {
        "score": round(score, 2),
        "similarity": round(similarity, 2),
        "keywords": round(mots_cles, 2),
        "experience": round(experience, 2),
    }
