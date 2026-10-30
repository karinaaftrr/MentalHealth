"""
Knowledge Base: Sistem Pakar Deteksi Kesehatan Mental pada Generasi Z
Berdasarkan Jurnal:
"Sistem Pakar Deteksi Kesehatan Mental Pada Generasi Z Menggunakan Metode
Forward Chaining dan Metode Dempster Shafer"
Penulis: Nanda Alifah & Rama Adistya Nurtjahya Pamudji
Publikasi: IKRAM: Jurnal Ilmu Komputer Al Muslim, Vol. IV No. 2, Oktober 2025, hal. 78-85.
"""

from typing import Dict, List, Any

# ==============================================================================
# 1. TIPE GEJALA / KONDISI KESEHATAN MENTAL (Tabel 2 Jurnal)
# ==============================================================================
CONDITIONS: Dict[str, Dict[str, str]] = {
    "G01": {
        "kode": "G01",
        "nama": "Stres",
        "deskripsi": (
            "Kondisi ketegangan emosional atau fisik akibat tekanan beban kerja, "
            "tuntutan akademik, masalah finansial, maupun relasi interpersonal."
        ),
        "saran": (
            "Lakukan manajemen stres secara bertahap, luangkan waktu untuk relaksasi, "
            "atur prioritas kegiatan, dan bicarakan beban yang Anda rasakan kepada orang terpercaya "
            "atau konselor jika tekanan terus berlanjut."
        )
    },
    "G02": {
        "kode": "G02",
        "nama": "Gangguan Kecemasan",
        "deskripsi": (
            "Rasa cemas, gugup, atau khawatir yang berlebihan dan persisten di berbagai situasi, "
            "sering disertai ketegangan otot dan gangguan tidur."
        ),
        "saran": (
            "Latihan pernapasan dalam (deep breathing), kurangi konsumsi kafein, "
            "serta pertimbangkan untuk berkonsultasi dengan psikolog guna mempelajari teknik cognitive-behavioral."
        )
    },
    "G03": {
        "kode": "G03",
        "nama": "Depresi",
        "deskripsi": (
            "Gangguan suasana hati yang ditandai dengan perasaan sedih mendalam, kehilangan minat, "
            "keputusasaan, perubahan pola tidur/makan, hingga penurunan energi yang signifikan."
        ),
        "saran": (
            "Sangat disarankan untuk mencari bantuan profesional psikolog atau psikiater. "
            "Dukungan orang terdekat dan intervensi terstruktur sangat krusial dalam pemulihan kondisi depresi."
        )
    },
    "G04": {
        "kode": "G04",
        "nama": "Panic Disorder",
        "deskripsi": (
            "Serangan panik yang muncul secara mendadak dan berulang, ditandai dengan gejala fisik intens "
            "seperti nyeri dada, sakit perut/kepala tanpa sebab medis, dan ketakutan ekstrem."
        ),
        "saran": (
            "Penting untuk melakukan pemeriksaan medis untuk menyingkirkan penyebab fisik, "
            "kemudian berkonsultasi dengan psikolog atau psikiater untuk terapi pengendalian serangan panik."
        )
    },
    "G05": {
        "kode": "G05",
        "nama": "Bipolar",
        "deskripsi": (
            "Kondisi fluktuasi suasana hati yang ekstrem, meliputi episode mania/hipomania "
            "(kemarahan, energi berlebih, perubahan nafsu makan) dan episode depresi (kesedihan mendalam, hilang percaya diri)."
        ),
        "saran": (
            "Diperlukan evaluasi komprehensif oleh psikiater untuk penegakan diagnosis klinis "
            "serta manajemen suasana hati (mood stabilizer) yang teratur."
        )
    },
    "G06": {
        "kode": "G06",
        "nama": "Skizofrenia",
        "deskripsi": (
            "Gangguan kejiwaan kompleks yang dapat memengaruhi cara berpikir, merasa, dan berperilaku, "
            "sering berkaitan dengan penarikan diri sosial ekstrem, perlambatan motorik/bicara, dan riwayat trauma berat."
        ),
        "saran": (
            "Sangat disarankan segera berkonsultasi ke fasilitas psikiatri atau dokter spesialis kedokteran jiwa "
            "untuk asesmen medis klinis formal dan terapi berkelanjutan."
        )
    }
}

