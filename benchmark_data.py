"""
Modul Benchmark Data: 10 Kasus Uji Acuan Sistem Pakar Kesehatan Mental
Menyediakan akses terstruktur ke 10 data kasus acuan berlabel untuk pengujian
dan demonstrasi langsung logika inferensi Forward Chaining & Dempster-Shafer.
"""

import os
import csv
from typing import Dict, List, Any, Optional

from forward_chaining import run_forward_chaining
from dempster_shafer import evaluate_dempster_shafer

DATASET_CSV_PATH = os.path.join(os.path.dirname(__file__), "dataset", "dataset_uji.csv")

# Data cadangan 10 kasus jika file csv tidak sengaja terhapus/dipindah
FALLBACK_10_CASES = [
    {
        "id_kasus": "CASE-002",
        "label_acuan_kode": "G01",
        "label_acuan_nama": "Stres",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K12", "K13", "K14", "K15", "K17", "K19"]
    },
    {
        "id_kasus": "CASE-005",
        "label_acuan_kode": "G01",
        "label_acuan_nama": "Stres",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K07", "K12", "K13", "K14", "K15", "K17"]
    },
    {
        "id_kasus": "CASE-007",
        "label_acuan_kode": "G02",
        "label_acuan_nama": "Gangguan Kecemasan",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K05", "K09", "K16", "K17", "K21", "K22"]
    },
    {
        "id_kasus": "CASE-010",
        "label_acuan_kode": "G02",
        "label_acuan_nama": "Gangguan Kecemasan",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K05", "K06", "K09", "K16", "K17", "K21"]
    },
    {
        "id_kasus": "CASE-012",
        "label_acuan_kode": "G03",
        "label_acuan_nama": "Depresi",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K05", "K20", "K22", "K23", "K24", "K25"]
    },
    {
        "id_kasus": "CASE-017",
        "label_acuan_kode": "G04",
        "label_acuan_nama": "Panic Disorder",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K05", "K07", "K08", "K09", "K16", "K21"]
    },
    {
        "id_kasus": "CASE-022",
        "label_acuan_kode": "G05",
        "label_acuan_nama": "Bipolar",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K03", "K04", "K06", "K20", "K22", "K23"]
    },
    {
        "id_kasus": "CASE-027",
        "label_acuan_kode": "G06",
        "label_acuan_nama": "Skizofrenia",
        "kategori_kasus": "Kanonikal",
        "gejala_aktif": ["K01", "K02", "K08", "K10", "K11", "K18", "K19", "K24"]
    },
    {
        "id_kasus": "CASE-031",
        "label_acuan_kode": "TIDAK_ADA",
        "label_acuan_nama": "Tidak Ada Gangguan",
        "kategori_kasus": "Kontrol Negatif",
        "gejala_aktif": []
    },
    {
        "id_kasus": "CASE-033",
        "label_acuan_kode": "TIDAK_ADA",
        "label_acuan_nama": "Tidak Ada Gangguan",
        "kategori_kasus": "Sub-ambang",
        "gejala_aktif": ["K05", "K12"]
    }
]


