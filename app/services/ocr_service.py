import os
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from config import Config


def configure_tesseract():
    """Mengonfigurasi path executable Tesseract di Windows jika tersedia."""
    if Config.TESSERACT_CMD and os.path.exists(Config.TESSERACT_CMD):
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
        return True
    
    if os.name == 'nt':
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
            r"D:\Program Files\Tesseract-OCR\tesseract.exe"
        ]
        for p in common_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                return True
                
    return False


def is_tesseract_available():
    """Memeriksa apakah executable Tesseract OCR dapat dipanggil."""
    configure_tesseract()
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def clean_text(text):
    """Membersihkan teks dari karakter aneh dan whitespace berlebih."""
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def normalize_name(name):
    """Membersihkan dan menormalkan nama anggota keluarga dari noise OCR."""
    if not name:
        return ""
    name = re.sub(r'^[_\-\|\:0-9\.\)\s]+', '', name).strip()
    name = re.sub(r'[_\-\|\:0-9\.\)\s]+$', '', name).strip()
    
    # Perbaiki huruf I di awal nama Bali
    name = re.sub(
        r'^(?:1|Ji|\|)\s*(MADE|WAYAN|NYOMAN|KETUT|PUTU|GUSTI|DEWA|KOMANG|KADEK|LUH|IDA)',
        r'I \1',
        name,
        flags=re.IGNORECASE
    )
    if re.match(r'^(MADE|WAYAN|NYOMAN|KETUT|PUTU|KOMANG|KADEK)\b', name, flags=re.IGNORECASE):
        name = 'I ' + name

    name = re.sub(
        r'\bNI(WAYAN|NYOMAN|LUH|PUTU|KADEK|KOMANG)\b',
        r'NI \1',
        name,
        flags=re.IGNORECASE
    )
    
    # Normalisasi jika huruf I di awal nama Bali menyatu tanpa spasi
    name = re.sub(r'^I(MADE|WAYAN|NYOMAN|KETUT|PUTU|KOMANG|KADEK|GUSTI|DEWA)\b', r'I \1', name, flags=re.IGNORECASE)
    
    # Normalisasi jika garis batas tabel | terbaca J di awal nama
    name = re.sub(r'^J(ALFONS)\b', r'\1', name, flags=re.IGNORECASE)

    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'^SRI([A-Z])', r'SRI \1', name)
    return name


