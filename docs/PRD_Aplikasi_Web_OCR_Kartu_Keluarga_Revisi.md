# PRD — Aplikasi Web Pendataan Penduduk Berbasis OCR Kartu Keluarga

**Versi:** 1.1  
**Status:** Revisi  
**Jenis Proyek:** Mini Project  
**Bahasa:** Indonesia

---

## 1. Ringkasan Produk

Aplikasi web pendataan penduduk yang memungkinkan pengguna memasukkan data Kartu Keluarga (KK) melalui dua input, yaitu nama kepala keluarga dan gambar KK. Sistem menggunakan teknologi OCR (*Optical Character Recognition*) untuk membaca teks pada gambar, mengekstrak informasi identitas KK serta seluruh anggota keluarga, lalu menampilkan hasil pembacaan dalam halaman konfirmasi yang dapat diedit sebelum disimpan ke database.

Aplikasi juga menyediakan halaman penelusuran data KK, halaman detail KK dan anggota keluarga, serta fitur CRUD (*Create, Read, Update, Delete*) untuk mengelola data identitas KK maupun data anggota keluarga.

## 2. Tujuan Produk

- Mempermudah proses input data penduduk dari dokumen Kartu Keluarga.
- Mengurangi input data manual melalui ekstraksi OCR.
- Memungkinkan pengguna memeriksa dan mengoreksi hasil OCR sebelum penyimpanan.
- Menyimpan data identitas KK dan seluruh anggota keluarga secara terstruktur.
- Menyediakan fitur pencarian, penelusuran, dan pengelolaan data KK.

## 3. Ruang Lingkup

### 3.1 Termasuk dalam scope

- Input nama kepala keluarga.
- Upload gambar KK.
- OCR untuk membaca data pada gambar KK.
- Ekstraksi data identitas KK.
- Ekstraksi 17 field data anggota keluarga sesuai kolom KK.
- Halaman konfirmasi hasil OCR dengan form editable.
- Penyimpanan data ke database.
- Halaman daftar/penelusuran KK.
- Halaman detail KK dan daftar anggota keluarga.
- CRUD data identitas KK.
- CRUD data anggota keluarga.
- Validasi input dan penanganan kesalahan dasar.

### 3.2 Tidak termasuk dalam scope awal

- Upload atau pemrosesan dokumen PDF.
- Integrasi dengan database kependudukan pemerintah.
- Verifikasi keaslian KK atau validasi NIK ke layanan eksternal.
- OCR yang dijamin 100% akurat tanpa pemeriksaan pengguna.
- Multi-user atau role/permission kompleks, kecuali diwajibkan kemudian.

## 4. Target Pengguna

Pengguna aplikasi adalah operator/admin yang melakukan input, pemeriksaan, penelusuran, dan pengelolaan data KK. Pada versi mini project, aplikasi dapat digunakan oleh satu operator tanpa sistem role yang kompleks.

## 5. Alur Utama Pengguna

1. Pengguna membuka halaman input KK.
2. Pengguna mengisi nama kepala keluarga dan mengunggah gambar KK.
3. Sistem memvalidasi format dan ukuran file.
4. Sistem memproses gambar menggunakan OCR.
5. Sistem mengekstrak data identitas KK dan seluruh anggota keluarga yang terbaca.
6. Sistem menampilkan hasil OCR pada halaman konfirmasi dalam bentuk form editable.
7. Pengguna memeriksa dan mengoreksi data yang keliru atau kosong.
8. Pengguna menekan tombol **Simpan**.
9. Sistem menyimpan identitas KK dan anggota keluarga ke database dalam satu proses transaksi.
10. Sistem menampilkan notifikasi berhasil dan mengarahkan pengguna ke detail atau daftar KK.

## 6. Kebutuhan Fungsional (Functional Requirements)

