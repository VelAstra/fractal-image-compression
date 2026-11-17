# Fractal Image Compression and Reconstruction Suite (FIC)

> **Proyek Capstone**: Pengembangan Aplikasi Kompresi dan Rekonstruksi Citra Digital Berbasis Fraktal  
> **Program Studi**: S1 Ilmu Komputer / Informatika, FMIPA, Universitas Gadjah Mada  
> **Anggota Tim Pengembang**:  
> - Aji Kusuma Putra (NIM: 22/503701/PA/21657)  
> - Rayhan Haldi Hermawan (NIM: 24/545406/PA/23176)  

---

## 1. Ringkasan Proyek

Repositori ini memuat implementasi lengkap dari **Fractal Image Compression (FIC)** dan **Iterated Function System (IFS) Decoder** untuk kompresi dan rekonstruksi citra digital. Berbeda dengan kompresi berbasis transformasi frekuensi tradisional (seperti DCT pada JPEG), FIC memanfaatkan redundansi *piecewise self-similarity* (keserupaan mandiri spasial) pada citra alami, di mana citra direpresentasikan sebagai *fixed-point attractor* tunggal yang dijamin konvergen oleh **Teorema Titik Tetap Banach (*Banach Fixed-Point Theorem*)**.

### Fitur Utama:
- **Vectorized BLAS Domain-Range Matching**: Menggunakan perkalian matriks cross-covariance tertutup di NumPy/BLAS, memangkas waktu kompresi dari beberapa menit menjadi <0,3 detik.
- **8 Dihedral Square Symmetries ($D_4$)**: Mengeksplorasi 8 transformasi isometri (rotasi $90^\circ, 180^\circ, 270^\circ$, refleksi horizontal, vertikal, transpose, dan anti-transpose).
- **Format Kontainer Biner Kompak (`.fic`)**: Header 15 bita dan record tetap 8 bita per blok, menghasilkan Compression Ratio terverifikasi hingga **7,99x (87,48% space saving)**.
- **Multi-pass IFS Attractor Reconstruction**: Dekoder iteratif dengan visualisasi konvergensi dinamis dari kanvas awal acak/abu-abu hingga attractor sempurna.
- **Metrik Evaluasi Lengkap**: Penghitungan otomatis Peak Signal-to-Noise Ratio (PSNR), Structural Similarity Index (SSIM), Compression Ratio (CR), dan latensi komputasi.
- **Antarmuka Desktop GUI & CLI**: Aplikasi grafis interaktif berbasis Tkinter & Pillow serta antarmuka baris perintah lengkap untuk batch ablation testing.

---

## 2. Struktur Repositori

```
fractal-image-compression/
├── fic/                          # Paket Inti Algoritma Fraktal
│   ├── __init__.py
│   ├── preprocessing.py          # Modul 1: Preprocessing & Partisi Blok (Aji)
│   ├── transforms.py             # 8 Isometri Grup Dihedral D4
│   ├── encoder.py                # Modul 2: Domain-Range Matching & Least Squares (Aji)
│   ├── decoder.py                # Modul 3: IFS Reconstruction & Attractor (Rayhan)
│   ├── binary_format.py          # Serialisasi Biner .FIC (Header + Quantization)
│   └── evaluation.py             # Modul 4: Metrik PSNR, SSIM, CR, Ablasi (Rayhan)
├── gui/                          # Antarmuka Pengguna Desktop
│   ├── __init__.py
│   └── app.py                    # Aplikasi Tkinter Modern Kanvas Ganda (Rayhan)
├── report/                       # Laporan Capstone & Naskah Akademik
│   ├── LAPORAN_CAPSTONE_FIC.md   # Laporan Capstone Lengkap (BAB I s/d BAB V)
│   ├── main.tex                  # Naskah Ilmiah Format LaTeX Article (Academic Style)
│   └── references.bib            # Sitasi Akademik (Barnsley, Jacquin, Fisher, Wang)
├── sample_data/                  # Citra Uji Sintetis & Generator
│   ├── generate_samples.py       # Pembangkit pola geometris & fraktal
│   ├── geometric.png
│   └── sierpinski.png
├── tests/                        # Pengujian Otomatis
│   ├── __init__.py
│   └── test_fic.py               # 5 Unit & Integration Tests (Exit Code 0)
├── cli.py                        # Antarmuka Baris Perintah (CLI)
├── requirements.txt              # Ketergantungan Pustaka Python
├── .gitignore
└── README.md
```

