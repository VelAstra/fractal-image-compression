"""
generate_report.py - Capstone Report PDF Generator for Fractal Image Compression
Standardized for Universitas Gadjah Mada (UGM) DIKE FMIPA.
"""

import os
import sys
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, Table, PageBreak, KeepTogether

# Ensure local imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from shared.styles import (
    get_ugm_styles,
    get_booktabs_style,
    get_callout_box_style,
    UGM_NAVY,
    UGM_GOLD,
    UGM_BLUE,
)
from shared.pdf_engine import UGMReportBuilder


def build_pdf_report():
    project_root = os.path.abspath(os.path.dirname(__file__))
    output_pdf = os.path.join(project_root, "reports", "Laporan_Capstone_Fractal_Image_Compression.pdf")
    builder = UGMReportBuilder(output_pdf)
    styles = get_ugm_styles()
    story = []

    # -------------------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------------------
    story.append(Spacer(1, 1.0 * cm))
    story.append(Paragraph("UNIVERSITAS GADJAH MADA", styles["CoverUniversity"]))
    story.append(Paragraph("FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM<br/>DEPARTEMEN ILMU KOMPUTER DAN ELEKTRONIKA", styles["CoverFaculty"]))
    story.append(Spacer(1, 1.2 * cm))

    story.append(Paragraph("LAPORAN CAPSTONE PROJECT", styles["CoverDocType"]))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("PENGEMBANGAN APLIKASI KOMPRESI DAN REKONSTRUKSI CITRA DIGITAL BERBASIS FRAKTAL", styles["CoverTitle"]))
    story.append(Paragraph("Development of a Fractal-Based Image Compression and Reconstruction Application", styles["CoverSubtitle"]))
    story.append(Spacer(1, 2.5 * cm))

    identitas_text = """
    <b>Disusun Oleh:</b><br/>
    <b>Tim Pengembang Capstone DIKE FMIPA UGM</b><br/><br/>
    <b>Ketua Proyek:</b> Rayhan M. P. &nbsp;&nbsp;|&nbsp;&nbsp; <b>NIM:</b> 22/498765/PA/21345<br/>
    <b>Program Studi:</b> S1 Ilmu Komputer<br/>
    <b>Tahun Akademik:</b> 2026/2027
    """
    story.append(Paragraph(identitas_text, styles["CoverIdentity"]))
    story.append(Spacer(1, 3.0 * cm))
    story.append(Paragraph("YOGYAKARTA<br/>2026", styles["CoverYear"]))
    story.append(PageBreak())

    # -------------------------------------------------------------------------
    # RINGKASAN EKSEKUTIF
    # -------------------------------------------------------------------------
    story.append(Paragraph("RINGKASAN EKSEKUTIF", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.2 * cm))

    callout_data = [[
        Paragraph(
            "<b>Intisari Proyek:</b> Proyek capstone ini merancang dan mengimplementasikan sistem kompresi citra digital "
            "berbasis Fractal Image Compression (FIC) yang memanfaatkan sifat piecewise self-similarity pada citra alami. "
            "Pondasi matematis sistem didukung oleh Teorema Titik Tetap Banach dan Teorema Kolase. "
            "Tantangan komputasi kombinatorial diatasi melalui optimasi aljabar linier matriks kovariansi tervektorisasi (BLAS), "
            "memangkas waktu encoding menjadi 0,28 detik pada citra 256x256 piksel. Sistem mengemas parameter affine ke dalam format biner "
            ".fic (8 bita per record), menghasilkan Compression Ratio terverifikasi sebesar 7,99x (penghematan ruang 87,48%) "
            "dengan PSNR 19,23 dB dan SSIM 0,8115, serta dilengkapi GUI desktop interaktif.",
            styles["CalloutText"]
        )
    ]]
    callout_table = Table(callout_data, colWidths=[396])
    callout_table.setStyle(get_callout_box_style())
    story.append(callout_table)
    story.append(Spacer(1, 0.6 * cm))

    # -------------------------------------------------------------------------
    # BAB I: PENDAHULUAN
    # -------------------------------------------------------------------------
    story.append(Paragraph("BAB I<br/>PENDAHULUAN", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("1.1 Latar Belakang", styles["SectionHeading"]))
    story.append(Paragraph(
        "Lalu lintas data multimedia digital pada era komputasi modern menuntut efisiensi penyimpanan dan transmisi yang optimal. "
        "Format standar konvensional seperti JPEG berbasis Discrete Cosine Transform (DCT) membagi citra menjadi blok-blok "
        "independen berukuran 8x8 piksel dan mengeliminasi komponen frekuensi tinggi. Pendekatan berbasis frekuensi tersebut memicu "
        "artefak visual berupa garis batas kisi (blocking artifacts) pada rasio kompresi tinggi dan bersifat resolution-dependent.",
        styles["AcademicBody"]
    ))
    story.append(Paragraph(
        "Sebaliknya, Fractal Image Compression (FIC) yang diinisiasi oleh Barnsley dan Jacquin memodelkan citra sebagai attractor "
        "tunggal dari Partitioned Iterated Function System (PIFS). Transformasi kontraksi affine menyimpan parameter geometri dan "
        "intensitas yang merefleksikan keserupaan mandiri (self-similarity) lokal antar-wilayah citra. Pendekatan ini menawarkan "
        "keunggulan dekompresi asimetris yang sangat cepat serta independensi resolusi (fractal zoom). Proyek ini merealisasikan "
        "sistem FIC mandiri berkecepatan tinggi dengan integrasi antarmuka grafis dan format berkas biner nyata.",
        styles["AcademicBody"]
    ))

    story.append(Paragraph("1.2 Rumusan Masalah", styles["SectionHeading"]))
    story.append(Paragraph("1. Bagaimana merancang algoritma pencocokan domain-range tervektorisasi untuk mereduksi kompleksitas komputasi kuadratik O(NR * ND) menjadi waktu nyata?", styles["AcademicBullet"]))
    story.append(Paragraph("2. Bagaimana menyusun spesifikasi berkas biner kompak (.fic) yang mencakup header metadata dan kuantisasi parameter affine tanpa degradasi struktural?", styles["AcademicBullet"]))
    story.append(Paragraph("3. Bagaimana mengimplementasikan mesin rekonstruksi iteratif IFS berbasis Teorema Titik Tetap Banach yang stabil dan mengintegrasikannya ke dalam desktop GUI?", styles["AcademicBullet"]))

    story.append(Paragraph("1.3 Batasan Masalah", styles["SectionHeading"]))
    story.append(Paragraph("• Format masukan mendukung citra digital (PNG, JPG, BMP) yang dikonversi ke grayscale 8-bit.", styles["AcademicBullet"]))
    story.append(Paragraph("• Partisi range menggunakan kisi reguler berukuran 4x4 atau 8x8 piksel.", styles["AcademicBullet"]))
    story.append(Paragraph("• Domain blocks diekstraksi dengan ukuran 2x ukuran range dan langkah geser (stride) terkonfigurasi.", styles["AcademicBullet"]))
    story.append(Paragraph("• Transformasi geometris menerapkan 8 isometri dari grup dihedral D4.", styles["AcademicBullet"]))
    story.append(Paragraph("• Skala kontras dibatasi secara ketat |s| <= 0,95 guna menjamin kondisi kontraksi Lipschitz.", styles["AcademicBullet"]))

    story.append(Paragraph("1.4 Tujuan dan Manfaat Proyek", styles["SectionHeading"]))
    story.append(Paragraph(
        "Tujuan proyek adalah menghasilkan perangkat lunak kompresi dan dekompresi citra fraktal yang teruji secara fungsional, "
        "memiliki format berkas mandiri (.fic), dan dilengkapi antarmuka evaluasi metrik objektif (CR, PSNR, SSIM, dan latensi komputasi). "
        "Manfaatnya mencakup pembuktian empiris komputasi fraktal dalam ilmu komputer terapan dan penguatan kolaborasi rekayasa perangkat lunak tim.",
        styles["AcademicBody"]
    ))
    story.append(Spacer(1, 0.4 * cm))

    # -------------------------------------------------------------------------
    # BAB II: LANDASAN TEORI & FORMULASI MATEMATIKA
    # -------------------------------------------------------------------------
    story.append(Paragraph("BAB II<br/>LANDASAN TEORI DAN FORMULASI MATEMATIKA", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("2.1 Teorema Titik Tetap Banach (Banach Fixed-Point Theorem)", styles["SectionHeading"]))
    story.append(Paragraph(
        "Misalkan (X, d) merupakan ruang metrik lengkap yang merepresentasikan ruang citra berdimensi H x W dengan metrik jarak RMSE. "
        "Suatu pemetaan W: X -> X dinamakan kontraksi apabila terdapat konstanta s dalam rentang [0, 1) sedemikian rupa sehingga:",
        styles["AcademicBody"]
    ))
    story.append(Paragraph("d(W(u), W(v)) &le; s &middot; d(u, v), &nbsp;&nbsp; &forall; u, v &isin; X", styles["FormulaBlock"]))
    story.append(Paragraph(
        "Teorema Banach menjamin bahwa W memiliki tepat satu titik tetap unik x* (attractor) sedemikian rupa sehingga W(x*) = x*. "
        "Barisan iteratif x_{k+1} = W(x_k) terjamin konvergen menuju x* secara eksponensial dari sebarang citra awal x_0.",
        styles["AcademicBody"]
    ))

    story.append(Paragraph("2.2 Formulasi Least-Squares Kontras (s) dan Offset (o)", styles["SectionHeading"]))
    story.append(Paragraph(
        "Untuk setiap blok range target r dan blok domain terisometri d berdimensi P = BR x BR piksel, transformasi intensitas "
        "didefinisikan sebagai r_hat = s * d + o. Parameter optimal yang meminimalkan galat kuadrat terkecil (SSE) diturunkan secara analitis:",
        styles["AcademicBody"]
    ))
    story.append(Paragraph("s = Cov(d, r) / (&sigma;_d^2 + &epsilon;), &nbsp;&nbsp;&nbsp;&nbsp; o = r_mean - s &middot; d_mean", styles["FormulaBlock"]))
    story.append(Paragraph("SSE = s^2 &middot; &sigma;_d^2 - 2s &middot; Cov(d, r) + &sigma;_r^2", styles["FormulaBlock"]))

    story.append(Paragraph("2.3 Tabel Perbandingan Paradigma Kompresi Citra", styles["SectionHeading"]))
    story.append(Paragraph("Tabel 2.1: Perbandingan Karakteristik Algoritma Kompresi Citra Digital", styles["TableCaption"]))

    t2_data = [
        [
            Paragraph("Karakteristik", styles["TableHeaderCell"]),
            Paragraph("JPEG (DCT)", styles["TableHeaderCell"]),
            Paragraph("JPEG 2000 (DWT)", styles["TableHeaderCell"]),
            Paragraph("Fractal (FIC - Ours)", styles["TableHeaderCell"]),
        ],
        [
            Paragraph("Representasi Inti", styles["TableCellLeft"]),
            Paragraph("Koefisien Frekuensi", styles["TableCellCenter"]),
            Paragraph("Koefisien Subband", styles["TableCellCenter"]),
            Paragraph("Atraktor Transformasi Affine", styles["TableCellCenter"]),
        ],
        [
            Paragraph("Artefak Degradasi", styles["TableCellLeft"]),
            Paragraph("Blocking Grid", styles["TableCellCenter"]),
            Paragraph("Ringing / Blur", styles["TableCellCenter"]),
            Paragraph("Pola Lembut Terfraktalisasi", styles["TableCellCenter"]),
        ],
        [
            Paragraph("Independensi Resolusi", styles["TableCellLeft"]),
            Paragraph("Tidak (Pikselasi)", styles["TableCellCenter"]),
            Paragraph("Parsial (Multi-resolusi)", styles["TableCellCenter"]),
            Paragraph("Penuh (Fractal Zooming)", styles["TableCellCenter"]),
        ],
        [
            Paragraph("Asimetri Komputasi", styles["TableCellLeft"]),
            Paragraph("Simetris Cepat", styles["TableCellCenter"]),
            Paragraph("Simetris Sedang", styles["TableCellCenter"]),
            Paragraph("Asimetris (Encode Lambat, Decode Cepat)", styles["TableCellCenter"]),
        ],
    ]
    t2_table = Table(t2_data, colWidths=[100, 95, 95, 106])
    t2_table.setStyle(get_booktabs_style(len(t2_data)))
    story.append(t2_table)
    story.append(Spacer(1, 0.4 * cm))

    # -------------------------------------------------------------------------
    # BAB III: METODOLOGI & PERANCANGAN SISTEM
    # -------------------------------------------------------------------------
    story.append(Paragraph("BAB III<br/>METODOLOGI DAN PERANCANGAN SISTEM", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("3.1 Arsitektur Pipeline Sistem", styles["SectionHeading"]))
    story.append(Paragraph(
        "Sistem dibangun atas empat modul fungsional: Preprocessing, Encoding Engine, Binary Persistence (.fic), dan Decoding Engine. "
        "Pencarian domain dioptimalkan dengan mengelompokkan blok domain ke dalam matriks terpusat sehingga kalkulasi kovariansi "
        "dapat dieksekusi serentak melalui perkalian matriks BLAS berkecepatan tinggi.",
        styles["AcademicBody"]
    ))

    story.append(Paragraph("3.2 Struktur Berkas Biner Kompak (.fic)", styles["SectionHeading"]))
    story.append(Paragraph(
        "Format berkas .fic terdiri atas Header 15 bita (magic number FIC1, dimensi WxH, ukuran blok, dan stride) serta payload rekaman "
        "transformasi 8 bita per blok (dx 2B, dy 2B, scale int8 1B, offset int16 2B, isometry 1B). Eliminasi koordinat range berhasil "
        "menghemat 33% alokasi bita dibandingkan format naif.",
        styles["AcademicBody"]
    ))

    story.append(Paragraph("3.3 Pembagian Tanggung Jawab Tim Pengembang", styles["SectionHeading"]))
    story.append(Paragraph("Tabel 3.1: Matriks Pembagian Tugas Rekayasa Tim Capstone (4 Mahasiswa)", styles["TableCaption"]))

    t3_data = [
        [
            Paragraph("No", styles["TableHeaderCell"]),
            Paragraph("Anggota Tim", styles["TableHeaderCell"]),
            Paragraph("Peran & Tanggung Jawab", styles["TableHeaderCell"]),
            Paragraph("Modul Berkas", styles["TableHeaderCell"]),
        ],
        [
            Paragraph("1", styles["TableCellCenter"]),
            Paragraph("Mahasiswa 1", styles["TableCellLeft"]),
            Paragraph("Preprocessing citra, konversi grayscale, partisi range dan sliding domain blocks.", styles["TableCellLeft"]),
            Paragraph("fic/preprocessing.py", styles["TableCellCode"]),
        ],
        [
            Paragraph("2", styles["TableCellCenter"]),
            Paragraph("Mahasiswa 2", styles["TableCellLeft"]),
            Paragraph("Pembangkitan 8 isometri dihedral D4, matriks kovariansi BLAS, least-squares matcher.", styles["TableCellLeft"]),
            Paragraph("fic/encoder.py<br/>fic/transforms.py", styles["TableCellCode"]),
        ],
        [
            Paragraph("3", styles["TableCellCenter"]),
            Paragraph("Mahasiswa 3", styles["TableCellLeft"]),
            Paragraph("Mesin decoding IFS teriterasi, inisialisasi kanvas, verifikasi konvergensi.", styles["TableCellLeft"]),
            Paragraph("fic/decoder.py", styles["TableCellCode"]),
        ],
        [
            Paragraph("4", styles["TableCellCenter"]),
            Paragraph("Mahasiswa 4", styles["TableCellLeft"]),
            Paragraph("Format biner .fic, evaluasi metrik (CR, PSNR, SSIM), GUI Tkinter, dan integrasi CLI.", styles["TableCellLeft"]),
            Paragraph("fic/binary_format.py<br/>gui/app.py, cli.py", styles["TableCellCode"]),
        ],
    ]
    t3_table = Table(t3_data, colWidths=[24, 76, 196, 100])
    t3_table.setStyle(get_booktabs_style(len(t3_data)))
    story.append(t3_table)
    story.append(Spacer(1, 0.4 * cm))

    # -------------------------------------------------------------------------
    # BAB IV: IMPLEMENTASI, PENGUJIAN DAN EVALUASI
    # -------------------------------------------------------------------------
    story.append(Paragraph("BAB IV<br/>IMPLEMENTASI, PENGUJIAN DAN EVALUASI", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("4.1 Verifikasi Pengujian Otomatis (Unit Testing)", styles["SectionHeading"]))
    story.append(Paragraph(
        "Seluruh fungsionalitas diuji melalui suite pengujian otomatis tests/test_fic.py. "
        "Pengujian mencakup uji dimensi partisi, ortogonalitas 8 isometri, siklus simpan-baca format biner, "
        "konvergensi monotonik rekursif IFS, dan keabsahan metrik evaluasi. Hasil pengujian menunjukkan seluruh "
        "5 test case lulus sempurna (Ran 5 tests in 0.060s, Exit Code 0).",
        styles["AcademicBody"]
    ))

    story.append(Paragraph("4.2 Hasil Evaluasi Kuantitatif dan Studi Ablasi", styles["SectionHeading"]))
    story.append(Paragraph("Tabel 4.1: Benchmark Kinerja Kompresi dan Rekonstruksi Citra 256x256 Piksel (64 KB Mentah)", styles["TableCaption"]))

    t4_data = [
        [
            Paragraph("Ukuran Range", styles["TableHeaderCell"]),
            Paragraph("Stride Domain", styles["TableHeaderCell"]),
            Paragraph("Ukuran .FIC", styles["TableHeaderCell"]),
            Paragraph("CR", styles["TableHeaderCell"]),
            Paragraph("PSNR (dB)", styles["TableHeaderCell"]),
            Paragraph("SSIM", styles["TableHeaderCell"]),
            Paragraph("Waktu Enc", styles["TableHeaderCell"]),
            Paragraph("Waktu Dec", styles["TableHeaderCell"]),
        ],
        [
            Paragraph("4x4", styles["TableCellCenter"]),
            Paragraph("8", styles["TableCellCenter"]),
            Paragraph("32.783 B", styles["TableCellRight"]),
            Paragraph("2,00x", styles["TableCellCenter"]),
            Paragraph("24,67", styles["TableCellCenter"]),
            Paragraph("0,9488", styles["TableCellCenter"]),
            Paragraph("1,028 s", styles["TableCellCenter"]),
            Paragraph("1,318 s", styles["TableCellCenter"]),
        ],
        [
            Paragraph("4x4", styles["TableCellCenter"]),
            Paragraph("16", styles["TableCellCenter"]),
            Paragraph("32.783 B", styles["TableCellRight"]),
            Paragraph("2,00x", styles["TableCellCenter"]),
            Paragraph("23,56", styles["TableCellCenter"]),
            Paragraph("0,9390", styles["TableCellCenter"]),
            Paragraph("0,264 s", styles["TableCellCenter"]),
            Paragraph("1,324 s", styles["TableCellCenter"]),
        ],
        [
            Paragraph("8x8", styles["TableCellCenter"]),
            Paragraph("8", styles["TableCellCenter"]),
            Paragraph("8.207 B", styles["TableCellRight"]),
            Paragraph("7,99x", styles["TableCellCenter"]),
            Paragraph("19,23", styles["TableCellCenter"]),
            Paragraph("0,8115", styles["TableCellCenter"]),
            Paragraph("0,305 s", styles["TableCellCenter"]),
            Paragraph("0,417 s", styles["TableCellCenter"]),
        ],
        [
            Paragraph("8x8", styles["TableCellCenter"]),
            Paragraph("16", styles["TableCellCenter"]),
            Paragraph("8.207 B", styles["TableCellRight"]),
            Paragraph("7,99x", styles["TableCellCenter"]),
            Paragraph("18,89", styles["TableCellCenter"]),
            Paragraph("0,8002", styles["TableCellCenter"]),
            Paragraph("0,078 s", styles["TableCellCenter"]),
            Paragraph("0,426 s", styles["TableCellCenter"]),
        ],
    ]
    t4_table = Table(t4_data, colWidths=[52, 48, 54, 38, 52, 46, 52, 54])
    t4_table.setStyle(get_booktabs_style(len(t4_data)))
    story.append(t4_table)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("4.3 Pembahasan Temuan", styles["SectionHeading"]))
    story.append(Paragraph(
        "Hasil eksperimen menunjukkan trade-off yang jelas antara rasio kompresi dan fidelitas rekonstruksi. "
        "Blok range 4x4 menghasilkan rekonstruksi sangat tajam dengan SSIM 0,9488, namun rasio kompresi terbatas pada 2,00x. "
        "Konfigurasi blok 8x8 memberikan efisiensi ruang optimal hingga 7,99x (penghematan ruang 87,48%) dengan SSIM 0,8115. "
        "Peningkatan stride domain dari 8 ke 16 piksel berhasil mempercepat proses encoding sebesar 74,4% (menjadi 0,078 detik) "
        "dengan penurunan PSNR yang sangat minim (hanya 0,34 dB). Konvergensi IFS terbukti stabil dalam 6–8 iterasi.",
        styles["AcademicBody"]
    ))
    story.append(Spacer(1, 0.4 * cm))

    # -------------------------------------------------------------------------
    # BAB V: KESIMPULAN & SARAN
    # -------------------------------------------------------------------------
    story.append(Paragraph("BAB V<br/>KESIMPULAN DAN SARAN", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("5.1 Kesimpulan", styles["SectionHeading"]))
    story.append(Paragraph(
        "1. Perangkat lunak kompresi dan dekompresi citra berbasis prinsip Fractal Image Compression berhasil diimplementasikan secara utuh dan mandiri.<br/>"
        "2. Vektorisasi aljabar matriks BLAS pada estimasi least-squares memangkas bottleneck waktu encoding hingga 0,078–0,305 detik.<br/>"
        "3. Format biner mandiri .fic memberikan rasio kompresi terverifikasi 7,99x (penghematan ruang 87,48%) dengan struktur data kompak 8 bita.<br/>"
        "4. Teorema Titik Tetap Banach terbukti secara empiris di mana dekompresi IFS konvergen stabil ke citra target dari kanvas awal acak.<br/>"
        "5. Antarmuka GUI Tkinter dan CLI menyediakan kemudahan operasional dan visualisasi metrik kuantitatif lengkap.",
        styles["AcademicBodyNoIndent"]
    ))

    story.append(Paragraph("5.2 Saran Pengembangan Lanjutan", styles["SectionHeading"]))
    story.append(Paragraph(
        "1. Mengimplementasikan skema partisi adaptif Quadtree untuk meningkatkan ketajaman area kontur berfrekuensi tinggi.<br/>"
        "2. Menambahkan akselerasi GPU (CUDA/CuPy) untuk mendukung pemrosesan citra resolusi tinggi secara waktu-nyata.<br/>"
        "3. Memperluas sistem ke domain citra berwarna RGB melalui dekomposisi ruang warna YCbCr.",
        styles["AcademicBodyNoIndent"]
    ))
    story.append(Spacer(1, 0.4 * cm))

    # -------------------------------------------------------------------------
    # DAFTAR PUSTAKA
    # -------------------------------------------------------------------------
    story.append(Paragraph("DAFTAR PUSTAKA", styles["ChapterHeading"]))
    story.append(Spacer(1, 0.3 * cm))

    pustaka = [
        "Banach, S. (1922). Sur les opérations dans les ensembles abstraits et leur application aux équations intégrales. <i>Fundamenta Mathematicae</i>, 3(1), 133–181.",
        "Barnsley, M. F., & Sloan, A. D. (1988). A Better Way to Compress Images. <i>Byte Magazine</i>, 13(1), 215–223.",
        "Fisher, Y. (1995). <i>Fractal Image Compression: Theory and Application</i>. New York: Springer-Verlag.",
        "Jacquin, A. E. (1992). Image Coding Based on a Fractal Theory of Iterated Contractive Image Transformations. <i>IEEE Transactions on Image Processing</i>, 1(1), 18–30.",
        "Saupe, D. (1996). Accelerating Fractal Image Compression by Multi-Dimensional Nearest Neighbor Search. <i>IEEE Transactions on Image Processing</i>, 5(12), 1664–1670.",
        "Wang, Z., Bovik, A. C., Sheikh, H. R., & Simoncelli, E. P. (2004). Image Quality Assessment: From Error Visibility to Structural Similarity. <i>IEEE Transactions on Image Processing</i>, 13(4), 600–612.",
    ]
    for p in pustaka:
        story.append(Paragraph(p, styles["BibEntry"]))

    builder.build(story)
    print(f"Report compiled successfully: {output_pdf}")


if __name__ == "__main__":
    build_pdf_report()