| ID | Fitur | Deskripsi | Prioritas |
|---|---|---|---|
| FR-01 | Input nama kepala keluarga | Pengguna dapat memasukkan nama kepala keluarga melalui input teks. | High |
| FR-02 | Upload gambar KK | Pengguna dapat mengunggah gambar KK dengan format JPG, JPEG, atau PNG. PDF tidak diterima. | High |
| FR-03 | Validasi file | Sistem memeriksa format dan ukuran file sebelum OCR dijalankan. | High |
| FR-04 | Proses OCR | Sistem membaca teks pada gambar KK dan mengekstrak data identitas serta anggota keluarga. | High |
| FR-05 | Ekstraksi identitas KK | Sistem mengidentifikasi Nomor KK, nama kepala keluarga, alamat, RT/RW, desa/kelurahan, kecamatan, kabupaten/kota, kode pos, dan provinsi. | High |
| FR-06 | Ekstraksi anggota keluarga | Sistem mengidentifikasi seluruh 17 field anggota keluarga sesuai struktur KK yang ditetapkan pada bagian database. | High |
| FR-07 | Konfirmasi hasil OCR | Sistem menampilkan hasil OCR dalam form yang dapat diedit sebelum disimpan. | High |
| FR-08 | Koreksi data | Pengguna dapat mengubah, melengkapi, atau menghapus nilai hasil OCR pada form konfirmasi. | High |
| FR-09 | Simpan data KK | Sistem menyimpan identitas KK dan seluruh anggota keluarga ke tabel yang sesuai. | High |
| FR-10 | Daftar KK | Sistem menampilkan data identitas KK dalam tabel penelusuran. | High |
| FR-11 | Pencarian KK | Pengguna dapat mencari KK berdasarkan Nomor KK atau nama kepala keluarga. | Medium |
| FR-12 | Detail KK | Pengguna dapat membuka detail identitas KK beserta anggota keluarga yang terhubung. | High |
| FR-13 | Update identitas KK | Pengguna dapat mengubah data identitas KK yang tersimpan. | High |
| FR-14 | Delete identitas KK | Pengguna dapat menghapus data KK dengan konfirmasi terlebih dahulu. | High |
| FR-15 | Update anggota keluarga | Pengguna dapat mengubah data anggota keluarga. | High |
| FR-16 | Delete anggota keluarga | Pengguna dapat menghapus data anggota keluarga dengan konfirmasi terlebih dahulu. | High |
| FR-17 | Tambah anggota keluarga manual | Pengguna dapat menambahkan anggota keluarga melalui form jika diperlukan. | Medium |
| FR-18 | Feedback proses | Sistem menampilkan status loading, pesan sukses, atau pesan error selama proses upload, OCR, dan penyimpanan. | Medium |

## 7. Struktur Database

Database terdiri dari dua tabel utama.

### 7.1 Tabel `tbl_identitasKK`

Menyimpan informasi utama/identitas setiap Kartu Keluarga. Tabel ini memiliki 9 field, termasuk Nomor KK sebagai primary key.

| No. | Field | Tipe Data (rekomendasi) | Constraint | Keterangan |
|---:|---|---|---|---|
| 1 | `no_kk` | VARCHAR(16) | PRIMARY KEY | Nomor Kartu Keluarga |
| 2 | `nama_kepala_keluarga` | VARCHAR(100) | NOT NULL | Nama kepala keluarga |
| 3 | `alamat` | TEXT | - | Alamat |
| 4 | `rt_rw` | VARCHAR(10) | - | RT/RW |
| 5 | `desa_kelurahan` | VARCHAR(100) | - | Desa/kelurahan |
| 6 | `kecamatan` | VARCHAR(100) | - | Kecamatan |
| 7 | `kabupaten_kota` | VARCHAR(100) | - | Kabupaten/kota |
| 8 | `kode_pos` | VARCHAR(10) | - | Kode pos |
| 9 | `provinsi` | VARCHAR(100) | - | Provinsi |

**Catatan:** Nomor KK disimpan sebagai string, bukan integer, agar format dan angka nol di depan tidak berubah.

### 7.2 Tabel `tbl_anggotaKeluargaKK`

Menyimpan seluruh anggota keluarga yang tercantum pada KK. Tabel ini memiliki **19 field**, yaitu 17 field data anggota sesuai kolom KK, ditambah `id_anggota` sebagai primary key dan `no_kk` sebagai foreign key.

