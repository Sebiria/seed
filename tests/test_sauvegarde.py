import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import sauvegarde


class TestSauvegarde(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.original_save_path = sauvegarde.SAVE_PATH
        sauvegarde.SAVE_PATH = Path(self.temp_dir.name) / "sauvegarde.json"
        self.addCleanup(self._restore_save_path)

    def _restore_save_path(self):
        sauvegarde.SAVE_PATH = self.original_save_path

    def test_charger_cree_fichier_et_donnees_par_defaut(self):
        profils = {}
        periodes = {}

        sauvegarde.charger_donnees(profils, periodes)

        self.assertTrue(sauvegarde.SAVE_PATH.exists())
        self.assertEqual(len(profils), 5)
        for cle in ["p1", "p2", "p3", "p4", "p5", "ferie"]:
            self.assertIn(cle, periodes)

    def test_roundtrip_profil_avec_projet_et_penalite(self):
        profils = {
            "TEST USER": {
                "date_debut": datetime(2025, 9, 10),
                "activites": {
                    "p1": {"lundi": "sportive", "mardi": "simple", "jeudi": "libre", "vendredi": "manuelle"},
                    "p2": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                    "p3": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                    "p4": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                    "p5": {"lundi": "", "mardi": "", "jeudi": "", "vendredi": ""},
                },
                "penalite": {datetime(2025, 9, 12): 2},
                "projet": {"objectif": "mentor"},
                "niveau": 3,
            }
        }
        periodes = {
            "p1": [datetime(2025, 9, 1), datetime(2025, 10, 17)],
            "p2": [],
            "p3": [],
            "p4": [],
            "p5": [],
            "ferie": [datetime(2025, 11, 1)],
        }

        sauvegarde.sauvegarder_donnees(profils, periodes)

        profils_charges = {}
        periodes_charges = {}
        sauvegarde.charger_donnees(profils_charges, periodes_charges)

        self.assertIn("TEST USER", profils_charges)
        profil = profils_charges["TEST USER"]
        self.assertEqual(profil["projet"], {"objectif": "mentor"})
        self.assertEqual(profil["niveau"], 3)
        self.assertEqual(len(profil["penalite"]), 1)
        self.assertIn("ferie", periodes_charges)
        self.assertEqual(len(periodes_charges["ferie"]), 1)

    def test_niveau_invalide_revient_a_1_au_chargement(self):
        payload = {
            "profils": {
                "BAD LEVEL": {
                    "date_debut": "2025-09-10T00:00:00",
                    "activites": {},
                    "penalite": {},
                    "projet": {},
                    "niveau": "abc",
                }
            },
            "periodes": {"p1": [], "p2": [], "p3": [], "p4": [], "p5": [], "ferie": []},
        }
        sauvegarde.SAVE_PATH.write_text(json.dumps(payload), encoding="utf-8")

        profils = {}
        periodes = {}
        sauvegarde.charger_donnees(profils, periodes)

        self.assertEqual(profils["BAD LEVEL"]["niveau"], 1)

    def test_projet_manquant_ou_invalide_revient_a_dict_vide(self):
        payload = {
            "profils": {
                "NO PROJET": {
                    "date_debut": "2025-09-10T00:00:00",
                    "activites": {},
                    "penalite": {},
                    "niveau": 1,
                },
                "BAD PROJET": {
                    "date_debut": "2025-09-11T00:00:00",
                    "activites": {},
                    "penalite": {},
                    "projet": "oops",
                    "niveau": 1,
                },
            },
            "periodes": {"p1": [], "p2": [], "p3": [], "p4": [], "p5": [], "ferie": []},
        }
        sauvegarde.SAVE_PATH.write_text(json.dumps(payload), encoding="utf-8")

        profils = {}
        periodes = {}
        sauvegarde.charger_donnees(profils, periodes)

        self.assertEqual(profils["NO PROJET"]["projet"], {})
        self.assertEqual(profils["BAD PROJET"]["projet"], {})

    def test_cles_periodes_manquantes_sont_completees(self):
        payload = {
            "profils": {},
            "periodes": {"p1": [], "ferie": []},
        }
        sauvegarde.SAVE_PATH.write_text(json.dumps(payload), encoding="utf-8")

        profils = {}
        periodes = {}
        sauvegarde.charger_donnees(profils, periodes)

        for cle in ["p1", "p2", "p3", "p4", "p5", "ferie"]:
            self.assertIn(cle, periodes)


if __name__ == "__main__":
    unittest.main()