# ==============================================================================
# 2. INDIKATOR GEJALA KESEHATAN MENTAL K01 - K25 (Tabel 3 Jurnal)
# ==============================================================================
# Catatan K11: Tercantum dalam Tabel 3 jurnal hal. 81 sebagai:
# "Apakah anda mengalami kelebihan berat badan atau obesitas".
# Deskripsi indikator K11 telah diverifikasi langsung dari naskah publikasi asli.
INDICATORS: Dict[str, Dict[str, Any]] = {
    "K01": {
        "kode": "K01",
        "pertanyaan": "Apakah Anda menggunakan minuman beralkohol atau obat-obatan terlarang?",
        "teks_asli_jurnal": "Apakah anda menggunaka minuman beralkohol atau obat obatan terlarang"
    },
    "K02": {
        "kode": "K02",
        "pertanyaan": "Apakah Anda sering menjadi penyendiri dan enggan berinteraksi dengan orang lain?",
        "teks_asli_jurnal": "Apakah anda sering menjadi penyendiri dan enggan berinteraksi dengan orang lain"
    },
    "K03": {
        "kode": "K03",
        "pertanyaan": "Apakah Anda mengalami perubahan pola makan, seperti enggan makan atau makan secara berlebihan?",
        "teks_asli_jurnal": "Apakah anda mengalami perubahan pola makan, seperti enggan makan atau makan secara berlebihan"
    },
    "K04": {
        "kode": "K04",
        "pertanyaan": "Apakah Anda sering merasa marah-marah dan sulit mengendalikan kemarahan?",
        "teks_asli_jurnal": "Apakah anda sering merasa marah-marah dan sukit mengendalikan kemarahan"
    },
    "K05": {
        "kode": "K05",
        "pertanyaan": "Apakah Anda mengalami gangguan tidur, seperti sulit tidur atau sering terbangun di malam hari?",
        "teks_asli_jurnal": "Apakah anda mengalami gangguan tidur, seperti sulit tidur atau sering terbangun dimalam hari"
    },
    "K06": {
        "kode": "K06",
        "pertanyaan": "Apakah Anda merasa lelah berlebihan?",
        "teks_asli_jurnal": "Apakah anda merasa Lelah berlebihan"
    },
    "K07": {
        "kode": "K07",
        "pertanyaan": "Apakah Anda sering mengalami sakit kepala yang tidak dapat dijelaskan secara medis?",
        "teks_asli_jurnal": "Apakah anda sering mengalami sakit kepala yang tidak dapat dijelaskan secara medis"
    },
    "K08": {
        "kode": "K08",
        "pertanyaan": "Apakah Anda sering mengalami sakit perut yang tidak dapat dijelaskan secara medis?",
        "teks_asli_jurnal": "Apakah anda sering mengalami sakit perut yang tidak dapat dijelaskan secara medis"
    },
    "K09": {
        "kode": "K09",
        "pertanyaan": "Apakah Anda mengalami nyeri dada atau ketegangan pada otot-otot tubuh?",
        "teks_asli_jurnal": "Apakah anda mengalami nyeri dada atau ketegangan pada otot-otot tubuh"
    },
    "K10": {
        "kode": "K10",
        "pertanyaan": "Apakah Anda mengalami penurunan gairah seksual atau masalah dalam kehidupan seksual Anda?",
        "teks_asli_jurnal": "Apakah anda mengalami penurunan gairah seksual atau masalah dalam kehidupan seksual anda"
    },
    "K11": {
        "kode": "K11",
        "pertanyaan": "Apakah Anda mengalami kelebihan berat badan atau obesitas?",
        "teks_asli_jurnal": "Apakah anda mengalami kelebihan berat badan atau obesitas",
        "catatan_verifikasi": "Telah diverifikasi dari naskah publikasi IKRAM Vol 4 No 2 hal. 81 Tabel 3."
    },
    "K12": {
        "kode": "K12",
        "pertanyaan": "Apakah Anda mengalami tekanan atau tuntutan dalam pekerjaan atau kehidupan sehari-hari?",
        "teks_asli_jurnal": "Apakah anda mengalami tekanan atau tuntutan dalam pekerjaan atau kehidupan sehari-hari"
    },
    "K13": {
        "kode": "K13",
        "pertanyaan": "Apakah Anda mengalami masalah keuangan yang menyebabkan stres?",
        "teks_asli_jurnal": "Apakah anda mengalami masalah keuangan yang menyebabkan stress?"
    },
    "K14": {
        "kode": "K14",
        "pertanyaan": "Apakah Anda mengalami masalah dalam hubungan sosial atau interpersonal?",
        "teks_asli_jurnal": "Apkaah anda mengalami masalah dalam hubungan sosial atau interpersonal?"
    },
    "K15": {
        "kode": "K15",
        "pertanyaan": "Apakah Anda merasa sulit mengatasi permasalahan atau menemukan solusi untuk mengurangi stres?",
        "teks_asli_jurnal": "Apakah anda merasa sulit mengatasi permasalaahn atau menemukan solusi untuk mengurangi stress?"
    },
    "K16": {
        "kode": "K16",
        "pertanyaan": "Apakah Anda sering merasa cemas atau gelisah pada berbagai situasi, bukan hanya pada kejadian tertentu?",
        "teks_asli_jurnal": "Apakah anda sering merasa cemas atau gelisah pada berbagai situasi, bukan hanya pada kejadian tertentu?"
    },
    "K17": {
        "kode": "K17",
        "pertanyaan": "Apakah Anda sulit berkonsentrasi dan merasa tidak dapat fokus dengan baik?",
        "teks_asli_jurnal": "Apakah anda sulit berkonsentrasi dan merasa tidak dapat focus dengan baik?"
    },
    "K18": {
        "kode": "K18",
        "pertanyaan": "Apakah Anda memiliki riwayat trauma atau pengalaman intimidasi, pelecehan, atau kekerasan?",
        "teks_asli_jurnal": "Apakah anda memiliki Riwayat trauma atau pengalaman intimidasi, pelecehan, atau kekerasan?"
    },
    "K19": {
        "kode": "K19",
        "pertanyaan": "Apakah Anda mengalami tingkat stres yang tinggi dalam jangka waktu yang lama?",
        "teks_asli_jurnal": "Apakah anda mengalami tingkat stress yang tinggi dalam ajngka waktu yang lama"
    },
    "K20": {
        "kode": "K20",
        "pertanyaan": "Apakah Anda terus-menerus merasa sedih, bahkan terus-menerus menangis?",
        "teks_asli_jurnal": "Apakah anda terus menerus merasa sedih, bahkan terus menerus menangis?"
    },
    "K21": {
        "kode": "K21",
        "pertanyaan": "Apakah Anda merasa sangat bersalah dan khawatir berlebihan?",
        "teks_asli_jurnal": "Apakah anda merasa sangat bersalah dan khawatir berlebihan"
    },
    "K22": {
        "kode": "K22",
        "pertanyaan": "Apakah Anda merasa tidak dapat menikmati hidup karena kehilangan rasa percaya diri?",
        "teks_asli_jurnal": "Apakah anda merasa tidak dapat menikmati hidup karena kehilangan rasa percaya diri"
    },
    "K23": {
        "kode": "K23",
        "pertanyaan": "Apakah Anda mengalami kesulitan membuat keputusan dan mudah tersinggung?",
        "teks_asli_jurnal": "Apakah anda mengalami kesulitan membuat keputusan dan mudah tersinggung"
    },
    "K24": {
        "kode": "K24",
        "pertanyaan": "Apakah bicara atau gerakan Anda menjadi lebih lambat?",
        "teks_asli_jurnal": "Apakah bicara atau Gerakan anda menjadi lebih lambat"
    },
    "K25": {
        "kode": "K25",
        "pertanyaan": "Apakah Anda memiliki pikiran untuk menyakiti diri sendiri atau bunuh diri?",
        "teks_asli_jurnal": "Apakah anda memiliki pikiran untuk menyakiti diri sendiri atau bunuh diri?"
    }
}

