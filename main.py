from datetime import datetime

#region Infos header
#region Date du jour
date_du_jour = datetime.now()
jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
mois_annee = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
              "août", "septembre", "octobre", "novembre", "décembre"]
date_du_jour_propre = f"{jours_semaine[date_du_jour.weekday()]} {date_du_jour.day:02d} {mois_annee[date_du_jour.month-1]} {date_du_jour.year}"
#endregion

#region Heure actuelle
# Récupération de l'heure depuis la variable date_du_jour existante
# (pas besoin de créer un nouvel appel à datetime.now())
_heure_actuelle_propre = f"{date_du_jour.hour}H{date_du_jour.minute:02d}"
#endregion

#region Année scolaire actuelle
annee_scolaire_propre = "2026-2027"
#endregion

#endregion

#region Données
profils = {}

# Clé : identifiant de période (ex: "p1")
# Valeur : [date_debut (datetime), date_fin (datetime)] — vide jusqu'à saisie dans Paramètre/Vacances
periodes = {p: [] for p in ["p1", "p2", "p3", "p4", "p5", "ferie"]}
#endregion
