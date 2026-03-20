# Charte UI/UX minimale - Seed / Dynanim

## 1) Identite visuelle
- Fond principal body: `#D8F3DC`
- Couleur action principale: `#FF7500`
- Couleur de contraste sombre: `#190F58`
- Texte principal clair sur fonds colores: `white`
- Texte principal sur champs blancs: `black`

## 2) Typographie
- Police principale interface: `Comic Sans MS`
- Titre section: `("Comic Sans MS", 12, "bold")`
- Champ de saisie: `("Comic Sans MS", 11)`
- Bouton primaire: `("Comic Sans MS", 13, "bold")`

## 3) Composants
- Titres de section: fond image `label_nav_dynanim.png` + cartouche texte orange.
- Champs de saisie et listes: fond blanc, texte noir, bordure simple.
- Bouton `VALIDER`:
  - inactif: `#F3A6A6`
  - actif (formulaire valide): `#FF7500`

## 4) Feedback utilisateur
- Erreur: rouge, style lisible, message explicite.
- Succes: vert (`#2E7D32`), gras, fond `#D8F3DC`, disparition auto apres 5s.

## 5) Regles UX de validation
- Validation dynamique en temps reel.
- Nom/Prénom valide: au moins 3 lettres, lettres + espaces uniquement.
- Nom/Prénom affiche et stocke en `UPPER` apres normalisation des espaces.
- Date valide: annee/mois/jour completement selectionnes et date calendrier valide.
- Activites: toutes selectionnees.
- Anti-doublon: un participant deja existant ne peut pas etre ajoute.

## 6) Convention de mise en page
- Utiliser des constantes pour positions/sizes.
- Ajuster visuellement par pas de 5px pour le pixel-perfect.
- Garder une structure de blocs claire (region titre, region champ, region feedback).

