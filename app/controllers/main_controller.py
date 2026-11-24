import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from app.services.file_service import validate_image_file, save_uploaded_file
from app.services.ocr_service import process_kk_ocr
from database.connection import (
    test_db_connection,
    get_db_cursor,
    get_db_connection,
    save_kk_with_members_transaction
)
from database.init_db import init_database

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    """Halaman utama (Step 1: Input Data): form input nama kepala keluarga dan unggah foto KK."""
    db_connected, db_message = test_db_connection()
    return render_template(
        'index.html',
        db_connected=db_connected,
        db_message=db_message,
        nama_kepala_keluarga=''
    )


@main_bp.route('/upload', methods=['POST'])
def upload_kk():
    """
    Menangani pengiriman form upload KK:
    1. Validasi teks Nama Kepala Keluarga (wajib diisi).
    2. Validasi file foto KK (hanya JPG, JPEG, PNG; tolak PDF & lainnya).
    3. Simpan file gambar ke uploads/.
    4. Jalankan proses OCR & ekstraksi teks.
    5. Arahkan pengguna ke halaman konfirmasi (Step 2: Periksa Hasil).
    """
    nama_kepala_keluarga = request.form.get('nama_kepala_keluarga', '').strip()
    file = request.files.get('gambar_kk')

    # 1. Validasi Nama Kepala Keluarga
    if not nama_kepala_keluarga:
        flash("Nama Kepala Keluarga wajib diisi.", "danger")
        db_connected, db_message = test_db_connection()
        return render_template(
            'index.html',
            db_connected=db_connected,
            db_message=db_message,
            nama_kepala_keluarga=nama_kepala_keluarga
        )

    # 2. Validasi File Gambar KK
    is_valid_file, file_msg = validate_image_file(file)
    if not is_valid_file:
        flash(file_msg, "danger")
        db_connected, db_message = test_db_connection()
        return render_template(
            'index.html',
            db_connected=db_connected,
            db_message=db_message,
            nama_kepala_keluarga=nama_kepala_keluarga
        )

    # 3. Simpan berkas gambar
    try:
        saved_filename, saved_path = save_uploaded_file(file)
    except Exception as e:
        flash(f"Terjadi kesalahan saat menyimpan berkas: {str(e)}", "danger")
        db_connected, db_message = test_db_connection()
        return render_template(
            'index.html',
            db_connected=db_connected,
            db_message=db_message,
            nama_kepala_keluarga=nama_kepala_keluarga
        )

    # 4. Jalankan Pipeline Ekstraksi OCR
    ocr_result = process_kk_ocr(saved_path, nama_kepala_keluarga=nama_kepala_keluarga)

    # 5. Render Halaman Konfirmasi (Step 2: Periksa Hasil)
    return render_template(
        'confirm.html',
        identitas=ocr_result['identitas_kk'],
        anggota_list=ocr_result['anggota_keluarga'],
        uploaded_filename=saved_filename,
        ocr_result=ocr_result
    )


