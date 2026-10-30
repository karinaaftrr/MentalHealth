"""
Automated Integration and Functional Tests: Sistem Pakar Kesehatan Mental Gen Z
Memverifikasi fungsionalitas inferensi, kalkulasi Dempster-Shafer, database,
dan seluruh alur routing Flask (beranda -> kuesioner -> proses -> hasil).
"""

import unittest
import os
import json
from app import app
from knowledge_base import INDICATORS, RULES, CONDITIONS, DS_WEIGHTS_JOURNAL
from forward_chaining import run_forward_chaining
from dempster_shafer import calculate_dempster_shafer_for_condition, reproduce_journal_narrative_example
from database import init_db, save_screening, get_screening


class TestExpertSystemCore(unittest.TestCase):
    def setUp(self):
        self.zero_answers = {f"K{i:02d}": 0 for i in range(1, 26)}

    def test_forward_chaining_no_match(self):
        """Uji kondisi ketika tidak ada aturan yang cocok."""
        res = run_forward_chaining(self.zero_answers)
        self.assertEqual(res["status"], "NO_MATCH")
        self.assertEqual(len(res["matched_rules"]), 0)
        self.assertEqual(len(res["matched_conditions"]), 0)

    def test_forward_chaining_r1_stres(self):
        """Uji kecocokan Rule 1 (Stres: K12, K13, K14, K15, K17)."""
        answers = self.zero_answers.copy()
        for k in ["K12", "K13", "K14", "K15", "K17"]:
            answers[k] = 1
        res = run_forward_chaining(answers)
        self.assertEqual(res["status"], "MATCH")
        self.assertEqual(len(res["matched_rules"]), 1)
        self.assertEqual(res["matched_rules"][0]["rule_id"], "R1")
        self.assertEqual(res["matched_conditions"][0]["kode"], "G01")
        self.assertEqual(res["matched_conditions"][0]["nama"], "Stres")

    def test_forward_chaining_multiple_rules(self):
        """Uji jika beberapa aturan cocok secara simultan."""
        answers = self.zero_answers.copy()
        # Aktifkan R1 (K12, K13, K14, K15, K17) dan R2 (K05, K09, K16, K17, K21)
        for k in ["K12", "K13", "K14", "K15", "K17", "K05", "K09", "K16", "K21"]:
            answers[k] = 1
        res = run_forward_chaining(answers)
        self.assertEqual(res["status"], "MATCH")
        self.assertEqual(len(res["matched_rules"]), 2)
        cond_codes = [c["kode"] for c in res["matched_conditions"]]
        self.assertIn("G01", cond_codes)
        self.assertIn("G02", cond_codes)

    def test_dempster_shafer_g01_complete(self):
        """Uji perhitungan Dempster-Shafer untuk G01 dengan bobot resmi jurnal."""
        res = calculate_dempster_shafer_for_condition("G01", ["K12", "K13", "K14", "K15", "K17"])
        self.assertTrue(res["can_calculate"])
        self.assertEqual(res["status"], "CALCULATED")
        # Nilai kombinasi matematis: 0.99952 (99.95%)
        self.assertAlmostEqual(res["belief_value"], 0.99952, places=4)
        self.assertEqual(len(res["steps"]), 5)

    def test_dempster_shafer_incomplete_weights(self):
        """Uji penolakan perhitungan Dempster-Shafer jika bobot tidak lengkap di jurnal."""
        res = calculate_dempster_shafer_for_condition("G02", ["K05", "K09", "K16", "K17", "K21"])
        self.assertFalse(res["can_calculate"])
        self.assertEqual(res["status"], "INCOMPLETE_WEIGHTS")
        self.assertIsNone(res["belief_value"])
        self.assertIn("K05", res["missing_indicators"])

    def test_reproduce_journal_example(self):
        """Uji fungsi audit reproduksi contoh perhitungan numerik naskah jurnal."""
        audit_res = reproduce_journal_narrative_example()
        final_mass = audit_res["final_mass"]
        self.assertGreater(final_mass["G01"], 0.99)
        self.assertLessEqual(final_mass["G01"], 1.0)


class TestFlaskWebRoutes(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()
        init_db()

    def test_home_page(self):
        """Uji akses halaman Beranda."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Sistem Pakar Deteksi Indikasi Awal", resp.data)
        self.assertIn(b"Mulai Kuesioner", resp.data)

    def test_questionnaire_page(self):
        """Uji akses halaman Kuesioner."""
        resp = self.client.get("/kuesioner")
        self.assertEqual(resp.status_code, 200)
        for i in range(1, 26):
            code = f"K{i:02d}".encode()
            self.assertIn(code, resp.data)

    def test_about_page(self):
        """Uji akses halaman Tentang Sistem."""
        resp = self.client.get("/tentang")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"IKRAM: Jurnal Ilmu Komputer Al Muslim", resp.data)

    def test_process_validation_missing_fields(self):
        """Uji validasi jika pertanyaan kuesioner tidak lengkap."""
        partial_data = {f"K{i:02d}": "0" for i in range(1, 15)} # Hanya 14 pertanyaan
        resp = self.client.post("/proses", data=partial_data, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Terdapat 11 pertanyaan yang belum Anda jawab", resp.data)

    def test_process_and_result_flow_no_match(self):
        """Uji alur lengkap ketika tidak ada aturan yang cocok."""
        full_zero = {f"K{i:02d}": "0" for i in range(1, 26)}
        resp = self.client.post("/proses", data=full_zero, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Sistem Belum Menemukan Pola Aturan yang Cocok", resp.data)

    def test_process_and_result_flow_stres_match(self):
        """Uji alur lengkap ketika kondisi Stres (R1) cocok."""
        answers = {f"K{i:02d}": "0" for i in range(1, 26)}
        for k in ["K12", "K13", "K14", "K15", "K17"]:
            answers[k] = "1"
        resp = self.client.post("/proses", data=answers, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Stres", resp.data)
        self.assertIn(b"99.95%", resp.data)
        self.assertIn(b"Tingkat Keyakinan", resp.data)

    def test_process_and_result_flow_anxiety_match(self):
        """Uji alur lengkap ketika kondisi Gangguan Kecemasan (R2) cocok dengan bobot tidak lengkap."""
        answers = {f"K{i:02d}": "0" for i in range(1, 26)}
        for k in ["K05", "K09", "K16", "K17", "K21"]:
            answers[k] = "1"
        resp = self.client.post("/proses", data=answers, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Gangguan Kecemasan", resp.data)
        self.assertIn(b"Nilai Keyakinan Belum Dapat Dihitung", resp.data)


if __name__ == "__main__":
    unittest.main()
