from datetime import datetime
from tkinter import Label, TclError
from PIL import Image, ImageTk
from main import annee_scolaire_propre, date_du_jour_propre

# Constantes UI (tailles / positions)
HEADER_BG_SIZE = (700, 200)
BODY_BG_SIZE = (700, 600)
BODY_BG_POS = (0, 200)
BODY_BG_REL = (1, 0.75)

LOGO_HEADER_SIZE = (120, 60)
LOGO_LE_MANS_POS = (230, 10)
LOGO_SEED_POS = (355, 10)

LABEL_INFO_DATE_SIZE = (270, 40)
LABEL_INFO_DATE_BG_POS = (215, 70)
LABEL_INFO_DATE_TEXT_POS = (350, 90)

LABEL_INFO_HEURE_SIZE = (70, 40)
LABEL_INFO_HEURE_BG_POS = (70, 20)
LABEL_INFO_HEURE_TEXT_POS = (107, 40)

LABEL_INFO_ANNEE_SIZE = (150, 60)
LABEL_INFO_ANNEE_BG_POS = (500, 20)
LABEL_INFO_ANNEE_TITLE_POS = (575, 37)
LABEL_INFO_ANNEE_VALUE_POS = (575, 62)

LABEL_INFO_APP_SIZE = (200, 40)
LABEL_INFO_APP_BG_POS = (250, 222)
LABEL_INFO_APP_TEXT_POS = (350, 241)
LABEL_INFO_PARAMETRE_SIZE = (40, 40)
LABEL_INFO_PARAMETRE_POS = (460, 225)

COLOR_LABEL_TEXT_BG = "#1B4332"
COLOR_PARAM_BG = "#D8F3DC"
CLOCK_FORMAT = "%HH%M"
IMG_HEADER_BG = "img/header_bg.png"
IMG_LABEL_INFO = "img/label_info.png"


def _charger_photo(path, size):
    """Charge une image et retourne un PhotoImage redimensionné."""
    image_originale = Image.open(path)
    image_redimensionnee = image_originale.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image_redimensionnee)


def _creer_label_image(fenetre, photo, **kwargs):
    """Crée un Label image et garde la référence pour éviter le garbage collection."""
    label = Label(fenetre, image=photo, **kwargs)
    label.image = photo
    return label

def afficher_header(fenetre):
    # Background du header
    photo = _charger_photo(IMG_HEADER_BG, HEADER_BG_SIZE)
    label_image = _creer_label_image(fenetre, photo)
    label_image.pack(fill="x", pady=0)

    # Second affichage de la même image pour le body
    photo_body = _charger_photo(IMG_HEADER_BG, BODY_BG_SIZE)
    label_body = _creer_label_image(fenetre, photo_body)
    label_body.place(
        x=BODY_BG_POS[0],
        y=BODY_BG_POS[1],
        relwidth=BODY_BG_REL[0],
        relheight=BODY_BG_REL[1],
    )

    # Logo Le Mans
    photo_logo_le_mans = _charger_photo("img/logo_le_mans.png", LOGO_HEADER_SIZE)
    label_logo_le_mans = _creer_label_image(fenetre, photo_logo_le_mans, bd=0, highlightthickness=0)
    label_logo_le_mans.place(x=LOGO_LE_MANS_POS[0], y=LOGO_LE_MANS_POS[1])

    # Logo Seed
    photo_logo_seed = _charger_photo("img/logo_seed.png", LOGO_HEADER_SIZE)
    label_logo_seed = _creer_label_image(fenetre, photo_logo_seed, bd=0, highlightthickness=0)
    label_logo_seed.place(x=LOGO_SEED_POS[0], y=LOGO_SEED_POS[1])

    return label_image, label_body, label_logo_le_mans, label_logo_seed

