from datetime import date, datetime, timedelta

ACTIVITE_POINTS = {
    "sportive": 3,
    "manuelle": 3,
    "simple": 2,
    "libre": 1,
}

JOURS_TRAVAIL = {
    0: "lundi",
    1: "mardi",
    3: "jeudi",
    4: "vendredi",
}

# Niveau 1 au départ, puis passage au niveau suivant aux seuils ci-dessous.
PALIERS_XP_CUMULEE = [13, 27, 42, 58, 75, 93, 112, 132, 153, 175, 198, 222, 247, 290, 365]
LETTRES_NOTES = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]


def _to_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def extraire_dates_ferie(periodes):
    dates = set()
    for item in periodes.get("ferie", []):
        d = _to_date(item)
        if d:
            dates.add(d)
    return dates


def iter_periodes_scolaires(periodes):
    for cle_periode, bornes in periodes.items():
        if cle_periode == "ferie":
            continue
        if not isinstance(bornes, list) or len(bornes) != 2:
            continue
        debut = _to_date(bornes[0])
        fin = _to_date(bornes[1])
        if debut and fin:
            yield cle_periode, debut, fin


def trouver_periode_pour_date(date_cible, periodes):
    cible = _to_date(date_cible)
    if not cible:
        return None

    for cle_periode, debut, fin in iter_periodes_scolaires(periodes):
        if debut <= cible <= fin:
            return cle_periode
    return None


def points_activite(activite):
    if not isinstance(activite, str):
        return 0
    return ACTIVITE_POINTS.get(activite.strip().lower(), 0)


def est_jour_travail_compte(date_cible, periodes, ferie_dates=None):
    cible = _to_date(date_cible)
    if not cible:
        return False

    if cible.weekday() not in JOURS_TRAVAIL:
        return False

    if ferie_dates is None:
        ferie_dates = extraire_dates_ferie(periodes)
    if cible in ferie_dates:
        return False

    return trouver_periode_pour_date(cible, periodes) is not None


def points_jour_profil(profil, periodes, date_cible, ferie_dates=None):
    cible = _to_date(date_cible)
    if not cible:
        return 0

    if not est_jour_travail_compte(cible, periodes, ferie_dates=ferie_dates):
        return 0

    cle_periode = trouver_periode_pour_date(cible, periodes)
    if not cle_periode:
        return 0

    cle_jour = JOURS_TRAVAIL[cible.weekday()]
    activites = profil.get("activites", {})
    activite_jour = activites.get(cle_periode, {}).get(cle_jour, "")
    return points_activite(activite_jour)


def penalites_par_date(profil, date_fin=None):
    """Retourne les pénalités valides normalisées au format {date: int}.

    La valeur est interprétée comme un override des points du jour.
    """
    penalites = profil.get("penalite", {})
    if not isinstance(penalites, dict):
        return {}

    fin = _to_date(date_fin) or date.today()
    resultat = {}
    for date_penalite, valeur in penalites.items():
        d = _to_date(date_penalite)
        if not d or d > fin:
            continue
        try:
            resultat[d] = int(valeur)
        except (TypeError, ValueError):
            continue
    return resultat


def compter_jours_penalises_reels(profil, periodes):
    """
    Compte les jours où la pénalité réduit effectivement les points de base.
    Un jour n'est pénalisé que si la valeur override < points de base de l'activité prévue.
    Si la pénalité est >= aux points de base (ex: 1 pt prévu, 3 pts appliqués), ce n'est pas une pénalité.
    """
    penalites = profil.get("penalite", {})
    if not isinstance(penalites, dict):
        return 0

    ferie_dates = extraire_dates_ferie(periodes)
    count = 0
    for date_penalite, valeur in penalites.items():
        d = _to_date(date_penalite)
        if not d:
            continue
        try:
            val = int(valeur)
        except (TypeError, ValueError):
            continue
        base = points_jour_profil(profil, periodes, d, ferie_dates=ferie_dates)
        if val < base:
            count += 1
    return count


