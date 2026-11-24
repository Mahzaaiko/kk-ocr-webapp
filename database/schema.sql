-- ========================================================
-- Schema Database: db_mini_project_citra
-- Sesuai Spesifikasi PRD Aplikasi Web OCR Kartu Keluarga
-- ========================================================

CREATE DATABASE IF NOT EXISTS `db_mini_project_citra`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `db_mini_project_citra`;

-- --------------------------------------------------------
-- 1. Tabel Identitas Kartu Keluarga (Tepat 9 Field)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tbl_identitasKK` (
    `no_kk` VARCHAR(16) NOT NULL,
    `nama_kepala_keluarga` VARCHAR(100) NOT NULL,
    `alamat` TEXT NULL,
    `rt_rw` VARCHAR(10) NULL,
    `desa_kelurahan` VARCHAR(100) NULL,
    `kecamatan` VARCHAR(100) NULL,
    `kabupaten_kota` VARCHAR(100) NULL,
    `kode_pos` VARCHAR(10) NULL,
    `provinsi` VARCHAR(100) NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`no_kk`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- 2. Tabel Anggota Keluarga Kartu Keluarga (Tepat 19 Field)
-- Urutan 17 kolom anggota keluarga mengikuti PRD Bagian 7.2
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tbl_anggotaKeluargaKK` (
    `id_anggota` BIGINT NOT NULL AUTO_INCREMENT,
    `no_kk` VARCHAR(16) NOT NULL,
    `nama_lengkap` VARCHAR(100) NULL,
    `nik` VARCHAR(16) NULL,
    `jenis_kelamin` VARCHAR(20) NULL,
    `tempat_lahir` VARCHAR(100) NULL,
    `tanggal_lahir` DATE NULL,
    `agama` VARCHAR(30) NULL,
    `pendidikan` VARCHAR(100) NULL,
    `jenis_pekerjaan` VARCHAR(100) NULL,
    `golongan_darah` VARCHAR(5) NULL,
    `status_perkawinan` VARCHAR(30) NULL,
    `tanggal_perkawinan` DATE NULL,
    `status_hubungan_dalam_keluarga` VARCHAR(50) NULL,
    `kewarganegaraan` VARCHAR(10) NULL,
    `no_paspor` VARCHAR(30) NULL,
    `no_kitap` VARCHAR(30) NULL,
    `nama_ayah` VARCHAR(100) NULL,
    `nama_ibu` VARCHAR(100) NULL,
    PRIMARY KEY (`id_anggota`),
    KEY `idx_anggota_no_kk` (`no_kk`),
    CONSTRAINT `fk_anggota_identitas`
        FOREIGN KEY (`no_kk`)
        REFERENCES `tbl_identitasKK` (`no_kk`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
