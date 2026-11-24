import os
import sys

# Menambahkan root direktori proyek ke sys.path agar modul root seperti config.py dapat ditemukan
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import mysql.connector
from mysql.connector import Error
from config import Config


def init_database():
    """
    Inisialisasi database db_mini_project_citra dan membuat tabel:
    1. tbl_identitasKK (9 field)
    2. tbl_anggotaKeluargaKK (19 field)
    Sesuai file database/schema.sql.
    """
    print("=" * 60)
    print("Menjalankan Inisialisasi Database MySQL (Laragon)...")
    print(f"Target Host: {Config.DB_HOST}:{Config.DB_PORT}")
    print(f"Target Database: {Config.DB_NAME}")
    print("=" * 60)

    # 1. Koneksi ke server MySQL tanpa memilih database (untuk memastikan DB ada)
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Buat database jika belum ada
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        print(f"[OK] Database `{Config.DB_NAME}` dipastikan telah tersedia.")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[ERROR] Gagal terhubung ke MySQL Server: {e}")
        print("Pastikan Laragon / MySQL Service sudah di-start (Start All).")
        return False, str(e)

    # 2. Buka file schema.sql dan eksekusi pernyataan SQL pada database target
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema_path):
        err_msg = f"File schema tidak ditemukan di: {schema_path}"
        print(f"[ERROR] {err_msg}")
        return False, err_msg

    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Eksekusi multi-statement SQL
        # Bersihkan komentar satu baris (-- ...) sebelum memproses statement
        cleaned_lines = []
        for line in sql_script.splitlines():
            line_stripped = line.strip()
            if not line_stripped.startswith('--'):
                cleaned_lines.append(line)
        cleaned_sql = "\n".join(cleaned_lines)

        statements = cleaned_sql.split(';')
        for stmt in statements:
            stmt_clean = stmt.strip()
            # Abaikan perintah kosong atau USE database (sudah terkoneksi ke DB)
            if stmt_clean and not stmt_clean.upper().startswith("USE ") and not stmt_clean.upper().startswith("CREATE DATABASE"):
                cursor.execute(stmt_clean)

        conn.commit()
        print("[OK] Seluruh tabel berhasil dibuat / diverifikasi dari schema.sql.")

        # 3. Verifikasi jumlah kolom tiap tabel
        cursor.execute("DESCRIBE `tbl_identitasKK`;")
        cols_identitas = cursor.fetchall()
        print(f"[VERIFIKASI] tbl_identitasKK memiliki {len(cols_identitas)} kolom (Target: 9 kolom).")
        for col in cols_identitas:
            print(f"  - {col[0]} ({col[1]})")

        cursor.execute("DESCRIBE `tbl_anggotaKeluargaKK`;")
        cols_anggota = cursor.fetchall()
        print(f"[VERIFIKASI] tbl_anggotaKeluargaKK memiliki {len(cols_anggota)} kolom (Target: 19 kolom).")
        for col in cols_anggota:
            print(f"  - {col[0]} ({col[1]})")

        cursor.close()
        conn.close()

        print("=" * 60)
        print("Inisialisasi Database Selesai dengan Sukses!")
        print("=" * 60)
        return True, "Inisialisasi database dan pembuatan tabel berhasil."

    except Error as e:
        print(f"[ERROR] Terjadi kesalahan saat eksekusi schema SQL: {e}")
        return False, str(e)


if __name__ == '__main__':
    success, msg = init_database()
    if not success:
        exit(1)