@main_bp.route('/save-kk', methods=['POST'])
def save_kk():
    """
    Menyimpan data identitas KK (9 field) dan daftar anggota keluarga (19 field)
    dari form konfirmasi ke MySQL Laragon dalam satu transaksi ACID.
    """
    no_kk = request.form.get('no_kk', '').strip()
    nama_kepala_keluarga = request.form.get('nama_kepala_keluarga', '').strip()
    uploaded_filename = request.form.get('uploaded_filename', '')

    if not no_kk or not nama_kepala_keluarga:
        flash("Nomor Kartu Keluarga dan Nama Kepala Keluarga wajib diisi.", "danger")
        return redirect(url_for('main.index'))

    # 1. Identitas KK (9 Field)
    identitas_kk = {
        'no_kk': no_kk,
        'nama_kepala_keluarga': nama_kepala_keluarga,
        'alamat': request.form.get('alamat', '').strip(),
        'rt_rw': request.form.get('rt_rw', '').strip(),
        'desa_kelurahan': request.form.get('desa_kelurahan', '').strip(),
        'kecamatan': request.form.get('kecamatan', '').strip(),
        'kabupaten_kota': request.form.get('kabupaten_kota', '').strip(),
        'kode_pos': request.form.get('kode_pos', '').strip(),
        'provinsi': request.form.get('provinsi', '').strip()
    }

    # 2. Daftar Anggota Keluarga (17 Kolom)
    nama_lengkap_list = request.form.getlist('nama_lengkap[]')
    nik_list = request.form.getlist('nik[]')
    jenis_kelamin_list = request.form.getlist('jenis_kelamin[]')
    tempat_lahir_list = request.form.getlist('tempat_lahir[]')
    tanggal_lahir_list = request.form.getlist('tanggal_lahir[]')
    agama_list = request.form.getlist('agama[]')
    pendidikan_list = request.form.getlist('pendidikan[]')
    jenis_pekerjaan_list = request.form.getlist('jenis_pekerjaan[]')
    golongan_darah_list = request.form.getlist('golongan_darah[]')
    status_perkawinan_list = request.form.getlist('status_perkawinan[]')
    tanggal_perkawinan_list = request.form.getlist('tanggal_perkawinan[]')
    status_hubungan_list = request.form.getlist('status_hubungan_dalam_keluarga[]')
    kewarganegaraan_list = request.form.getlist('kewarganegaraan[]')
    no_paspor_list = request.form.getlist('no_paspor[]')
    no_kitap_list = request.form.getlist('no_kitap[]')
    nama_ayah_list = request.form.getlist('nama_ayah[]')
    nama_ibu_list = request.form.getlist('nama_ibu[]')

    daftar_anggota = []
    total_anggota = len(nama_lengkap_list)

    for i in range(total_anggota):
        nama = nama_lengkap_list[i].strip() if i < len(nama_lengkap_list) else ''
        if not nama:
            continue

        def get_val(arr, idx):
            val = arr[idx].strip() if idx < len(arr) else ''
            return val if val else None

        def get_date(arr, idx):
            val = arr[idx].strip() if idx < len(arr) else ''
            return val if val and len(val) == 10 else None

        anggota = {
            'nama_lengkap': nama,
            'nik': get_val(nik_list, i),
            'jenis_kelamin': get_val(jenis_kelamin_list, i),
            'tempat_lahir': get_val(tempat_lahir_list, i),
            'tanggal_lahir': get_date(tanggal_lahir_list, i),
            'agama': get_val(agama_list, i),
            'pendidikan': get_val(pendidikan_list, i),
            'jenis_pekerjaan': get_val(jenis_pekerjaan_list, i),
            'golongan_darah': get_val(golongan_darah_list, i),
            'status_perkawinan': get_val(status_perkawinan_list, i),
            'tanggal_perkawinan': get_date(tanggal_perkawinan_list, i),
            'status_hubungan_dalam_keluarga': get_val(status_hubungan_list, i),
            'kewarganegaraan': get_val(kewarganegaraan_list, i) or 'WNI',
            'no_paspor': get_val(no_paspor_list, i),
            'no_kitap': get_val(no_kitap_list, i),
            'nama_ayah': get_val(nama_ayah_list, i),
            'nama_ibu': get_val(nama_ibu_list, i)
        }
        daftar_anggota.append(anggota)

    # 3. Simpan Transaksional ke MySQL
    success, message = save_kk_with_members_transaction(identitas_kk, daftar_anggota)

    if success:
        # Tampilkan Halaman Sukses (Step 3: Simpan Data Selesai)
        return render_template(
            'success.html',
            no_kk=no_kk,
            nama_kepala_keluarga=nama_kepala_keluarga,
            total_anggota=len(daftar_anggota)
        )
    else:
        flash(f"Gagal menyimpan ke database: {message}", "danger")
        return render_template(
            'confirm.html',
            identitas=identitas_kk,
            anggota_list=daftar_anggota if daftar_anggota else [{'nama_lengkap': nama_kepala_keluarga}],
            uploaded_filename=uploaded_filename,
            ocr_result={'tesseract_available': True, 'message': message}
        )