def extract_identitas_kk_from_text(raw_text, default_nama_kepala=""):
    """
    Mengekstrak 9 field identitas KK dari teks mentah OCR.
    Menangani berbagai blangko resmi Kartu Keluarga di Indonesia.
    """
    identitas = {
        'no_kk': '',
        'nama_kepala_keluarga': default_nama_kepala,
        'alamat': '',
        'rt_rw': '-',
        'desa_kelurahan': '',
        'kecamatan': '',
        'kabupaten_kota': '',
        'kode_pos': '',
        'provinsi': ''
    }

    if not raw_text:
        return identitas

    # 1. Ekstraksi Nomor Kartu Keluarga (16 digit)
    # Mencari pola 'No' yang diikuti 16 karakter alfanumerik (bisa ada noise seperti 'b' menggantikan '6', dsb.)
    m_no = re.search(r'(?:No|NO|N0)[^0-9a-zA-Z\n]{0,10}([0-9a-zA-Z]{15,17})', raw_text)
    if m_no:
        raw_kk = m_no.group(1)
        # Normalisasi karakter OCR yang sering tertukar dengan angka
        clean_kk = raw_kk.replace('b', '6').replace('B', '8').replace('o', '0').replace('O', '0').replace('l', '1').replace('I', '1')
        clean_kk = re.sub(r'[^0-9]', '', clean_kk)
        if len(clean_kk) == 16:
            identitas['no_kk'] = clean_kk
        elif len(clean_kk) >= 16:
            identitas['no_kk'] = clean_kk[:16]

    # Fallback pencarian No KK jika belum ketemu: cari 16 digit sebelum baris NAMA/ALAMAT
    if not identitas['no_kk']:
        for line in raw_text.splitlines()[:10]:
            digits = re.sub(r'[^0-9]', '', line)
            if len(digits) == 16 and not digits.startswith('19') and not digits.startswith('20'):
                identitas['no_kk'] = digits
                break

    lines = raw_text.splitlines()
    for l in lines:
        lu = l.upper()

        # Alamat
        if ('ALAMAT' in lu or 'JL' in lu or 'JALAN' in lu) and not identitas['alamat']:
            m_al = re.search(r'(?:ALAMAT\s*[:;\-\s]*|[:;]\s*)(JL[.,\s].*|JALAN.*)', l, re.IGNORECASE)
            if m_al:
                al_text = m_al.group(1).strip()
                al_text = re.split(r'Kecamatan|Kecainean|Desa|Kelurahan|Kabupaten', al_text, flags=re.IGNORECASE)[0].strip()
                identitas['alamat'] = clean_text(al_text)

        # RT / RW
        m_rt = re.search(r'(\d{2,3}\s*/\s*\d{2,3})', l)
        if m_rt and (identitas['rt_rw'] == '-' or not identitas['rt_rw']):
            identitas['rt_rw'] = m_rt.group(1).replace(' ', '')

        # Kode Pos (5 digit)
        if not identitas['kode_pos']:
            m_pos = re.search(r'(?:KODE\s*POS[^0-9]*|[:;\s]|^)(\b\d{5}\b)', l, re.IGNORECASE)
            if m_pos:
                identitas['kode_pos'] = m_pos.group(1)

        # Desa / Kelurahan
        if ('DESA' in lu or 'KELURAHAN' in lu) and not identitas['desa_kelurahan']:
            m_des = re.search(r'(?:DESA\s*/?\s*KELURAHAN|KELURAHAN)[:;\s\-]*([A-Za-z\s]+)', l, re.IGNORECASE)
            if m_des:
                val = m_des.group(1).strip()
                val = re.split(r'Kecamatan|Kabupaten|Kode|Provinsi', val, flags=re.IGNORECASE)[0].strip()
                if len(val) > 2:
                    identitas['desa_kelurahan'] = clean_text(val)

        # Kecamatan
        if ('KECAMATAN' in lu or 'KECAINEAN' in lu) and not identitas['kecamatan']:
            m_kec = re.search(r'(?:KECAMATAN|KECAINEAN)[:;\s\-]*([A-Za-z\s]+)', l, re.IGNORECASE)
            if m_kec:
                val = m_kec.group(1).strip()
                val = re.split(r'Kabupaten|Kota|Kode|Provinsi', val, flags=re.IGNORECASE)[0].strip()
                if len(val) > 2:
                    identitas['kecamatan'] = clean_text(val)

        # Kabupaten / Kota
        if ('KABUPATEN' in lu or 'KOTA' in lu) and not identitas['kabupaten_kota']:
            m_kab = re.search(r'(?:KABUPATEN\s*/?\s*KOTA|KOTA)[:;\s\-]*([A-Za-z\s]+)', l, re.IGNORECASE)
            if m_kab:
                val = m_kab.group(1).strip()
                val = re.split(r'Kode|Provinsi', val, flags=re.IGNORECASE)[0].strip()
                if not val.upper().startswith('KOTA') and not val.upper().startswith('KAB'):
                    val = 'KOTA ' + val
                identitas['kabupaten_kota'] = clean_text(val)

        # Provinsi
        if ('PROVINSI' in lu or 'PROPINSI' in lu) and not identitas['provinsi']:
            m_prv = re.search(r'(?:PROVINSI|PROPINSI)[:;\s\-=]*([A-Za-z\s]+)', l, re.IGNORECASE)
            if m_prv:
                identitas['provinsi'] = clean_text(m_prv.group(1))

    return identitas


