from tkinter import Label, Entry, OptionMenu, StringVar, Button
from PIL import Image, ImageTk
from datetime import datetime
import calendar

# Constantes UI Dynanim (tailles / positions)
BODY_RETOUR_SIZE = (30, 30)
BODY_RETOUR_POS = (200, 230)
BODY_DYNANIM_SIZE = (100, 100)
BODY_DYNANIM_POS = (50, 300)
COLOR_BODY_BG = "#D8F3DC"
COLOR_NAV_TEXT_BG = "#FF7500"
COLOR_VALIDER_INACTIF = "#F3A6A6"

BODY_WIDTH = 700
BODY_X = 0

NAV_TAB_SIZE = (110, 40)
NAV_TAB_Y = 267  # Juste sous le label app_actif (y=222 + h=40 + 5px gap)
NAV_TAB_LABELS = ["AJOUT", "PROFIL", "ACCUEIL", "+ / -", "STATS"]
NAV_TAB_FONT = ("Comic Sans MS", 11)
NAV_TAB_FONT_ACTIVE = ("Comic Sans MS", 12, "bold")

# Constantes AJOUT
ACTIVITES = ["sportive", "manuelle", "simple", "libre"]
JOURS_ACTIVITE = ["Lundi", "Mardi", "Jeudi", "Vendredi"]
AJOUT_FONT_LABEL = ("Comic Sans MS", 12, "bold")
AJOUT_FONT_ENTRY = ("Comic Sans MS", 11)
AJOUT_CENTER_X = 350
AJOUT_Y_START = 335          # Décalé pour éviter collision avec la barre de navigation
AJOUT_TITLE_BG_SIZE = (250, 35)  # Fond label_nav_dynanim derrière chaque titre de section


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
        nom = nom.strip()
        lettres = nom.replace(" ", "")
        return len(lettres) >= 3 and all(char.isalpha() or char == " " for char in nom)

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
            afficher_erreur("⚠ Nom / Prénom invalide (3 lettres min, seulement lettres et espaces).")
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


def afficher_dynanim_body(
    fenetre,
    app_actif,
    dynanim_onglet_actif="ACCUEIL",
    on_logo_click=None,
    on_retour_click=None,
    on_tab_click=None,
    on_ajout_valider=None,
    on_nom_existe=None,
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
    # endregion

    return label_dynanim or label_retour