def load_10_benchmark_cases() -> List[Dict[str, Any]]:
    """
    Memuat 10 data kasus acuan dari dataset CSV.
    Jika file CSV tidak tersedia, menggunakan fallback data kasus kanonikal.
    """
    cases = []
    
    if os.path.exists(DATASET_CSV_PATH):
        try:
            with open(DATASET_CSV_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    answers = {}
                    gejala_aktif = []
                    for i in range(1, 26):
                        k = f"K{i:02d}"
                        val = 1 if str(row.get(k, "0")).strip() in ["1", "true", "ya", "y", "yes"] else 0
                        answers[k] = val
                        if val == 1:
                            gejala_aktif.append(k)
                    
                    cases.append({
                        "id_kasus": row.get("id_kasus", f"CASE-{len(cases)+1:03d}"),
                        "label_acuan_kode": row.get("label_acuan_kode", "TIDAK_ADA"),
                        "label_acuan_nama": row.get("label_acuan_nama", "Tidak Ada Gangguan"),
                        "kategori_kasus": row.get("kategori_kasus", "Kanonikal"),
                        "answers": answers,
                        "gejala_aktif": gejala_aktif,
                        "total_gejala": len(gejala_aktif)
                    })
            if cases:
                return cases
        except Exception as e:
            print(f"[PERINGATAN] Gagal membaca CSV dataset, beralih ke fallback: {e}")

    # Fallback jika CSV tidak terbaca
    for item in FALLBACK_10_CASES:
        answers = {f"K{i:02d}": 1 if f"K{i:02d}" in item["gejala_aktif"] else 0 for i in range(1, 26)}
        cases.append({
            "id_kasus": item["id_kasus"],
            "label_acuan_kode": item["label_acuan_kode"],
            "label_acuan_nama": item["label_acuan_nama"],
            "kategori_kasus": item["kategori_kasus"],
            "answers": answers,
            "gejala_aktif": item["gejala_aktif"],
            "total_gejala": len(item["gejala_aktif"])
        })
    return cases


def get_benchmark_case(case_id: str) -> Optional[Dict[str, Any]]:
    """Mengambil satu kasus acuan berdasarkan ID kasus (misal: 'CASE-002')."""
    cases = load_10_benchmark_cases()
    for c in cases:
        if c["id_kasus"].upper() == case_id.upper():
            return c
    return None


def run_benchmark_case_inference(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menjalankan inferensi Forward Chaining & Dempster-Shafer untuk sebuah kasus acuan,
    serta membandingkan luaran prediksi terhadap label acuan kebenaran (ground truth).
    """
    answers = case["answers"]
    fc_result = run_forward_chaining(answers)
    matched_conditions = fc_result.get("matched_conditions", [])
    
    # Jalankan Dempster-Shafer jika ada kondisi yang cocok
    ds_result = evaluate_dempster_shafer(fc_result) if matched_conditions else None
    
    # Tentukan kode prediksi sistem
    if not matched_conditions:
        pred_kode = "TIDAK_ADA"
        pred_nama = "Tidak Ada Gangguan"
    else:
        pred_kode = matched_conditions[0]["kode"]
        pred_nama = matched_conditions[0]["nama"]
        
    label_acuan_kode = case["label_acuan_kode"]
    is_correct = (pred_kode == label_acuan_kode)
    
    # Ambil nilai belief jika tersedia
    belief_percentage = None
    if ds_result and "results" in ds_result and pred_kode in ds_result["results"]:
        info = ds_result["results"][pred_kode]
        if info.get("can_calculate"):
            belief_percentage = info.get("percentage")
            
    return {
        "id_kasus": case["id_kasus"],
        "kategori_kasus": case["kategori_kasus"],
        "label_acuan_kode": label_acuan_kode,
        "label_acuan_nama": case["label_acuan_nama"],
        "prediksi_kode": pred_kode,
        "prediksi_nama": pred_nama,
        "is_correct": is_correct,
        "matched_rules": [r["rule_id"] for r in fc_result.get("matched_rules", [])],
        "matched_conditions": matched_conditions,
        "belief_percentage": belief_percentage,
        "total_gejala": case["total_gejala"],
        "gejala_aktif": case["gejala_aktif"],
        "fc_result": fc_result,
        "ds_result": ds_result
    }


def evaluate_all_10_cases() -> Dict[str, Any]:
    """
    Menjalankan evaluasi lengkap terhadap seluruh 10 data kasus acuan,
    menghitung metrik akurasi, perbandingan hasil, dan ringkasan performa.
    """
    cases = load_10_benchmark_cases()
    results = []
    correct_count = 0
    
    for case in cases:
        res = run_benchmark_case_inference(case)
        if res["is_correct"]:
            correct_count += 1
        results.append(res)
        
    total_cases = len(cases)
    accuracy_pct = (correct_count / total_cases * 100.0) if total_cases > 0 else 0.0
    
    return {
        "total_cases": total_cases,
        "correct_count": correct_count,
        "accuracy_percentage": accuracy_pct,
        "results": results
    }
