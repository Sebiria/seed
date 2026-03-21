import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from calculs import trouver_periode_pour_date

SAVE_PATH = Path(__file__).resolve().parent / "sauvegarde.json"
PERIODES_ORDRE = ["p1", "p2", "p3", "p4", "p5"]
JOURS_ORDRE = ["lundi", "mardi", "jeudi", "vendredi"]
ACTIVITES_POSSIBLES = ["sportive", "manuelle", "simple", "libre"]


def _dt_to_iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return None


def _iso_to_dt(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _serialiser_periodes(periodes):
    resultat = {}
    for cle, valeur in periodes.items():
        if cle == "ferie":
            resultat[cle] = [_dt_to_iso(item) for item in valeur if isinstance(item, datetime)]
            continue
        if isinstance(valeur, list) and len(valeur) == 2:
            debut = _dt_to_iso(valeur[0])
            fin = _dt_to_iso(valeur[1])
            resultat[cle] = [debut, fin] if debut and fin else []
        else:
            resultat[cle] = []
    return resultat


def _deserialiser_periodes(brut):
    periodes = {}
    for cle, valeur in brut.items():
        if cle == "ferie":
            periodes[cle] = [d for d in (_iso_to_dt(item) for item in valeur) if d]
            continue
        if isinstance(valeur, list) and len(valeur) == 2:
            debut = _iso_to_dt(valeur[0])
            fin = _iso_to_dt(valeur[1])
            periodes[cle] = [debut, fin] if debut and fin else []
        else:
            periodes[cle] = []
    return periodes


def _serialiser_profils(profils):
    resultat = {}
    for nom, profil in profils.items():
        penalites = profil.get("penalite", {})
        penalites_json = {}
        if isinstance(penalites, dict):
            for date_penalite, valeur in penalites.items():
                cle = _dt_to_iso(date_penalite)
                if cle:
                    penalites_json[cle] = valeur

        resultat[nom] = {
            "date_debut": _dt_to_iso(profil.get("date_debut")),
            "activites": profil.get("activites", {}),
            "penalite": penalites_json,
            "projet": profil.get("projet", {}),
            "niveau": int(profil.get("niveau", 1)),
        }
    return resultat


def _deserialiser_profils(brut):
    profils = {}
    for nom, profil in brut.items():
        penalites_brut = profil.get("penalite", {})
        penalites = {}
        if isinstance(penalites_brut, dict):
            for date_penalite, valeur in penalites_brut.items():
                d = _iso_to_dt(date_penalite)
                if d:
                    penalites[d] = valeur

        try:
            niveau = max(1, int(profil.get("niveau", 1)))
        except (TypeError, ValueError):
            niveau = 1

        profils[nom] = {
            "date_debut": _iso_to_dt(profil.get("date_debut")),
            "activites": profil.get("activites", {}),
            "penalite": penalites,
            "projet": profil.get("projet", {}) if isinstance(profil.get("projet", {}), dict) else {},
            "niveau": niveau,
        }
    return profils


def _periodes_par_defaut():
    return {
        "p1": [datetime(2025, 9, 1), datetime(2025, 10, 17)],
        "p2": [datetime(2025, 11, 3), datetime(2025, 12, 19)],
        "p3": [datetime(2026, 1, 5), datetime(2026, 2, 20)],
        "p4": [datetime(2026, 3, 9), datetime(2026, 4, 17)],
        "p5": [datetime(2026, 5, 4), datetime(2026, 7, 3)],
        "ferie": [],
    }


def _profil_vide(date_debut):
    return {
        "date_debut": date_debut,
        "activites": {
            periode: {jour: "" for jour in JOURS_ORDRE}
            for periode in PERIODES_ORDRE
        },
        "penalite": {},
        "projet": {},
        "niveau": 1,
    }


def _creer_profils_exemple(periodes):
    rnd = random.Random(2025)
    noms = [
        "ALICE MARTIN",
        "JULIEN ROBERT",
        "MAYA DUPONT",
        "THOMAS BERNARD",
        "LOLA MOREAU",
    ]

    profils = {}
    debut_fenetre = datetime(2025, 9, 10)
    fin_fenetre = datetime(2025, 9, 30)
    delta = (fin_fenetre - debut_fenetre).days

    for nom in noms:
        date_debut = debut_fenetre + timedelta(days=rnd.randint(0, delta))
        profil = _profil_vide(date_debut)
        periode = trouver_periode_pour_date(date_debut, periodes)
        if periode:
            for jour in JOURS_ORDRE:
                profil["activites"][periode][jour] = rnd.choice(ACTIVITES_POSSIBLES)
        profils[nom] = profil

    return profils


def _payload_par_defaut():
    periodes = _periodes_par_defaut()
    profils = _creer_profils_exemple(periodes)
    return {
        "profils": _serialiser_profils(profils),
        "periodes": _serialiser_periodes(periodes),
    }


def sauvegarder_donnees(profils, periodes):
    payload = {
        "profils": _serialiser_profils(profils),
        "periodes": _serialiser_periodes(periodes),
    }
    SAVE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def charger_donnees(profils, periodes):
    if not SAVE_PATH.exists():
        SAVE_PATH.write_text(json.dumps(_payload_par_defaut(), indent=2), encoding="utf-8")

    contenu = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
    profils_charges = _deserialiser_profils(contenu.get("profils", {}))
    periodes_chargees = _deserialiser_periodes(contenu.get("periodes", {}))

    profils.clear()
    profils.update(profils_charges)

    periodes.clear()
    periodes.update(periodes_chargees)

    for periode in PERIODES_ORDRE:
        periodes.setdefault(periode, [])
    periodes.setdefault("ferie", [])

