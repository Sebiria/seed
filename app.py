from tkinter import Tk
from affichage import afficher_header, afficher_info_header
from dynanim import afficher_dynanim_body
from main import profils

#region Paramétrage de la fenètre
fenetre = Tk()
fenetre.title("Seed")
fenetre.geometry(f"700x800+{(fenetre.winfo_screenwidth()-700)//2}+{(fenetre.winfo_screenheight()-800)//2}")
fenetre.resizable(width=False, height=False)
#endregion

#region Variables
app_actif = "ACCUEIL"
dynanim_onglet_actif = "ACCUEIL"
#endregion

#region Fonctions utilitaires
def normaliser_nom(nom):
    return " ".join(nom.strip().split()).upper()


def cle_nom(nom):
    return normaliser_nom(nom).casefold()


def nom_profil_existe(nom):
    nom_normalise = cle_nom(nom)
    if not nom_normalise:
        return False
    return any(cle_nom(nom_existant) == nom_normalise for nom_existant in profils)


def render_ui():
    afficher_header(fenetre)
    afficher_info_header(fenetre, app_actif)
    afficher_dynanim_body(
        fenetre,
        app_actif,
        dynanim_onglet_actif,
        on_logo_click,
        on_retour_click,
        on_tab_click,
        on_ajout_valider,
        nom_profil_existe,
    )


def update_ui():
    # Détruire tous les widgets sauf la fenêtre
    for widget in fenetre.winfo_children():
        widget.destroy()
    # Redessiner l'interface
    render_ui()

def on_logo_click():
    global app_actif, dynanim_onglet_actif
    app_actif = "DYNANIM"
    dynanim_onglet_actif = "ACCUEIL"
    update_ui()

def on_retour_click():
    global app_actif, dynanim_onglet_actif
    app_actif = "ACCUEIL"
    dynanim_onglet_actif = "ACCUEIL"
    update_ui()

def on_tab_click(onglet):
    global dynanim_onglet_actif
    dynanim_onglet_actif = onglet
    update_ui()

def on_ajout_valider(nom_prenom, date_debut, activites):
    """Crée un nouveau profil animateur en restant sur l'onglet AJOUT de Dynanim."""
    nom_propre = normaliser_nom(nom_prenom)
    if nom_profil_existe(nom_propre):
        raise ValueError("DOUBLON_PROFIL")

    profils[nom_propre] = {
        "date_debut": date_debut,
        "activites": activites,
        "points": 0,
        "niveau": 1,
    }
#endregion

#region Background et affichage permanent

# Affichage
render_ui()
#endregion




fenetre.mainloop()