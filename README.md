# Sistem Pakar Deteksi Indikasi Awal Kesehatan Mental Generasi Z

Aplikasi web sistem pakar berbasis **Python Flask** untuk mendeteksi indikasi awal kondisi kesehatan mental pada Generasi Z menggunakan metode **Forward Chaining** dan **Dempster-Shafer**.

Proyek ini dibangun berdasarkan naskah publikasi ilmiah:
> **"Sistem Pakar Deteksi Kesehatan Mental Pada Generasi Z Menggunakan Metode Forward Chaining dan Metode Dempster Shafer"**  
> Penulis: **Nanda Alifah & Rama Adistya Nurtjahya Pamudji**  
> Diterbitkan dalam: *IKRAM: Jurnal Ilmu Komputer Al Muslim*, Volume IV No. 2, Oktober 2025, hal. 78–85. ISSN: 2964-5115.

---

## 1. Arsitektur & Struktur Proyek

Proyek dirancang secara modular memisahkan antara aplikasi web publik, basis pengetahuan, mesin inferensi, basis data, dan pipeline penelitian ilmiah:

```text
MentalHealt_Project/
├── app.py                     # Entry point & controller aplikasi web Flask
├── knowledge_base.py          # Definisi indikator (K01-K25), kondisi (G01-G06), aturan (R1-R6), dan bobot
├── forward_chaining.py        # Mesin inferensi penalaran berbasis aturan deduktif
├── dempster_shafer.py         # Mesin kalkulasi fungsi massa & Teori Kombinasi Dempster
├── storage.py                 # Penyimpanan In-Memory (RAM) murni (Bebas Database Fisik SQLite)
├── benchmark_data.py          # Modul manajemen & evaluasi 10 kasus acuan berlabel
├── research_pipeline.py       # Script pipeline eksperimen & evaluasi ilmiah (Akurasi 100%)
├── evaluation.py              # Perhitungan metrik evaluasi & visualisasi grafik
├── requirements.txt           # Daftar dependensi Python
├── README.md                  # Dokumentasi teknis & panduan operasional
├── dataset/
│   ├── README.md              # Dokumentasi struktur & metodologi dataset acuan
│   └── dataset_uji.csv        # Dataset 10 kasus acuan berlabel (benchmark suite)
├── outputs/
│   ├── preprocessing/
│   │   ├── hasil_preprocessing.csv      # Data hasil pembersihan & validasi biner
│   │   └── ringkasan_preprocessing.txt  # Ringkasan data & distribusi label
│   ├── testing/
│   │   ├── hasil_pengujian.csv          # Perbandingan label acuan vs prediksi
│   │   ├── laporan_akurasi.txt          # Laporan akurasi lengkap & classification report
│   │   ├── metrik_evaluasi.json         # Metrik evaluasi dalam format terstruktur
│   │   └── confusion_matrix.png         # Visualisasi Confusion Matrix
│   └── graphs/
│       ├── grafik_akurasi.png           # Diagram batang akurasi keseluruhan
│       ├── grafik_precision_recall_f1.png # Perbandingan Precision, Recall, F1 per kelas
│       └── grafik_evaluasi.png          # Visualisasi ringkasan metrik komprehensif
├── templates/
│   ├── base.html              # Layout induk & navigasi utama
│   ├── index.html             # Halaman beranda layanan skrining
│   ├── questionnaire.html     # Kuesioner interaktif 25 pertanyaan + Auto-fill 10 Kasus
│   ├── uji_10_kasus.html      # Dashboard khusus pengujian & verifikasi 10 data acuan
│   ├── result.html            # Halaman hasil inferensi & saran
│   └── about.html             # Transparansi metodologi & aturan
└── static/
    ├── css/
    │   └── style.css          # Desain antarmuka modern, minimalis, dan profesional
    └── js/
        └── script.js          # Validasi form, kalkulasi progres, & interaktivitas
```

---

## 2. Persyaratan Sistem & Instalasi