---

## 3. Pembagian Peran Tim (2 Mahasiswa)

| No | Anggota Tim | Modul Utama | Tanggung Jawab Rekayasa |
|:---|:---|:---|:---|
| 1 | **Aji Kusuma Putra**<br/>`22/503701/PA/21657` | `fic/preprocessing.py`, `fic/encoder.py`, `fic/transforms.py` | Preprocessing citra, konversi grayscale, partisi range dan sliding domain blocks, pembangkitan 8 isometri dihedral D4, matriks kovariansi BLAS, dan least-squares matcher. |
| 2 | **Rayhan Haldi Hermawan**<br/>`24/545406/PA/23176` | `fic/decoder.py`, `fic/binary_format.py`, `fic/evaluation.py`, `gui/app.py`, `cli.py` | Mesin decoding IFS teriterasi, inisialisasi kanvas, verifikasi konvergensi attractor, perancangan format biner .fic, evaluasi metrik (CR, PSNR, SSIM), GUI Tkinter, dan integrasi CLI. |

---

## 4. Instalasi & Menjalankan Proyek

### Prasyarat
- Python 3.10+ (Direkomendasikan Python 3.12)
- Pip package manager

### Langkah Instalasi
```bash
# Masuk ke direktori repositori
cd fractal-image-compression

# Instal ketergantungan pustaka
pip install -r requirements.txt
```

---

## 5. Penggunaan

### A. Menjalankan Antarmuka Grafis (GUI)
```bash
python cli.py gui
```
Atau langsung:
```bash
python gui/app.py
```

### B. Menjalankan Demonstrasi Instan (Demo Mode)
```bash
python cli.py demo
```

### C. Kompresi Citra (Encode)
```bash
# Kompresi citra ke berkas model fraktal .fic
python cli.py encode sample_data/geometric.png -o sample_data/output.fic --range-size 8 --stride 8
```

### D. Rekonstruksi Citra (Decode)
```bash
# Rekonstruksi citra dari berkas .fic dan bandingkan metrik dengan citra asli
python cli.py decode sample_data/output.fic -o sample_data/recon.png --iterations 8 --compare-with sample_data/geometric.png
```

### E. Studi Ablasi Parametrik (Benchmark Evaluation)
```bash
python cli.py evaluate sample_data/geometric.png --range-sizes 4 8 --strides 8 16
```

---

## 6. Verifikasi & Pengujian Otomatis

Seluruh komponen memiliki cakupan pengujian unit otomatis:
```bash
python -m unittest discover tests
```
Output terverifikasi:
```
.....
----------------------------------------------------------------------
Ran 5 tests in 0.060s

OK
```

---

## 7. Dokumen Laporan Capstone

- **Laporan Lengkap Bahasa Indonesia**: [LAPORAN_CAPSTONE_FIC.md](file:///c:/Users/Rayhan/Documents/Antigravity/fractal-image-compression/report/LAPORAN_CAPSTONE_FIC.md) mencakup BAB I (Pendahuluan) hingga BAB V (Kesimpulan & Saran).
- **Naskah Ilmiah LaTeX**: [main.tex](file:///c:/Users/Rayhan/Documents/Antigravity/fractal-image-compression/report/main.tex) dan [references.bib](file:///c:/Users/Rayhan/Documents/Antigravity/fractal-image-compression/report/references.bib) siap dikompilasi dengan `pdflatex` atau Overleaf.
