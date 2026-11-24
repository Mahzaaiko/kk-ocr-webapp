import os
import sys

# Menambahkan root direktori proyek ke sys.path jika dipanggil mandiri
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import mysql.connector
from mysql.connector import Error
from config import Config
from contextlib import contextmanager


def get_db_connection(use_database=True):
    """
    Membuka koneksi ke MySQL server menggunakan konfigurasi dari Config.
    Jika use_database=False, koneksi dibuka tanpa memilih database spesifik
    (berguna untuk inisialisasi CREATE DATABASE IF NOT EXISTS).
    """
    config_params = {
        'host': Config.DB_HOST,
        'port': Config.DB_PORT,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD,
        'charset': 'utf8mb4',
        'use_unicode': True
    }
    
    if use_database:
        config_params['database'] = Config.DB_NAME

    try:
        connection = mysql.connector.connect(**config_params)
        return connection
    except Error as e:
        # Menampilkan pesan bantuan jika MySQL belum aktif
        print(f"[ERROR] Gagal terhubung ke MySQL ({Config.DB_HOST}:{Config.DB_PORT}): {e}")
        raise e


@contextmanager
def get_db_cursor(dictionary=True, commit=False):
    """
    Context manager untuk menangani cursor dan transaksi database.
    Memastikan koneksi dan cursor ditutup dengan aman,
    serta melakukan commit otomatis jika commit=True, atau rollback jika terjadi error.
    """
    conn = get_db_connection(use_database=True)
    cursor = conn.cursor(dictionary=dictionary)
    try:
        yield cursor, conn
        if commit:
            conn.commit()
    except Exception as exc:
        conn.rollback()
        raise exc
    finally:
        cursor.close()
        conn.close()


def test_db_connection():
    """Menguji apakah koneksi ke database berhasil."""
    try:
        conn = get_db_connection(use_database=True)
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            current_db = cursor.fetchone()
            cursor.close()
            conn.close()
            return True, f"Koneksi berhasil ke database: {current_db[0]}"
    except Error as e:
        return False, str(e)
    return False, "Tidak dapat terhubung ke database."


def save_kk_with_members_transaction(identitas_kk, daftar_anggota):
    """
    Menyimpan data identitas KK (9 field) dan daftar anggota keluarga (19 field)
    ke dalam database MySQL secara transaksional (ACID).
    Jika salah satu query gagal, seluruh perubahan akan di-ROLLBACK secara otomatis.
    """
    conn = get_db_connection(use_database=True)
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # 1. Simpan Data Identitas Kartu Keluarga (9 Field + created_at)
        query_identitas = """
            INSERT INTO `tbl_identitasKK` (
                `no_kk`, `nama_kepala_keluarga`, `alamat`, `rt_rw`,
                `desa_kelurahan`, `kecamatan`, `kabupaten_kota`, `kode_pos`, `provinsi`, `created_at`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                `nama_kepala_keluarga` = VALUES(`nama_kepala_keluarga`),
                `alamat` = VALUES(`alamat`),
                `rt_rw` = VALUES(`rt_rw`),
                `desa_kelurahan` = VALUES(`desa_kelurahan`),
                `kecamatan` = VALUES(`kecamatan`),
                `kabupaten_kota` = VALUES(`kabupaten_kota`),
                `kode_pos` = VALUES(`kode_pos`),
                `provinsi` = VALUES(`provinsi`),
                `created_at` = NOW();
        """
        val_identitas = (
            str(identitas_kk.get('no_kk', '')).strip(),
            str(identitas_kk.get('nama_kepala_keluarga', '')).strip(),
            identitas_kk.get('alamat') or None,
            identitas_kk.get('rt_rw') or None,
            identitas_kk.get('desa_kelurahan') or None,
            identitas_kk.get('kecamatan') or None,
            identitas_kk.get('kabupaten_kota') or None,
            identitas_kk.get('kode_pos') or None,
            identitas_kk.get('provinsi') or None
        )
        cursor.execute(query_identitas, val_identitas)

        # 2. Hapus data anggota keluarga lama untuk no_kk ini (mencegah duplikasi data saat simpan ulang / re-upload)
        cursor.execute("DELETE FROM `tbl_anggotaKeluargaKK` WHERE `no_kk` = %s;", (str(identitas_kk.get('no_kk', '')).strip(),))

        # 3. Simpan Seluruh Anggota Keluarga (17 Field Data + no_kk)
        query_anggota = """
            INSERT INTO `tbl_anggotaKeluargaKK` (
                `no_kk`, `nama_lengkap`, `nik`, `jenis_kelamin`, `tempat_lahir`,
                `tanggal_lahir`, `agama`, `pendidikan`, `jenis_pekerjaan`,
                `golongan_darah`, `status_perkawinan`, `tanggal_perkawinan`,
                `status_hubungan_dalam_keluarga`, `kewarganegaraan`, `no_paspor`,
                `no_kitap`, `nama_ayah`, `nama_ibu`
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );
        """
        
        for anggota in daftar_anggota:
            # Nilai yang tidak terbaca atau kosong dijadikan None (NULL di SQL)
            val_anggota = (
                str(identitas_kk.get('no_kk', '')).strip(),
                anggota.get('nama_lengkap') or None,
                str(anggota.get('nik', '')).strip() if anggota.get('nik') else None,
                anggota.get('jenis_kelamin') or None,
                anggota.get('tempat_lahir') or None,
                anggota.get('tanggal_lahir') or None,
                anggota.get('agama') or None,
                anggota.get('pendidikan') or None,
                anggota.get('jenis_pekerjaan') or None,
                anggota.get('golongan_darah') or None,
                anggota.get('status_perkawinan') or None,
                anggota.get('tanggal_perkawinan') or None,
                anggota.get('status_hubungan_dalam_keluarga') or None,
                anggota.get('kewarganegaraan') or None,
                anggota.get('no_paspor') or None,
                anggota.get('no_kitap') or None,
                anggota.get('nama_ayah') or None,
                anggota.get('nama_ibu') or None
            )
            cursor.execute(query_anggota, val_anggota)

        # 3. Commit Transaksi jika semua query berhasil
        conn.commit()
        return True, "Data Kartu Keluarga dan seluruh anggota berhasil disimpan secara transaksional."

    except Exception as e:
        # 4. Rollback jika ada kegagalan query
        conn.rollback()
        print(f"[TRANSACTION ERROR] Gagal menyimpan data, rollback dijalankan: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
