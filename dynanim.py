from tkinter import Label, Entry, OptionMenu, StringVar, Button, Listbox, Canvas, Frame, Scrollbar, TclError
from tkinter import font as tkfont
from PIL import Image, ImageTk
from datetime import datetime
import calendar
from main import periodes, profils
from calculs import (
    calculer_repartition_types_anim_profil,
    calculer_xp_globale_profil,
    calculer_xp_reelle_totale_profil,
    calculer_score_engagement_profil,
    compter_jours_penalises_reels,
    infos_progression_niveau,
    note_depuis_points_semaine,
    points_projets_profil,
    points_semaine_type_periode,
)

# Constantes UI Dynanim (tailles / positions)
BODY_RETOUR_SIZE = (30, 30)
BODY_RETOUR_POS = (200, 230)
BODY_DYNANIM_SIZE = (100, 100)
BODY_DYNANIM_POS = (50, 300)
COLOR_BODY_BG = "#D8F3DC"
COLOR_NAV_TEXT_BG = "#FF7500"
COLOR_VALIDER_INACTIF = "#F3A6A6"
COLOR_PARAMETRE_TEXT = "#1B4332"

BODY_WIDTH = 700
BODY_X = 0

NAV_TAB_SIZE = (110, 40)
NAV_TAB_Y = 267  # Juste sous le label app_actif (y=222 + h=40 + 5px gap)
NAV_TAB_LABELS = ["AJOUT", "PROFILS", "ACCUEIL", "+ / -", "STATS"]
NAV_TAB_FONT = ("Comic Sans MS", 11)
NAV_TAB_FONT_ACTIVE = ("Comic Sans MS", 12, "bold")
PARAM_TAB_LABELS = ["VACANCES", "FÉRIÉ", "RÉINITIALISATION"]

# Constantes AJOUT
ACTIVITES = ["sportive", "manuelle", "simple", "libre"]
JOURS_ACTIVITE = ["Lundi", "Mardi", "Jeudi", "Vendredi"]
MAX_NOM_PROFIL = 20
AJOUT_FONT_LABEL = ("Comic Sans MS", 12, "bold")
AJOUT_FONT_ENTRY = ("Comic Sans MS", 11)
AJOUT_CENTER_X = 350
AJOUT_Y_START = 335          # Décalé pour éviter collision avec la barre de navigation
AJOUT_TITLE_BG_SIZE = (250, 35)  # Fond label_nav_dynanim derrière chaque titre de section
VACANCES_CENTER_X = 350
VACANCES_Y_START = 335
VACANCES_DATE_Y_OFFSET = 53
PERIODES_SCOLAIRES = ["p1", "p2", "p3", "p4", "p5"]
FERIE_Y_OFFSET = 30
RESET_TITLE_Y = 338
RESET_LIST_Y = 370
RESET_LIST_HEIGHT = 12
RESET_LEFT_X = 175
RESET_RIGHT_X = 525
RESET_LIST_WIDTH = 30
RESET_SEPARATOR_X = 350
RESET_SEPARATOR_TOP = 330
RESET_SEPARATOR_BOTTOM = 760


def _charger_photo(path, size):
    image_originale = Image.open(path)
    image_redimensionnee = image_originale.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image_redimensionnee)


def _creer_label_image(fenetre, photo, **kwargs):
    label = Label(fenetre, image=photo, **kwargs)
    label.image = photo
    return label


def _style_optionmenu_blanc(option_menu):
    option_menu.config(font=AJOUT_FONT_ENTRY, bg="white", fg="black", bd=1, highlightthickness=0)
    option_menu["menu"].config(font=AJOUT_FONT_ENTRY, bg="white", fg="black")


