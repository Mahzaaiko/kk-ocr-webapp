/**
 * JavaScript Utama - Pendataan Penduduk Berbasis OCR KK
 * Validasi client-side, drag-and-drop, preview gambar KK, dan animasi loading
 */

document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('gambar_kk');
    const dropzone = document.getElementById('uploadDropzone');
    const previewCard = document.getElementById('previewCard');
    const previewThumb = document.getElementById('previewThumb');
    const previewName = document.getElementById('previewName');
    const previewSize = document.getElementById('previewSize');
    const btnRemove = document.getElementById('btnRemovePreview');
    const uploadForm = document.getElementById('uploadForm');
    const btnSubmit = document.getElementById('btnSubmit');
    const loadingOverlay = document.getElementById('loadingOverlay');

    if (!fileInput) return;

    const allowedExtensions = ['jpg', 'jpeg', 'png'];

    function handleFile(file) {
        if (!file) return;

        const filename = file.name;
        const ext = filename.split('.').pop().toLowerCase();

        // 1. Validasi Tolak PDF secara eksplisit
        if (ext === 'pdf') {
            alert('Format file PDF tidak didukung. Harap unggah foto Kartu Keluarga dengan format JPG, JPEG, atau PNG.');
            clearFileInput();
            return;
        }

        // 2. Validasi ekstensi yang diizinkan
        if (!allowedExtensions.includes(ext)) {
            alert(`Format file '${ext}' tidak didukung. Hanya berkas gambar JPG, JPEG, atau PNG yang diperbolehkan.`);
            clearFileInput();
            return;
        }

        // 3. Validasi batas ukuran 16MB
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            alert('Ukuran berkas melebihi 16MB. Harap perkecil resolusi/ukuran gambar Anda.');
            clearFileInput();
            return;
        }

        // Tampilkan thumbnail preview
        const reader = new FileReader();
        reader.onload = function (e) {
            previewThumb.src = e.target.result;
            previewName.textContent = file.name;
            previewSize.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB (' + (file.size / 1024).toFixed(0) + ' KB)';
            previewCard.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }

    function clearFileInput() {
        fileInput.value = '';
        previewCard.style.display = 'none';
        previewThumb.src = '';
        previewName.textContent = '';
        previewSize.textContent = '';
    }

    // Event listener input change
    fileInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            handleFile(this.files[0]);
        }
    });

    // Tombol hapus preview
    if (btnRemove) {
        btnRemove.addEventListener('click', function (e) {
            e.preventDefault();
            clearFileInput();
        });
    }

    // Dukungan Drag and Drop
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', function (e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                handleFile(files[0]);
            }
        });
    }

            // Tampilkan Loading Overlay saat submit form
            if (uploadForm) {
                uploadForm.addEventListener('submit', function (e) {
                    const namaInput = document.getElementById('nama_kepala_keluarga');
                    if (namaInput && !namaInput.value.trim()) {
                        alert('Nama Kepala Keluarga wajib diisi.');
                        e.preventDefault();
                        return;
                    }

                    if (!fileInput.files || fileInput.files.length === 0) {
                        alert('Silakan pilih berkas foto Kartu Keluarga terlebih dahulu.');
                        e.preventDefault();
                        return;
                    }

                    if (btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.innerHTML = 'Memproses Data...';
                    }

                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'flex';
                    }
                });
            }
        });