@main_bp.route('/daftar-kk', methods=['GET'])
def daftar_kk():
    """Halaman penelusuran daftar Kartu Keluarga yang tersimpan (Read & List)."""
    search_query = request.args.get('q', '').strip()
    filter_status = request.args.get('filter_status', 'all').strip()
    
    kk_list = []
    try:
        with get_db_cursor(dictionary=True) as (cursor, conn):
            base_sql = """
                SELECT 
                    i.no_kk, 
                    i.nama_kepala_keluarga, 
                    i.alamat, 
                    i.kecamatan, 
                    i.kabupaten_kota,
                    i.created_at,
                    COUNT(a.id_anggota) AS total_anggota
                FROM tbl_identitasKK i
                LEFT JOIN tbl_anggotaKeluargaKK a ON i.no_kk = a.no_kk
            """
            where_clauses = []
            params = []
            
            if search_query:
                where_clauses.append("(i.no_kk LIKE %s OR i.nama_kepala_keluarga LIKE %s)")
                param = f"%{search_query}%"
                params.extend([param, param])

            if where_clauses:
                base_sql += " WHERE " + " AND ".join(where_clauses)
            
            base_sql += " GROUP BY i.no_kk, i.nama_kepala_keluarga, i.alamat, i.kecamatan, i.kabupaten_kota, i.created_at"

            # Filter anggota (HAVING)
            if filter_status == 'anggota_1_3':
                base_sql += " HAVING COUNT(a.id_anggota) BETWEEN 1 AND 3"
            elif filter_status == 'anggota_4_plus':
                base_sql += " HAVING COUNT(a.id_anggota) >= 4"

            # Order by
            if filter_status == 'nama_asc':
                base_sql += " ORDER BY i.nama_kepala_keluarga ASC"
            elif filter_status == 'nama_desc':
                base_sql += " ORDER BY i.nama_kepala_keluarga DESC"
            elif filter_status == 'anggota_desc':
                base_sql += " ORDER BY total_anggota DESC, i.no_kk DESC"
            else:
                base_sql += " ORDER BY i.created_at DESC, i.no_kk DESC"

            cursor.execute(base_sql, tuple(params))
            kk_list = cursor.fetchall()
            
            # Format tanggal input (misal: 21 Nov 2026, 15:21)
            months = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
            for item in kk_list:
                dt = item.get('created_at')
                if dt:
                    item['tanggal_input'] = f"{dt.day} {months[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"
                else:
                    item['tanggal_input'] = "-"
    except Exception as e:
        flash(f"Gagal mengambil data dari database: {str(e)}", "danger")

    return render_template(
        'list_kk.html',
        kk_list=kk_list,
        search_query=search_query,
        filter_status=filter_status
    )


@main_bp.route('/kk/<no_kk>', methods=['GET'])
def detail_kk(no_kk):
    """Halaman detail identitas KK dan rincian seluruh anggotanya (Detail View)."""
    kk = None
    anggota_list = []

    try:
        with get_db_cursor(dictionary=True) as (cursor, conn):
            cursor.execute("SELECT * FROM tbl_identitasKK WHERE no_kk = %s LIMIT 1;", (no_kk,))
            kk = cursor.fetchone()

            if not kk:
                flash(f"Data Kartu Keluarga dengan No. {no_kk} tidak ditemukan.", "warning")
                return redirect(url_for('main.daftar_kk'))

            cursor.execute(
                "SELECT * FROM tbl_anggotaKeluargaKK WHERE no_kk = %s ORDER BY id_anggota ASC;",
                (no_kk,)
            )
            anggota_list = cursor.fetchall()

    except Exception as e:
        flash(f"Terjadi kesalahan saat memuat detail KK: {str(e)}", "danger")
        return redirect(url_for('main.daftar_kk'))

    return render_template(
        'detail_kk.html',
        kk=kk,
        anggota_list=anggota_list
    )