def _placer_titre_section(fenetre, img_path, y, texte, bg=None):
    if bg is None:
        bg = COLOR_NAV_TEXT_BG
    # Largeur dynamique selon le texte + marges
    f = tkfont.Font(family="Comic Sans MS", size=12, weight="bold")
    img_width = f.measure(texte) + 40  # 20px de marge de chaque côté
    img_height = AJOUT_TITLE_BG_SIZE[1]
    photo = _charger_photo(img_path, (img_width, img_height))
    label_bg = _creer_label_image(fenetre, photo, bd=0, highlightthickness=0)
    label_bg.place(x=VACANCES_CENTER_X - img_width // 2, y=y)
    Label(fenetre, text=texte, font=AJOUT_FONT_LABEL, fg="white", bg=bg).place(
        x=VACANCES_CENTER_X, y=y + img_height // 2, anchor="center"
    )


def _creer_selecteur_date(fenetre, y, annees_list, mois_list):
    """Crée un sélecteur date (année/mois/jour) avec jours conditionnels."""
    var_annee = StringVar()
    var_mois = StringVar()
    var_jour = StringVar()

    opt_annee = OptionMenu(fenetre, var_annee, *annees_list)
    _style_optionmenu_blanc(opt_annee)
    opt_annee.config(width=6)
    opt_annee.place(x=220, y=y, anchor="center")

    opt_mois = OptionMenu(fenetre, var_mois, *mois_list)
    _style_optionmenu_blanc(opt_mois)
    opt_mois.config(width=12)
    opt_mois.place(x=350, y=y, anchor="center")

    opt_jour = OptionMenu(fenetre, var_jour, "")
    _style_optionmenu_blanc(opt_jour)
    opt_jour.config(width=4)
    opt_jour.place(x=480, y=y, anchor="center")

    def mettre_a_jour_jours(*_args):
        annee_str = var_annee.get().strip()
        mois_str = var_mois.get().strip()
        opt_jour["menu"].delete(0, "end")

        if not annee_str or not mois_str:
            var_jour.set("")
            return

        nb_jours = calendar.monthrange(int(annee_str), int(mois_str.split("-")[0]))[1]
        for jour in range(1, nb_jours + 1):
            jour_label = f"{jour:02d}"
            opt_jour["menu"].add_command(label=jour_label, command=lambda j=jour_label: var_jour.set(j))
        var_jour.set("")

    var_annee.trace_add("write", mettre_a_jour_jours)
    var_mois.trace_add("write", mettre_a_jour_jours)

    return {
        "annee": var_annee,
        "mois": var_mois,
        "jour": var_jour,
    }


def afficher_onglet_ajout(fenetre, on_valider=None, nom_existe=None):
    """Affiche le formulaire d'ajout de profil animateur."""

    # Chargement unique de l'image de fond pour les titres de section
    photo_title_bg = _charger_photo("img/label_nav_dynanim.png", AJOUT_TITLE_BG_SIZE)
    fenetre._ajout_photo_title = photo_title_bg  # Garder la référence

    # Chargement de l'image pour les titres de jours
    photo_jour_bg = _charger_photo("img/label_nav_dynanim.png", (80, 35))
    fenetre._ajout_photo_jour = photo_jour_bg  # Garder la référence

    def placer_titre(y, texte):
        """Place label_nav_dynanim en fond + texte titre en #FF7500 centré par-dessus."""
        _creer_label_image(fenetre, photo_title_bg, bd=0, highlightthickness=0).place(
            x=AJOUT_CENTER_X - AJOUT_TITLE_BG_SIZE[0] // 2, y=y
        )
        Label(fenetre, text=texte, font=AJOUT_FONT_LABEL, fg="white", bg=COLOR_NAV_TEXT_BG).place(
            x=AJOUT_CENTER_X, y=y + AJOUT_TITLE_BG_SIZE[1] // 2, anchor="center"
        )

    def placer_titre_jour(x, y, texte):
        """Place label_nav_dynanim en fond + texte titre jour en #FF7500 centré par-dessus."""
        _creer_label_image(fenetre, photo_jour_bg, bd=0, highlightthickness=0).place(x=x - 40, y=y)
        Label(fenetre, text=texte, font=AJOUT_FONT_ENTRY, fg="white", bg=COLOR_NAV_TEXT_BG).place(
            x=x, y=y + 17, anchor="center"
        )

    # region Nom / Prénom
    placer_titre(AJOUT_Y_START, "Nom / Prénom")
    var_nom = StringVar()
    Entry(fenetre, textvariable=var_nom, font=AJOUT_FONT_ENTRY, width=25).place(
        x=AJOUT_CENTER_X, y=AJOUT_Y_START + 48, anchor="center"
    )
    # endregion

    # region Premier jour de travail (3 listes: année, mois, jour)
    placer_titre(AJOUT_Y_START + 80, "Premier jour de travail")
    
    annee_actuelle = datetime.now().year
    annees_list = [str(annee_actuelle - 1), str(annee_actuelle), str(annee_actuelle + 1)]
    mois_list = ["01-Janvier", "02-Février", "03-Mars", "04-Avril", "05-Mai", "06-Juin",
                 "07-Juillet", "08-Août", "09-Septembre", "10-Octobre", "11-Novembre", "12-Décembre"]
    
    var_annee = StringVar()
    var_mois = StringVar()
    var_jour = StringVar()

    def nom_est_valide(nom):
        nom = " ".join(nom.strip().split())
        lettres = nom.replace(" ", "")
        return (
            len(lettres) >= 3
            and len(nom) <= MAX_NOM_PROFIL
            and all(char.isalpha() or char == " " for char in nom)
        )

    def nom_affichage(nom):
        return " ".join(nom.strip().split()).upper()

    def majuscule_nom_temps_reel(*args):
        # Évite la boucle infinie quand on réécrit la StringVar depuis son propre trace.
        if getattr(fenetre, "_nom_trace_lock", False):
            return

        saisie = var_nom.get()
        saisie_upper = saisie.upper()
        if saisie != saisie_upper:
            fenetre._nom_trace_lock = True
            var_nom.set(saisie_upper)
            fenetre._nom_trace_lock = False

    def nom_est_disponible(nom):
        if not nom_existe:
            return True
        return not nom_existe(nom)
    
    def mettre_a_jour_jours(*args):
        """Met à jour la liste des jours en fonction de l'année et du mois sélectionnés."""
        annee_str = var_annee.get().strip()
        mois_str = var_mois.get().strip()

        opt_jour["menu"].delete(0, "end")
        if not annee_str or not mois_str:
            var_jour.set("")
            rafraichir_etat_bouton()
            return

        annee = int(annee_str)
        mois = int(mois_str.split("-")[0])
        
        # Calculer le nombre de jours du mois (gère les années bissextiles automatiquement)
        nb_jours = calendar.monthrange(annee, mois)[1]
        jours_list = [f"{i:02d}" for i in range(1, nb_jours + 1)]
        
        # Réinitialiser l'OptionMenu des jours
        for jour in jours_list:
            opt_jour["menu"].add_command(label=jour, command=lambda j=jour: var_jour.set(j))
        
        # Vider le champ jour (au lieu de sélectionner le premier)
        var_jour.set("")
        rafraichir_etat_bouton()
    
    # OptionMenu Année
    opt_annee = OptionMenu(fenetre, var_annee, *annees_list, command=mettre_a_jour_jours)
    _style_optionmenu_blanc(opt_annee)
    opt_annee.config(width=6)
    opt_annee.place(x=220, y=AJOUT_Y_START + 133, anchor="center")
    
    # OptionMenu Mois
    opt_mois = OptionMenu(fenetre, var_mois, *mois_list, command=mettre_a_jour_jours)
    _style_optionmenu_blanc(opt_mois)
    opt_mois.config(width=12)
    opt_mois.place(x=350, y=AJOUT_Y_START + 133, anchor="center")
    
    # OptionMenu Jour (initialisé vide, sera rempli quand année/mois sont sélectionnés)
    opt_jour = OptionMenu(fenetre, var_jour, "")
    _style_optionmenu_blanc(opt_jour)
    opt_jour.config(width=4)
    opt_jour.place(x=480, y=AJOUT_Y_START + 133, anchor="center")
    # endregion

    # region Activités par jour
    placer_titre(AJOUT_Y_START + 160, "Activités par jour")
    
    # Positions X pour les 4 jours (espacés horizontalement)
    x_positions = [150, 280, 410, 540]  # X pour Lundi, Mardi, Jeudi, Vendredi
    y_titres = AJOUT_Y_START + 208      # Y pour les titres des jours
    y_activites = AJOUT_Y_START + 263   # Y pour les champs d'activités (sous les titres)
    
    # Étape 1 : Placer les titres jours horizontalement
    for i, jour in enumerate(JOURS_ACTIVITE):
        placer_titre_jour(x_positions[i], y_titres, jour)
    
    # Étape 2 : Placer les champs d'activités sous chaque titre
    vars_activites = {}
    for i, jour in enumerate(JOURS_ACTIVITE):
        var = StringVar()  # Vide par défaut
        vars_activites[jour] = var
        opt = OptionMenu(fenetre, var, *ACTIVITES)
        _style_optionmenu_blanc(opt)
        opt.config(width=10)
        opt.place(x=x_positions[i], y=y_activites, anchor="center")
    # endregion

    def date_est_valide():
        annee_str = var_annee.get().strip()
        mois_str = var_mois.get().strip()
        jour_str = var_jour.get().strip()
        if not annee_str or not mois_str or not jour_str:
            return False
        try:
            datetime(int(annee_str), int(mois_str.split("-")[0]), int(jour_str))
            return True
        except ValueError:
            return False

    def activites_sont_valides():
        return all(vars_activites[jour].get().strip() for jour in JOURS_ACTIVITE)

    def formulaire_est_valide():
        return (
            nom_est_valide(var_nom.get())
            and nom_est_disponible(var_nom.get())
            and date_est_valide()
            and activites_sont_valides()
        )

    def rafraichir_etat_bouton(*args):
        couleur = COLOR_NAV_TEXT_BG if formulaire_est_valide() else COLOR_VALIDER_INACTIF
        bouton_valider.config(bg=couleur, activebackground=couleur)

    # Garder les StringVar en vie (évite le garbage collection)
    fenetre._ajout_vars = {
        "nom": var_nom,
        "annee": var_annee,
        "mois": var_mois,
        "jour": var_jour,
        "activites": vars_activites
    }

    # region Erreur + Bouton valider
    label_erreur = Label(fenetre, text="", font=("Comic Sans MS", 10, "italic"), fg="red", bg="white")
    label_erreur.place(x=AJOUT_CENTER_X, y=AJOUT_Y_START + 375, anchor="center")

    def annuler_disparition_message():
        after_id = getattr(fenetre, "_ajout_message_after_id", None)
        if after_id:
            fenetre.after_cancel(after_id)
            fenetre._ajout_message_after_id = None

    def masquer_message():
        label_erreur.config(text="")
        fenetre._ajout_message_after_id = None

    def afficher_erreur(message):
        annuler_disparition_message()
        label_erreur.config(text=message, fg="red", bg="white", font=("Comic Sans MS", 10, "italic"))

    def afficher_succes(nom):
        annuler_disparition_message()
        label_erreur.config(
            text=f"Le participant {nom_affichage(nom)} a bien été ajouté",
            fg="#2E7D32",
            bg=COLOR_BODY_BG,
            font=("Comic Sans MS", 13, "bold"),
        )
        fenetre._ajout_message_after_id = fenetre.after(5000, masquer_message)

    def vider_formulaire():
        var_nom.set("")
        var_annee.set("")
        var_mois.set("")
        opt_jour["menu"].delete(0, "end")
        opt_jour["menu"].add_command(label="", command=lambda: var_jour.set(""))
        var_jour.set("")
        for jour in JOURS_ACTIVITE:
            vars_activites[jour].set("")
        rafraichir_etat_bouton()

    def valider():
        nom = var_nom.get().strip()
        annee_str = var_annee.get().strip()
        mois_str = var_mois.get().strip()
        jour_str = var_jour.get().strip()
        activites_vals = {j: vars_activites[j].get() for j in JOURS_ACTIVITE}

        if not nom_est_valide(nom):
            afficher_erreur(
                f"⚠ Nom / Prénom invalide (3 lettres min, lettres/espaces, {MAX_NOM_PROFIL} caractères max)."
            )
            return

        if not nom_est_disponible(nom):
            afficher_erreur("⚠ Ce participant existe déjà.")
            return
        
        if not annee_str or not mois_str or not jour_str:
            afficher_erreur("⚠ Veuillez sélectionner une date complète.")
            return

        # Vérifier que toutes les activités sont sélectionnées
        if not activites_sont_valides():
            afficher_erreur("⚠ Veuillez sélectionner une activité pour chaque jour.")
            return

        try:
            annee = int(annee_str)
            mois = int(mois_str.split("-")[0])
            jour = int(jour_str)
            date_debut = datetime(annee, mois, jour)
        except ValueError:
            afficher_erreur("⚠ Date invalide.")
            return

        try:
            if on_valider:
                on_valider(nom, date_debut, activites_vals)
        except ValueError as erreur:
            if str(erreur) == "DOUBLON_PROFIL":
                afficher_erreur("⚠ Ce participant existe déjà.")
                return
            if str(erreur) == "PERIODE_INTROUVABLE":
                afficher_erreur("⚠ La date de début n'est dans aucune période configurée.")
                return
            afficher_erreur("⚠ Impossible d'ajouter ce participant.")
            return

        vider_formulaire()
        afficher_succes(nom)

    bouton_valider = Button(
        fenetre,
        text="VALIDER",
        font=("Comic Sans MS", 13, "bold"),
        bg=COLOR_VALIDER_INACTIF,
        fg="white",
        cursor="hand2",
        command=valider,
        bd=0,
        padx=20,
        pady=5,
        activebackground=COLOR_VALIDER_INACTIF,
    )
    bouton_valider.place(x=AJOUT_CENTER_X, y=AJOUT_Y_START + 418, anchor="center")

    # Validation dynamique: toute modification recalcule l'état du bouton
    var_nom.trace_add("write", majuscule_nom_temps_reel)
    var_nom.trace_add("write", rafraichir_etat_bouton)
    var_annee.trace_add("write", rafraichir_etat_bouton)
    var_mois.trace_add("write", rafraichir_etat_bouton)
    var_jour.trace_add("write", rafraichir_etat_bouton)
    for jour in JOURS_ACTIVITE:
        vars_activites[jour].trace_add("write", rafraichir_etat_bouton)

    rafraichir_etat_bouton()
    # endregion


def afficher_onglet_vacances(fenetre, on_valider=None):
    """Formulaire de saisie d'une période scolaire entre deux vacances."""
    img_titre = "img/label_info.png"

    annee_actuelle = datetime.now().year
    annees_list = [str(annee_actuelle - 1), str(annee_actuelle), str(annee_actuelle + 1)]
    mois_list = [
        "01-Janvier", "02-Février", "03-Mars", "04-Avril", "05-Mai", "06-Juin",
        "07-Juillet", "08-Août", "09-Septembre", "10-Octobre", "11-Novembre", "12-Décembre",
    ]

    _placer_titre_section(fenetre, img_titre, VACANCES_Y_START, "Période", bg=COLOR_PARAMETRE_TEXT)
    var_periode = StringVar()
    opt_periode = OptionMenu(fenetre, var_periode, *PERIODES_SCOLAIRES)
    _style_optionmenu_blanc(opt_periode)
    opt_periode.config(width=12)
    opt_periode.place(x=VACANCES_CENTER_X, y=VACANCES_Y_START + 53, anchor="center")

    _placer_titre_section(fenetre, img_titre, VACANCES_Y_START + 85, "Date de début", bg=COLOR_PARAMETRE_TEXT)
    debut = _creer_selecteur_date(
        fenetre,
        VACANCES_Y_START + 85 + VACANCES_DATE_Y_OFFSET,
        annees_list,
        mois_list,
    )

    _placer_titre_section(fenetre, img_titre, VACANCES_Y_START + 170, "Date de fin", bg=COLOR_PARAMETRE_TEXT)
    fin = _creer_selecteur_date(
        fenetre,
        VACANCES_Y_START + 170 + VACANCES_DATE_Y_OFFSET,
        annees_list,
        mois_list,
    )

    label_message = Label(fenetre, text="", font=("Comic Sans MS", 10, "italic"), fg="red", bg=COLOR_BODY_BG)
    label_message.place(x=VACANCES_CENTER_X, y=VACANCES_Y_START + 300, anchor="center")

    def lire_date(date_vars):
        annee_str = date_vars["annee"].get().strip()
        mois_str = date_vars["mois"].get().strip()
        jour_str = date_vars["jour"].get().strip()
        if not annee_str or not mois_str or not jour_str:
            return None
        try:
            return datetime(int(annee_str), int(mois_str.split("-")[0]), int(jour_str))
        except ValueError:
            return None

    def annuler_disparition_message():
        after_id = getattr(fenetre, "_vacances_message_after_id", None)
        if after_id:
            fenetre.after_cancel(after_id)
            fenetre._vacances_message_after_id = None

    def masquer_message():
        label_message.config(text="")
        fenetre._vacances_message_after_id = None

    def formulaire_est_valide():
        date_debut = lire_date(debut)
        date_fin = lire_date(fin)
        return bool(var_periode.get().strip()) and bool(date_debut) and bool(date_fin) and date_debut <= date_fin

    def rafraichir_etat_bouton(*_args):
        couleur = COLOR_NAV_TEXT_BG if formulaire_est_valide() else COLOR_VALIDER_INACTIF
        bouton_valider.config(bg=couleur, activebackground=couleur)

    def vider_formulaire():
        var_periode.set("")
        for bloc in (debut, fin):
            bloc["annee"].set("")
            bloc["mois"].set("")
            bloc["jour"].set("")
        rafraichir_etat_bouton()

    def afficher_succes():
        annuler_disparition_message()
        label_message.config(
            text="La période a bien été prise en compte",
            fg="#2E7D32",
            bg=COLOR_BODY_BG,
            font=("Comic Sans MS", 13, "bold"),
        )
        fenetre._vacances_message_after_id = fenetre.after(5000, masquer_message)

    def afficher_erreur(message):
        annuler_disparition_message()
        label_message.config(text=message, fg="red", bg=COLOR_BODY_BG, font=("Comic Sans MS", 10, "bold", "italic"))

    def valider():
        date_debut = lire_date(debut)
        date_fin = lire_date(fin)
        periode = var_periode.get().strip()

        if not periode:
            afficher_erreur("⚠ Veuillez sélectionner une période.")
            return
        if not date_debut or not date_fin:
            afficher_erreur("⚠ Veuillez sélectionner deux dates complètes.")
            return
        if date_debut > date_fin:
            afficher_erreur("⚠ La date de début doit être antérieure ou égale à la date de fin.")
            return

        if on_valider:
            on_valider(periode, date_debut, date_fin)
        vider_formulaire()
        afficher_succes()

    bouton_valider = Button(
        fenetre,
        text="VALIDER",
        font=("Comic Sans MS", 13, "bold"),
        bg=COLOR_VALIDER_INACTIF,
        fg="white",
        cursor="hand2",
        command=valider,
        bd=0,
        padx=20,
        pady=5,
        activebackground=COLOR_VALIDER_INACTIF,
    )
    bouton_valider.place(x=VACANCES_CENTER_X, y=VACANCES_Y_START + 345, anchor="center")

    var_periode.trace_add("write", rafraichir_etat_bouton)
    for bloc in (debut, fin):
        bloc["annee"].trace_add("write", rafraichir_etat_bouton)
        bloc["mois"].trace_add("write", rafraichir_etat_bouton)
        bloc["jour"].trace_add("write", rafraichir_etat_bouton)

    fenetre._vacances_vars = {
        "periode": var_periode,
        "date_debut": debut,
        "date_fin": fin,
    }
    rafraichir_etat_bouton()


def afficher_parametre_body(
    fenetre,
    parametre_onglet_actif="VACANCES",
    on_parametre_tab_click=None,
    on_vacances_valider=None,
    on_ferie_valider=None,
    on_parametre_mutation=None,
):
    """Affiche la navigation de l'app PARAMETRE et son contenu actif."""
    tab_height = NAV_TAB_SIZE[1]
    font_mesure = tkfont.Font(family="Comic Sans MS", size=12, weight="bold")
    tab_widths = [font_mesure.measure(texte) + 36 for texte in PARAM_TAB_LABELS]

    total_tabs_width = sum(tab_widths)
    # Centrage réel depuis le milieu de la fenêtre
    espace_x = (BODY_WIDTH - total_tabs_width) // (len(PARAM_TAB_LABELS) + 1)
    x_tab = espace_x

    for index, texte in enumerate(PARAM_TAB_LABELS):
        tab_width = tab_widths[index]
        nav_font = NAV_TAB_FONT_ACTIVE if texte == parametre_onglet_actif else NAV_TAB_FONT
        photo_nav = _charger_photo("img/label_info.png", (tab_width, tab_height))

        label_nav_bg = _creer_label_image(fenetre, photo_nav, bd=0, highlightthickness=0, cursor="hand2")
        label_nav_bg.place(x=x_tab, y=NAV_TAB_Y)

        label_nav_text = Label(
            fenetre,
            text=texte,
            font=nav_font,
            fg="white",
            bg=COLOR_PARAMETRE_TEXT,
            cursor="hand2",
        )
        label_nav_text.place(
            x=x_tab + tab_width // 2,
            y=NAV_TAB_Y + tab_height // 2,
            anchor="center",
        )

        if on_parametre_tab_click:
            onglet = texte
            label_nav_bg.bind("<Button-1>", lambda _e, o=onglet: on_parametre_tab_click(o))
            label_nav_text.bind("<Button-1>", lambda _e, o=onglet: on_parametre_tab_click(o))

        x_tab += tab_width + espace_x

    if parametre_onglet_actif == "VACANCES":
        afficher_onglet_vacances(fenetre, on_valider=on_vacances_valider)
    elif parametre_onglet_actif == "FÉRIÉ":
        afficher_onglet_ferie(fenetre, on_valider=on_ferie_valider)
    elif parametre_onglet_actif == "RÉINITIALISATION":
        afficher_onglet_reinitialisation(fenetre, on_mutation=on_parametre_mutation)


def afficher_onglet_ferie(fenetre, on_valider=None):
    """Formulaire de saisie des jours fériés (une seule date)."""
    img_titre = "img/label_info.png"
    annee_actuelle = datetime.now().year
    annees_list = [str(annee_actuelle - 1), str(annee_actuelle), str(annee_actuelle + 1)]
    mois_list = [
        "01-Janvier", "02-Février", "03-Mars", "04-Avril", "05-Mai", "06-Juin",
        "07-Juillet", "08-Août", "09-Septembre", "10-Octobre", "11-Novembre", "12-Décembre",
    ]

    _placer_titre_section(fenetre, img_titre, VACANCES_Y_START + FERIE_Y_OFFSET, "Jour férié", bg=COLOR_PARAMETRE_TEXT)
    ferie = _creer_selecteur_date(
        fenetre,
        VACANCES_Y_START + VACANCES_DATE_Y_OFFSET + FERIE_Y_OFFSET,
        annees_list,
        mois_list,
    )

    label_message = Label(fenetre, text="", font=("Comic Sans MS", 10, "italic"), fg="red", bg=COLOR_BODY_BG)
    label_message.place(x=VACANCES_CENTER_X, y=VACANCES_Y_START + 190 + FERIE_Y_OFFSET, anchor="center")

    def lire_date(date_vars):
        annee_str = date_vars["annee"].get().strip()
        mois_str = date_vars["mois"].get().strip()
        jour_str = date_vars["jour"].get().strip()
        if not annee_str or not mois_str or not jour_str:
            return None
        try:
            return datetime(int(annee_str), int(mois_str.split("-")[0]), int(jour_str))
        except ValueError:
            return None

    def annuler_disparition_message():
        after_id = getattr(fenetre, "_ferie_message_after_id", None)
        if after_id:
            fenetre.after_cancel(after_id)
            fenetre._ferie_message_after_id = None

    def masquer_message():
        label_message.config(text="")
        fenetre._ferie_message_after_id = None

    def formulaire_est_valide():
        return bool(lire_date(ferie))

    def rafraichir_etat_bouton(*_args):
        couleur = COLOR_NAV_TEXT_BG if formulaire_est_valide() else COLOR_VALIDER_INACTIF
        bouton_valider.config(bg=couleur, activebackground=couleur)

    def vider_formulaire():
        ferie["annee"].set("")
        ferie["mois"].set("")
        ferie["jour"].set("")
        rafraichir_etat_bouton()

    def afficher_succes():
        annuler_disparition_message()
        label_message.config(
            text="Le jour férié a bien été pris en compte",
            fg="#2E7D32",
            bg=COLOR_BODY_BG,
            font=("Comic Sans MS", 13, "bold"),
        )
        fenetre._ferie_message_after_id = fenetre.after(5000, masquer_message)

    def afficher_erreur(message):
        annuler_disparition_message()
        label_message.config(text=message, fg="red", bg=COLOR_BODY_BG, font=("Comic Sans MS", 10, "bold", "italic"))

    def valider():
        date_ferie = lire_date(ferie)
        if not date_ferie:
            afficher_erreur("⚠ Veuillez sélectionner une date complète.")
            return

        if on_valider:
            on_valider(date_ferie)
        vider_formulaire()
        afficher_succes()

    bouton_valider = Button(
        fenetre,
        text="VALIDER",
        font=("Comic Sans MS", 13, "bold"),
        bg=COLOR_VALIDER_INACTIF,
        fg="white",
        cursor="hand2",
        command=valider,
        bd=0,
        padx=20,
        pady=5,
        activebackground=COLOR_VALIDER_INACTIF,
    )
    bouton_valider.place(x=VACANCES_CENTER_X, y=VACANCES_Y_START + 235 + FERIE_Y_OFFSET, anchor="center")

    ferie["annee"].trace_add("write", rafraichir_etat_bouton)
    ferie["mois"].trace_add("write", rafraichir_etat_bouton)
    ferie["jour"].trace_add("write", rafraichir_etat_bouton)

    fenetre._ferie_vars = {"date": ferie}
    rafraichir_etat_bouton()


def afficher_onglet_reinitialisation(fenetre, on_mutation=None):
    """Affiche les périodes et jours fériés avec sélection rouge/verte et suppression."""

    def formater_date(dt):
        return dt.strftime("%d/%m/%Y") if isinstance(dt, datetime) else "--/--/----"

    Label(
        fenetre,
        text="PÉRIODES",
        font=("Comic Sans MS", 13),
        fg="white",
        bg=COLOR_PARAMETRE_TEXT,
    ).place(x=RESET_LEFT_X, y=RESET_TITLE_Y, anchor="center")

    Label(
        fenetre,
        text="JOURS FÉRIÉS",
        font=("Comic Sans MS", 13),
        fg="white",
        bg=COLOR_PARAMETRE_TEXT,
    ).place(x=RESET_RIGHT_X, y=RESET_TITLE_Y, anchor="center")

    Label(fenetre, bg=COLOR_PARAMETRE_TEXT).place(
        x=RESET_SEPARATOR_X,
        y=RESET_SEPARATOR_TOP,
        width=2,
        height=RESET_LIST_Y - RESET_SEPARATOR_TOP + tkfont.Font(family="Comic Sans MS", size=11).metrics("linespace") * RESET_LIST_HEIGHT,
    )

    lb_periodes = Listbox(
        fenetre,
        width=RESET_LIST_WIDTH,
        height=RESET_LIST_HEIGHT,
        font=("Comic Sans MS", 11),
        bg="white",
        fg="#1B4332",
        selectbackground="#D8F3DC",
        activestyle="none",
    )
    lb_periodes.place(x=RESET_LEFT_X, y=RESET_LIST_Y, anchor="n")

    lb_feries = Listbox(
        fenetre,
        width=RESET_LIST_WIDTH,
        height=RESET_LIST_HEIGHT,
        font=("Comic Sans MS", 11),
        bg="white",
        fg="#1B4332",
        selectbackground="#D8F3DC",
        activestyle="none",
    )
    lb_feries.place(x=RESET_RIGHT_X, y=RESET_LIST_Y, anchor="n")

    label_message = Label(fenetre, text="", font=("Comic Sans MS", 11, "bold"), fg="#2E7D32", bg=COLOR_BODY_BG)
    label_message.place(x=VACANCES_CENTER_X, y=742, anchor="center")

    red_periodes = set()
    red_feries = set()
    ferie_values = []

    def mettre_couleur_ligne(listbox, index, rouge):
        listbox.itemconfig(index, fg=("red" if rouge else "#1B4332"))

    def annuler_disparition_message():
        after_id = getattr(fenetre, "_reset_message_after_id", None)
        if after_id:
            fenetre.after_cancel(after_id)
            fenetre._reset_message_after_id = None

    def masquer_message():
        label_message.config(text="")
        fenetre._reset_message_after_id = None

    def maj_bouton():
        actif = bool(red_periodes or red_feries)
        couleur = "#2E7D32" if actif else COLOR_VALIDER_INACTIF
        bouton_valider.config(bg=couleur, activebackground=couleur)

    def recharger_listes():
        nonlocal ferie_values
        red_periodes.clear()
        red_feries.clear()
        annuler_disparition_message()
        label_message.config(text="")

        lb_periodes.delete(0, "end")
        for idx, periode in enumerate(PERIODES_SCOLAIRES):
            bornes = periodes.get(periode, [])
            if len(bornes) == 2:
                date_debut, date_fin = bornes
                texte = f"{periode.upper()} : {formater_date(date_debut)} -> {formater_date(date_fin)}"
            else:
                texte = f"{periode.upper()} : --/--/---- -> --/--/----"
            lb_periodes.insert("end", texte)
            mettre_couleur_ligne(lb_periodes, idx, False)

        lb_feries.delete(0, "end")
        ferie_values = list(periodes.get("ferie", []))
        if ferie_values:
            for idx, date_ferie in enumerate(ferie_values):
                lb_feries.insert("end", formater_date(date_ferie))
                mettre_couleur_ligne(lb_feries, idx, False)
        else:
            lb_feries.insert("end", "Aucun jour férié enregistré")
            mettre_couleur_ligne(lb_feries, 0, False)

        maj_bouton()

    def toggle_ligne(listbox, index, red_set):
        if index in red_set:
            red_set.remove(index)
            mettre_couleur_ligne(listbox, index, False)
        else:
            red_set.add(index)
            mettre_couleur_ligne(listbox, index, True)
        maj_bouton()

    def on_click_periodes(_event):
        selection = lb_periodes.curselection()
        if not selection:
            return "break"
        idx = selection[0]
        toggle_ligne(lb_periodes, idx, red_periodes)
        lb_periodes.selection_clear(0, "end")
        return "break"

    def on_click_feries(_event):
        selection = lb_feries.curselection()
        if not selection:
            return "break"
        idx = selection[0]
        if not ferie_values:
            lb_feries.selection_clear(0, "end")
            return "break"
        toggle_ligne(lb_feries, idx, red_feries)
        lb_feries.selection_clear(0, "end")
        return "break"

    def scroll_listbox(listbox, event):
        listbox.yview_scroll(-1 * int(event.delta / 120), "units")
        return "break"

    def valider_suppression():
        if not red_periodes and not red_feries:
            return

        periodes_supprimees = 0
        for idx in sorted(red_periodes):
            cle_periode = PERIODES_SCOLAIRES[idx]
            if periodes.get(cle_periode):
                periodes_supprimees += 1
            periodes[cle_periode] = []

        feries_supprimes = 0
        if ferie_values and red_feries:
            restants = [date_val for i, date_val in enumerate(ferie_values) if i not in red_feries]
            feries_supprimes = len(ferie_values) - len(restants)
            periodes["ferie"] = restants

        if on_mutation:
            on_mutation()

        recharger_listes()
        label_message.config(
            text=f"Suppression effectuée: {periodes_supprimees} période(s), {feries_supprimes} férié(s)."
        )
        fenetre._reset_message_after_id = fenetre.after(5000, masquer_message)

    bouton_valider = Button(
        fenetre,
        text="VALIDER",
        font=("Comic Sans MS", 13, "bold"),
        bg=COLOR_VALIDER_INACTIF,
        fg="white",
        cursor="hand2",
        command=valider_suppression,
        bd=0,
        padx=20,
        pady=5,
        activebackground=COLOR_VALIDER_INACTIF,
    )
    bouton_valider.place(x=VACANCES_CENTER_X, y=705, anchor="center")

    lb_periodes.bind("<<ListboxSelect>>", on_click_periodes)
    lb_feries.bind("<<ListboxSelect>>", on_click_feries)
    lb_periodes.bind("<MouseWheel>", lambda event: scroll_listbox(lb_periodes, event))
    lb_feries.bind("<MouseWheel>", lambda event: scroll_listbox(lb_feries, event))

    recharger_listes()


def afficher_onglet_profil(
    fenetre,
    profil_selectionne=None,
    on_profil_click=None,
    on_profil_back=None,
    on_profil_activites_valider=None,
    on_profil_renommer=None,
    on_nom_existe=None,
):
    """Affiche la liste des profils ou le détail d'un profil sélectionné."""
    if profil_selectionne and profil_selectionne in profils:
        afficher_onglet_profil_detail(
            fenetre,
            profil_selectionne,
            on_profil_back=on_profil_back,
            on_profil_activites_valider=on_profil_activites_valider,
            on_profil_renommer=on_profil_renommer,
            on_nom_existe=on_nom_existe,
        )
        return

    # Liste des profils
    zone_x = (BODY_WIDTH - 440) // 2 + 20
    zone_y = 365
    zone_w = 440
    zone_h = 365

    _placer_titre_section(
        fenetre,
        "img/label_nav_dynanim.png",
        325,
        "LISTE DES PROFILS",
        bg=COLOR_NAV_TEXT_BG,
    )

    canvas = Canvas(fenetre, bg=COLOR_BODY_BG, highlightthickness=0)
    canvas.place(x=zone_x, y=zone_y, width=zone_w, height=zone_h)

    scrollbar = Scrollbar(fenetre, orient="vertical", command=canvas.yview)
    scrollbar.place(x=zone_x + zone_w, y=zone_y, height=zone_h)
    canvas.configure(yscrollcommand=scrollbar.set)

    contenu = Frame(canvas, bg=COLOR_BODY_BG)
    canvas_window = canvas.create_window((0, 0), window=contenu, anchor="nw")

    noms = sorted(profils.keys())
    if not noms:
        Label(
            contenu,
            text="Aucun profil enregistré",
            font=("Comic Sans MS", 12, "italic"),
            fg="#1B4332",
            bg=COLOR_BODY_BG,
        ).pack(anchor="w", padx=10, pady=6)
    else:
        for nom in noms:
            label_profil = Label(
                contenu,
                text=nom,
                font=("Comic Sans MS", 15, "bold"),
                fg="#1B4332",
                bg=COLOR_BODY_BG,
                anchor="w",
                justify="left",
                cursor="hand2",
            )
            label_profil.pack(fill="x", padx=10, pady=4)
            if on_profil_click:
                label_profil.bind("<Button-1>", lambda _e, n=nom: on_profil_click(n))

    def refresh_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ajuster_largeur_contenu(event):
        canvas.itemconfigure(canvas_window, width=event.width)

    def on_mousewheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        return "break"

    contenu.bind("<Configure>", refresh_scroll_region)
    canvas.bind("<Configure>", ajuster_largeur_contenu)
    canvas.bind("<MouseWheel>", on_mousewheel)
    contenu.bind("<MouseWheel>", on_mousewheel)


def afficher_onglet_profil_detail(
    fenetre,
    nom_profil,
    on_profil_back=None,
    on_profil_activites_valider=None,
    on_profil_renommer=None,
    on_nom_existe=None,
):
    """Affiche une interface récapitulative d'un profil."""
    profil = profils.get(nom_profil)
    if not profil:
        return

    _placer_titre_section(
        fenetre,
        "img/label_nav_dynanim.png",
        318,
        nom_profil,
        bg=COLOR_NAV_TEXT_BG,
    )

    # Titre cliquable pour éditer le nom du profil.
    titre_click = Label(
        fenetre,
        text=nom_profil,
        font=("Comic Sans MS", 12, "bold"),
        fg="white",
        bg=COLOR_NAV_TEXT_BG,
        cursor="hand2",
    )
    titre_click.place(x=VACANCES_CENTER_X, y=335, anchor="center")

    label_retour_liste = Label(
        fenetre,
        text="← Retour à la liste",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
        cursor="hand2",
    )
    label_retour_liste.place(x=15, y=327, anchor="w")
    if on_profil_back:
        label_retour_liste.bind("<Button-1>", lambda _e: on_profil_back())

    xp = calculer_xp_reelle_totale_profil(profil, periodes)
    engagement = calculer_score_engagement_profil(profil, periodes)
    progression = infos_progression_niveau(xp)

    # Place l'image d'étoiles à 10 px à droite du titre profil.
    titre_font = tkfont.Font(family="Comic Sans MS", size=12, weight="bold")
    titre_width = titre_font.measure(nom_profil) + 40
    titre_right = VACANCES_CENTER_X + titre_width // 2

    photo_etoiles = _charger_photo(engagement["image_etoiles"], (200, 45))
    label_etoiles = _creer_label_image(fenetre, photo_etoiles, bd=0, highlightthickness=0, bg="#D8F3DC")
    label_etoiles.place(x=titre_right + 10, y=311)

    Label(
        fenetre,
        text=f"Niveau: {progression['niveau']}   |   XP totale réelle: {xp}",
        font=("Comic Sans MS", 14, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=350, y=372, anchor="center")

    Label(
        fenetre,
        text=f"Prochain palier: {progression['xp_palier_suivant']} XP",
        font=("Comic Sans MS", 11),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=350, y=397, anchor="center")

    photo_progress = _charger_photo(progression["image_progression"], (73, 73))
    label_progress = _creer_label_image(fenetre, photo_progress, bd=0, highlightthickness=0, bg="#D8F3DC")
    label_progress.place(x=350, y=445, anchor="center")

    repartition = calculer_repartition_types_anim_profil(profil, periodes)
    type_anim_x = 165
    Label(
        fenetre,
        text="Type d'anim",
        font=("Comic Sans MS", 17, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=type_anim_x, y=420, anchor="center")

    libelles_types = {
        "sportive": "Sportif",
        "manuelle": "Manuelle",
        "simple": "Simple",
        "libre": "Libre",
    }
    y_type = 442
    for type_activite, pourcentage in repartition["types_tries"]:
        texte = f"{libelles_types.get(type_activite, type_activite.title())} a {pourcentage}%"
        Label(
            fenetre,
            text=texte,
            font=("Comic Sans MS", 9, "bold"),
            fg="#1B4332",
            bg=COLOR_BODY_BG,
        ).place(x=type_anim_x, y=y_type, anchor="center")
        y_type += 18


    Frame(fenetre, bg="#FF7500", height=2, width=560).place(x=70, y=522)


    projets = profil.get("projet", {})
    if not isinstance(projets, dict):
        projets = {}
    nb_projets = len(projets)
    points_projets = points_projets_profil(profil)

    penalites = profil.get("penalite", {})
    if not isinstance(penalites, dict):
        penalites = {}
    nb_jours_penalises = compter_jours_penalises_reels(profil, periodes)

    Label(
        fenetre,
        text="Nombre de projets",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=350, y=600, anchor="center")

    Label(
        fenetre,
        text=str(nb_projets),
        font=("Comic Sans MS", 22, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=350, y=635, anchor="center")

    Label(
        fenetre,
        text="Points des projets",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=350, y=670, anchor="center")

    Label(
        fenetre,
        text=str(points_projets),
        font=("Comic Sans MS", 22, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=350, y=705, anchor="center")

    Label(
        fenetre,
        text="Nombre de jours pénalisés",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=560, y=625, anchor="center")

    Label(
        fenetre,
        text=str(nb_jours_penalises),
        font=("Comic Sans MS", 28, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=560, y=680, anchor="center")

    recap_x = 90
    recap_font = ("Comic Sans MS", 11, "bold")
    recap_font_obj = tkfont.Font(family="Comic Sans MS", size=11, weight="bold")

    editeur_widgets = []
    editeur_nom_widgets = []

    def nettoyer_editeur_nom():
        for widget in editeur_nom_widgets:
            if widget.winfo_exists():
                widget.destroy()
        editeur_nom_widgets.clear()

    def ouvrir_editeur_nom(_event=None):
        nettoyer_editeur_nom()

        zone_x = 220
        zone_y = 352
        zone_w = 260
        zone_h = 95

        photo_nom_bg = _charger_photo("img/label_nav_dynanim.png", (zone_w, zone_h))
        label_nom_bg = _creer_label_image(fenetre, photo_nom_bg, bd=0, highlightthickness=0)
        label_nom_bg.place(x=zone_x, y=zone_y)
        editeur_nom_widgets.append(label_nom_bg)

        label_titre_nom = Label(
            fenetre,
            text="Nom / Prénom",
            font=("Comic Sans MS", 10, "bold"),
            fg="white",
            bg=COLOR_NAV_TEXT_BG,
        )
        label_titre_nom.place(x=zone_x + zone_w // 2, y=zone_y + 14, anchor="center")
        editeur_nom_widgets.append(label_titre_nom)

        var_nom = StringVar()
        var_nom.set(nom_profil)
        entree_nom = Entry(fenetre, textvariable=var_nom, font=("Comic Sans MS", 10), width=20)
        entree_nom.place(x=zone_x + zone_w // 2, y=zone_y + 40, anchor="center")
        editeur_nom_widgets.append(entree_nom)

        label_erreur_nom = Label(
            fenetre,
            text="",
            font=("Comic Sans MS", 9, "bold"),
            fg="white",
            bg=COLOR_NAV_TEXT_BG,
        )
        label_erreur_nom.place(x=zone_x + zone_w // 2, y=zone_y + zone_h + 8, anchor="center")
        editeur_nom_widgets.append(label_erreur_nom)

        def nom_est_valide_local(nom):
            nom_nettoye = " ".join(str(nom or "").strip().split())
            lettres = nom_nettoye.replace(" ", "")
            return (
                len(lettres) >= 3
                and len(nom_nettoye) <= MAX_NOM_PROFIL
                and all(char.isalpha() or char == " " for char in nom_nettoye)
            )

        def normaliser_nom_local(nom):
            return " ".join(str(nom or "").strip().split()).upper()

        def majuscule_nom_temps_reel(*_args):
            if getattr(fenetre, "_profil_nom_trace_lock", False):
                return
            saisie = var_nom.get()
            saisie_upper = saisie.upper()
            if saisie != saisie_upper:
                fenetre._profil_nom_trace_lock = True
                var_nom.set(saisie_upper)
                fenetre._profil_nom_trace_lock = False

        def annuler_nom():
            nettoyer_editeur_nom()

        def valider_nom():
            nom_saisi = normaliser_nom_local(var_nom.get())

            if not nom_est_valide_local(nom_saisi):
                label_erreur_nom.config(
                    text=f"Nom invalide (3 lettres min, lettres/espaces, {MAX_NOM_PROFIL} max)"
                )
                return

            if on_nom_existe and nom_saisi != nom_profil and on_nom_existe(nom_saisi):
                label_erreur_nom.config(text="Ce participant existe déjà")
                return

            try:
                if on_profil_renommer:
                    on_profil_renommer(nom_profil, nom_saisi)
            except ValueError as erreur:
                if str(erreur) == "DOUBLON_PROFIL":
                    label_erreur_nom.config(text="Ce participant existe déjà")
                    return
                if str(erreur) == "NOM_INVALIDE":
                    label_erreur_nom.config(
                        text=f"Nom invalide (3 lettres min, lettres/espaces, {MAX_NOM_PROFIL} max)"
                    )
                    return
                label_erreur_nom.config(text="Impossible de modifier ce nom")
                return

            nettoyer_editeur_nom()

        bouton_valider_nom = Button(
            fenetre,
            text="Valider",
            font=("Comic Sans MS", 10, "bold"),
            bg=COLOR_NAV_TEXT_BG,
            fg="white",
            cursor="hand2",
            bd=0,
            padx=12,
            pady=4,
            command=valider_nom,
        )
        bouton_valider_nom.place(x=zone_x + 5, y=zone_y + 70, anchor="w")
        editeur_nom_widgets.append(bouton_valider_nom)

        bouton_annuler_nom = Button(
            fenetre,
            text="Annuler",
            font=("Comic Sans MS", 10, "bold"),
            bg=COLOR_VALIDER_INACTIF,
            fg="white",
            cursor="hand2",
            bd=0,
            padx=12,
            pady=4,
            command=annuler_nom,
        )
        bouton_annuler_nom.place(x=zone_x + 105, y=zone_y + 70, anchor="w")
        editeur_nom_widgets.append(bouton_annuler_nom)

        var_nom.trace_add("write", majuscule_nom_temps_reel)
        entree_nom.focus_set()

    def nettoyer_editeur():
        for widget in editeur_widgets:
            if widget.winfo_exists():
                widget.destroy()
        editeur_widgets.clear()

    def ouvrir_editeur_periode(periode, y_ligne):
        nettoyer_editeur()

        x_depart = 220
        x_positions = [x_depart, x_depart + 110, x_depart + 220, x_depart + 330]
        y_titres = y_ligne - 2
        y_champs = y_ligne + 23

        editeur_width = (x_positions[-1] - x_positions[0]) + 130
        editeur_height = 84
        editeur_x = x_positions[0] - 65
        editeur_y = y_ligne - 22

        photo_editeur_bg = _charger_photo("img/label_nav_dynanim.png", (editeur_width, editeur_height))
        label_editeur_bg = _creer_label_image(fenetre, photo_editeur_bg, bd=0, highlightthickness=0)
        label_editeur_bg.place(x=editeur_x, y=editeur_y)
        editeur_widgets.append(label_editeur_bg)

        activites_periode = profil.get("activites", {}).get(periode, {})
        vars_activites = {}

        for index, jour in enumerate(JOURS_ACTIVITE):
            label_jour = Label(
                fenetre,
                text=jour,
                font=("Comic Sans MS", 10, "bold"),
                fg="white",
                bg=COLOR_NAV_TEXT_BG,
            )
            label_jour.place(x=x_positions[index], y=y_titres, anchor="center")
            editeur_widgets.append(label_jour)

            var_activite = StringVar()
            mapping_jour = {
                "Lundi": "lundi",
                "Mardi": "mardi",
                "Jeudi": "jeudi",
                "Vendredi": "vendredi",
            }
            valeur_initiale = activites_periode.get(mapping_jour[jour], "")
            var_activite.set(valeur_initiale)
            vars_activites[jour] = var_activite

            opt = OptionMenu(fenetre, var_activite, "", *ACTIVITES)
            _style_optionmenu_blanc(opt)
            opt.config(width=10)
            opt.place(x=x_positions[index], y=y_champs, anchor="center")
            editeur_widgets.append(opt)

        label_erreur = Label(
            fenetre,
            text="",
            font=("Comic Sans MS", 9, "bold"),
            fg="white",
            bg=COLOR_NAV_TEXT_BG,
        )
        label_erreur.place(x=x_positions[1] + 70, y=y_champs + 27, anchor="center")
        editeur_widgets.append(label_erreur)

        def valider_editeur():
            nouvelles_activites = {jour: vars_activites[jour].get().strip() for jour in JOURS_ACTIVITE}
            if not all(nouvelles_activites.values()):
                label_erreur.config(text="Veuillez compléter tous les champs")
                return

            label_erreur.config(text="")
            activites_profil = profil.setdefault("activites", {})
            activites_profil.setdefault(periode, {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""})

            mapping_jour = {
                "Lundi": "lundi",
                "Mardi": "mardi",
                "Jeudi": "jeudi",
                "Vendredi": "vendredi",
            }
            for jour, valeur in nouvelles_activites.items():
                activites_profil[periode][mapping_jour[jour]] = valeur

            if on_profil_activites_valider:
                on_profil_activites_valider(nom_profil, periode, nouvelles_activites)
            nettoyer_editeur()

        bouton_valider = Button(
            fenetre,
            text="Valider",
            font=("Comic Sans MS", 10, "bold"),
            bg=COLOR_NAV_TEXT_BG,
            fg="white",
            cursor="hand2",
            bd=0,
            padx=12,
            pady=4,
            command=valider_editeur,
        )
        bouton_valider.place(x=75, y=470, anchor="w")
        editeur_widgets.append(bouton_valider)

        bouton_annuler = Button(
            fenetre,
            text="Annuler",
            font=("Comic Sans MS", 10, "bold"),
            bg=COLOR_VALIDER_INACTIF,
            fg="white",
            cursor="hand2",
            bd=0,
            padx=12,
            pady=4,
            command=nettoyer_editeur,
        )
        bouton_annuler.place(x=75, y=500, anchor="w")
        editeur_widgets.append(bouton_annuler)

    y = 550
    for periode in PERIODES_SCOLAIRES:
        y_ligne = y
        points_semaine = points_semaine_type_periode(profil, periode)
        note_image = None
        texte_ligne = f"{periode.upper()}  |"
        if points_semaine > 0:
            _note_lettre, note_image = note_depuis_points_semaine(points_semaine)
        else:
            texte_ligne = f"{periode.upper()}  |  Non compté"

        nav_width = recap_font_obj.measure(texte_ligne) + 24
        nav_height = 28
        photo_periode_bg = _charger_photo("img/label_nav_dynanim.png", (nav_width, nav_height))
        label_periode_bg = _creer_label_image(
            fenetre,
            photo_periode_bg,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        label_periode_bg.place(x=recap_x, y=y_ligne - 2)

        label_periode = Label(
            fenetre,
            text=texte_ligne,
            font=recap_font,
            fg="white",
            bg=COLOR_NAV_TEXT_BG,
            cursor="hand2",
        )
        label_periode.place(x=recap_x + nav_width // 2, y=y_ligne + 12, anchor="center")
        label_periode_bg.bind("<Button-1>", lambda _e, p=periode, yl=y_ligne: ouvrir_editeur_periode(p, yl))
        label_periode.bind("<Button-1>", lambda _e, p=periode, yl=y_ligne: ouvrir_editeur_periode(p, yl))

        if note_image:
            photo_note = _charger_photo(note_image, (55, 32))
            label_note = _creer_label_image(fenetre, photo_note, bd=0, highlightthickness=0, bg=COLOR_BODY_BG)
            note_x = recap_x + nav_width + 8
            label_note.place(x=note_x, y=y_ligne - 4)
            label_note.bind("<Button-1>", lambda _e, p=periode, yl=y_ligne: ouvrir_editeur_periode(p, yl))
        y += 45

    titre_click.bind("<Button-1>", ouvrir_editeur_nom)


def afficher_dynanim_body(
    fenetre,
    app_actif,
    dynanim_onglet_actif="ACCUEIL",
    parametre_onglet_actif="VACANCES",
    profil_selectionne=None,
    on_logo_click=None,
    on_retour_click=None,
    on_tab_click=None,
    on_parametre_tab_click=None,
    on_profil_click=None,
    on_profil_back=None,
    on_profil_activites_valider=None,
    on_profil_renommer=None,
    on_ajout_valider=None,
    on_nom_existe=None,
    on_vacances_valider=None,
    on_ferie_valider=None,
    on_parametre_mutation=None,
    on_projets_valider=None,
    on_penalites_valider=None,
):
    label_dynanim = None
    label_retour = None

    # region Logo Retour
    if app_actif != "ACCUEIL":
        photo_retour = _charger_photo("img/retour.png", BODY_RETOUR_SIZE)
        label_retour = _creer_label_image(
            fenetre,
            photo_retour,
            bd=0,
            highlightthickness=0,
            bg=COLOR_BODY_BG,
            cursor="hand2",
        )
        label_retour.place(x=BODY_RETOUR_POS[0], y=BODY_RETOUR_POS[1])
        if on_retour_click:
            label_retour.bind("<Button-1>", lambda _e: on_retour_click())
    # endregion

    # region Logo Dynanim
    if app_actif == "ACCUEIL":
        photo_dynanim = _charger_photo("img/logo_dynanim.png", BODY_DYNANIM_SIZE)
        label_dynanim = _creer_label_image(
            fenetre,
            photo_dynanim,
            bd=0,
            highlightthickness=0,
            bg=COLOR_BODY_BG,
            cursor="hand2",
        )
        label_dynanim.place(x=BODY_DYNANIM_POS[0], y=BODY_DYNANIM_POS[1])
        if on_logo_click:
            label_dynanim.bind("<Button-1>", lambda _e: on_logo_click())
    # endregion

    # region Navigation Dynanim
    if app_actif == "DYNANIM":
        dynanim_onglet_actif = dynanim_onglet_actif or "ACCUEIL"

        photo_nav = _charger_photo("img/label_nav_dynanim.png", NAV_TAB_SIZE)

        total_tabs_width = len(NAV_TAB_LABELS) * NAV_TAB_SIZE[0]
        espace_x = int((BODY_WIDTH - total_tabs_width) / (len(NAV_TAB_LABELS) + 1))

        for index, texte in enumerate(NAV_TAB_LABELS):
            x_tab = BODY_X + espace_x + index * (NAV_TAB_SIZE[0] + espace_x)
            nav_font = NAV_TAB_FONT_ACTIVE if texte == dynanim_onglet_actif else NAV_TAB_FONT

            label_nav_bg = _creer_label_image(fenetre, photo_nav, bd=0, highlightthickness=0, cursor="hand2")
            label_nav_bg.place(x=x_tab, y=NAV_TAB_Y)

            label_nav_text = Label(
                fenetre,
                text=texte,
                font=nav_font,
                fg="white",
                bg=COLOR_NAV_TEXT_BG,
                cursor="hand2",
            )
            label_nav_text.place(
                x=x_tab + NAV_TAB_SIZE[0] // 2,
                y=NAV_TAB_Y + NAV_TAB_SIZE[1] // 2,
                anchor="center",
            )

            if on_tab_click:
                onglet = texte  # capture locale pour la lambda
                label_nav_bg.bind("<Button-1>", lambda _e, o=onglet: on_tab_click(o))
                label_nav_text.bind("<Button-1>", lambda _e, o=onglet: on_tab_click(o))
    # endregion

    # region Contenu onglet actif (Dynanim)
    if app_actif == "DYNANIM":
        if dynanim_onglet_actif == "AJOUT":
            afficher_onglet_ajout(fenetre, on_valider=on_ajout_valider, nom_existe=on_nom_existe)
        elif dynanim_onglet_actif == "PROFILS":
            afficher_onglet_profil(
                fenetre,
                profil_selectionne=profil_selectionne,
                on_profil_click=on_profil_click,
                on_profil_back=on_profil_back,
                on_profil_activites_valider=on_profil_activites_valider,
                on_profil_renommer=on_profil_renommer,
                on_nom_existe=on_nom_existe,
            )
        elif dynanim_onglet_actif == "+ / -":
            afficher_onglet_bonus_malus(
                fenetre,
                on_projets_valider=on_projets_valider,
                on_penalites_valider=on_penalites_valider,
            )

    if app_actif == "PARAMETRE":
        afficher_parametre_body(
            fenetre,
            parametre_onglet_actif=parametre_onglet_actif,
            on_parametre_tab_click=on_parametre_tab_click,
            on_vacances_valider=on_vacances_valider,
            on_ferie_valider=on_ferie_valider,
            on_parametre_mutation=on_parametre_mutation,
        )
    # endregion

    return label_dynanim or label_retour


def afficher_onglet_bonus_malus(
    fenetre,
    on_projets_valider=None,
    on_penalites_valider=None,
):
    """Affiche l'onglet BONUS/MALUS pour gérer projets et pénalités."""
    def _safe_set_error(label_widget, message):
        """Evite les crashs si le callback a redessine l'UI et detruit le widget."""
        try:
            if label_widget and label_widget.winfo_exists():
                label_widget.config(text=message)
        except TclError:
            pass

    # Fonction pour calculer la taille du label_nav adapté au texte
    def _creer_titre_avec_nav(x_center, y, texte):
        f = tkfont.Font(family="Comic Sans MS", size=14, weight="bold")
        texte_width = f.measure(texte) + 40  # 20px de marge de chaque côté
        texte_height = 40
        
        photo_titre = _charger_photo("img/label_nav_dynanim.png", (texte_width, texte_height))
        label_nav_bg = _creer_label_image(fenetre, photo_titre, bd=0, highlightthickness=0)
        label_nav_bg.place(x=x_center - texte_width // 2, y=y)
        
        Label(
            fenetre,
            text=texte,
            font=("Comic Sans MS", 14, "bold"),
            fg="white",
            bg="#FF7500",
        ).place(x=x_center, y=y + 20, anchor="center")
    
    # region Projets
    # Titre PROJETS avec label_nav adapté
    _creer_titre_avec_nav(150, 320, "PROJETS")

    Label(
        fenetre,
        text="Nom du projet:",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=150, y=380, anchor="center")

    var_projet_nom = StringVar()
    entry_projet_nom = Entry(fenetre, textvariable=var_projet_nom, font=("Comic Sans MS", 10), width=20)
    entry_projet_nom.place(x=150, y=405, anchor="center")

    Label(
        fenetre,
        text="Valeur:",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=150, y=435, anchor="center")

    var_projet_valeur = StringVar()
    var_projet_valeur.set("10")
    opt_projet_valeur = OptionMenu(fenetre, var_projet_valeur, "10", "20", "30")
    opt_projet_valeur.place(x=150, y=465, anchor="center")

    Label(
        fenetre,
        text="Profils:",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=150, y=500, anchor="center")

    noms_profils = sorted(profils.keys())
    profils_selectionnes = set()
    labels_profils = {}

    def rafraichir_style_profil(nom):
        label = labels_profils.get(nom)
        if not label:
            return
        try:
            if not label.winfo_exists():
                return
            if nom in profils_selectionnes:
                label.config(bg="#FF7500", fg="white")
            else:
                label.config(bg=COLOR_BODY_BG, fg="#1B4332")
        except TclError:
            pass

    def toggle_profil(nom):
        if nom in profils_selectionnes:
            profils_selectionnes.remove(nom)
        else:
            profils_selectionnes.add(nom)
        rafraichir_style_profil(nom)

    y_depart_profils = 525
    ecart_profils = 26
    for index, nom in enumerate(noms_profils):
        label_profil = Label(
            fenetre,
            text=nom,
            font=("Comic Sans MS", 10),
            fg="#1B4332",
            bg=COLOR_BODY_BG,
            cursor="hand2",
        )
        label_profil.place(x=150, y=y_depart_profils + index * ecart_profils, anchor="center")
        label_profil.bind("<Button-1>", lambda _e, n=nom: toggle_profil(n))
        labels_profils[nom] = label_profil

    def valider_projets():
        nom = var_projet_nom.get().strip()
        if not nom:
            _safe_set_error(label_erreur_projet, "⚠ Saisir un nom de projet")
            return
        if len(nom) < 3 or len(nom) > 20:
            _safe_set_error(label_erreur_projet, "⚠ Nom projet: 3 a 20 caracteres")
            return
        valeur = var_projet_valeur.get()
        profils_selectes = [nom_profil for nom_profil in noms_profils if nom_profil in profils_selectionnes]
        if not profils_selectes:
            _safe_set_error(label_erreur_projet, "⚠ Selectionner au moins un profil")
            return
        try:
            if on_projets_valider:
                on_projets_valider(nom, valeur, profils_selectes)
        except Exception:
            _safe_set_error(label_erreur_projet, "⚠ Impossible d'enregistrer le projet")
            return
        _safe_set_error(label_erreur_projet, "")
        try:
            if entry_projet_nom.winfo_exists():
                var_projet_nom.set("")
            profils_selectionnes.clear()
            for nom_profil in noms_profils:
                rafraichir_style_profil(nom_profil)
        except TclError:
            pass

    Button(
        fenetre,
        text="Valider Projets",
        font=("Comic Sans MS", 11, "bold"),
        bg="#FF7500",
        fg="white",
        cursor="hand2",
        command=valider_projets,
    ).place(x=150, y=690, anchor="center")

    label_erreur_projet = Label(
        fenetre,
        text="",
        font=("Comic Sans MS", 9, "bold"),
        fg="red",
        bg=COLOR_BODY_BG,
    )
    label_erreur_projet.place(x=150, y=730, anchor="center")
    # endregion

    # region Pénalités
    # Titre PÉNALITÉS avec label_nav adapté
    _creer_titre_avec_nav(450, 320, "PÉNALITÉS")

    Label(
        fenetre,
        text="Profil:",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=450, y=380, anchor="center")

    var_penalite_profil = StringVar()
    opt_penalite_profil = OptionMenu(fenetre, var_penalite_profil, *noms_profils)
    opt_penalite_profil.place(x=450, y=405, anchor="center")

    Label(
        fenetre,
        text="Date:",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=450, y=435, anchor="center")

    annee_actuelle = datetime.now().year
    annees_list = [str(annee_actuelle - 1), str(annee_actuelle), str(annee_actuelle + 1)]
    mois_list = ["01-Janvier", "02-Février", "03-Mars", "04-Avril", "05-Mai", "06-Juin",
                 "07-Juillet", "08-Août", "09-Septembre", "10-Octobre", "11-Novembre", "12-Décembre"]

    var_penalite_annee = StringVar()
    var_penalite_annee.set(str(annee_actuelle))
    var_penalite_mois = StringVar()
    var_penalite_jour = StringVar()

    opt_annee = OptionMenu(fenetre, var_penalite_annee, *annees_list)
    _style_optionmenu_blanc(opt_annee)
    opt_annee.config(width=6)
    opt_annee.place(x=350, y=465, anchor="center")

    opt_mois = OptionMenu(fenetre, var_penalite_mois, *mois_list)
    _style_optionmenu_blanc(opt_mois)
    opt_mois.config(width=12)
    opt_mois.place(x=465, y=465, anchor="center")

    opt_jour = OptionMenu(fenetre, var_penalite_jour, "")
    _style_optionmenu_blanc(opt_jour)
    opt_jour.config(width=4)
    opt_jour.place(x=575, y=465, anchor="center")

    def mettre_a_jour_jours_penalite(*_args):
        annee_str = var_penalite_annee.get().strip()
        mois_str = var_penalite_mois.get().strip()
        opt_jour["menu"].delete(0, "end")

        # Le jour est toujours réinitialisé quand année/mois change.
        var_penalite_jour.set("")

        if not annee_str or not mois_str:
            return

        try:
            mois_int = int(mois_str.split("-")[0])
            nb_jours = calendar.monthrange(int(annee_str), mois_int)[1]
        except (ValueError, IndexError):
            return

        for i in range(1, nb_jours + 1):
            jour_str = f"{i:02d}"
            opt_jour["menu"].add_command(label=jour_str, command=lambda j=jour_str: var_penalite_jour.set(j))

    var_penalite_annee.trace_add("write", mettre_a_jour_jours_penalite)
    var_penalite_mois.trace_add("write", mettre_a_jour_jours_penalite)

    Label(
        fenetre,
        text="Valeur (points):",
        font=("Comic Sans MS", 11, "bold"),
        fg="#1B4332",
        bg=COLOR_BODY_BG,
    ).place(x=450, y=500, anchor="center")

    var_penalite_valeur = StringVar()
    var_penalite_valeur.set("0")
    opt_penalite_valeur = OptionMenu(fenetre, var_penalite_valeur, "0", "1", "2", "3")
    opt_penalite_valeur.place(x=450, y=530, anchor="center")

    def _set_message_penalite(message, color="red", ttl_ms=None):
        try:
            if not label_message_penalite.winfo_exists():
                return
            label_message_penalite.config(text=message, fg=color)
            ancien_after = getattr(fenetre, "_penalite_msg_after_id", None)
            if ancien_after:
                try:
                    fenetre.after_cancel(ancien_after)
                except TclError:
                    pass
                fenetre._penalite_msg_after_id = None

            if ttl_ms:
                fenetre._penalite_msg_after_id = fenetre.after(
                    ttl_ms,
                    lambda: _safe_set_error(label_message_penalite, ""),
                )
        except TclError:
            pass

    def valider_penalites():
        profil_nom = var_penalite_profil.get()
        if not profil_nom:
            _set_message_penalite("⚠ Sélectionner un profil", "red")
            return
        annee = var_penalite_annee.get()
        mois_str = var_penalite_mois.get()
        jour = var_penalite_jour.get()
        if not annee or not mois_str or not jour:
            _set_message_penalite("⚠ Date incomplète", "red")
            return
        try:
            mois = int(mois_str.split("-")[0])
            date_penalite = datetime(int(annee), mois, int(jour))
        except ValueError:
            _set_message_penalite("⚠ Date invalide", "red")
            return
        valeur = int(var_penalite_valeur.get())
        if on_penalites_valider:
            on_penalites_valider(profil_nom, date_penalite, valeur)

        try:
            var_penalite_profil.set("")
            var_penalite_annee.set(str(annee_actuelle))
            var_penalite_mois.set("")
            var_penalite_jour.set("")
            var_penalite_valeur.set("0")
        except TclError:
            pass
        _set_message_penalite("Pénalité enregistrée", "#1B4332", ttl_ms=5000)

    Button(
        fenetre,
        text="Valider Pénalité",
        font=("Comic Sans MS", 11, "bold"),
        bg="#FF7500",
        fg="white",
        cursor="hand2",
        command=valider_penalites,
    ).place(x=450, y=690, anchor="center")

    label_message_penalite = Label(
        fenetre,
        text="",
        font=("Comic Sans MS", 9, "bold"),
        fg="red",
        bg=COLOR_BODY_BG,
    )
    label_message_penalite.place(x=450, y=730, anchor="center")
    # endregion


