def safe_float(val):
    """Convertit une valeur en float de manière sécurisée."""
    if isinstance(val, dict):
        val = val.get("value", 0)
    try:
        return float(val)
    except:
        return 0

def normalize_weights(sim: float, keywords: float, exp: float) -> tuple[float,float,float]:
    """Normalise les poids pour qu'ils fassent 1."""
    total = sim + keywords + exp
    if total == 0:
        return 0, 0, 0
    return sim/total, keywords/total, exp/total
