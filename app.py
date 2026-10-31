"""
Aplikasi Utama: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Menggunakan Forward Chaining dan Dempster-Shafer.
Bebas Database Fisik (Murni In-Memory Storage & Logika Algoritma Sistem Pakar).
Dilengkapi Pengujian 10 Data Kasus Acuan (Benchmark Gold Standard).
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from knowledge_base import INDICATORS, CONDITIONS, RULES, DS_WEIGHTS_JOURNAL
from forward_chaining import run_forward_chaining
from dempster_shafer import evaluate_dempster_shafer
from storage import save_screening, get_screening
from benchmark_data import (
    load_10_benchmark_cases,
    get_benchmark_case,
    run_benchmark_case_inference,
    evaluate_all_10_cases
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mentalkey_expert_system_genz_2026_secured")


@app.route("/")
def index():
    """Halaman Beranda Sistem Pakar."""
    return render_template("index.html")


@app.route("/kuesioner")
def kuesioner():
    """
    Halaman Kuesioner Skrining 25 Indikator (K01 - K25).
    Menyertakan 10 data kasus acuan untuk opsi pengujian cepat / demo otomatis.
    """
    cases = load_10_benchmark_cases()
    load_case_id = request.args.get("load", "").strip()
    return render_template(
        "questionnaire.html",
        indicators=INDICATORS,
        benchmark_cases=cases,
        load_case_id=load_case_id
    )


@app.route("/proses", methods=["POST"])
def proses_kuesioner():
    """
    Memproses jawaban kuesioner dari pengguna.
    Menjalankan inferensi Forward Chaining & kalkulasi Dempster-Shafer,
    kemudian menyimpan hasilnya secara aman di memori (In-Memory RAM).
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

    # 4. Simpan ke In-Memory Storage (RAM murni, tanpa database)
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
        flash("Data pemeriksaan tidak ditemukan di memori atau ID tidak valid.", "error")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        screening=screening_data,
        indicators=INDICATORS
    )


@app.route("/uji-10-kasus")
def uji_10_kasus():
    """
    Dashboard Khusus Pengujian 10 Data Kasus Acuan (Benchmark Dataset).
    Menampilkan tabel perbandingan label acuan vs prediksi sistem,
    metrik evaluasi akurasi, dan tautan untuk menguji masing-masing kasus.
    """
    eval_summary = evaluate_all_10_cases()
    return render_template(
        "uji_10_kasus.html",
        total_cases=eval_summary["total_cases"],
        correct_count=eval_summary["correct_count"],
        accuracy=eval_summary["accuracy_percentage"],
        results=eval_summary["results"]
    )


@app.route("/uji-kasus/<case_id>")
def uji_kasus_langsung(case_id):
    """
    Menjalankan inferensi Forward Chaining & Dempster-Shafer langsung
    untuk satu data kasus acuan tertentu, menyimpannya di memori,
    dan langsung menampilkan halaman hasil pemeriksaan.
    """
    case = get_benchmark_case(case_id)
    if not case:
        flash(f"Kasus acuan dengan ID '{case_id}' tidak ditemukan.", "error")
        return redirect(url_for("uji_10_kasus"))

    answers = case["answers"]
    fc_result = run_forward_chaining(answers)
    matched_rules = fc_result["matched_rules"]
    matched_conditions = fc_result["matched_conditions"]
    ds_result = evaluate_dempster_shafer(fc_result) if matched_conditions else None

    if not matched_conditions:
        status_perhitungan = "Tidak Ada Aturan Cocok"
    else:
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

    screening_id = save_screening(
        answers=answers,
        matched_rules=matched_rules,
        matched_conditions=matched_conditions,
        ds_results=ds_result,
        status_perhitungan=status_perhitungan
    )

    return redirect(url_for("hasil", screening_id=screening_id))


@app.route("/api/benchmark/<case_id>")
def api_benchmark_case(case_id):
    """Endpoint API JSON untuk mengambil rincian jawaban satu kasus acuan."""
    case = get_benchmark_case(case_id)
    if not case:
        return jsonify({"error": "Kasus tidak ditemukan"}), 404
    return jsonify(case)


@app.route("/api/evaluasi-10-kasus")
def api_evaluasi_10_kasus():
    """Endpoint API JSON hasil evaluasi batch 10 kasus acuan."""
    eval_summary = evaluate_all_10_cases()
    # Bersihkan objek kompleks agar aman di-serialize ke JSON
    clean_results = []
    for r in eval_summary["results"]:
        clean_results.append({
            "id_kasus": r["id_kasus"],
            "kategori_kasus": r["kategori_kasus"],
            "label_acuan_kode": r["label_acuan_kode"],
            "label_acuan_nama": r["label_acuan_nama"],
            "prediksi_kode": r["prediksi_kode"],
            "prediksi_nama": r["prediksi_nama"],
            "is_correct": r["is_correct"],
            "belief_percentage": r["belief_percentage"],
            "total_gejala": r["total_gejala"],
            "gejala_aktif": r["gejala_aktif"]
        })
    return jsonify({
        "total_cases": eval_summary["total_cases"],
        "correct_count": eval_summary["correct_count"],
        "accuracy_percentage": eval_summary["accuracy_percentage"],
        "results": clean_results
    })


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
    app.run(host="127.0.0.1", port=5000, debug=True)
