"""
Modul Forward Chaining: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Mengimplementasikan inferensi berbasis aturan (rule-based) sesuai logika pada jurnal:
IKRAM: Jurnal Ilmu Komputer Al Muslim, Vol. IV No. 2, Oktober 2025.
"""

from typing import Dict, List, Any, Union
from knowledge_base import RULES, CONDITIONS, INDICATORS


def normalize_answers(answers: Dict[str, Any]) -> Dict[str, bool]:
    """
    Normalisasi jawaban pengguna ke format boolean (True/False).
    Menerima input berupa 1/0, True/False, '1'/'0', 'Ya'/'Tidak', 'ya'/'tidak', 'yes'/'no'.
    """
    normalized = {}
    for code in INDICATORS.keys():
        val = answers.get(code)
        if val is None:
            normalized[code] = False
        elif isinstance(val, bool):
            normalized[code] = val
        elif isinstance(val, (int, float)):
            normalized[code] = (val == 1)
        elif isinstance(val, str):
            val_clean = val.strip().lower()
            normalized[code] = val_clean in ["1", "true", "ya", "y", "yes"]
        else:
            normalized[code] = False
    return normalized


def run_forward_chaining(answers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Menjalankan proses inferensi Forward Chaining.
    
    Aturan dinyatakan cocok (fired) jika dan hanya jika SELURUH indikator
    dalam premis aturan bernilai Ya/True (logika AND).
    
    Returns:
        dict berisi:
        - status: 'MATCH' | 'NO_MATCH'
        - matched_rules: list rule objek yang cocok
        - matched_conditions: list data kondisi lengkap (G01–G06) yang terdeteksi
        - answers_summary: ringkasan indikator yang dijawab 'Ya'
        - total_matched: jumlah aturan yang cocok
    """
    norm_answers = normalize_answers(answers)
    user_facts = {code for code, ans in norm_answers.items() if ans}
    
    matched_rules = []
    matched_conditions_map = {}
    
    for rule in RULES:
        premise = set(rule["premis"])
        # Logika AND: seluruh indikator dalam premis harus ada dalam fakta pengguna
        if premise.issubset(user_facts):
            cond_code = rule["kesimpulan"]
            cond_info = CONDITIONS.get(cond_code, {})
            
            supporting_indicators = [
                {
                    "kode": ind_code,
                    "pertanyaan": INDICATORS[ind_code]["pertanyaan"]
                }
                for ind_code in rule["premis"]
            ]
            
            rule_match_info = {
                "rule_id": rule["id"],
                "nama_rule": rule["nama"],
                "teks_aturan": rule["teks_aturan"],
                "kondisi_kode": cond_code,
                "nama_kondisi": cond_info.get("nama", rule["nama_kondisi"]),
                "premis": rule["premis"],
                "supporting_indicators": supporting_indicators,
                "catatan": rule.get("catatan", "")
            }
            matched_rules.append(rule_match_info)
            
            if cond_code not in matched_conditions_map:
                matched_conditions_map[cond_code] = {
                    "kode": cond_code,
                    "nama": cond_info.get("nama", rule["nama_kondisi"]),
                    "deskripsi": cond_info.get("deskripsi", ""),
                    "saran": cond_info.get("saran", ""),
                    "supporting_indicators": supporting_indicators,
                    "rules_triggered": [rule["id"]],
                }
            else:
                matched_conditions_map[cond_code]["rules_triggered"].append(rule["id"])

    matched_conditions = list(matched_conditions_map.values())
    status = "MATCH" if len(matched_conditions) > 0 else "NO_MATCH"
    
    return {
        "status": status,
        "is_match": (status == "MATCH"),
        "total_matched": len(matched_rules),
        "matched_rules": matched_rules,
        "matched_conditions": matched_conditions,
        "user_positive_indicators": sorted(list(user_facts)),
        "total_positive_indicators": len(user_facts)
    }
