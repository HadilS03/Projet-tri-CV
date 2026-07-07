"""Compare le modèle anglo-centré et le modèle multilingue sur des paires FR.

Support de la diapositive « pourquoi le modèle multilingue » : sur des paires
françaises (proximité de sens, synonymie, cas négatif), on affiche côte à côte la
similarité donnée par chaque modèle. Le multilingue doit mieux rapprocher les
paires de sens proche et bien séparer le cas négatif.

Lancer :  python scripts/comparer_modeles.py
(Attention : télécharge les deux modèles au premier lancement.)
"""
from sentence_transformers import SentenceTransformer, util  # type: ignore

MODELE_ANGLAIS = "all-MiniLM-L6-v2"
MODELE_MULTILINGUE = "paraphrase-multilingual-MiniLM-L12-v2"

# Paires françaises : les 3 premières sont de sens proche, la dernière est un
# cas négatif (métiers sans rapport) qui doit obtenir une similarité basse.
PAIRES = [
    ("développeur Python confirmé",
     "5 ans d'expérience en développement logiciel Python"),
    ("gestion d'équipe", "management"),
    ("chef de projet", "coordination et pilotage de projets"),
    ("comptable", "soudeur"),
]


def similarite(modele, a, b):
    """Similarité cosinus (en %) entre deux textes selon un modèle donné."""
    emb_a = modele.encode(a, convert_to_tensor=True)
    emb_b = modele.encode(b, convert_to_tensor=True)
    return util.pytorch_cos_sim(emb_a, emb_b).item() * 100


def main():
    print("Chargement des modeles (peut telecharger au premier lancement)...")
    modele_en = SentenceTransformer(MODELE_ANGLAIS)
    modele_multi = SentenceTransformer(MODELE_MULTILINGUE)

    print(f"\n{'Paire':48} | {'all-MiniLM':>11} | {'multilingue':>12}")
    print("-" * 78)
    for a, b in PAIRES:
        score_en = similarite(modele_en, a, b)
        score_multi = similarite(modele_multi, a, b)
        etiquette = f"{a[:20]} / {b[:20]}"
        print(f"{etiquette:48} | {score_en:9.1f} % | {score_multi:10.1f} %")


if __name__ == "__main__":
    main()
