"""
Modul Dempster-Shafer: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Mengimplementasikan Teori Dempster-Shafer (Dempster's Rule of Combination)
secara ketat, mathematically sound, dan transparan.
"""

from typing import Dict, List, Any, Optional, Tuple
from knowledge_base import DS_WEIGHTS_JOURNAL, RULES, CONDITIONS


def combine_two_mass_functions(
    m1: Dict[str, float],
    m2: Dict[str, float],
    focal_hypothesis: str
) -> Tuple[Dict[str, float], float, List[Dict[str, Any]]]:
    """
    Menggabungkan dua mass function m1 dan m2 untuk sebuah hipotesis tunggal H
    terhadap lingkungan ketidakpastian Theta (frame of discernment).
    
    Focal elements:
    - {H}
    - {theta}
    
    Returns:
        (m_combined, conflict_k, detail_kombinasi)
    """
    m1_h = m1.get(focal_hypothesis, 0.0)
    m1_theta = m1.get("theta", 0.0)
    m2_h = m2.get(focal_hypothesis, 0.0)
    m2_theta = m2.get("theta", 0.0)
    
    # 4 irisan elemen:
    # 1. H ∩ H = H
    term_hh = m1_h * m2_h
    # 2. H ∩ theta = H
    term_htheta = m1_h * m2_theta
    # 3. theta ∩ H = H
    term_thetah = m1_theta * m2_h
    # 4. theta ∩ theta = theta
    term_thetatheta = m1_theta * m2_theta
    
    # Karena kedua eviden mendukung hipotesis yang sama atau theta, tidak ada irisan kosong (conflict k = 0)
    conflict_k = 0.0
    denominator = 1.0 - conflict_k
    
    combined_h = (term_hh + term_htheta + term_thetah) / denominator
    combined_theta = term_thetatheta / denominator
    
    # Normalisasi presisi numerik agar total mass = 1.0
    total_mass = combined_h + combined_theta
    if total_mass > 0:
        combined_h /= total_mass
        combined_theta /= total_mass
        
    details = [
        {"x": focal_hypothesis, "y": focal_hypothesis, "result": focal_hypothesis, "val": round(term_hh, 6)},
        {"x": focal_hypothesis, "y": "theta", "result": focal_hypothesis, "val": round(term_htheta, 6)},
        {"x": "theta", "y": focal_hypothesis, "result": focal_hypothesis, "val": round(term_thetah, 6)},
        {"x": "theta", "y": "theta", "result": "theta", "val": round(term_thetatheta, 6)},
    ]
    
    return {focal_hypothesis: combined_h, "theta": combined_theta}, conflict_k, details