| No. | Field | Tipe Data (rekomendasi) | Constraint | Keterangan |
|---:|---|---|---|---|
| 1 | `id_anggota` | BIGINT / INTEGER | PRIMARY KEY, AUTO INCREMENT | ID unik anggota |
| 2 | `no_kk` | VARCHAR(16) | FOREIGN KEY | Relasi ke `tbl_identitasKK.no_kk` |
| 3 | `nama_lengkap` | VARCHAR(100) | - | Kolom 1 — Nama Lengkap |
| 4 | `nik` | VARCHAR(16) | - | Kolom 2 — NIK |
| 5 | `jenis_kelamin` | VARCHAR(20) | - | Kolom 3 — Jenis Kelamin |
| 6 | `tempat_lahir` | VARCHAR(100) | - | Kolom 4 — Tempat Lahir |
| 7 | `tanggal_lahir` | DATE | - | Kolom 5 — Tanggal Lahir |
| 8 | `agama` | VARCHAR(30) | - | Kolom 6 — Agama |
| 9 | `pendidikan` | VARCHAR(100) | - | Kolom 7 — Pendidikan |
| 10 | `jenis_pekerjaan` | VARCHAR(100) | - | Kolom 8 — Jenis Pekerjaan |
| 11 | `golongan_darah` | VARCHAR(5) | - | Kolom 9 — Golongan Darah |
| 12 | `status_perkawinan` | VARCHAR(30) | - | Kolom 10 — Status Perkawinan |
| 13 | `tanggal_perkawinan` | DATE | NULL | Kolom 11 — Tanggal Perkawinan |
| 14 | `status_hubungan_dalam_keluarga` | VARCHAR(50) | - | Kolom 12 — Status Hubungan Dalam Keluarga |
| 15 | `kewarganegaraan` | VARCHAR(10) | - | Kolom 13 — Kewarganegaraan |
| 16 | `no_paspor` | VARCHAR(30) | NULL | Kolom 14 — Dokumen Imigrasi: No. Paspor |
| 17 | `no_kitap` | VARCHAR(30) | NULL | Kolom 15 — Dokumen Imigrasi: No. KITAP |
| 18 | `nama_ayah` | VARCHAR(100) | - | Kolom 16 — Nama Orang Tua: Ayah |
| 19 | `nama_ibu` | VARCHAR(100) | - | Kolom 17 — Nama Orang Tua: Ibu |

**Aturan database:**
- `id_anggota` menjadi primary key unik dan dibuat otomatis.
- `no_kk` pada tabel anggota menjadi foreign key yang mengacu ke `tbl_identitasKK.no_kk`.
- Relasi kedua tabel adalah one-to-many: satu KK dapat memiliki banyak anggota keluarga.
- Nomor KK dan NIK harus disimpan sebagai string, bukan integer.
- Field yang tidak tercantum, kosong, atau tidak terbaca pada dokumen dapat bernilai NULL sesuai kebutuhan.
- Penyimpanan identitas KK dan seluruh anggota keluarga dilakukan dalam satu transaksi database agar tidak terjadi penyimpanan sebagian.
- Penghapusan identitas KK harus meminta konfirmasi karena dapat menghapus anggota keluarga yang terhubung. Gunakan cascade delete atau proses penghapusan terkontrol.

## 8. Spesifikasi Halaman

### 8.1 Halaman Input KK

Komponen:
- Input teks Nama Kepala Keluarga.
- Input file Gambar Kartu Keluarga.
- Preview gambar yang diunggah (opsional).
- Tombol **Proses OCR**.

Perilaku:
- Nama kepala keluarga wajib diisi.
- File wajib berupa JPG, JPEG, atau PNG.
- PDF dan format selain gambar ditolak.
- Tampilkan pesan error jika input tidak valid.

### 8.2 Halaman Konfirmasi Data OCR

Komponen:
- Form identitas KK.
- Form/tabel anggota keluarga yang memuat seluruh 17 field.
- Tombol **Simpan**.
- Tombol **Kembali/Upload Ulang**.

Perilaku:
- Seluruh nilai hasil OCR dapat diedit.
- Nilai yang tidak terbaca ditampilkan kosong agar dapat diisi manual.
- Pengguna dapat menambah atau menghapus baris anggota keluarga.
- Pengguna dapat memeriksa dan memperbaiki data sebelum penyimpanan.
- Nomor KK wajib diisi.
- Sistem melakukan validasi sebelum menyimpan.

### 8.3 Halaman Penelusuran KK

Komponen:
- Tabel daftar KK.
- Kolom pencarian.
- Tombol **Detail**, **Edit**, dan **Hapus**.

Informasi minimum:
- Nomor KK.
- Nama kepala keluarga.
- Alamat.
- Kecamatan.
- Kabupaten/kota.

Perilaku:
- Data ditampilkan dari database.
- Pencarian dapat dilakukan berdasarkan Nomor KK atau nama kepala keluarga.
- Tombol Detail membuka halaman detail KK.

### 8.4 Halaman Detail KK dan Anggota Keluarga

Komponen:
- Informasi identitas KK.
- Tabel seluruh anggota keluarga.
- Aksi Edit/Hapus identitas KK.
- Aksi Tambah/Edit/Hapus anggota keluarga.

Perilaku:
- Anggota keluarga yang ditampilkan hanya anggota dengan Nomor KK terkait.
- Pengguna dapat mengelola identitas KK dan anggota keluarga secara terpisah.

## 9. Kebutuhan Non-Fungsional

