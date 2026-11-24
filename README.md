# Aplikasi Web Pendataan Penduduk Berbasis OCR Kartu Keluarga

Aplikasi web berbasis Python Flask untuk mendata penduduk secara efisien melalui ekstraksi teks otomatis (*Optical Character Recognition*) dari foto/scan Kartu Keluarga (KK).

---

## 1. Arsitektur & Struktur Direktori

Proyek ini dibangun dengan struktur modular untuk memastikan maintainability dan pemisahan *concern* yang jelas:

```text
Project_Citra/
├── app/
│   ├── __init__.py               # Application Factory Flask (create_app)
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── main_controller.py   # Handler route input KK, upload, & status DB
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_service.py       # Validasi file (JPG/JPEG/PNG, tolak PDF, cek MIME)
│   │   └── ocr_service.py        # Service & pipeline OCR Tesseract
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css         # Styling modern, responsif, table overflow-x: auto
│   │   └── js/
│   │       └── main.js           # Client-side validation, drag & drop, image preview
│   └── templates/
│       ├── base.html             # Layout utama (Navbar, Flash alerts, Footer)
│       └── index.html            # Halaman input Kepala Keluarga & upload KK
├── database/
│   ├── __init__.py
│   ├── connection.py             # Koneksi raw SQL MySQL (mysql-connector-python)
│   ├── init_db.py                # Script inisialisasi otomatis DB & tabel
│   └── schema.sql                # Skema DDL tbl_identitasKK & tbl_anggotaKeluargaKK
├── docs/
│   └── PRD_Aplikasi_Web_OCR_Kartu_Keluarga_Revisi.md
├── uploads/                      # Direktori penyimpanan sementara berkas gambar KK
│   └── .gitkeep
├── .env                          # Konfigurasi environment lokal (Laragon)
├── .env.example                  # Template environment variables
├── .gitignore                    # Berkas pengecualian Git
├── config.py                     # Konfigurasi aplikasi terpusat
├── requirements.txt              # Daftar dependensi Python
├── run.py                        # Entry point server Flask
└── README.md                     # Panduan penggunaan & dokumentasi
```

---

## 2. Struktur Database (Bagian 7 & 13 PRD)

Database MySQL menggunakan nama **`db_mini_project_citra`**.

### 2.1 Tabel `tbl_identitasKK` (Tepat 9 Field)
| No | Field | Tipe Data | Keterangan |
|---|---|---|---|
| 1 | `no_kk` | VARCHAR(16) | PRIMARY KEY (String) |
| 2 | `nama_kepala_keluarga` | VARCHAR(100) | NOT NULL |
| 3 | `alamat` | TEXT | Alamat tempat tinggal |
| 4 | `rt_rw` | VARCHAR(10) | RT / RW |
| 5 | `desa_kelurahan` | VARCHAR(100) | Kelurahan / Desa |
| 6 | `kecamatan` | VARCHAR(100) | Kecamatan |
| 7 | `kabupaten_kota` | VARCHAR(100) | Kabupaten / Kota |
| 8 | `kode_pos` | VARCHAR(10) | Kode Pos |
| 9 | `provinsi` | VARCHAR(100) | Provinsi |