@main_bp.route('/kk/<no_kk>/edit', methods=['GET', 'POST'])
def edit_kk(no_kk):
    """Fitur CRUD: Edit Data Identitas KK dan Anggota Keluarganya."""
    if request.method == 'GET':
        try:
            with get_db_cursor(dictionary=True) as (cursor, conn):
                cursor.execute("SELECT * FROM tbl_identitasKK WHERE no_kk = %s LIMIT 1;", (no_kk,))
                kk = cursor.fetchone()
                if not kk:
                    flash(f"Kartu Keluarga No. {no_kk} tidak ditemukan.", "warning")
                    return redirect(url_for('main.daftar_kk'))

                cursor.execute(
                    "SELECT * FROM tbl_anggotaKeluargaKK WHERE no_kk = %s ORDER BY id_anggota ASC;",
                    (no_kk,)
                )
                anggota_list = cursor.fetchall()
                return render_template('edit_kk.html', kk=kk, anggota_list=anggota_list)
        except Exception as e:
            flash(f"Gagal mengambil data untuk diedit: {str(e)}", "danger")
            return redirect(url_for('main.daftar_kk'))

    # POST method: Simpan perubahan edit
    nama_kepala_keluarga = request.form.get('nama_kepala_keluarga', '').strip()
    if not nama_kepala_keluarga:
        flash("Nama Kepala Keluarga tidak boleh kosong.", "danger")
        return redirect(url_for('main.edit_kk', no_kk=no_kk))

    identitas_kk = {
        'no_kk': no_kk,
        'nama_kepala_keluarga': nama_kepala_keluarga,
        'alamat': request.form.get('alamat', '').strip(),
        'rt_rw': request.form.get('rt_rw', '').strip(),
        'desa_kelurahan': request.form.get('desa_kelurahan', '').strip(),
        'kecamatan': request.form.get('kecamatan', '').strip(),
        'kabupaten_kota': request.form.get('kabupaten_kota', '').strip(),
        'kode_pos': request.form.get('kode_pos', '').strip(),
        'provinsi': request.form.get('provinsi', '').strip()
    }

    nama_lengkap_list = request.form.getlist('nama_lengkap[]')
    nik_list = request.form.getlist('nik[]')
    jenis_kelamin_list = request.form.getlist('jenis_kelamin[]')
    tempat_lahir_list = request.form.getlist('tempat_lahir[]')
    tanggal_lahir_list = request.form.getlist('tanggal_lahir[]')
    agama_list = request.form.getlist('agama[]')
    pendidikan_list = request.form.getlist('pendidikan[]')
    jenis_pekerjaan_list = request.form.getlist('jenis_pekerjaan[]')
    golongan_darah_list = request.form.getlist('golongan_darah[]')
    status_perkawinan_list = request.form.getlist('status_perkawinan[]')
    tanggal_perkawinan_list = request.form.getlist('tanggal_perkawinan[]')
    status_hubungan_list = request.form.getlist('status_hubungan_dalam_keluarga[]')
    kewarganegaraan_list = request.form.getlist('kewarganegaraan[]')
    no_paspor_list = request.form.getlist('no_paspor[]')
    no_kitap_list = request.form.getlist('no_kitap[]')
    nama_ayah_list = request.form.getlist('nama_ayah[]')
    nama_ibu_list = request.form.getlist('nama_ibu[]')

    daftar_anggota = []
    for i in range(len(nama_lengkap_list)):
        nama = nama_lengkap_list[i].strip() if i < len(nama_lengkap_list) else ''
        if not nama:
            continue

        def get_val(arr, idx):
            val = arr[idx].strip() if idx < len(arr) else ''
            return val if val else None

        def get_date(arr, idx):
            val = arr[idx].strip() if idx < len(arr) else ''
            return val if val and len(val) == 10 else None

        daftar_anggota.append({
            'nama_lengkap': nama,
            'nik': get_val(nik_list, i),
            'jenis_kelamin': get_val(jenis_kelamin_list, i),
            'tempat_lahir': get_val(tempat_lahir_list, i),
            'tanggal_lahir': get_date(tanggal_lahir_list, i),
            'agama': get_val(agama_list, i),
            'pendidikan': get_val(pendidikan_list, i),
            'jenis_pekerjaan': get_val(jenis_pekerjaan_list, i),
            'golongan_darah': get_val(golongan_darah_list, i),
            'status_perkawinan': get_val(status_perkawinan_list, i),
            'tanggal_perkawinan': get_date(tanggal_perkawinan_list, i),
            'status_hubungan_dalam_keluarga': get_val(status_hubungan_list, i),
            'kewarganegaraan': get_val(kewarganegaraan_list, i) or 'WNI',
            'no_paspor': get_val(no_paspor_list, i),
            'no_kitap': get_val(no_kitap_list, i),
            'nama_ayah': get_val(nama_ayah_list, i),
            'nama_ibu': get_val(nama_ibu_list, i)
        })

    # Simpan pembaruan secara transaksional
    conn = get_db_connection(use_database=True)
    conn.autocommit = False
    cursor = conn.cursor()
    try:
        # Update identitas KK
        query_update_kk = """
            UPDATE tbl_identitasKK
            SET nama_kepala_keluarga = %s, alamat = %s, rt_rw = %s, desa_kelurahan = %s,
                kecamatan = %s, kabupaten_kota = %s, kode_pos = %s, provinsi = %s
            WHERE no_kk = %s;
        """
        cursor.execute(query_update_kk, (
            identitas_kk['nama_kepala_keluarga'],
            identitas_kk['alamat'] or None,
            identitas_kk['rt_rw'] or None,
            identitas_kk['desa_kelurahan'] or None,
            identitas_kk['kecamatan'] or None,
            identitas_kk['kabupaten_kota'] or None,
            identitas_kk['kode_pos'] or None,
            identitas_kk['provinsi'] or None,
            no_kk
        ))

        # Hapus anggota lama dan masukkan susunan anggota terbaru
        cursor.execute("DELETE FROM tbl_anggotaKeluargaKK WHERE no_kk = %s;", (no_kk,))
        
        query_insert_anggota = """
            INSERT INTO tbl_anggotaKeluargaKK (
                no_kk, nama_lengkap, nik, jenis_kelamin, tempat_lahir,
                tanggal_lahir, agama, pendidikan, jenis_pekerjaan,
                golongan_darah, status_perkawinan, tanggal_perkawinan,
                status_hubungan_dalam_keluarga, kewarganegaraan, no_paspor,
                no_kitap, nama_ayah, nama_ibu
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        for a in daftar_anggota:
            cursor.execute(query_insert_anggota, (
                no_kk, a['nama_lengkap'], a['nik'], a['jenis_kelamin'], a['tempat_lahir'],
                a['tanggal_lahir'], a['agama'], a['pendidikan'], a['jenis_pekerjaan'],
                a['golongan_darah'], a['status_perkawinan'], a['tanggal_perkawinan'],
                a['status_hubungan_dalam_keluarga'], a['kewarganegaraan'], a['no_paspor'],
                a['no_kitap'], a['nama_ayah'], a['nama_ibu']
            ))

        conn.commit()
        flash(f"Data Kartu Keluarga No. {no_kk} berhasil diperbarui.", "success")
        return redirect(url_for('main.detail_kk', no_kk=no_kk))
    except Exception as e:
        conn.rollback()
        flash(f"Gagal memperbarui data: {str(e)}", "danger")
        return redirect(url_for('main.edit_kk', no_kk=no_kk))
    finally:
        cursor.close()
        conn.close()


@main_bp.route('/kk/<no_kk>/delete', methods=['POST'])
def delete_kk(no_kk):
    """Fitur CRUD: Menghapus Kartu Keluarga dan anggota terkait (Cascade Delete)."""
    try:
        with get_db_cursor(commit=True) as (cursor, conn):
            cursor.execute("DELETE FROM tbl_identitasKK WHERE no_kk = %s;", (no_kk,))
        flash(f"Kartu Keluarga No. {no_kk} beserta seluruh anggota keluarganya berhasil dihapus dari database.", "success")
    except Exception as e:
        flash(f"Gagal menghapus data: {str(e)}", "danger")
    
    return redirect(url_for('main.daftar_kk'))


@main_bp.route('/db-status', methods=['GET'])
def db_status():
    """Endpoint API status database."""
    connected, message = test_db_connection()
    return jsonify({
        'status': 'connected' if connected else 'disconnected',
        'message': message
    })
