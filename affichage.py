from datetime import datetime
from tkinter import Label
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

LABEL_INFO_ONGLET_SIZE = (200, 40)
LABEL_INFO_ONGLET_BG_POS = (250, 222)
LABEL_INFO_ONGLET_TEXT_POS = (350, 241)

BODY_RETOUR_SIZE = (30, 30)
BODY_RETOUR_POS = (200, 230)
BODY_DYNANIM_SIZE = (100, 100)
BODY_DYNANIM_POS = (50, 300)

COLOR_BODY_BG = "#D8F3DC"
COLOR_LABEL_TEXT_BG = "#1B4332"
CLOCK_FORMAT = "%HH%M"

def afficher_header(fenetre):
    # Background du header
    image_originale = Image.open("img/header_bg.png")
    image_redimensionnee = image_originale.resize(HEADER_BG_SIZE, Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redimensionnee)
    label_image = Label(fenetre, image=photo)
    label_image.image = photo  # Garder la référence
    label_image.pack(fill="x", pady=0)
    # Second affichage de la même image pour le body
    image_originale_body = Image.open("img/header_bg.png")
    image_redimensionnee_body = image_originale_body.resize(BODY_BG_SIZE, Image.Resampling.LANCZOS)  # Couvre jusqu'en bas
    photo_body = ImageTk.PhotoImage(image_redimensionnee_body)
    label_body = Label(fenetre, image=photo_body)
    label_body.image = photo_body  # Garder la référence
    label_body.place(x=BODY_BG_POS[0], y=BODY_BG_POS[1], relwidth=BODY_BG_REL[0], relheight=BODY_BG_REL[1])  # Couvre 75% de la hauteur totale

    # Logo Le Mans
    image_logo_le_mans = Image.open("img/logo_le_mans.png")
    image_logo_le_mans_redim = image_logo_le_mans.resize(LOGO_HEADER_SIZE, Image.Resampling.LANCZOS)
    photo_logo_le_mans = ImageTk.PhotoImage(image_logo_le_mans_redim)
    label_logo_le_mans = Label(fenetre, image=photo_logo_le_mans, bd=0, highlightthickness=0)
    label_logo_le_mans.image = photo_logo_le_mans  # Garder la référence
    label_logo_le_mans.place(x=LOGO_LE_MANS_POS[0], y=LOGO_LE_MANS_POS[1])

    # Logo Seed
    image_logo_seed = Image.open("img/logo_seed.png")
    image_logo_seed_redim = image_logo_seed.resize(LOGO_HEADER_SIZE, Image.Resampling.LANCZOS)
    photo_logo_seed = ImageTk.PhotoImage(image_logo_seed_redim)
    label_logo_seed = Label(fenetre, image=photo_logo_seed, bd=0, highlightthickness=0)
    label_logo_seed.image = photo_logo_seed  # Garder la référence
    label_logo_seed.place(x=LOGO_SEED_POS[0], y=LOGO_SEED_POS[1])

    return label_image, label_body, label_logo_le_mans, label_logo_seed

