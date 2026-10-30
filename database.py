"""
Modul Database: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Mengelola penyimpanan data pemeriksaan secara aman, privat (tanpa data pribadi/NIK),
dan terstruktur menggunakan SQLite.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_FILE = "database.db"


def get_db_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    """Membuka koneksi database SQLite."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_FILE) -> None:
    """Inisialisasi skema tabel database."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pemeriksaan (
            id TEXT PRIMARY KEY,
            waktu_pemeriksaan TIMESTAMP NOT NULL,
            jawaban_json TEXT NOT NULL,
            aturan_cocok_json TEXT NOT NULL,
            hasil_inferensi_json TEXT NOT NULL,
            nilai_keyakinan_json TEXT,
            status_perhitungan TEXT NOT NULL,
            total_ya INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_screening(
    answers: Dict[str, Any],
    matched_rules: List[Dict[str, Any]],
    matched_conditions: List[Dict[str, Any]],
    ds_results: Dict[str, Any],
    status_perhitungan: str,
    db_path: str = DB_FILE
) -> str:
    """
    Menyimpan data hasil skrining secara anonim ke SQLite.
    Returns:
        screening_id (str)
    """
    screening_id = f"CHK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    now_iso = datetime.now().isoformat()
    
    # Hitung total jawaban 'Ya'
    total_ya = sum(1 for v in answers.values() if v in [True, 1, '1', 'Ya', 'ya', 'yes'])
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pemeriksaan (
            id,
            waktu_pemeriksaan,
            jawaban_json,
            aturan_cocok_json,
            hasil_inferensi_json,
            nilai_keyakinan_json,
            status_perhitungan,
            total_ya
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        screening_id,
        now_iso,
        json.dumps(answers, ensure_ascii=False),
        json.dumps(matched_rules, ensure_ascii=False),
        json.dumps(matched_conditions, ensure_ascii=False),
        json.dumps(ds_results, ensure_ascii=False),
        status_perhitungan,
        total_ya
    ))
    conn.commit()
    conn.close()
    
    return screening_id


def get_screening(screening_id: str, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Mengambil satu data pemeriksaan berdasarkan ID pemeriksaan privat."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pemeriksaan WHERE id = ?", (screening_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "waktu_pemeriksaan": row["waktu_pemeriksaan"],
        "jawaban": json.loads(row["jawaban_json"]),
        "aturan_cocok": json.loads(row["aturan_cocok_json"]),
        "hasil_inferensi": json.loads(row["hasil_inferensi_json"]),
        "nilai_keyakinan": json.loads(row["nilai_keyakinan_json"]) if row["nilai_keyakinan_json"] else None,
        "status_perhitungan": row["status_perhitungan"],
        "total_ya": row["total_ya"]
    }


def get_all_screenings_summary(db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Mengambil daftar ringkas pemeriksaan untuk audit internal (tanpa PII)."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, waktu_pemeriksaan, status_perhitungan, total_ya, hasil_inferensi_json
        FROM pemeriksaan
        ORDER BY waktu_pemeriksaan DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        inf = json.loads(r["hasil_inferensi_json"])
        cond_names = [c.get("nama", "") for c in inf] if isinstance(inf, list) else []
        results.append({
            "id": r["id"],
            "waktu_pemeriksaan": r["waktu_pemeriksaan"],
            "status_perhitungan": r["status_perhitungan"],
            "total_ya": r["total_ya"],
            "kondisi_terdeteksi": ", ".join(cond_names) if cond_names else "Tidak Ada Kecocokan"
        })
    return results
