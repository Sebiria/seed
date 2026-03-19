from tkinter import Label
from PIL import Image, ImageTk
from main import annee_scolaire_propre, date_du_jour_propre, heure_actuelle_propre

def afficher_header(fenetre):
    # Background du header
    image_originale = Image.open("img/header_bg.png")
    image_redimensionnee = image_originale.resize((700, 200), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redimensionnee)
    label_image = Label(fenetre, image=photo)
    label_image.image = photo  # Garder la référence
    label_image.pack(fill="x", pady=0)
    # Second affichage de la même image pour le body
    image_originale_body = Image.open("img/header_bg.png")
    image_redimensionnee_body = image_originale_body.resize((700, 600), Image.Resampling.LANCZOS)  # Couvre jusqu'en bas
    photo_body = ImageTk.PhotoImage(image_redimensionnee_body)
    label_body = Label(fenetre, image=photo_body)
    label_body.image = photo_body  # Garder la référence
    label_body.place(x=0, y=200, relwidth=1, relheight=0.75)  # Couvre 75% de la hauteur totale

    # Logo Le Mans
    image_logo_le_mans = Image.open("img/logo_le_mans.png")
    image_logo_le_mans_redim = image_logo_le_mans.resize((120, 60), Image.Resampling.LANCZOS)
    photo_logo_le_mans = ImageTk.PhotoImage(image_logo_le_mans_redim)
    label_logo_le_mans = Label(fenetre, image=photo_logo_le_mans, bd=0, highlightthickness=0)
    label_logo_le_mans.image = photo_logo_le_mans  # Garder la référence
    label_logo_le_mans.place(x=230, y=10)

    # Logo Seed
    image_logo_seed = Image.open("img/logo_seed.png")
    image_logo_seed_redim = image_logo_seed.resize((120, 60), Image.Resampling.LANCZOS)
    photo_logo_seed = ImageTk.PhotoImage(image_logo_seed_redim)
    label_logo_seed = Label(fenetre, image=photo_logo_seed, bd=0, highlightthickness=0)
    label_logo_seed.image = photo_logo_seed  # Garder la référence
    label_logo_seed.place(x=355, y=10)

    return label_image, label_body, label_logo_le_mans, label_logo_seed

def afficher_info_header(fenetre, onglet_actif):
    #region Date du jour
    # BACKGROUND
    image_info = Image.open("img/label_info.png")
    image_info_redim = image_info.resize((270, 40), Image.Resampling.LANCZOS)
    photo_info = ImageTk.PhotoImage(image_info_redim)
    label_info = Label(fenetre, image=photo_info)
    label_info.image = photo_info  # Garder la référence
    label_info.place(x=215, y=70)  # Placement aléatoire à modifier
    # DATE
    label_date = Label(fenetre, text=date_du_jour_propre, font=("Comic Sans MS", 12), fg="white", bg="#1B4332")
    label_date.place(x=350, y=90, anchor="center")  # Centre du label à cette position
    #endregion

    #region Heure actuelle
    # BACKGROUND
    image_heure = Image.open("img/label_info.png")
    image_heure_redim = image_heure.resize((70, 40), Image.Resampling.LANCZOS)
    photo_heure = ImageTk.PhotoImage(image_heure_redim)
    label_heure_bg = Label(fenetre, image=photo_heure)
    label_heure_bg.image = photo_heure  # Garder la référence
    label_heure_bg.place(x=70, y=20)  # Placement aléatoire à modifier
    # HEURE
    label_heure = Label(fenetre, text=heure_actuelle_propre, font=("Comic Sans MS", 12), fg="white", bg="#1B4332")
    label_heure.place(x=107, y=40, anchor="center")  # Centre du label à cette position
    #endregion

    #region Année scolaire actuelle
    # BACKGROUND
    image_annee = Image.open("img/label_info.png")
    image_annee_redim = image_annee.resize((150, 60), Image.Resampling.LANCZOS)
    photo_annee = ImageTk.PhotoImage(image_annee_redim)
    label_annee_bg = Label(fenetre, image=photo_annee)
    label_annee_bg.image = photo_annee  # Garder la référence
    label_annee_bg.place(x=500, y=20)
    # TEXTE FIXE
    label_annee = Label(fenetre, text="Année scolaire", font=("Comic Sans MS", 12), fg="white", bg="#1B4332")
    label_annee.place(x=575, y=37, anchor="center")
    # VALEUR
    label_annee_valeur = Label(fenetre, text=annee_scolaire_propre, font=("Comic Sans MS", 12), fg="white", bg="#1B4332")
    label_annee_valeur.place(x=575, y=62, anchor="center")
    #endregion

    #region Onglet actif
    # BACKGROUND
    image_onglet = Image.open("img/label_info.png")
    image_onglet_redim = image_onglet.resize((200, 40), Image.Resampling.LANCZOS)
    photo_onglet = ImageTk.PhotoImage(image_onglet_redim)
    label_onglet_bg = Label(fenetre, image=photo_onglet)
    label_onglet_bg.image = photo_onglet  # Garder la référence
    label_onglet_bg.place(x=250, y=222)  # Placement aléatoire à modifier
    # VALEUR
    label_onglet = Label(fenetre, text=onglet_actif, font=("Comic Sans MS", 15), fg="white", bg="#1B4332")
    label_onglet.place(x=350, y=241, anchor="center")  # Centre du label à cette position
    #endregion

    return label_info, label_date, label_heure_bg, label_heure, label_annee_bg, label_annee, label_annee_valeur, label_onglet_bg, label_onglet

def affichage_body(fenetre):
    #region Logo Dynanim
    # LOGO DYNANIM
    image_dynanim = Image.open("img/logo_dynanim.png")
    image_dynanim_redim = image_dynanim.resize((140, 140), Image.Resampling.LANCZOS)
    photo_dynanim = ImageTk.PhotoImage(image_dynanim_redim)
    label_dynanim = Label(fenetre, image=photo_dynanim, bd=0, highlightthickness=0, bg="#D8F3DC")
    label_dynanim.image = photo_dynanim  # Garder la référence
    label_dynanim.place(x=280, y=350)
    #endregion

    return label_dynanim
