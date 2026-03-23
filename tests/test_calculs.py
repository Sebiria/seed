import unittest
from datetime import datetime

from calculs import (
    calculer_repartition_types_anim_profil,
    calculer_score_engagement_profil,
    calculer_xp_globale_profil,
    calculer_xp_reelle_totale_profil,
    etoiles_depuis_score,
    lister_penalites_reelles,
    note_depuis_points_semaine,
    points_max_theoriques_profil,
    profils_a_mettre_a_jour_periode,
)


class TestCalculsProfils(unittest.TestCase):
    def setUp(self):
        self.periodes = {
            "p1": [datetime(2025, 9, 1), datetime(2025, 9, 30)],
            "p2": [],
            "p3": [],
            "p4": [],
            "p5": [],
            "ferie": [],
        }
        self.profil = {
            "date_debut": datetime(2025, 9, 1),
            "activites": {
                "p1": {
                    "lundi": "sportive",
                    "mardi": "sportive",
                    "jeudi": "sportive",
                    "vendredi": "sportive",
                },
                "p2": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                "p3": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                "p4": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                "p5": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
            },
            "penalite": {},
            "projet": {},
            "niveau": 1,
        }

    def test_engagement_100_sans_penalite(self):
        # Date de référence: 6 septembre -> on calcule jusqu'au 5 (lun, mar, jeu, ven = 12 points)
        reference = datetime(2025, 9, 6)
        score = calculer_score_engagement_profil(self.profil, self.periodes, date_reference=reference)

        self.assertEqual(score["points_actuels"], 12)
        self.assertEqual(score["points_max"], 12)
        self.assertEqual(score["score"], 100)
        self.assertEqual(score["etoiles"], 5)

    def test_engagement_baisse_avec_penalite(self):
        reference = datetime(2025, 9, 6)
        # Vendredi valait 3 points, il est forcé à 0 -> total 9.
        self.profil["penalite"] = {datetime(2025, 9, 5): 0}

        score = calculer_score_engagement_profil(self.profil, self.periodes, date_reference=reference)

        self.assertEqual(score["points_actuels"], 9)
        self.assertEqual(score["points_max"], 12)
        self.assertEqual(score["score"], 75)
        self.assertEqual(score["etoiles"], 1)

    def test_xp_exclut_jour_courant(self):
        # Référence 2 septembre: seul le lundi 1 est compté (3 points)
        xp = calculer_xp_globale_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 2))
        self.assertEqual(xp, 3)

    def test_seuils_etoiles(self):
        self.assertEqual(etoiles_depuis_score(95), 5)
        self.assertEqual(etoiles_depuis_score(90), 4)
        self.assertEqual(etoiles_depuis_score(85), 3)
        self.assertEqual(etoiles_depuis_score(80), 2)
        self.assertEqual(etoiles_depuis_score(79), 1)

    def test_note_depuis_points_semaine(self):
        self.assertEqual(note_depuis_points_semaine(12)[0], "A")
        self.assertEqual(note_depuis_points_semaine(9)[0], "D")
        self.assertEqual(note_depuis_points_semaine(4)[0], "I")

    def test_points_theoriques_suivent_activites_prevues(self):
        # Si vendredi est vide, il n'est pas compté dans le théorique.
        self.profil["activites"]["p1"]["vendredi"] = ""
        points_max = points_max_theoriques_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(points_max, 9)

    def test_points_theoriques_excluent_ferie(self):
        # Vendredi 5 septembre devient férié: on ne compte plus ce jour.
        self.periodes["ferie"] = [datetime(2025, 9, 5)]
        points_max = points_max_theoriques_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(points_max, 9)

    def test_engagement_zero_si_aucun_point_theorique(self):
        # Toutes les activités sont vides: aucun point attendu.
        for jour in ["lundi", "mardi", "jeudi", "vendredi"]:
            self.profil["activites"]["p1"][jour] = ""

        score = calculer_score_engagement_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(score["points_max"], 0)
        self.assertEqual(score["score"], 0)
        self.assertEqual(score["etoiles"], 1)

    def test_engagement_borne_a_100(self):
        # Override identique à la valeur de base: score reste à 100.
        self.profil["penalite"] = {datetime(2025, 9, 5): 3}
        score = calculer_score_engagement_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(score["score"], 100)

    def test_penalite_remplace_valeur_du_jour(self):
        # Vendredi (3) devient 1 => total: 3 + 3 + 3 + 1 = 10.
        self.profil["penalite"] = {datetime(2025, 9, 5): 1}
        xp = calculer_xp_globale_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(xp, 10)

    def test_lister_penalites_reelles_filtre_les_non_penalisantes(self):
        self.profil["penalite"] = {
            datetime(2025, 9, 2): 1,
            datetime(2025, 9, 4): 3,
            datetime(2025, 9, 5): 0,
        }

        penalites = lister_penalites_reelles(self.profil, self.periodes)

        self.assertEqual(
            [item["date"] for item in penalites],
            [datetime(2025, 9, 2).date(), datetime(2025, 9, 5).date()],
        )
        self.assertEqual([item["valeur"] for item in penalites], [1, 0])
        self.assertEqual([item["base"] for item in penalites], [3, 3])

    def test_lister_penalites_reelles_trie_par_date(self):
        self.profil["penalite"] = {
            datetime(2025, 9, 5): 0,
            datetime(2025, 9, 1): 1,
            datetime(2025, 9, 2): 2,
        }

        penalites = lister_penalites_reelles(self.profil, self.periodes)

        self.assertEqual(
            [item["date"] for item in penalites],
            [
                datetime(2025, 9, 1).date(),
                datetime(2025, 9, 2).date(),
                datetime(2025, 9, 5).date(),
            ],
        )

    def test_penalite_format_objet_est_prise_en_compte(self):
        # Compatibilité avec le format {'valeur': int}.
        self.profil["penalite"] = {datetime(2025, 9, 5): {"valeur": 1, "date": datetime(2025, 9, 5)}}
        xp = calculer_xp_globale_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(xp, 10)

    def test_xp_reelle_inclut_points_projets(self):
        self.profil["projet"] = {"A": 5, "B": 7}
        xp_reelle = calculer_xp_reelle_totale_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(xp_reelle, 24)

    def test_xp_reelle_inclut_points_projets_format_objet(self):
        self.profil["projet"] = {
            "A": {"valeur": 5, "date_creation": None},
            "B": {"valeur": 7, "date_creation": None},
        }
        xp_reelle = calculer_xp_reelle_totale_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(xp_reelle, 24)

    def test_engagement_ignore_points_projets(self):
        self.profil["projet"] = {"A": 999}
        score = calculer_score_engagement_profil(self.profil, self.periodes, date_reference=datetime(2025, 9, 6))
        self.assertEqual(score["points_actuels"], 12)
        self.assertEqual(score["points_max"], 12)
        self.assertEqual(score["score"], 100)

    def test_repartition_types_anim_triee_decroissante(self):
        # Semaine type: sportive(1), manuelle(2), libre(1) => 25/50/0/25
        self.profil["activites"]["p1"] = {
            "lundi": "sportive",
            "mardi": "manuelle",
            "jeudi": "manuelle",
            "vendredi": "libre",
        }
        repartition = calculer_repartition_types_anim_profil(
            self.profil,
            self.periodes,
            date_reference=datetime(2025, 9, 6),
        )
        self.assertEqual(repartition["total_jours_activite"], 4)
        self.assertEqual(
            repartition["types_tries"],
            [("manuelle", 50), ("sportive", 25), ("libre", 25), ("simple", 0)],
        )

    def test_repartition_types_anim_tous_types_meme_sous_30(self):
        # 1 occurrence de chaque type => 25% chacun.
        self.profil["activites"]["p1"] = {
            "lundi": "sportive",
            "mardi": "manuelle",
            "jeudi": "simple",
            "vendredi": "libre",
        }
        repartition = calculer_repartition_types_anim_profil(
            self.profil,
            self.periodes,
            date_reference=datetime(2025, 9, 6),
        )
        self.assertEqual(repartition["total_jours_activite"], 4)
        self.assertEqual(
            repartition["types_tries"],
            [("sportive", 25), ("manuelle", 25), ("simple", 25), ("libre", 25)],
        )

    def test_profils_a_mettre_a_jour_sur_periode_active(self):
        periodes = {
            "p1": [datetime(2025, 9, 1), datetime(2025, 9, 30)],
            "p2": [datetime(2025, 10, 1), datetime(2025, 10, 31)],
            "p3": [],
            "p4": [],
            "p5": [],
            "ferie": [],
        }
        profils = {
            "ALICE": {
                "date_debut": datetime(2025, 9, 1),
                "activites": {
                    "p1": {"lundi": "sportive", "mardi": "simple", "jeudi": "libre", "vendredi": "manuelle"},
                    "p2": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                },
            },
            "BRUNO": {
                "date_debut": datetime(2025, 9, 1),
                "activites": {
                    "p1": {"lundi": "sportive", "mardi": "simple", "jeudi": "libre", "vendredi": "manuelle"},
                    "p2": {"lundi": "sportive", "mardi": "simple", "jeudi": "libre", "vendredi": "manuelle"},
                },
            },
        }

        resultat = profils_a_mettre_a_jour_periode(
            profils,
            periodes,
            date_reference=datetime(2025, 10, 15),
        )

        self.assertEqual(resultat["periode"], "p2")
        self.assertEqual(resultat["profils"], ["ALICE"])

    def test_profils_a_mettre_a_jour_exclut_profils_pas_commences(self):
        periodes = {
            "p1": [datetime(2025, 9, 1), datetime(2025, 9, 30)],
            "p2": [datetime(2025, 10, 1), datetime(2025, 10, 31)],
            "p3": [],
            "p4": [],
            "p5": [],
            "ferie": [],
        }
        profils = {
            "CHARLIE": {
                "date_debut": datetime(2025, 11, 3),
                "activites": {
                    "p2": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                },
            }
        }

        resultat = profils_a_mettre_a_jour_periode(
            profils,
            periodes,
            date_reference=datetime(2025, 10, 15),
        )

        self.assertEqual(resultat["periode"], "p2")
        self.assertEqual(resultat["profils"], [])

    def test_profils_a_mettre_a_jour_aucune_periode_active(self):
        periodes = {"p1": [], "p2": [], "p3": [], "p4": [], "p5": [], "ferie": []}
        resultat = profils_a_mettre_a_jour_periode({}, periodes, date_reference=datetime(2025, 10, 15))
        self.assertIsNone(resultat["periode"])
        self.assertEqual(resultat["profils"], [])


if __name__ == "__main__":
    unittest.main()

