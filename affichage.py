from tkinter import *
from PIL import Image, ImageTk

def afficher_header(fenetre):
    # Background du header
    image_originale = Image.open("img/header_bg.png")
    image_redimensionnee = image_originale.resize((700, 200), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redimensionnee)
    label_image = Label(fenetre, image=photo)
    label_image.image = photo  # Garder la référence
    label_image.pack(fill=X, pady=0)
    # Second affichage de la même image pour le body
    image_originale_body = Image.open("img/header_bg.png")
    image_redimensionnee_body = image_originale_body.resize((700, 600), Image.Resampling.LANCZOS)  # Couvre jusqu'en bas
    photo_body = ImageTk.PhotoImage(image_redimensionnee_body)
    label_body = Label(fenetre, image=photo_body)
    label_body.image = photo_body  # Garder la référence
    label_body.place(x=0, y=200, relwidth=1, relheight=0.75)  # Couvre 75% de la hauteur totale
    return label_image, label_body

def afficher_info_header(fenetre):
    #region Date du jour
    # BACKGROUND
    image_info = Image.open("img/label_info.png")
    image_info_redim = image_info.resize((270, 40), Image.Resampling.LANCZOS)
    photo_info = ImageTk.PhotoImage(image_info_redim)
    label_info = Label(fenetre, image=photo_info)
    label_info.image = photo_info  # Garder la référence
    label_info.place(x=215, y=70)  # Placement aléatoire à modifier
    # DATE
    from main import date_du_jour_propre
    label_date = Label(fenetre, text=date_du_jour_propre, font=("Comic Sans MS", 12), fg="white", bg="#1B4332")
    label_date.place(x=350, y=90, anchor=CENTER)  # Centre du label à cette position
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
    from main import heure_actuelle_propre
    label_heure = Label(fenetre, text=heure_actuelle_propre, font=("Comic Sans MS", 12), fg="white", bg="#1B4332")
    label_heure.place(x=107, y=40, anchor=CENTER)  # Centre du label à cette position
    #endregion

    return label_info, label_date, label_heure_bg, label_heure