### Prasyarat
- Python versi 3.10 atau yang lebih baru.
- Pip (Python Package Manager).
- Browser modern (Chrome, Edge, Firefox, Safari).

### Langkah 1: Clone / Siapkan Repositori
Masuk ke direktori proyek:
```bash
cd d:\MentalHealt_Project
```

### Langkah 2: Buat Virtual Environment (Direkomendasikan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Langkah 3: Pasang Dependensi
```bash
pip install -r requirements.txt
```

---

## 3. Menjalankan Website Flask

Jalankan aplikasi dengan perintah:
```bash
python app.py
```
Aplikasi akan berjalan di:
```text
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

Buka peramban (browser) dan akses alamat:
```
http://127.0.0.1:5000
```

---

## 4. Alur Layanan Website Publik

1. **Beranda (`/`)**: Pengenalan fungsi skrining mandiri, alur 3 langkah pemeriksaan, cakupan 6 kondisi, jaminan privasi data, dan peringatan medis.
2. **Kuesioner (`/kuesioner`)**: 
   - 25 pertanyaan indikator gejala (K01–K25) dengan pilihan Ya dan Tidak.
   - Indikator progres pengisian otomatis (X dari 25 terjawab).
   - Validasi ketat memastikan seluruh 25 pertanyaan terisi sebelum diproses.
3. **Hasil Pemeriksaan (`/hasil/<id>`)**:
   - Menampilkan kondisi yang terindikasi dari aturan Forward Chaining yang cocok.
   - Indikator gejala pendukung yang dijawab Ya oleh pengguna.
   - Nilai keyakinan Dempster-Shafer secara sah dan transparan.
   - Penjelasan kondisi dan saran tindakan awal.
   - Jika tidak ada aturan yang cocok, sistem memberikan penjelasan bahwa kondisi berada di bawah ambang batas aturan yang ada saat ini.

---

## 5. Pemeriksaan Data di Database SQLite

Data hasil pemeriksaan disimpan secara anonim tanpa meminta nama atau NIK di tabel `pemeriksaan` pada file `database.db`.

Untuk melihat data melalui Python:
```bash
python -c "import sqlite3; conn = sqlite3.connect('database.db'); conn.row_factory = sqlite3.Row; rows = conn.cursor().execute('SELECT id, waktu_pemeriksaan, status_perhitungan, total_ya, hasil_inferensi_json FROM pemeriksaan').fetchall(); print([dict(r) for r in rows])"
```
Atau gunakan software pembaca SQLite seperti DB Browser for SQLite atau VSCode SQLite Viewer.

---

## 6. Menjalankan Pipeline Penelitian Ilmiah

Untuk memproses dataset acuan, menjalankan pengujian otomatis, menghitung metrik performa, dan menghasilkan seluruh grafik penelitian, jalankan:

```bash
python research_pipeline.py
```

### Output yang Dihasilkan:
1. **Preprocessing (`outputs/preprocessing/`)**:
   - `hasil_preprocessing.csv`: Dataset acuan yang telah dibersihkan dan dinormalisasi.
   - `ringkasan_preprocessing.txt`: Ringkasan statistik dataset, kelengkapan, dan distribusi kelas.
2. **Pengujian (`outputs/testing/`)**:
   - `hasil_pengujian.csv`: Perbandingan baris-per-baris antara label acuan, prediksi sistem, dan status kesesuaian.
   - `laporan_akurasi.txt`: Laporan metrik ilmiah (Accuracy, Precision, Recall, F1-Score, dan Classification Report).
   - `metrik_evaluasi.json`: File JSON terstruktur untuk kebutuhan integrasi data.
   - `confusion_matrix.png`: Grafik visualisasi matriks kebingungan.
3. **Visualisasi Grafik (`outputs/graphs/`)**:
   - `grafik_akurasi.png`: Grafik batang tingkat kesesuaian sistem.
   - `grafik_precision_recall_f1.png`: Grafik komparasi performa tiap kelas kondisi.
   - `grafik_evaluasi.png`: Grafik ringkasan komprehensif metrik agregat.

---

## 7. Format Dataset Acuan (`dataset/dataset_uji.csv`)

Dataset acuan berformat CSV dengan kolom:
- `id_kasus`: Pengenal kasus (misal: `CASE-001`).
- `K01` s/d `K25`: Nilai biner (`1` = Ya, `0` = Tidak).
- `label_acuan_kode`: Kode kondisi acuan (`G01`, `G02`, `G03`, `G04`, `G05`, `G06`, `TIDAK_ADA`).
- `label_acuan_nama`: Nama kondisi acuan (misal: `Stres`, `Depresi`, `Tidak Ada Gangguan`).
- `kategori_kasus`: Tipe kasus (`Kanonikal`, `Sub-ambang`, `Kontrol Negatif`).

---

## 8. Basis Pengetahuan & Audit Metodologi Jurnal

### A. Kaidah Aturan Forward Chaining (Tabel 1 Jurnal)
- **R1:** `IF K12 AND K13 AND K14 AND K15 AND K17 THEN G01 (Stres)`
- **R2:** `IF K05 AND K09 AND K16 AND K17 AND K21 THEN G02 (Gangguan Kecemasan)`  
  *(Dokumentasi: Teks jurnal mencantumkan angka '21', dinormalisasi menjadi 'K21' berdasarkan pola penomoran kode indikator)*
- **R3:** `IF K20 AND K22 AND K23 AND K24 AND K25 THEN G03 (Depresi)`
- **R4:** `IF K05 AND K07 AND K08 AND K09 AND K16 THEN G04 (Panic Disorder)`
- **R5:** `IF K03 AND K04 AND K06 AND K20 AND K22 THEN G05 (Bipolar)`
- **R6:** `IF K01 AND K02 AND K08 AND K10 AND K11 AND K18 AND K24 THEN G06 (Skizofrenia)`

### B. Deskripsi Indikator K11
Tercantum pada Tabel 3 halaman 81 jurnal:  
`"Apakah anda mengalami kelebihan berat badan atau obesitas"`.  
Teks ini telah diverifikasi langsung dari publikasi asli tanpa interpretasi buatan.

### C. Teori Dempster-Shafer & Temuan Audit
Tabel bobot pada naskah jurnal (hal. 82) hanya mencantumkan bobot untuk 8 indikator:
`K01 (0.80), K12 (0.80), K13 (0.70), K14 (0.80), K15 (0.80), K17 (0.80), K19 (0.80), K20 (0.80)`.

- **Kondisi G01 (Stres):** Seluruh 5 indikator premis (K12, K13, K14, K15, K17) memiliki bobot resmi di jurnal. Nilai keyakinan Dempster-Shafer untuk kondisi Stres dapat dihitung secara valid (mencapai 99.95%).
- **Kondisi G02–G06:** Sebagian besar indikator premis tidak memiliki bobot dalam publikasi jurnal. Sistem secara tegas **tidak mengarang bobot palsu** dan menampilkan status informatif bahwa nilai keyakinan belum dapat dihitung karena keterbatasan data publikasi ilmiah.
- **Inkonsistensi Naskah Jurnal:** Jurnal memuat galat aritmatika manual pada teks perhitungannya (misalnya $1 - 0.9962$ ditulis $0.338$, dan densitas kombinasi menghasilkan $1.000388$). Sistem ini mengimplementasikan formula kombinasi Dempster yang murni matematis, ternormalisasi, dan presisi.

---

## 9. Penafian Medis (Medical Disclaimer)

Sistem ini adalah aplikasi perangkat lunak berbasis aturan (*expert system*) untuk tujuan edukasi dan peningkatan kesadaran diri (*early self-screening*). Hasil pemeriksaan sistem ini **bukan merupakan diagnosis medis klinis**. Pengguna yang mengalami gangguan emosional atau tekanan psikologis disarankan untuk menghubungi psikolog, psikiater, atau fasilitas kesehatan resmi.