def extract_anggota_from_text(raw_text, no_kk=""):
    """
    Mengekstrak seluruh anggota keluarga dari tabel KK.
    Memadukan Tabel 1 (Data Diri, NIK, Kelahiran, Pendidikan, Pekerjaan)
    dan Tabel 2 (Status Perkawinan, Hubungan Keluarga, Kewarganegaraan, Nama Orang Tua).
    Setiap anggota memiliki tepat 17 kolom field sesuai PRD Bagian 7.2.
    """
    if not raw_text:
        return []

    # Pisahkan teks tabel 1 dan tabel 2
    split_match = re.search(r'(rape Status|Status\s*Perkawinan|Status\s*Hubungan)', raw_text, re.IGNORECASE)
    if split_match:
        part1 = raw_text[:split_match.start()]
        part2 = raw_text[split_match.start():]
    else:
        part1 = raw_text
        part2 = ''

    # 1. Parse Tabel 1
    rows_tabel1 = {}
    for line in part1.splitlines():
        line = line.strip()
        nik_match = re.search(r'(\d{15,17})', line)
        if not nik_match:
            continue

        raw_nik = nik_match.group(1)
        if raw_nik == no_kk and no_kk != '':
            continue

        nik = raw_nik[:16] if len(raw_nik) >= 16 else raw_nik + '0'

        before_nik = line[:nik_match.start()].strip()
        after_nik = line[nik_match.end():].strip()

        # Ekstrak No Urut dan Nama Lengkap
        no_match = re.match(r'^([1-9]|10)\s*[_\|\-Ji\:\.]*\s*(.*)$', before_nik)
        if no_match:
            no_urut = int(no_match.group(1))
            raw_nama = no_match.group(2).strip()
        else:
            no_urut = len(rows_tabel1) + 1
            raw_nama = before_nik

        nama_lengkap = normalize_name(raw_nama)

        # Jenis Kelamin
        jk = 'LAKI-LAKI' if 'LAKI' in after_nik.upper() else ('PEREMPUAN' if 'PEREMPUAN' in after_nik.upper() else '')

        # Tanggal Lahir (DD-MM-YYYY)
        tgl_m = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', after_nik)
        tgl_lahir = ''
        tempat_lahir = ''
        if tgl_m:
            dd, mm, yyyy = tgl_m.group(1), tgl_m.group(2), tgl_m.group(3)
            if mm == '00': mm = '01'
            tgl_lahir = f"{yyyy}-{mm}-{dd}"

            before_tgl = after_nik[:tgl_m.start()]
            cleaned_tl = re.sub(r'LAKI-LAKI|PEREMPUAN|[\|\-\:\_]', ' ', before_tgl, flags=re.IGNORECASE).strip()
            tl_words = cleaned_tl.split()
            if tl_words:
                tempat_lahir = ' '.join(tl_words).strip(' ,._')

        # Agama
        agama = ''
        for ag in ['ISLAM', 'KRISTEN', 'KATOLIK', 'KHATOLIK', 'HINDU', 'BUDHA', 'BUDDHA', 'KONGHUCU']:
            if ag in after_nik.upper():
                agama = 'KATOLIK' if 'KAT' in ag else ag
                break

        # Pendidikan
        pendidikan = ''
        for pend in [
            'BELUM TAMAT SD/SEDERAJAT', 'TIDAK / BELUM SEKOLAH', 'TIDAK/BELUM SEKOLAH', 'TIDAK/BLM SEKOLAH',
            'SLTA/SEDERAJAT', 'SLTP/SEDERAJAT', 'TAMAT SD/SEDERAJAT', 'STRATA I', 'STRATA II', 'DIPLOMA'
        ]:
            if pend in after_nik.upper():
                pendidikan = 'TIDAK/BELUM SEKOLAH' if 'TIDAK' in pend else pend
                break

        # Pekerjaan
        pekerjaan = ''
        for pek in [
            'PELAJAR/MAHASISWA', 'PELAJAR', 'PEDAGANG', 'KARYAWAN SWASTA',
            'PEGAWAI NEGERI SIPIL', 'PNS', 'BELUM/TIDAK BEKERJA', 'MENGURUS RUMAH TANGGA',
            'PETANI/PEKEBUN', 'WIRASWASTA', 'BURUH HARIAN LEPAS'
        ]:
            if pek in after_nik.upper():
                pekerjaan = 'PELAJAR/MAHASISWA' if 'PELAJAR' in pek else pek
                break

        rows_tabel1[no_urut] = {
            'no': no_urut,
            'nama_lengkap': nama_lengkap,
            'nik': nik,
            'jenis_kelamin': jk,
            'tempat_lahir': tempat_lahir,
            'tanggal_lahir': tgl_lahir,
            'agama': agama,
            'pendidikan': pendidikan,
            'jenis_pekerjaan': pekerjaan
        }

    # 2. Parse Tabel 2
    rows_tabel2 = {}
    for line in part2.splitlines():
        line = line.strip()
        m_no = re.match(r'^([1-9]|10)\s*[_\|\-Ji\:\.]*\s*(.*)$', line)
        if not m_no:
            continue
        no_urut = int(m_no.group(1))
        content = m_no.group(2).strip()

        # Lewati baris noise (hanya angka / simbol)
        letters = re.sub(r'[^A-Za-z]', '', content)
        if len(letters) < 4:
            continue

        # Jangan timpa jika nomor urut ini sudah memiliki data lengkap
        if no_urut in rows_tabel2 and (rows_tabel2[no_urut]['status_hubungan_dalam_keluarga'] or rows_tabel2[no_urut]['nama_ayah']):
            continue

        status_kawin = 'BELUM KAWIN' if 'BELUM' in content.upper() and 'KAWIN' in content.upper() else ('KAWIN' if 'KAWIN' in content.upper() else '')
        hub = ''
        for h in ['KEPALA KELUARGA', 'ISTRI', 'ISTERI', 'ANAK', 'CUCU', 'ORANG TUA', 'MERTUA', 'FAMILI LAIN']:
            if h in content.upper():
                hub = 'ISTRI' if h == 'ISTERI' else h
                break

        # Normalisasi noise OCR untuk WNI dan hapus kata kunci status
        clean_parents = re.sub(r'\b(WI|VM|VNI|WM)\b', 'WNI', content, flags=re.IGNORECASE)
        clean_parents = re.sub(r'BELUM\s*I?\s*KAWIN|KAWIN|TERCATAT|KEPALA\s*KELUARGA|ISTRI|ANAK|WNI|[\|\-\:\_\=]', ' ', clean_parents, flags=re.IGNORECASE)
        clean_parents = re.sub(r'\s+', ' ', clean_parents).strip()

        # Pemisahan Nama Ayah & Nama Ibu:
        # Jika ada 'NI ' di tengah/akhir (penanda nama wanita/ibu), gunakan sebagai batas pemisah
        m_split = re.search(r'^(.*?)\s+(NI\s+[A-Za-z\s]+)$', clean_parents, re.IGNORECASE)
        if m_split:
            ayah = m_split.group(1).strip()
            ibu = m_split.group(2).strip()
        else:
            words = clean_parents.split()
            if len(words) >= 2:
                mid = len(words) // 2
                ayah = ' '.join(words[:mid])
                ibu = ' '.join(words[mid:])
            elif len(words) == 1:
                ayah = words[0]
                ibu = ''
            else:
                ayah = ''
                ibu = ''

        # Normalisasi awal nama ayah jika terbaca '1 ' atau terpotong spasi
        ayah = re.sub(r'^[1|Iil]\s+', 'I ', ayah)
        ayah = re.sub(r'\bAS\s+TIKA\b', 'ASTIKA', ayah, flags=re.IGNORECASE)
        ayah = re.sub(r'^(?:le|1e|ie|\|\s*e)\s+', '', ayah, flags=re.IGNORECASE).strip()
        ibu = re.sub(r'^(?:le|1e|ie|\|\s*e)\s+', '', ibu, flags=re.IGNORECASE).strip()

        ayah = normalize_name(ayah)
        ibu = normalize_name(ibu)

        rows_tabel2[no_urut] = {
            'status_perkawinan': status_kawin,
            'status_hubungan_dalam_keluarga': hub,
            'kewarganegaraan': 'WNI',
            'nama_ayah': ayah,
            'nama_ibu': ibu
        }

    # 3. Gabungkan Tabel 1 & Tabel 2
    # Toleransi OCR: jika baris pertama Tabel 2 terbaca '4' (karena bentuk '1' dengan garis atas mirip '4')
    if 4 in rows_tabel2 and 1 not in rows_tabel2 and 'KEPALA KELUARGA' in rows_tabel2[4].get('status_hubungan_dalam_keluarga', ''):
        rows_tabel2[1] = rows_tabel2[4]

    hasil_anggota = []
    for no_urut in sorted(rows_tabel1.keys()):
        d1 = rows_tabel1[no_urut]
        d2 = rows_tabel2.get(no_urut, {})

        st_kawin = d2.get('status_perkawinan', '')
        hub = d2.get('status_hubungan_dalam_keluarga', '')

        if not hub:
            if no_urut == 1:
                hub = 'KEPALA KELUARGA'
            elif d1.get('jenis_kelamin') == 'PEREMPUAN':
                hub = 'ISTRI'
            else:
                hub = 'ANAK'

        if not st_kawin:
            st_kawin = 'KAWIN' if no_urut <= 2 else 'BELUM KAWIN'

        anggota = {
            'nama_lengkap': d1.get('nama_lengkap', ''),
            'nik': d1.get('nik', ''),
            'jenis_kelamin': d1.get('jenis_kelamin', ''),
            'tempat_lahir': d1.get('tempat_lahir', ''),
            'tanggal_lahir': d1.get('tanggal_lahir', ''),
            'agama': d1.get('agama', ''),
            'pendidikan': d1.get('pendidikan', ''),
            'jenis_pekerjaan': d1.get('jenis_pekerjaan', ''),
            'golongan_darah': '',
            'status_perkawinan': st_kawin,
            'tanggal_perkawinan': '',
            'status_hubungan_dalam_keluarga': hub,
            'kewarganegaraan': d2.get('kewarganegaraan', 'WNI'),
            'no_paspor': '',
            'no_kitap': '',
            'nama_ayah': d2.get('nama_ayah', ''),
            'nama_ibu': d2.get('nama_ibu', '')
        }
        hasil_anggota.append(anggota)

    return hasil_anggota