def calculate_dempster_shafer_for_condition(
    condition_code: str,
    indicator_codes: List[str]
) -> Dict[str, Any]:
    """
    Menghitung nilai keyakinan Dempster-Shafer untuk suatu kondisi berdasarkan
    indikator-indikator yang terpenuhi.
    
    Aturan Ketat:
    - Memeriksa kelengkapan bobot di DS_WEIGHTS_JOURNAL.
    - Jika ada indikator yang bobotnya tidak tercantum dalam jurnal, perhitungan DITOLAK
      secara transparan dengan status INCOMPLETE_WEIGHTS (tidak mengarang bobot palsu).
    """
    if not indicator_codes:
        return {
            "status": "NO_INDICATORS",
            "can_calculate": False,
            "belief_value": None,
            "percentage": None,
            "message": "Tidak ada indikator yang diberikan untuk perhitungan Dempster-Shafer."
        }
        
    # Cek ketersediaan bobot di jurnal
    missing_weights = [code for code in indicator_codes if code not in DS_WEIGHTS_JOURNAL]
    available_weights = {code: DS_WEIGHTS_JOURNAL[code] for code in indicator_codes if code in DS_WEIGHTS_JOURNAL}
    
    if missing_weights:
        return {
            "status": "INCOMPLETE_WEIGHTS",
            "can_calculate": False,
            "condition_code": condition_code,
            "belief_value": None,
            "percentage": None,
            "missing_indicators": missing_weights,
            "available_indicators": list(available_weights.keys()),
            "message": (
                f"Nilai keyakinan Dempster-Shafer belum dapat dihitung karena bobot untuk indikator "
                f"({', '.join(missing_weights)}) tidak dipublikasikan dalam tabel bobot jurnal sumber. "
                f"Sistem tidak mengarang bobot estimasi agar integritas ilmiah tetap terjaga."
            )
        }
        
    # Jika seluruh indikator memiliki bobot resmi:
    # Lakukan kombinasi Dempster-Shafer secara berurutan
    steps = []
    
    # Eviden pertama
    first_code = indicator_codes[0]
    w1 = available_weights[first_code]
    current_mass = {
        condition_code: float(w1),
        "theta": round(1.0 - float(w1), 6)
    }
    steps.append({
        "step": 1,
        "indicator": first_code,
        "weight": w1,
        "mass_h": current_mass[condition_code],
        "mass_theta": current_mass["theta"]
    })
    
    # Kombinasi dengan eviden berikutnya
    for idx, next_code in enumerate(indicator_codes[1:], start=2):
        w_next = available_weights[next_code]
        next_mass = {
            condition_code: float(w_next),
            "theta": round(1.0 - float(w_next), 6)
        }
        combined_mass, conflict_k, detail_grid = combine_two_mass_functions(
            current_mass, next_mass, condition_code
        )
        current_mass = combined_mass
        steps.append({
            "step": idx,
            "combined_with_indicator": next_code,
            "weight": w_next,
            "conflict_k": conflict_k,
            "mass_h": current_mass[condition_code],
            "mass_theta": current_mass["theta"],
            "grid": detail_grid
        })
        
    final_belief = current_mass[condition_code]
    percentage = round(final_belief * 100, 2)
    
    return {
        "status": "CALCULATED",
        "can_calculate": True,
        "condition_code": condition_code,
        "condition_name": CONDITIONS.get(condition_code, {}).get("nama", condition_code),
        "belief_value": round(final_belief, 5),
        "percentage": percentage,
        "steps": steps,
        "used_indicators": indicator_codes,
        "message": f"Tingkat keyakinan terhitung secara sah: {percentage}% ({round(final_belief, 4)})."
    }


def evaluate_dempster_shafer(forward_chaining_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluasi Dempster-Shafer untuk seluruh kondisi yang lolos inferensi Forward Chaining.
    """
    matched_conditions = forward_chaining_result.get("matched_conditions", [])
    results_per_condition = {}
    
    for cond in matched_conditions:
        cond_code = cond["kode"]
        # Ambil indikator yang relevan dengan kondisi ini dari premis aturan
        # Cari aturan yang menghasilkan kondisi ini
        relevant_indicators = []
        for r in RULES:
            if r["kesimpulan"] == cond_code:
                relevant_indicators = r["premis"]
                break
                
        ds_res = calculate_dempster_shafer_for_condition(cond_code, relevant_indicators)
        results_per_condition[cond_code] = ds_res
        
    return {
        "conditions_evaluated": len(matched_conditions),
        "results": results_per_condition
    }


def reproduce_journal_narrative_example() -> Dict[str, Any]:
    """
    Fungsi audit untuk mereproduksi contoh numerik yang ditulis dalam naskah jurnal
    (hal. 82-83), di mana penulis menggabungkan K01, K12, K14, K15, K19, K20 untuk G01.
    
    Catatan temuan audit:
    - Jurnal menyertakan indikator non-premis (K01, K19, K20) dalam kombinasi.
    - Terjadi galat aritmatika manual pada teks jurnal di M7 {θ} = 0.338 dan M11 {G01} = 1.000388.
    """
    seq = [
        ("K01", 0.80),
        ("K12", 0.80),
        ("K14", 0.70), # Catatan: pada teks narasi jurnal hal. 82 ditulis 0.70 meskipun di tabel bobot 0.80
        ("K15", 0.80),
        ("K19", 0.80),
        ("K20", 0.80)
    ]
    
    current_mass = {"G01": seq[0][1], "theta": 1.0 - seq[0][1]}
    history = [("M1", seq[0][0], current_mass.copy())]
    
    for idx, (code, weight) in enumerate(seq[1:], start=2):
        next_m = {"G01": weight, "theta": 1.0 - weight}
        combined_m, _, _ = combine_two_mass_functions(current_mass, next_m, "G01")
        current_mass = combined_m
        history.append((f"M{2*idx-1}", code, current_mass.copy()))
        
    return {
        "final_mass": current_mass,
        "history": history,
        "note": "Perhitungan murni matematis bebas dari akumulasi pembulatan manual atau galat ketik naskah."
    }