def points_jour_effectifs_profil(profil, periodes, date_cible, ferie_dates=None, penalites_dates=None):
    """Retourne les points effectifs du jour (activité ou override de pénalité)."""
    cible = _to_date(date_cible)
    if not cible:
        return 0

    points_base = points_jour_profil(profil, periodes, cible, ferie_dates=ferie_dates)
    if penalites_dates is None:
        penalites_dates = penalites_par_date(profil)
    return penalites_dates.get(cible, points_base)


def total_penalites(profil, date_fin=None):
    penalites = profil.get("penalite", {})
    if not isinstance(penalites, dict):
        return 0

    fin = _to_date(date_fin) or date.today()
    total = 0
    for date_penalite, valeur in penalites.items():
        d = _to_date(date_penalite)
        if not d or d > fin:
            continue
        try:
            total += int(valeur)
        except (TypeError, ValueError):
            continue
    return total


def calculer_xp_globale_profil(profil, periodes, date_reference=None):
    """
    Calcule l'XP globale du profil.
    - Commence au premier jour de travail du profil.
    - S'arrête au jour precedent la date de reference (jour courant exclu).
    - Ne compte que les jours ouvrés dans une periode scolaire et non fériés.
    - Applique les pénalités enregistrées dans profil['penalite'] en override
      de la valeur du jour concerné.
    """
    date_debut = _to_date(profil.get("date_debut"))
    if not date_debut:
        return 0

    reference = _to_date(date_reference) or date.today()
    date_fin = reference - timedelta(days=1)
    if date_fin < date_debut:
        return 0

    ferie_dates = extraire_dates_ferie(periodes)
    penalites_dates = penalites_par_date(profil, date_fin)
    total = 0
    courant = date_debut

    while courant <= date_fin:
        total += points_jour_effectifs_profil(
            profil,
            periodes,
            courant,
            ferie_dates=ferie_dates,
            penalites_dates=penalites_dates,
        )
        courant += timedelta(days=1)
    return total


def calculer_xp_brute_profil(profil, periodes, date_reference=None):
    """
    Calcule l'XP brute (avant pénalités) du profil.
    Même base de calcul que l'XP globale, mais sans déduction des pénalités.
    """
    date_debut = _to_date(profil.get("date_debut"))
    if not date_debut:
        return 0

    reference = _to_date(date_reference) or date.today()
    date_fin = reference - timedelta(days=1)
    if date_fin < date_debut:
        return 0

    ferie_dates = extraire_dates_ferie(periodes)
    total = 0
    courant = date_debut

    while courant <= date_fin:
        total += points_jour_profil(profil, periodes, courant, ferie_dates=ferie_dates)
        courant += timedelta(days=1)

    return total


def points_projets_profil(profil):
    """Somme des points projets d'un profil (valeurs non numériques ignorées)."""
    projets = profil.get("projet", {})
    if not isinstance(projets, dict):
        return 0

    total = 0
    for valeur in projets.values():
        try:
            total += int(valeur)
        except (TypeError, ValueError):
            continue
    return total


def calculer_xp_reelle_totale_profil(profil, periodes, date_reference=None):
    """XP réelle totale = XP activités/pénalités + points projets."""
    xp_activites = calculer_xp_globale_profil(profil, periodes, date_reference=date_reference)
    return xp_activites + points_projets_profil(profil)


def points_max_theoriques_profil(profil, periodes, date_reference=None):
    """
    Calcule les points théoriques supposés du profil (sans pénalité) entre date_debut et hier.
    Cette valeur correspond à ce que le profil devait gagner selon ses activités planifiées.
    """
    return calculer_xp_brute_profil(profil, periodes, date_reference=date_reference)


def etoiles_depuis_score(score_engagement):
    """Mappe un score d'engagement (%) vers 1..5 étoiles."""
    score = max(0.0, min(100.0, float(score_engagement or 0.0)))
    if score >= 95:
        return 5
    if score >= 90:
        return 4
    if score >= 85:
        return 3
    if score >= 80:
        return 2
    return 1