def afficher_info_header(fenetre, onglet_actif):
    #region Date du jour
    # BACKGROUND
    image_info = Image.open("img/label_info.png")
    image_info_redim = image_info.resize(LABEL_INFO_DATE_SIZE, Image.Resampling.LANCZOS)
    photo_info = ImageTk.PhotoImage(image_info_redim)
    label_info = Label(fenetre, image=photo_info)
    label_info.image = photo_info  # Garder la référence
    label_info.place(x=LABEL_INFO_DATE_BG_POS[0], y=LABEL_INFO_DATE_BG_POS[1])  # Placement aléatoire à modifier
    # DATE
    label_date = Label(fenetre, text=date_du_jour_propre, font=("Comic Sans MS", 12), fg="white", bg=COLOR_LABEL_TEXT_BG)
    label_date.place(x=LABEL_INFO_DATE_TEXT_POS[0], y=LABEL_INFO_DATE_TEXT_POS[1], anchor="center")  # Centre du label à cette position
    #endregion

    #region Heure actuelle
    # BACKGROUND
    image_heure = Image.open("img/label_info.png")
    image_heure_redim = image_heure.resize(LABEL_INFO_HEURE_SIZE, Image.Resampling.LANCZOS)
    photo_heure = ImageTk.PhotoImage(image_heure_redim)
    label_heure_bg = Label(fenetre, image=photo_heure)
    label_heure_bg.image = photo_heure  # Garder la référence
    label_heure_bg.place(x=LABEL_INFO_HEURE_BG_POS[0], y=LABEL_INFO_HEURE_BG_POS[1])  # Placement aléatoire à modifier
    # HEURE
    label_heure = Label(fenetre, text=datetime.now().strftime(CLOCK_FORMAT), font=("Comic Sans MS", 12), fg="white", bg=COLOR_LABEL_TEXT_BG)
    label_heure.place(x=LABEL_INFO_HEURE_TEXT_POS[0], y=LABEL_INFO_HEURE_TEXT_POS[1], anchor="center")  # Centre du label à cette position

    # Horloge temps réel (annule l'ancienne boucle si l'UI est redessinée)
    if hasattr(fenetre, "_heure_after_id") and fenetre._heure_after_id:
        try:
            fenetre.after_cancel(fenetre._heure_after_id)
        except Exception:
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
    image_annee = Image.open("img/label_info.png")
    image_annee_redim = image_annee.resize(LABEL_INFO_ANNEE_SIZE, Image.Resampling.LANCZOS)
    photo_annee = ImageTk.PhotoImage(image_annee_redim)
    label_annee_bg = Label(fenetre, image=photo_annee)
    label_annee_bg.image = photo_annee  # Garder la référence
    label_annee_bg.place(x=LABEL_INFO_ANNEE_BG_POS[0], y=LABEL_INFO_ANNEE_BG_POS[1])
    # TEXTE FIXE
    label_annee = Label(fenetre, text="Année scolaire", font=("Comic Sans MS", 12), fg="white", bg=COLOR_LABEL_TEXT_BG)
    label_annee.place(x=LABEL_INFO_ANNEE_TITLE_POS[0], y=LABEL_INFO_ANNEE_TITLE_POS[1], anchor="center")
    # VALEUR
    label_annee_valeur = Label(fenetre, text=annee_scolaire_propre, font=("Comic Sans MS", 12), fg="white", bg=COLOR_LABEL_TEXT_BG)
    label_annee_valeur.place(x=LABEL_INFO_ANNEE_VALUE_POS[0], y=LABEL_INFO_ANNEE_VALUE_POS[1], anchor="center")
    #endregion

    #region Onglet actif
    # BACKGROUND
    image_onglet = Image.open("img/label_info.png")
    image_onglet_redim = image_onglet.resize(LABEL_INFO_ONGLET_SIZE, Image.Resampling.LANCZOS)
    photo_onglet = ImageTk.PhotoImage(image_onglet_redim)
    label_onglet_bg = Label(fenetre, image=photo_onglet)
    label_onglet_bg.image = photo_onglet  # Garder la référence
    label_onglet_bg.place(x=LABEL_INFO_ONGLET_BG_POS[0], y=LABEL_INFO_ONGLET_BG_POS[1])  # Placement aléatoire à modifier
    # VALEUR
    label_onglet = Label(fenetre, text=onglet_actif, font=("Comic Sans MS", 15), fg="white", bg=COLOR_LABEL_TEXT_BG)
    label_onglet.place(x=LABEL_INFO_ONGLET_TEXT_POS[0], y=LABEL_INFO_ONGLET_TEXT_POS[1], anchor="center")  # Centre du label à cette position
    #endregion

    return label_info, label_date, label_heure_bg, label_heure, label_annee_bg, label_annee, label_annee_valeur, label_onglet_bg, label_onglet

def affichage_body(fenetre, onglet_actif, on_logo_click=None, on_retour_click=None):
    label_dynanim = None
    label_retour = None

    # region Logo Retour
    if onglet_actif != "ACCUEIL":
        # LOGO RETOUR
        image_retour = Image.open("img/retour.png")
        image_retour_redim = image_retour.resize(BODY_RETOUR_SIZE, Image.Resampling.LANCZOS)
        photo_retour = ImageTk.PhotoImage(image_retour_redim)
        label_retour = Label(fenetre, image=photo_retour, bd=0, highlightthickness=0, bg=COLOR_BODY_BG, cursor="hand2")
        label_retour.image = photo_retour  # Garder la référence
        label_retour.place(x=BODY_RETOUR_POS[0], y=BODY_RETOUR_POS[1])
        if on_retour_click:
            label_retour.bind("<Button-1>", lambda e: on_retour_click())
    # endregion

    #region Logo Dynanim
    if onglet_actif == "ACCUEIL":
        # LOGO DYNANIM
        image_dynanim = Image.open("img/logo_dynanim.png")
        image_dynanim_redim = image_dynanim.resize(BODY_DYNANIM_SIZE, Image.Resampling.LANCZOS)
        photo_dynanim = ImageTk.PhotoImage(image_dynanim_redim)
        label_dynanim = Label(fenetre, image=photo_dynanim, bd=0, highlightthickness=0, bg=COLOR_BODY_BG, cursor="hand2")
        label_dynanim.image = photo_dynanim  # Garder la référence
        label_dynanim.place(x=BODY_DYNANIM_POS[0], y=BODY_DYNANIM_POS[1])
        if on_logo_click:
            label_dynanim.bind("<Button-1>", lambda e: on_logo_click())
    #endregion

    return label_dynanim or label_retour
