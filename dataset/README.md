# Dokumentasi Dataset Uji Acuan (Benchmark Test Dataset)

## 1. Deskripsi Dataset
Dataset acuan ini (`dataset_uji.csv`) digunakan untuk mengevaluasi kinerja inferensi berbasis aturan (*Forward Chaining*) pada Sistem Pakar Deteksi Kesehatan Mental Generasi Z. 

Dalam metodologi rekayasa sistem pakar (*knowledge engineering*), pengujian kinerja mesin inferensi dilakukan dengan membandingkan luaran sistem terhadap **kasus acuan berlabel** (*gold standard / benchmark cases*) yang mencakup:
1. Kasus kanonikal penuh yang memenuhi premis aturan (R1–R6).
2. Kasus parsial / sub-ambang (gejala aktif namun tidak memenuhi aturan secara utuh).
3. Kasus kontrol negatif (individu sehat / tanpa indikasi gangguan).
4. Kasus komorbiditas (memenuhi lebih dari satu aturan secara simultan).

## 2. Peringatan Metodologis
- **Bukan Jawaban Pengguna**: Sesuai kaidah penelitian ilmiah, jawaban kuesioner pengguna umum pada aplikasi publik **TIDAK DAPAT** diasumsikan sebagai label kebenaran (*ground truth*) medis. Evaluasi ilmiah harus menggunakan kasus acuan terverifikasi.
- **Sistem Berbasis Aturan (*Rule-Based*)**: Sistem ini menggunakan penalaran deduktif Forward Chaining yang bersifat deterministik, bukan model *Machine Learning* probabilistik yang dilatih dengan fungsi objektif gradien. Oleh karena itu, metrik yang dihitung mencerminkan **konsistensi aturan, sensitivitas premis, spesifisitas, dan akurasi pencocokan pola**, bukan akurasi pelatihan (*training/validation loss*).

## 3. Struktur Kolom Dataset
- `id_kasus`: Pengenal unik kasus uji (misal: `CASE-001`).
- `K01` s/d `K25`: Nilai biner (`1` = Ya, `0` = Tidak) untuk 25 indikator.
- `label_acuan_kode`: Kode kondisi acuan yang diharapkan (`G01`, `G02`, `G03`, `G04`, `G05`, `G06`, `TIDAK_ADA`).
- `label_acuan_nama`: Nama kondisi acuan (Stres, Gangguan Kecemasan, Depresi, Panic Disorder, Bipolar, Skizofrenia, atau Tidak Ada Gangguan).
- `kategori_kasus`: Deskripsi tipe kasus uji (`Kanonikal`, `Sub-ambang`, `Kontrol Negatif`, `Komorbiditas`).
