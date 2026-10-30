"""
Aplikasi Utama: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Backend Web menggunakan Python Flask, Forward Chaining, Dempster-Shafer, dan SQLite.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify

from knowledge_base import INDICATORS, CONDITIONS, RULES, DS_WEIGHTS_JOURNAL
from forward_chaining import run_forward_chaining
from dempster_shafer import evaluate_dempster_shafer
from database import init_db, save_screening, get_screening

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mentalkey_expert_system_genz_2026_secured")

# Inisialisasi basis data SQLite saat startup
init_db()


@app.route("/")
def index():
    """Halaman Beranda Sistem Pakar."""
    return render_template("index.html")


@app.route("/kuesioner")
def kuesioner():
    """Halaman Kuesioner Skrining 25 Indikator (K01 - K25)."""
    return render_template("questionnaire.html", indicators=INDICATORS)


@app.route("/proses", methods=["POST"])
def proses_kuesioner():
    """
    Memproses jawaban kuesioner dari pengguna.
    Menjalankan inferensi Forward Chaining & kalkulasi Dempster-Shafer,
    kemudian menyimpan hasilnya secara anonim ke SQLite.
    """
    expected_codes = [f"K{i:02d}" for i in range(1, 26)]
    answers = {}
    missing_codes = []

    for code in expected_codes:
        val = request.form.get(code)
        if val is None or val == "":
            missing_codes.append(code)
        else:
            answers[code] = 1 if str(val).strip() in ["1", "true", "ya", "y", "yes"] else 0

    if missing_codes:
        flash(
            f"Terdapat {len(missing_codes)} pertanyaan yang belum Anda jawab ({', '.join(missing_codes)}). "
            f"Seluruh 25 pertanyaan wajib dijawab.",
            "error"
        )
        return redirect(url_for("kuesioner"))

    # 1. Jalankan Forward Chaining
    fc_result = run_forward_chaining(answers)
    matched_rules = fc_result["matched_rules"]
    matched_conditions = fc_result["matched_conditions"]

    # 2. Jalankan Dempster-Shafer untuk kondisi yang cocok
    ds_result = evaluate_dempster_shafer(fc_result) if matched_conditions else None

    # 3. Tentukan status kelengkapan perhitungan
    if not matched_conditions:
        status_perhitungan = "Tidak Ada Aturan Cocok"
    else:
        # Cek apakah seluruh kondisi yang cocok dapat dihitung nilai Dempster-Shafer-nya
        all_calculated = True
        for cond in matched_conditions:
            code = cond["kode"]
            if ds_result and "results" in ds_result and code in ds_result["results"]:
                if not ds_result["results"][code].get("can_calculate", False):
                    all_calculated = False
                    break
            else:
                all_calculated = False
                break
        status_perhitungan = "Lengkap" if all_calculated else "Bobot Tidak Lengkap"

    # 4. Simpan ke database SQLite
    screening_id = save_screening(
        answers=answers,
        matched_rules=matched_rules,
        matched_conditions=matched_conditions,
        ds_results=ds_result,
        status_perhitungan=status_perhitungan
    )

    return redirect(url_for("hasil", screening_id=screening_id))


@app.route("/hasil/<screening_id>")
def hasil(screening_id):
    """
    Halaman Hasil Pemeriksaan.
    Menampilkan luaran Forward Chaining, Dempster-Shafer, indikator pendukung, dan saran.
    """
    screening_data = get_screening(screening_id)
    if not screening_data:
        flash("Data pemeriksaan tidak ditemukan atau ID tidak valid.", "error")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        screening=screening_data,
        indicators=INDICATORS
    )


@app.route("/tentang")
def tentang():
    """Halaman Informasi Metodologi, Basis Aturan, dan Batasan Sistem."""
    return render_template(
        "about.html",
        rules=RULES,
        conditions=CONDITIONS,
        weights=DS_WEIGHTS_JOURNAL
    )


@app.errorhandler(404)
def not_found_error(error):
    return render_template(
        "base.html",
        content="<div class='card text-center'><h2 class='card-title'>Halaman Tidak Ditemukan (404)</h2><p>Halaman yang Anda tuju tidak tersedia.</p><div class='mt-4'><a href='/' class='btn btn-primary'>Kembali ke Beranda</a></div></div>"
    ), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "base.html",
        content="<div class='card text-center'><h2 class='card-title'>Terjadi Kesalahan Server (500)</h2><p>Terjadi kesalahan internal. Silakan coba kembali beberapa saat lagi.</p><div class='mt-4'><a href='/' class='btn btn-primary'>Kembali ke Beranda</a></div></div>"
    ), 500


if __name__ == "__main__":
    # Jalankan server pengembangan Flask
    app.run(host="127.0.0.1", port=5000, debug=True)