def afficher_info_header(fenetre, app_actif, on_parametre_click=None):
    #region Date du jour
    # BACKGROUND
    photo_info = _charger_photo(IMG_LABEL_INFO, LABEL_INFO_DATE_SIZE)
    label_info = _creer_label_image(fenetre, photo_info)
    label_info.place(x=LABEL_INFO_DATE_BG_POS[0], y=LABEL_INFO_DATE_BG_POS[1])

    # DATE
    label_date = Label(
        fenetre,
        text=date_du_jour_propre,
        font=("Comic Sans MS", 12),
        fg="white",
        bg=COLOR_LABEL_TEXT_BG,
    )
    label_date.place(x=LABEL_INFO_DATE_TEXT_POS[0], y=LABEL_INFO_DATE_TEXT_POS[1], anchor="center")
    #endregion

    #region Heure actuelle
    # BACKGROUND
    photo_heure = _charger_photo(IMG_LABEL_INFO, LABEL_INFO_HEURE_SIZE)
    label_heure_bg = _creer_label_image(fenetre, photo_heure)
    label_heure_bg.place(x=LABEL_INFO_HEURE_BG_POS[0], y=LABEL_INFO_HEURE_BG_POS[1])

    # HEURE
    label_heure = Label(
        fenetre,
        text=datetime.now().strftime(CLOCK_FORMAT),
        font=("Comic Sans MS", 12),
        fg="white",
        bg=COLOR_LABEL_TEXT_BG,
    )
    label_heure.place(x=LABEL_INFO_HEURE_TEXT_POS[0], y=LABEL_INFO_HEURE_TEXT_POS[1], anchor="center")

    # Horloge temps réel (annule l'ancienne boucle si l'UI est redessinée)
    if hasattr(fenetre, "_heure_after_id") and fenetre._heure_after_id:
        try:
            fenetre.after_cancel(fenetre._heure_after_id)
        except TclError:
            pass

    def mettre_a_jour_heure():
        if not label_heure.winfo_exists():
            return
        label_heure.config(text=datetime.now().strftime(CLOCK_FORMAT))
        fenetre._heure_after_id = fenetre.after(1000, mettre_a_jour_heure)

    mettre_a_jour_heure()
    #endregion

    #region Année scolaire actuelle
    # BACKGROUND
    photo_annee = _charger_photo(IMG_LABEL_INFO, LABEL_INFO_ANNEE_SIZE)
    label_annee_bg = _creer_label_image(fenetre, photo_annee)
    label_annee_bg.place(x=LABEL_INFO_ANNEE_BG_POS[0], y=LABEL_INFO_ANNEE_BG_POS[1])

    # TEXTE FIXE
    label_annee = Label(
        fenetre,
        text="Année scolaire",
        font=("Comic Sans MS", 12),
        fg="white",
        bg=COLOR_LABEL_TEXT_BG,
    )
    label_annee.place(x=LABEL_INFO_ANNEE_TITLE_POS[0], y=LABEL_INFO_ANNEE_TITLE_POS[1], anchor="center")

    # VALEUR
    label_annee_valeur = Label(
        fenetre,
        text=annee_scolaire_propre,
        font=("Comic Sans MS", 12),
        fg="white",
        bg=COLOR_LABEL_TEXT_BG,
    )
    label_annee_valeur.place(x=LABEL_INFO_ANNEE_VALUE_POS[0], y=LABEL_INFO_ANNEE_VALUE_POS[1], anchor="center")
    #endregion

    #region App active
    # BACKGROUND
    photo_app = _charger_photo(IMG_LABEL_INFO, LABEL_INFO_APP_SIZE)
    label_app_bg = _creer_label_image(fenetre, photo_app)
    label_app_bg.place(x=LABEL_INFO_APP_BG_POS[0], y=LABEL_INFO_APP_BG_POS[1])

    # VALEUR
    label_app = Label(fenetre, text=app_actif, font=("Comic Sans MS", 15), fg="white", bg=COLOR_LABEL_TEXT_BG)
    label_app.place(x=LABEL_INFO_APP_TEXT_POS[0], y=LABEL_INFO_APP_TEXT_POS[1], anchor="center")

    # Logo Paramètre (visible uniquement depuis l'accueil)
    if app_actif == "ACCUEIL":
        photo_parametre = _charger_photo("img/logo_parametre.png", LABEL_INFO_PARAMETRE_SIZE)
        label_parametre = _creer_label_image(
            fenetre,
            photo_parametre,
            bd=0,
            highlightthickness=0,
            bg=COLOR_PARAM_BG,
            cursor="hand2",
        )
        label_parametre.place(x=LABEL_INFO_PARAMETRE_POS[0], y=LABEL_INFO_PARAMETRE_POS[1])
        if on_parametre_click:
            label_parametre.bind("<Button-1>", lambda _e: on_parametre_click())
    #endregion

    return label_info, label_date, label_heure_bg, label_heure, label_annee_bg, label_annee, label_annee_valeur, label_app_bg, label_app