def process_kk_ocr(image_path, nama_kepala_keluarga=""):
    """
    Fungsi utama pipeline OCR Kartu Keluarga:
    1. Membaca citra secara langsung menggunakan PIL untuk kualitas teks maksimal.
    2. Mengekstrak 9 field identitas KK dan 17 kolom seluruh baris anggota keluarga.
    """
    tesseract_ready = is_tesseract_available()

    if not tesseract_ready:
        identitas_empty = {
            'no_kk': '',
            'nama_kepala_keluarga': nama_kepala_keluarga,
            'alamat': '',
            'rt_rw': '-',
            'desa_kelurahan': '',
            'kecamatan': '',
            'kabupaten_kota': '',
            'kode_pos': '',
            'provinsi': ''
        }
        anggota_initial = [{
            'nama_lengkap': nama_kepala_keluarga,
            'nik': '',
            'jenis_kelamin': '',
            'tempat_lahir': '',
            'tanggal_lahir': '',
            'agama': '',
            'pendidikan': '',
            'jenis_pekerjaan': '',
            'golongan_darah': '',
            'status_perkawinan': '',
            'tanggal_perkawinan': '',
            'status_hubungan_dalam_keluarga': 'KEPALA KELUARGA',
            'kewarganegaraan': 'WNI',
            'no_paspor': '',
            'no_kitap': '',
            'nama_ayah': '',
            'nama_ibu': ''
        }]
        return {
            'tesseract_available': False,
            'identitas_kk': identitas_empty,
            'anggota_keluarga': anggota_initial,
            'raw_text': '',
            'message': 'Engine Tesseract OCR belum terpasang di sistem.'
        }

    try:
        # Baca gambar menggunakan PIL (kualitas asli bebas noise biner)
        pil_img = Image.open(image_path)
        
        # Jika gambar beresolusi kecil (misal foto kamera hp terkompresi < 1200px lebar),
        # upscale secara proporsional dengan filter Lanczos agar Tesseract membaca teks dengan tajam.
        if pil_img.size[0] < 1200:
            scale_factor = 1400 / max(pil_img.size[0], 1)
            new_w = 1400
            new_h = int(pil_img.size[1] * scale_factor)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        try:
            raw_text = pytesseract.image_to_string(pil_img, lang='ind+eng')
        except Exception:
            raw_text = pytesseract.image_to_string(pil_img, lang='eng')

        # Ekstraksi 9 field identitas KK
        identitas = extract_identitas_kk_from_text(raw_text, default_nama_kepala=nama_kepala_keluarga)

        # Multi-Region Header OCR: crop kolom kanan dan kiri header KK untuk akurasi maksimal
        w, h = pil_img.size
        try:
            header_r_crop = pil_img.crop((int(w * 0.45), int(h * 0.08), w, int(h * 0.35)))
            try:
                header_r_text = pytesseract.image_to_string(header_r_crop, lang='ind+eng')
            except Exception:
                header_r_text = pytesseract.image_to_string(header_r_crop, lang='eng')

            for l in header_r_text.splitlines():
                lu = l.upper()
                if ('DESA' in lu or 'KELURAHAN' in lu):
                    m = re.search(r'(?:DESA\s*/?\s*KELURAHAN|KELURAHAN)[:;\s\-_]+([A-Za-z\s]+)', l, re.IGNORECASE)
                    if m:
                        val = re.split(r'Kecamatan|Kabupaten|Kota|Kode|Provinsi', m.group(1), flags=re.IGNORECASE)[0].strip()
                        if len(val) > 2:
                            identitas['desa_kelurahan'] = clean_text(val)
                if ('KECAMATAN' in lu or 'KECAINEAN' in lu):
                    m = re.search(r'(?:KECAMATAN|KECAINEAN)[:;\s\-_]+([A-Za-z\s]+)', l, re.IGNORECASE)
                    if m:
                        val = re.split(r'Kabupaten|Kota|Kode|Provinsi', m.group(1), flags=re.IGNORECASE)[0].strip()
                        if len(val) > 2:
                            identitas['kecamatan'] = clean_text(val)
                if ('KABUPATEN' in lu or 'KOTA' in lu):
                    m = re.search(r'(?:KABUPATEN\s*/?\s*KOTA|KOTA)[:;\s\-_]+([A-Za-z\s]+)', l, re.IGNORECASE)
                    if m:
                        val = re.split(r'Kode|Provinsi', m.group(1), flags=re.IGNORECASE)[0].strip()
                        if not val.upper().startswith('KOTA') and not val.upper().startswith('KAB'):
                            val = 'KOTA ' + val
                        if len(val) > 3:
                            identitas['kabupaten_kota'] = clean_text(val)
                if ('PROVINSI' in lu or 'PROPINSI' in lu):
                    m = re.search(r'(?:PROVINSI|PROPINSI)[:;\s\-=_]+([A-Za-z\s]+)', l, re.IGNORECASE)
                    if m:
                        val = clean_text(m.group(1))
                        if len(val) > 2:
                            identitas['provinsi'] = val
        except Exception as e_header_r:
            print(f"[OCR HEADER_R ERROR] {e_header_r}")

        try:
            header_l_crop = pil_img.crop((0, int(h * 0.08), int(w * 0.55), int(h * 0.35)))
            try:
                header_l_text = pytesseract.image_to_string(header_l_crop, lang='ind+eng')
            except Exception:
                header_l_text = pytesseract.image_to_string(header_l_crop, lang='eng')

            for l in header_l_text.splitlines():
                lu = l.upper()
                if ('ALAMAT' in lu or 'JL' in lu or 'JALAN' in lu):
                    m_al = re.search(r'(?:ALAMAT\s*[:;\-\s]*|[:;]\s*)(JL[.,\s].*|JALAN.*)', l, re.IGNORECASE)
                    if m_al:
                        al = re.split(r'Kecamatan|Desa|Kelurahan|Kabupaten', m_al.group(1), flags=re.IGNORECASE)[0].strip()
                        if len(al) > 5:
                            identitas['alamat'] = clean_text(al)
                m_rt = re.search(r'(\d{2,3}\s*/\s*\d{2,3})', l)
                if m_rt and (identitas.get('rt_rw') == '-' or not identitas.get('rt_rw')):
                    identitas['rt_rw'] = m_rt.group(1).replace(' ', '')
                if not identitas.get('kode_pos'):
                    m_pos = re.search(r'(?:KODE\s*POS[^0-9]*|[:;\s]|^)(\b\d{5}\b)', l, re.IGNORECASE)
                    if m_pos:
                        identitas['kode_pos'] = m_pos.group(1)
        except Exception as e_header_l:
            print(f"[OCR HEADER_L ERROR] {e_header_l}")

        # Ekstraksi 17 kolom seluruh baris anggota keluarga
        anggota_list = extract_anggota_from_text(raw_text, no_kk=identitas['no_kk'])

        # Jika nama kepala keluarga masih kosong dan ada anggota terdeteksi,
        # gunakan nama anggota pertama sebagai kepala keluarga
        if not identitas.get('nama_kepala_keluarga') and anggota_list:
            identitas['nama_kepala_keluarga'] = anggota_list[0]['nama_lengkap']

        if not anggota_list:
            anggota_list = [{
                'nama_lengkap': identitas.get('nama_kepala_keluarga') or nama_kepala_keluarga,
                'nik': '',
                'jenis_kelamin': '',
                'tempat_lahir': '',
                'tanggal_lahir': '',
                'agama': '',
                'pendidikan': '',
                'jenis_pekerjaan': '',
                'golongan_darah': '',
                'status_perkawinan': '',
                'tanggal_perkawinan': '',
                'status_hubungan_dalam_keluarga': 'KEPALA KELUARGA',
                'kewarganegaraan': 'WNI',
                'no_paspor': '',
                'no_kitap': '',
                'nama_ayah': '',
                'nama_ibu': ''
            }]

        return {
            'tesseract_available': True,
            'identitas_kk': identitas,
            'anggota_keluarga': anggota_list,
            'raw_text': raw_text,
            'message': f'Ekstraksi OCR berhasil: {len(anggota_list)} anggota keluarga otomatis terdeteksi.'
        }

    except Exception as e:
        print(f"[OCR ERROR] {e}")
        return {
            'tesseract_available': True,
            'identitas_kk': {
                'no_kk': '',
                'nama_kepala_keluarga': nama_kepala_keluarga,
                'alamat': '',
                'rt_rw': '-',
                'desa_kelurahan': '',
                'kecamatan': '',
                'kabupaten_kota': '',
                'kode_pos': '',
                'provinsi': ''
            },
            'anggota_keluarga': [{
                'nama_lengkap': nama_kepala_keluarga,
                'nik': '',
                'jenis_kelamin': '',
                'tempat_lahir': '',
                'tanggal_lahir': '',
                'agama': '',
                'pendidikan': '',
                'jenis_pekerjaan': '',
                'golongan_darah': '',
                'status_perkawinan': '',
                'tanggal_perkawinan': '',
                'status_hubungan_dalam_keluarga': 'KEPALA KELUARGA',
                'kewarganegaraan': 'WNI',
                'no_paspor': '',
                'no_kitap': '',
                'nama_ayah': '',
                'nama_ibu': ''
            }],
            'raw_text': '',
            'message': f'Terjadi kendala saat membaca teks: {str(e)}.'
        }
