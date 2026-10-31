"""
Modul In-Memory Storage: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Menggantikan database fisik (SQLite) dengan penyimpanan memori (RAM) murni.
Fokus pada eksekusi logika inferensi Forward Chaining & Dempster-Shafer secara instan,
bersih, dan tanpa ketergantungan file database eksternal.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# Penyimpanan in-memory (RAM)
_SCREENING_STORAGE: Dict[str, Dict[str, Any]] = {}


def init_db(*args, **kwargs) -> None:
    """
    Fungsi kompatibilitas: Tidak memerlukan inisialisasi tabel atau file database.
    Seluruh data disimpan langsung di memori program (RAM).
    """
    pass


def save_screening(
    answers: Dict[str, Any],
    matched_rules: List[Dict[str, Any]],
    matched_conditions: List[Dict[str, Any]],
    ds_results: Optional[Dict[str, Any]],
    status_perhitungan: str
) -> str:
    """
    Menyimpan data hasil skrining langsung ke memori (RAM).
    
    Returns:
        screening_id (str): ID unik pemeriksaan (misal: CHK-20261031-A1B2C3D4)
    """
    screening_id = f"CHK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now().isoformat()
    
    # Hitung total jawaban 'Ya'
    total_ya = sum(1 for v in answers.values() if v in [True, 1, "1", "Ya", "ya", "yes"])
    
    _SCREENING_STORAGE[screening_id] = {
        "id": screening_id,
        "waktu_pemeriksaan": now_iso,
        "jawaban": answers,
        "aturan_cocok": matched_rules,
        "hasil_inferensi": matched_conditions,
        "nilai_keyakinan": ds_results,
        "status_perhitungan": status_perhitungan,
        "total_ya": total_ya
    }
    
    return screening_id


def get_screening(screening_id: str) -> Optional[Dict[str, Any]]:
    """
    Mengambil data pemeriksaan dari memori berdasarkan ID pemeriksaan.
    """
    record = _SCREENING_STORAGE.get(screening_id)
    if not record:
        return None
    return record


def list_screenings() -> List[Dict[str, Any]]:
    """Mengambil seluruh riwayat pemeriksaan yang tersimpan di memori."""
    return list(_SCREENING_STORAGE.values())


def clear_screenings() -> None:
    """Mengosongkan memori penyimpanan skrining (berguna untuk testing)."""
    _SCREENING_STORAGE.clear()
