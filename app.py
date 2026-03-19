from tkinter import *
from affichage import afficher_header, afficher_info_header, affichage_body

#region Paramétrage de la fenètre
fenetre = Tk()
fenetre.title("Seed")
fenetre.geometry(f"700x800+{(fenetre.winfo_screenwidth()-700)//2}+{(fenetre.winfo_screenheight()-800)//2}")
fenetre.resizable(width=False, height=False)
#endregion

#region Variables
onglet_actif = "ACCUEIL"
#endregion

#region Fonctions utilitaires
def update_ui():
    global onglet_actif
    # Détruire tous les widgets sauf la fenêtre
    for widget in fenetre.winfo_children():
        widget.destroy()
    # Redessiner l'interface
    afficher_header(fenetre)
    afficher_info_header(fenetre, onglet_actif)
    affichage_body(fenetre, onglet_actif, on_logo_click)

def on_logo_click():
    global onglet_actif
    onglet_actif = "DYNANIM"
    update_ui()
#endregion

#region Background et affichage permanent

# Affichage
afficher_header(fenetre)
afficher_info_header(fenetre, onglet_actif)
affichage_body(fenetre, onglet_actif, on_logo_click)
#endregion




fenetre.mainloop()