| ID | Kebutuhan | Deskripsi | Prioritas |
|---|---|---|---|
| NFR-01 | Kemudahan penggunaan | Antarmuka sederhana dan mudah dipahami operator. | High |
| NFR-02 | Validasi | Input dan file divalidasi untuk mencegah data tidak sesuai. | High |
| NFR-03 | Keamanan file | File upload dibatasi pada format gambar yang diizinkan dan ukuran maksimum yang ditentukan. | High |
| NFR-04 | Integritas data | Relasi foreign key dan transaksi database menjaga konsistensi data. | High |
| NFR-05 | Privasi | Gambar KK dan data penduduk tidak dibagikan kepada pihak yang tidak berkepentingan. | High |
| NFR-06 | Penanganan error | Error OCR, database, atau upload ditampilkan dengan pesan yang mudah dipahami. | Medium |
| NFR-07 | Maintainability | Struktur kode dipisahkan menjadi modul route, service OCR, model/database, dan template. | Medium |
| NFR-08 | Responsivitas | Halaman dapat digunakan pada desktop dan layar mobile. | Medium |

## 10. Rekomendasi Teknologi

- **Backend:** Python Flask.
- **Frontend:** HTML, CSS, Bootstrap, dan JavaScript.
- **Database:** MySQL atau SQLite.
- **OCR:** Tesseract OCR melalui `pytesseract`, dengan preprocessing gambar menggunakan OpenCV atau Pillow.
- **ORM:** SQLAlchemy (opsional).
- **File upload:** Flask file upload dengan validasi ekstensi, MIME type, dan batas ukuran.

## 11. Kriteria Penerimaan (Acceptance Criteria)

Aplikasi dinyatakan memenuhi kebutuhan mini project apabila:

1. Pengguna dapat menginput nama kepala keluarga dan mengunggah gambar KK.
2. Sistem menerima gambar JPG/JPEG/PNG dan menolak PDF.
3. Sistem menjalankan OCR dan menampilkan hasil pembacaan pada halaman konfirmasi.
4. Form konfirmasi dapat diedit untuk identitas KK dan seluruh 17 field anggota keluarga.
5. Data yang dikonfirmasi dapat disimpan ke dua tabel database dengan relasi yang benar.
6. Halaman daftar KK menampilkan data yang sudah tersimpan.
7. Pengguna dapat mencari dan membuka detail suatu KK.
8. Detail KK menampilkan seluruh anggota keluarga yang terhubung.
9. Pengguna dapat melakukan CRUD terhadap identitas KK dan anggota keluarga.
10. Sistem memberikan pesan yang jelas ketika proses berhasil atau gagal.

## 12. Catatan dan Batasan OCR

- OCR membaca teks dari gambar dan tidak menjamin akurasi 100%.
- Posisi kolom dan tabel KK dapat berbeda tergantung kualitas gambar, orientasi, resolusi, dan format dokumen.
- Sistem dapat melakukan preprocessing seperti rotasi, peningkatan kontras, dan penyesuaian ukuran gambar.
- Hasil OCR wajib melewati halaman konfirmasi pengguna sebelum masuk database.
- Akurasi dapat diuji menggunakan beberapa sampel gambar KK dan mencatat kesalahan pembacaan.
- Gunakan gambar KK contoh/dummy atau data yang telah disamarkan untuk pengembangan dan demonstrasi.

## 13. Instruksi Implementasi untuk AI Coding Assistant

Bangun aplikasi berdasarkan PRD ini secara bertahap:

1. Siapkan struktur project Python dan konfigurasi database.
2. Buat model serta relasi kedua tabel sesuai struktur field pada bagian 7.
3. Implementasikan halaman input dan upload gambar.
4. Implementasikan pipeline OCR dan ekstraksi data identitas serta 17 field anggota keluarga.
5. Buat halaman konfirmasi hasil OCR yang editable.
6. Implementasikan penyimpanan data secara transaksional.
7. Buat halaman daftar, pencarian, dan detail KK.
8. Implementasikan CRUD identitas KK dan anggota keluarga.
9. Tambahkan validasi, error handling, dan tampilan responsif.
10. Uji alur lengkap dari upload gambar sampai data tersimpan dan dapat dikelola.

**Ketentuan penting implementasi:**
- Jangan membuat seluruh aplikasi dalam satu file besar.
- Gunakan struktur project yang modular.
- Pastikan jumlah field tabel `tbl_identitasKK` adalah 9 dan `tbl_anggotaKeluargaKK` adalah 19.
- Pastikan 17 field anggota keluarga mengikuti urutan dan nama kolom pada bagian 7.2.
- Jangan menghilangkan `tanggal_perkawinan`.
- Sertakan `requirements.txt`, konfigurasi database, petunjuk instalasi, cara menjalankan aplikasi, dan langkah testing.
- Jangan mengarang hasil OCR. Data yang tidak terbaca harus ditampilkan kosong untuk diperiksa pengguna.
