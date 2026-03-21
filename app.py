from tkinter import Tk
from affichage import afficher_header, afficher_info_header
from dynanim import afficher_dynanim_body
from main import profils, periodes
from calculs import trouver_periode_pour_date, calculer_niveau_profil
from sauvegarde import charger_donnees, sauvegarder_donnees

#region Paramétrage de la fenètre
fenetre = Tk()
fenetre.title("Seed")
fenetre.geometry(f"700x800+{(fenetre.winfo_screenwidth()-700)//2}+{(fenetre.winfo_screenheight()-800)//2}")
fenetre.resizable(width=False, height=False)
#endregion

#region Variables
app_actif = "ACCUEIL"
dynanim_onglet_actif = "ACCUEIL"
parametre_onglet_actif = "VACANCES"
profil_selectionne = None
#endregion

#region Fonctions utilitaires
JOURS_PROFIL = ["lundi", "mardi", "jeudi", "vendredi"]
PERIODES_PROFIL = ["p1", "p2", "p3", "p4", "p5"]


def normaliser_nom(nom):
    return " ".join(nom.strip().split()).upper()


def cle_nom(nom):
    return normaliser_nom(nom).casefold()


def nom_profil_existe(nom):
    nom_normalise = cle_nom(nom)
    if not nom_normalise:
        return False
    return any(cle_nom(nom_existant) == nom_normalise for nom_existant in profils)


def recalculer_niveaux_profils():
    """Recalcule le niveau de tous les profils selon l'XP globale et les paliers."""
    for profil in profils.values():
        profil["niveau"] = calculer_niveau_profil(profil, periodes)


def sauvegarder_etat(recalculer_niveaux=False):
    """Sauvegarde centralisée de l'état applicatif."""
    if recalculer_niveaux:
        recalculer_niveaux_profils()
    sauvegarder_donnees(profils, periodes)


def render_ui():
    afficher_header(fenetre)
    afficher_info_header(fenetre, app_actif, on_parametre_click)
    afficher_dynanim_body(
        fenetre,
        app_actif,
        dynanim_onglet_actif,
        parametre_onglet_actif,
        profil_selectionne,
        on_logo_click,
        on_retour_click,
        on_tab_click,
        on_parametre_tab_click,
        on_profil_click,
        on_profil_back,
        on_ajout_valider,
        nom_profil_existe,
        on_vacances_valider,
        on_ferie_valider,
        on_parametre_mutation,
    )


def update_ui():
    # Détruire tous les widgets sauf la fenêtre
    for widget in fenetre.winfo_children():
        widget.destroy()
    # Redessiner l'interface
    render_ui()

def on_logo_click():
    global app_actif, dynanim_onglet_actif, profil_selectionne
    app_actif = "DYNANIM"
    dynanim_onglet_actif = "ACCUEIL"
    profil_selectionne = None
    update_ui()


def on_parametre_click():
    global app_actif, parametre_onglet_actif
    app_actif = "PARAMETRE"
    parametre_onglet_actif = "VACANCES"
    update_ui()

def on_retour_click():
    global app_actif, dynanim_onglet_actif, parametre_onglet_actif, profil_selectionne
    app_actif = "ACCUEIL"
    dynanim_onglet_actif = "ACCUEIL"
    parametre_onglet_actif = "VACANCES"
    profil_selectionne = None
    update_ui()

def on_tab_click(onglet):
    global dynanim_onglet_actif, profil_selectionne
    dynanim_onglet_actif = onglet
    if onglet != "PROFILS":
        profil_selectionne = None
    update_ui()


def on_profil_click(nom_profil):
    global profil_selectionne, dynanim_onglet_actif
    dynanim_onglet_actif = "PROFILS"
    profil_selectionne = nom_profil
    update_ui()


def on_profil_back():
    global profil_selectionne
    profil_selectionne = None
    update_ui()


def on_parametre_tab_click(onglet):
    global parametre_onglet_actif
    parametre_onglet_actif = onglet
    update_ui()

def on_ajout_valider(nom_prenom, date_debut, activites):
    """Crée un nouveau profil animateur en restant sur l'onglet AJOUT de Dynanim."""
    nom_propre = normaliser_nom(nom_prenom)
    if nom_profil_existe(nom_propre):
        raise ValueError("DOUBLON_PROFIL")

    periode_cible = trouver_periode_pour_date(date_debut, periodes)
    if not periode_cible:
        raise ValueError("PERIODE_INTROUVABLE")

    activites_par_periode = {
        periode: {jour: "" for jour in JOURS_PROFIL}
        for periode in PERIODES_PROFIL
    }

    mapping_jours = {
        "Lundi": "lundi",
        "Mardi": "mardi",
        "Jeudi": "jeudi",
        "Vendredi": "vendredi",
    }
    for jour_formulaire, activite in activites.items():
        jour_cle = mapping_jours.get(jour_formulaire)
        if jour_cle:
            activites_par_periode[periode_cible][jour_cle] = activite

    profils[nom_propre] = {
        "date_debut": date_debut,
        "activites": activites_par_periode,
        "penalite": {},
        "projet": {},
        "niveau": 1,
    }
    sauvegarder_etat()


def on_vacances_valider(periode, date_debut, date_fin):
    """Enregistre ou met à jour une période scolaire dans le dictionnaire periodes."""
    periodes[periode] = [date_debut, date_fin]
    sauvegarder_etat(recalculer_niveaux=True)


def on_ferie_valider(date_ferie):
    """Ajoute une date fériée dans periodes['ferie']."""
    periodes.setdefault("ferie", []).append(date_ferie)
    sauvegarder_etat(recalculer_niveaux=True)


def on_parametre_mutation():
    """Persiste les mutations faites depuis les vues Paramètre (ex: réinitialisation)."""
    sauvegarder_etat(recalculer_niveaux=True)


def on_close():
    """Sauvegarde de sécurité à la fermeture de l'application."""
    sauvegarder_etat()
    fenetre.destroy()
#endregion

#region Background et affichage permanent

charger_donnees(profils, periodes)
sauvegarder_etat(recalculer_niveaux=True)
fenetre.protocol("WM_DELETE_WINDOW", on_close)

# Affichage
render_ui()
#endregion




fenetre.mainloop()