# ==============================================================================
# 3. BASIS ATURAN FORWARD CHAINING (Tabel 1 Jurnal)
# ==============================================================================
# Dokumentasi normalisasi:
# Rule 2 dalam naskah jurnal menuliskan:
# "IF K05 AND K09 AND K16 AND K17 AND 21 THEN Pasien kemungkinan mengalami G02 – Gangguan Kecemasan"
# String '21' dinormalisasi menjadi 'K21' berdasarkan pola penomoran kode indikator K01–K25.
RULES: List[Dict[str, Any]] = [
    {
        "id": "R1",
        "nama": "Rule 1",
        "premis": ["K12", "K13", "K14", "K15", "K17"],
        "kesimpulan": "G01",
        "nama_kondisi": "Stres",
        "teks_aturan": "IF K12 AND K13 AND K14 AND K15 AND K17 THEN G01 (Stres)",
        "catatan": "Seluruh 5 indikator memiliki bobot pada Tabel Dempster-Shafer di jurnal."
    },
    {
        "id": "R2",
        "nama": "Rule 2",
        "premis": ["K05", "K09", "K16", "K17", "K21"],
        "kesimpulan": "G02",
        "nama_kondisi": "Gangguan Kecemasan",
        "teks_aturan": "IF K05 AND K09 AND K16 AND K17 AND K21 THEN G02 (Gangguan Kecemasan)",
        "catatan": "Naskah jurnal menuliskan '21'; dinormalisasi menjadi K21. Bobot K05, K09, K16, K21 tidak tersedia di jurnal."
    },
    {
        "id": "R3",
        "nama": "Rule 3",
        "premis": ["K20", "K22", "K23", "K24", "K25"],
        "kesimpulan": "G03",
        "nama_kondisi": "Depresi",
        "teks_aturan": "IF K20 AND K22 AND K23 AND K24 AND K25 THEN G03 (Depresi)",
        "catatan": "Bobot K22, K23, K24, K25 tidak dipublikasikan dalam jurnal."
    },
    {
        "id": "R4",
        "nama": "Rule 4",
        "premis": ["K05", "K07", "K08", "K09", "K16"],
        "kesimpulan": "G04",
        "nama_kondisi": "Panic Disorder",
        "teks_aturan": "IF K05 AND K07 AND K08 AND K09 AND K16 THEN G04 (Panic Disorder)",
        "catatan": "Bobot untuk seluruh indikator premis tidak dipublikasikan dalam jurnal."
    },
    {
        "id": "R5",
        "nama": "Rule 5",
        "premis": ["K03", "K04", "K06", "K20", "K22"],
        "kesimpulan": "G05",
        "nama_kondisi": "Bipolar",
        "teks_aturan": "IF K03 AND K04 AND K06 AND K20 AND K22 THEN G05 (Bipolar)",
        "catatan": "Hanya K20 yang memiliki bobot di jurnal; bobot K03, K04, K06, K22 tidak tersedia."
    },
    {
        "id": "R6",
        "nama": "Rule 6",
        "premis": ["K01", "K02", "K08", "K10", "K11", "K18", "K24"],
        "kesimpulan": "G06",
        "nama_kondisi": "Skizofrenia",
        "teks_aturan": "IF K01 AND K02 AND K08 AND K10 AND K11 AND K18 AND K24 THEN G06 (Skizofrenia)",
        "catatan": "Hanya K01 yang memiliki bobot di jurnal; bobot K02, K08, K10, K11, K18, K24 tidak tersedia."
    }
]