def calculer_score_engagement_profil(profil, periodes, date_reference=None):
    """
    Score d'engagement (%) = points actuels / points max théoriques * 100.
    - points actuels: XP activités/pénalités (hors projets)
    - points théoriques supposés: XP brute attendue selon les activités planifiées (sans pénalité)
    """
    points_actuels = calculer_xp_globale_profil(profil, periodes, date_reference=date_reference)
    points_max = points_max_theoriques_profil(profil, periodes, date_reference=date_reference)

    if points_max <= 0:
        return {
            "score": 0,
            "points_actuels": points_actuels,
            "points_max": 0,
            "etoiles": 1,
            "image_etoiles": "img/etoile_1.png",
        }

    score = int(max(0.0, min(100.0, (points_actuels / points_max) * 100)))
    etoiles = etoiles_depuis_score(score)
    return {
        "score": score,
        "points_actuels": points_actuels,
        "points_max": points_max,
        "etoiles": etoiles,
        "image_etoiles": f"img/etoile_{etoiles}.png",
    }


def calculer_niveau_depuis_xp(xp_totale):
    """Retourne le niveau selon les paliers d'XP cumulée (minimum 1)."""
    try:
        xp = int(xp_totale)
    except (TypeError, ValueError):
        xp = 0

    if xp < 0:
        xp = 0

    niveau = 1
    for palier in PALIERS_XP_CUMULEE:
        if xp >= palier:
            niveau += 1
        else:
            break
    return niveau


def calculer_niveau_profil(profil, periodes, date_reference=None):
    """Calcule le niveau d'un profil à partir de son XP réelle totale."""
    xp = calculer_xp_reelle_totale_profil(profil, periodes, date_reference=date_reference)
    return calculer_niveau_depuis_xp(xp)


def infos_progression_niveau(xp_totale):
    """Retourne les infos de progression vers le niveau suivant."""
    xp = max(0, int(xp_totale or 0))
    niveau = calculer_niveau_depuis_xp(xp)

    if niveau - 1 >= len(PALIERS_XP_CUMULEE):
        return {
            "niveau": niveau,
            "xp_courante": xp,
            "xp_palier_actuel": PALIERS_XP_CUMULEE[-1],
            "xp_palier_suivant": PALIERS_XP_CUMULEE[-1],
            "reste": 0,
            "pourcentage": 100,
            "image_progression": "img/moins_de_100.png",
        }

    xp_palier_suivant = PALIERS_XP_CUMULEE[niveau - 1]
    xp_palier_actuel = 0 if niveau == 1 else PALIERS_XP_CUMULEE[niveau - 2]
    plage = max(1, xp_palier_suivant - xp_palier_actuel)
    progression = max(0, xp - xp_palier_actuel)
    pourcentage = max(0, min(100, int((progression / plage) * 100)))

    seuils = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    image_progression = "img/moins_de_100.png"
    for seuil in seuils:
        if pourcentage < seuil:
            image_progression = f"img/moins_de_{seuil}.png"
            break

    return {
        "niveau": niveau,
        "xp_courante": xp,
        "xp_palier_actuel": xp_palier_actuel,
        "xp_palier_suivant": xp_palier_suivant,
        "reste": max(0, xp_palier_suivant - xp),
        "pourcentage": pourcentage,
        "image_progression": image_progression,
    }


def points_semaine_type_periode(profil, periode):
    """Retourne les points d'une semaine type (lundi/mardi/jeudi/vendredi) pour une période."""
    activites = profil.get("activites", {}).get(periode, {})
    total = 0
    for jour in ["lundi", "mardi", "jeudi", "vendredi"]:
        total += points_activite(activites.get(jour, ""))
    return total


def note_depuis_points_semaine(points_semaine):
    """Mappe les points de semaine type vers une note A..I (12 -> A, 4 -> I)."""
    try:
        points = int(points_semaine)
    except (TypeError, ValueError):
        points = 0

    borne = max(4, min(12, points))
    index = 12 - borne
    lettre = LETTRES_NOTES[index]
    return lettre, f"img/note_{lettre.lower()}.png"


