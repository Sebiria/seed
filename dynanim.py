from tkinter import Label
from PIL import Image, ImageTk

# Constantes UI Dynanim (tailles / positions)
BODY_RETOUR_SIZE = (30, 30)
BODY_RETOUR_POS = (200, 230)
BODY_DYNANIM_SIZE = (100, 100)
BODY_DYNANIM_POS = (50, 300)
COLOR_BODY_BG = "#D8F3DC"
COLOR_NAV_TEXT_BG = "#FF7500"

BODY_WIDTH = 700
BODY_X = 0

NAV_TAB_SIZE = (110, 40)
NAV_TAB_Y = 267  # Juste sous le label app_actif (y=222 + h=40 + 5px gap)
NAV_TAB_LABELS = ["AJOUT", "PROFIL", "ACCUEIL", "+ / -", "STATS"]
NAV_TAB_FONT = ("Comic Sans MS", 11)
NAV_TAB_FONT_ACTIVE = ("Comic Sans MS", 12, "bold")


def afficher_dynanim_body(
    fenetre,
    app_actif,
    dynanim_onglet_actif="ACCUEIL",
    on_logo_click=None,
    on_retour_click=None,
    on_tab_click=None,
):
    label_dynanim = None
    label_retour = None

    # region Logo Retour
    if app_actif != "ACCUEIL":
        image_retour = Image.open("img/retour.png")
        image_retour_redim = image_retour.resize(BODY_RETOUR_SIZE, Image.Resampling.LANCZOS)
        photo_retour = ImageTk.PhotoImage(image_retour_redim)
        label_retour = Label(
            fenetre,
            image=photo_retour,
            bd=0,
            highlightthickness=0,
            bg=COLOR_BODY_BG,
            cursor="hand2",
        )
        label_retour.image = photo_retour  # Garder la reference
        label_retour.place(x=BODY_RETOUR_POS[0], y=BODY_RETOUR_POS[1])
        if on_retour_click:
            label_retour.bind("<Button-1>", lambda e: on_retour_click())
    # endregion

    # region Logo Dynanim
    if app_actif == "ACCUEIL":
        image_dynanim = Image.open("img/logo_dynanim.png")
        image_dynanim_redim = image_dynanim.resize(BODY_DYNANIM_SIZE, Image.Resampling.LANCZOS)
        photo_dynanim = ImageTk.PhotoImage(image_dynanim_redim)
        label_dynanim = Label(
            fenetre,
            image=photo_dynanim,
            bd=0,
            highlightthickness=0,
            bg=COLOR_BODY_BG,
            cursor="hand2",
        )
        label_dynanim.image = photo_dynanim  # Garder la reference
        label_dynanim.place(x=BODY_DYNANIM_POS[0], y=BODY_DYNANIM_POS[1])
        if on_logo_click:
            label_dynanim.bind("<Button-1>", lambda e: on_logo_click())
    # endregion

    # region Navigation Dynanim
    if app_actif == "DYNANIM":
        dynanim_onglet_actif = dynanim_onglet_actif or "ACCUEIL"

        image_nav = Image.open("img/label_nav_dynanim.png")
        image_nav_redim = image_nav.resize(NAV_TAB_SIZE, Image.Resampling.LANCZOS)
        photo_nav = ImageTk.PhotoImage(image_nav_redim)

        total_tabs_width = len(NAV_TAB_LABELS) * NAV_TAB_SIZE[0]
        espace_x = int((BODY_WIDTH - total_tabs_width) / (len(NAV_TAB_LABELS) + 1))

        for index, texte in enumerate(NAV_TAB_LABELS):
            x_tab = BODY_X + espace_x + index * (NAV_TAB_SIZE[0] + espace_x)
            nav_font = NAV_TAB_FONT_ACTIVE if texte == dynanim_onglet_actif else NAV_TAB_FONT

            label_nav_bg = Label(fenetre, image=photo_nav, bd=0, highlightthickness=0, cursor="hand2")
            label_nav_bg.image = photo_nav  # Garder la reference
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
                label_nav_bg.bind("<Button-1>", lambda e, o=onglet: on_tab_click(o))
                label_nav_text.bind("<Button-1>", lambda e, o=onglet: on_tab_click(o))
    # endregion

    return label_dynanim or label_retour