# ==============================================================================
# 4. BOBOT RESMI DEMPSTER-SHAFER DARI JURNAL
# ==============================================================================
# Jurnal IKRAM Vol 4 No 2 hal. 82-83 hanya mencantumkan bobot berikut pada tabel:
DS_WEIGHTS_JOURNAL: Dict[str, float] = {
    "K01": 0.80,
    "K12": 0.80,
    "K13": 0.70,
    "K14": 0.80,
    "K15": 0.80,
    "K17": 0.80,
    "K19": 0.80,
    "K20": 0.80,
}

# ==============================================================================
# 5. DOKUMENTASI DISKREPANSI & KETERBATASAN METODOLOGI JURNAL
# ==============================================================================
JOURNAL_LIMITATIONS_DOC = """
CATATAN ILMIAH & AUDIT KETIDAKKONSISTENAN JURNAL:
1. Ketidaklengkapan Bobot:
   Tabel bobot pada naskah jurnal (hal. 82) hanya menyajikan bobot untuk 8 indikator
   (K01, K12, K13, K14, K15, K17, K19, K20). 17 indikator lainnya tidak memiliki
   nilai bobot keyakinan dari pakar.
2. Kesesuaian Premis Rule 1 (Stres):
   Rule 1 didefinisikan sebagai (K12, K13, K14, K15, K17). Kelima indikator ini
   seluruhnya tercantum dalam tabel bobot (K12=0.80, K13=0.70, K14=0.80, K15=0.80, K17=0.80).
   Oleh karena itu, perhitungan Dempster-Shafer untuk Rule 1 dapat dihitung secara sah
   dan valid tanpa mengarang data.
3. Inkonsistensi Narasi Perhitungan di Jurnal:
   - Pada halaman 82 naskah jurnal, penulis menuliskan narasi: "R1 = K01 and K02 Then G01",
     yang bertentangan dengan Tabel 1 (Rule 1).
   - Pada contoh perhitungan di jurnal, penulis menggabungkan K01, K12, K14, K15, K19, K20
     untuk G01 (Stres), memasukkan K01, K19, dan K20 yang sebenarnya bukan bagian dari Rule 1.
   - Terjadi galat aritmatika manual pada teks jurnal: M7 {θ} = 1 - 0.9962 ditulis 0.338
     (seharusnya 0.0038), dan densitas M11 menghasilkan 1.000388 (melebihi batas probabilitas 1.0).
4. Penanganan pada Sistem Ini:
   - Sistem ini TIDAK mengarang bobot palsu untuk indikator yang tidak ada di jurnal.
   - Jika Rule 1 (Stres) terpenuhi, Dempster-Shafer dihitung murni dengan formula kombinasi
     resmi pada indikator premis Rule 1 yang memiliki bobot sah di jurnal.
   - Untuk aturan lain (R2–R6) di mana bobot indikator tidak lengkap, sistem menampilkan hasil
     inferensi Forward Chaining secara transparan disertai status bahwa nilai keyakinan
     Dempster-Shafer belum dapat dihitung karena bobot tidak dipublikasikan dalam sumber.
"""
