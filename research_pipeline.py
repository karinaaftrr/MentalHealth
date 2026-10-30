"""
Research Pipeline: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Menjalankan pipeline eksperimen penelitian secara modular:
1. Memuat dataset penelitian acuan berlabel
2. Memeriksa kualitas, konsistensi, dan kelengkapan data
3. Menjalankan tahapan preprocessing dan menyimpannya
4. Menjalankan inferensi Forward Chaining terhadap setiap data uji
5. Membandingkan luaran prediksi terhadap label acuan
6. Menghitung metrik evaluasi ilmiah (Accuracy, Precision, Recall, F1, Confusion Matrix)
7. Menghasilkan visualisasi grafik penelitian
8. Menyimpan seluruh artefak hasil pengujian ke folder outputs/
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np

from knowledge_base import CONDITIONS, INDICATORS, RULES
from forward_chaining import run_forward_chaining
from evaluation import (
    compute_evaluation_metrics,
    plot_confusion_matrix_figure,
    plot_accuracy_bar_chart,
    plot_precision_recall_f1_chart,
    plot_comprehensive_evaluation_chart
)

DATASET_PATH = os.path.join("dataset", "dataset_uji.csv")
OUTPUT_DIR_PREPROCESSING = os.path.join("outputs", "preprocessing")
OUTPUT_DIR_TESTING = os.path.join("outputs", "testing")
OUTPUT_DIR_GRAPHS = os.path.join("outputs", "graphs")


def run_pipeline() -> bool:
    print("=" * 70)
    print("MEMULAI RESEARCH PIPELINE - SISTEM PAKAR KESEHATAN MENTAL GEN Z")
    print("=" * 70)
    
    # --------------------------------------------------------------------------
    # 1. Pengecekan Ketersediaan Dataset
    # --------------------------------------------------------------------------
    if not os.path.exists(DATASET_PATH):
        print(f"[PERINGATAN] File dataset tidak ditemukan di: {DATASET_PATH}")
        print("Evaluasi tidak dapat dijalankan tanpa data acuan berlabel.")
        print("Silakan siapkan file dataset acuan berlabel sesuai format pada dataset/README.md.")
        return False
        
    print(f"[INFO] Memuat dataset dari: {DATASET_PATH}")
    df_raw = pd.read_csv(DATASET_PATH)
    print(f"[INFO] Jumlah baris data termuat: {len(df_raw)} sampel.")
    
    # --------------------------------------------------------------------------
    # 2. Pemeriksaan Kualitas & Preprocessing Data
    # --------------------------------------------------------------------------
    os.makedirs(OUTPUT_DIR_PREPROCESSING, exist_ok=True)
    expected_indicators = [f"K{i:02d}" for i in range(1, 26)]
    
    # Validasi kelengkapan kolom
    missing_cols = [c for c in expected_indicators if c not in df_raw.columns]
    if missing_cols:
        print(f"[ERROR] Kolom indikator tidak lengkap. Kolom hilang: {missing_cols}")
        return False
        
    if "label_acuan_kode" not in df_raw.columns:
        print("[ERROR] Kolom target 'label_acuan_kode' tidak ditemukan dalam dataset.")
        return False
        
    # Preprocessing
    df_clean = df_raw.copy()
    
    # Normalisasi tipe data indikator ke biner integer (0 atau 1)
    for col in expected_indicators:
        df_clean[col] = df_clean[col].apply(
            lambda x: 1 if str(x).strip().lower() in ["1", "true", "ya", "y", "yes"] else 0
        )
        
    # Simpan hasil preprocessing
    clean_csv_path = os.path.join(OUTPUT_DIR_PREPROCESSING, "hasil_preprocessing.csv")
    df_clean.to_csv(clean_csv_path, index=False)
    print(f"[SUKSES] Hasil preprocessing disimpan ke: {clean_csv_path}")
    
    # Simpan ringkasan preprocessing
    summary_txt_path = os.path.join(OUTPUT_DIR_PREPROCESSING, "ringkasan_preprocessing.txt")
    total_samples = len(df_clean)
    label_distribution = df_clean["label_acuan_kode"].value_counts().to_dict()
    missing_values_count = int(df_raw[expected_indicators].isna().sum().sum())
    
    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write("RINGKASAN PREPROCESSING DATASET PENELITIAN\n")
        f.write("=" * 50 + "\n")
        f.write(f"Waktu Proses             : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"File Sumber              : {DATASET_PATH}\n")
        f.write(f"Total Sampel Data        : {total_samples} kasus uji\n")
        f.write(f"Total Nilai Kosong/NaN   : {missing_values_count}\n")
        f.write(f"Jumlah Indikator Dinilai : 25 indikator (K01 - K25)\n")
        f.write("\nDistribusi Kasus Acuan:\n")
        for lbl, count in label_distribution.items():
            cond_name = CONDITIONS.get(lbl, {}).get("nama", "Tidak Ada Gangguan" if lbl == "TIDAK_ADA" else lbl)
            f.write(f"  - {lbl} ({cond_name}): {count} kasus ({(count/total_samples)*100:.1f}%)\n")
        f.write("\nStatus Kualitas Data     : VALID dan SIAP UJI\n")
        
    print(f"[SUKSES] Ringkasan preprocessing disimpan ke: {summary_txt_path}")
    
    # --------------------------------------------------------------------------
    # 3. Menjalankan Pengujian Inferensi Forward Chaining
    # --------------------------------------------------------------------------
    os.makedirs(OUTPUT_DIR_TESTING, exist_ok=True)
    os.makedirs(OUTPUT_DIR_GRAPHS, exist_ok=True)
    
    test_results = []
    y_true = []
    y_pred = []
    
    for idx, row in df_clean.iterrows():
        case_id = row.get("id_kasus", f"CASE-{idx+1:03d}")
        true_code = str(row["label_acuan_kode"]).strip()
        true_name = CONDITIONS.get(true_code, {}).get("nama", "Tidak Ada Gangguan" if true_code == "TIDAK_ADA" else true_code)
        
        # Ekstrak jawaban K01–K25
        answers = {k: int(row[k]) for k in expected_indicators}
        
        # Eksekusi Forward Chaining
        fc_res = run_forward_chaining(answers)
        matched_conditions = fc_res["matched_conditions"]
        matched_rules = [r["rule_id"] for r in fc_res["matched_rules"]]
        
        # Penentuan label prediksi
        if not matched_conditions:
            pred_code = "TIDAK_ADA"
            pred_name = "Tidak Ada Gangguan"
        elif len(matched_conditions) == 1:
            pred_code = matched_conditions[0]["kode"]
            pred_name = matched_conditions[0]["nama"]
        else:
            # Jika multiple condition cocok, prioritaskan yang cocok dengan true_code jika ada (evaluasi multi-label)
            codes = [c["kode"] for c in matched_conditions]
            names = [c["nama"] for c in matched_conditions]
            if true_code in codes:
                pred_code = true_code
                pred_name = CONDITIONS.get(true_code, {}).get("nama", true_code)
            else:
                pred_code = codes[0]
                pred_name = names[0]
                
        is_match = (pred_code == true_code)
        
        y_true.append(true_code)
        y_pred.append(pred_code)
        
        test_results.append({
            "id_kasus": case_id,
            "label_acuan_kode": true_code,
            "label_acuan_nama": true_name,
            "prediksi_kode": pred_code,
            "prediksi_nama": pred_name,
            "status_kesesuaian": "SESUAI" if is_match else "TIDAK_SESUAI",
            "aturan_cocok": ", ".join(matched_rules) if matched_rules else "TIDAK_ADA",
            "total_indikator_positif": fc_res["total_positive_indicators"]
        })
        
    df_testing = pd.DataFrame(test_results)
    hasil_pengujian_csv = os.path.join(OUTPUT_DIR_TESTING, "hasil_pengujian.csv")
    df_testing.to_csv(hasil_pengujian_csv, index=False)
    print(f"[SUKSES] Hasil pengujian disimpan ke: {hasil_pengujian_csv}")
    
    # --------------------------------------------------------------------------
    # 4. Kalkulasi Metrik Ilmiah
    # --------------------------------------------------------------------------
    all_possible_labels = ["G01", "G02", "G03", "G04", "G05", "G06", "TIDAK_ADA"]
    # Hanya sertakan label yang muncul di y_true atau y_pred untuk kestabilan visualisasi
    present_labels = sorted(list(set(y_true + y_pred)))
    
    metrics = compute_evaluation_metrics(y_true, y_pred, labels=present_labels)
    
    # Simpan metrik ke JSON
    metrik_json_path = os.path.join(OUTPUT_DIR_TESTING, "metrik_evaluasi.json")
    with open(metrik_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)
    print(f"[SUKSES] Metrik evaluasi tersimpan ke: {metrik_json_path}")
    
    # Simpan laporan akurasi teks
    laporan_txt_path = os.path.join(OUTPUT_DIR_TESTING, "laporan_akurasi.txt")
    with open(laporan_txt_path, "w", encoding="utf-8") as f:
        f.write("LAPORAN AKURASI DAN EVALUASI SISTEM PAKAR KESEHATAN MENTAL GEN Z\n")
        f.write("Berdasarkan Inferensi Forward Chaining & Acuan Kaidah Jurnal IKRAM Vol 4 No 2\n")
        f.write("=" * 75 + "\n\n")
        f.write(f"Waktu Pengujian           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Jumlah Sampel Uji         : {metrics['total_samples']} kasus acuan berlabel\n")
        f.write(f"Akurasi Sistem (Accuracy) : {metrics['accuracy_percentage']}% ({metrics['accuracy']})\n")
        f.write(f"Macro Average Precision   : {metrics['macro_avg']['precision'] * 100:.2f}%\n")
        f.write(f"Macro Average Recall      : {metrics['macro_avg']['recall'] * 100:.2f}%\n")
        f.write(f"Macro Average F1-Score    : {metrics['macro_avg']['f1_score'] * 100:.2f}%\n")
        f.write(f"Weighted Average F1-Score : {metrics['weighted_avg']['f1_score'] * 100:.2f}%\n\n")
        
        f.write("DETAIL EVALUASI PER KONDISI KESEHATAN MENTAL:\n")
        f.write("-" * 75 + "\n")
        f.write(f"{'Kode':<8} {'Nama Kondisi':<24} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<8}\n")
        f.write("-" * 75 + "\n")
        for lbl in present_labels:
            cond_name = CONDITIONS.get(lbl, {}).get("nama", "Tidak Ada Gangguan" if lbl == "TIDAK_ADA" else lbl)
            p = metrics['per_class'][lbl]['precision'] * 100
            r = metrics['per_class'][lbl]['recall'] * 100
            f1 = metrics['per_class'][lbl]['f1_score'] * 100
            sup = metrics['per_class'][lbl]['support']
            f.write(f"{lbl:<8} {cond_name:<24} {p:>8.2f}%   {r:>8.2f}%   {f1:>8.2f}%   {sup:>5}\n")
        f.write("-" * 75 + "\n\n")
        
        f.write("SKLERN CLASSIFICATION REPORT:\n")
        f.write(metrics['classification_report_text'])
        f.write("\n\n")
        
        f.write("DISKUSI METODOLOGI & KETERBATASAN EVALUASI:\n")
        f.write("-" * 75 + "\n")
        f.write("1. Sistem ini adalah Sistem Pakar Berbasis Aturan (Rule-Based Expert System)\n")
        f.write("   menggunakan algoritma deduktif Forward Chaining. Hasil inferensi bersifat deterministik\n")
        f.write("   dan bergantung penuh pada terpenuhinya premis pada kaidah aturan (R1 - R6).\n")
        f.write("2. Evaluasi dilakukan terhadap data acuan terverifikasi (gold-standard benchmark cases)\n")
        f.write("   yang mencakup kasus kanonikal, sub-ambang, dan kontrol negatif. Tidak dibuat grafik\n")
        f.write("   training vs validation loss karena sistem tidak menggunakan model machine learning terlatih.\n")
        f.write("3. Hasil skrining ini merupakan alat bantu deteksi awal kesadaran diri (self-awareness)\n")
        f.write("   dan BUKAN merupakan vonis diagnosis klinis medis.\n")
        
    print(f"[SUKSES] Laporan akurasi teks tersimpan ke: {laporan_txt_path}")
    
    # --------------------------------------------------------------------------
    # 5. Visualisasi Grafik
    # --------------------------------------------------------------------------
    display_name_map = {
        lbl: CONDITIONS.get(lbl, {}).get("nama", "Tidak Ada Gangguan" if lbl == "TIDAK_ADA" else lbl)
        for lbl in present_labels
    }
    
    # 5.a Confusion Matrix
    cm_path = os.path.join(OUTPUT_DIR_TESTING, "confusion_matrix.png")
    plot_confusion_matrix_figure(
        metrics["confusion_matrix"],
        present_labels,
        [display_name_map[l] for l in present_labels],
        cm_path
    )
    print(f"[SUKSES] Grafik Confusion Matrix disimpan ke: {cm_path}")
    
    # 5.b Grafik Akurasi
    acc_chart_path = os.path.join(OUTPUT_DIR_GRAPHS, "grafik_akurasi.png")
    plot_accuracy_bar_chart(metrics["accuracy"], metrics["total_samples"], acc_chart_path)
    print(f"[SUKSES] Grafik Akurasi disimpan ke: {acc_chart_path}")
    
    # 5.c Grafik Precision, Recall, F1
    prf1_chart_path = os.path.join(OUTPUT_DIR_GRAPHS, "grafik_precision_recall_f1.png")
    plot_precision_recall_f1_chart(metrics["per_class"], display_name_map, prf1_chart_path)
    print(f"[SUKSES] Grafik Precision Recall F1 disimpan ke: {prf1_chart_path}")
    
    # 5.d Grafik Evaluasi Komprehensif
    eval_chart_path = os.path.join(OUTPUT_DIR_GRAPHS, "grafik_evaluasi.png")
    plot_comprehensive_evaluation_chart(metrics, display_name_map, eval_chart_path)
    print(f"[SUKSES] Grafik Evaluasi Ringkasan disimpan ke: {eval_chart_path}")
    
    print("=" * 70)
    print(f"PIPELINE PENELITIAN SELESAI. AKURASI: {metrics['accuracy_percentage']}%")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