### 2.2 Tabel `tbl_anggotaKeluargaKK` (Tepat 19 Field)
Urutan 17 kolom anggota keluarga mengikuti urutan resmi blangko KK:
| No | Field | Tipe Data | Keterangan |
|---|---|---|---|
| 1 | `id_anggota` | BIGINT | PRIMARY KEY, AUTO_INCREMENT |
| 2 | `no_kk` | VARCHAR(16) | FOREIGN KEY (REFERENCES `tbl_identitasKK.no_kk` ON DELETE CASCADE) |
| 3 | `nama_lengkap` | VARCHAR(100) | Kolom 1 — Nama Lengkap |
| 4 | `nik` | VARCHAR(16) | Kolom 2 — NIK (String) |
| 5 | `jenis_kelamin` | VARCHAR(20) | Kolom 3 — Jenis Kelamin |
| 6 | `tempat_lahir` | VARCHAR(100) | Kolom 4 — Tempat Lahir |
| 7 | `tanggal_lahir` | DATE | Kolom 5 — Tanggal Lahir |
| 8 | `agama` | VARCHAR(30) | Kolom 6 — Agama |
| 9 | `pendidikan` | VARCHAR(100) | Kolom 7 — Pendidikan |
| 10 | `jenis_pekerjaan` | VARCHAR(100) | Kolom 8 — Jenis Pekerjaan |
| 11 | `golongan_darah` | VARCHAR(5) | Kolom 9 — Golongan Darah |
| 12 | `status_perkawinan` | VARCHAR(30) | Kolom 10 — Status Perkawinan |
| 13 | `tanggal_perkawinan` | DATE | Kolom 11 — Tanggal Perkawinan |
| 14 | `status_hubungan_dalam_keluarga` | VARCHAR(50) | Kolom 12 — Hubungan Keluarga |
| 15 | `kewarganegaraan` | VARCHAR(10) | Kolom 13 — Kewarganegaraan |
| 16 | `no_paspor` | VARCHAR(30) | Kolom 14 — No. Paspor |
| 17 | `no_kitap` | VARCHAR(30) | Kolom 15 — No. KITAP |
| 18 | `nama_ayah` | VARCHAR(100) | Kolom 16 — Nama Ayah |
| 19 | `nama_ibu` | VARCHAR(100) | Kolom 17 — Nama Ibu |

---

## 3. Panduan Instalasi & Menjalankan Server Lokal

### Langkah 1: Pastikan Laragon Aktif
1. Buka aplikasi **Laragon**.
2. Klik tombol **Start All** untuk mengaktifkan service **MySQL** (Port: 3306) dan **Apache/Nginx**.

### Langkah 2: Buat & Aktifkan Virtual Environment
Buka terminal (PowerShell atau Command Prompt) di folder proyek `D:\Project\Project_Citra`:

```powershell
# Buat virtual environment jika belum ada
python -m venv venv

# Aktifkan virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Atau jika menggunakan Command Prompt (cmd.exe):
# .\venv\Scripts\activate.bat
```

> **Catatan PowerShell**: Jika muncul pesan *script execution policy*, jalankan perintah:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Langkah 3: Install Dependensi Python
```powershell
pip install -r requirements.txt
```

### Langkah 4: Inisialisasi Database & Tabel
Jalankan script inisialisasi otomatis:
```powershell
python database/init_db.py
```
*Script ini akan otomatis membuat database `db_mini_project_citra` (jika belum ada) dan membuat kedua tabel beserta relasi foreign key `ON DELETE CASCADE`.*

Atau Anda juga dapat menggunakan perintah Flask CLI:
```powershell
flask init-db
```

### Langkah 5: Jalankan Server Aplikasi Flask
```powershell
python run.py
```
Aplikasi akan aktif pada alamat:
👉 **http://127.0.0.1:5000**

---

## 4. Fitur yang Telah Diimplementasikan pada Tahap 1
1. **Form Input Lengkap:** Input Nama Kepala Keluarga (wajib diisi) dan berkas gambar KK.
2. **Validasi File Ketat:**
   - Format yang diterima: **JPG, JPEG, PNG** (Maks 16MB).
   - Format **PDF ditolak secara eksplisit** baik di sisi klien (JavaScript) maupun di sisi server (Python).
   - Verifikasi integritas format gambar menggunakan Pillow (mencegah manipulasi ekstensi palsu).
3. **Penyimpanan Berkas Terisolasi:** Berkas tersimpan di folder `uploads/` dengan nama unik berbasis UUID.
4. **Indikator Status Database Real-Time:** Menampilkan status konektivitas MySQL Laragon secara langsung pada UI.
5. **Horizontal Scroll Table (`overflow-x: auto`):** Pembungkus tabel anggota keluarga telah dirancang agar 17 kolom tabel tetap rapi dan tidak merusak layout pada perangkat apa pun.
