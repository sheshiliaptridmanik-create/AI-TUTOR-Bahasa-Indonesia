
# =========================================================
# MEDIA / EVALUASI SISWA
# =========================================================

def halaman_media():
    hero("Media / Evaluasi", "Video dan gambar yang dikenali akan tampil langsung di halaman.", "🎬")
    data = baca_perangkat_data()
    found = False

    for topik in data.get("materi", []):
        media = [x for x in topik.get("media", []) if normalize_media(x).get("url")]
        if not media:
            continue
        found = True
        st.markdown(f'<div class="section-title">📖 {html.escape(topik.get("judul", "Materi"))}</div>', unsafe_allow_html=True)
        for i, item in enumerate(media, start=1):
            render_media(item, i)

    config = baca_json(FILE_CONFIG, {})
    # Hanya entri "media" yang merupakan media; identitas sekolah bukan URL.
    if isinstance(config, dict):
        for i, item in enumerate(config.get("media", []), start=1):
            if isinstance(item, (str, dict)) and normalize_media(item).get("url"):
                found = True
                render_media(item, i)

    if not found:
        empty_state("Belum ada media/evaluasi yang ditambahkan guru.")
    footer()


# =========================================================
# PETUNJUK
# =========================================================

def halaman_petunjuk(mode):
    if mode == "guru":
        hero("Petunjuk Penggunaan Guru", "Kelola materi dan latihan secara bertahap.", "❔")
        c1, c2 = st.columns(2)
        with c1:
            card("1 • Buat materi", "Buka Perangkat Pembelajaran → Buat Materi Baru.", "➕", "LANGKAH")
            card("2 • Isi perangkat", "Buka satu materi, lalu pilih Identitas, CP & TP, Modul, Materi, Latihan, Media, atau Penilaian.", "📄", "LANGKAH")
            card("3 • Kelola latihan", "Tambah, edit, simpan, atau hapus soal khusus untuk materi yang dipilih.", "✏️", "LANGKAH")
        with c2:
            card("4 • Tambah media", "Pilih auto/video/gambar/link. YouTube atau video langsung akan ditampilkan sebagai pemutar.", "🎬", "LANGKAH")
            card("5 • Siswa", "Siswa melihat katalog materi dahulu, kemudian memilih satu materi dan satu bagian.", "👩‍🎓", "LANGKAH")
            card("6 • Hasil", "Pantau hasil pengerjaan melalui menu Hasil Siswa.", "📊", "LANGKAH")
    else:
        hero("Petunjuk Penggunaan Siswa", "Belajar dengan alur yang terpisah dan terarah.", "❔")
        c1, c2 = st.columns(2)
        with c1:
            card("1 • Masuk", "Masukkan nama untuk menyimpan hasil latihan.", "👤", "MULAI")
            card("2 • Pilih materi", "Menu Materi menampilkan daftar materi terlebih dahulu.", "📚", "BELAJAR")
            card("3 • Pilih bagian", "Setelah materi dibuka, pilih bagian yang dibutuhkan.", "🧭", "BELAJAR")
        with c2:
            card("4 • Tanya AI", "Gunakan konteks materi agar jawaban tidak bercampur dengan materi lain.", "🤖", "BERTANYA")
            card("5 • Media", "Video/gambar yang didukung akan tampil langsung.", "🎬", "MEDIA")
            card("6 • Latihan", "Pilih materi latihan, kerjakan soal, lalu kirim jawaban.", "✏️", "BERLATIH")
    footer()


# =========================================================
# LOGIN SISWA
# =========================================================

def login_siswa():
    hero("Masuk sebagai Siswa", "Masukkan nama untuk memulai sesi belajar.", "👩‍🎓")
    nama = st.text_input("Nama siswa", placeholder="Masukkan nama lengkap", key="login_name")
    if st.button("🚀 Mulai Belajar", use_container_width=True, key="login_btn"):
        if not nama.strip():
            st.warning("Silakan masukkan nama terlebih dahulu.")
        else:
            st.session_state.nama_siswa = nama.strip()
            st.session_state.mode = "siswa"
            st.session_state.student_material_view = "catalog"
            st.rerun()


# =========================================================
# ROUTER APLIKASI
# =========================================================

if st.session_state.mode is None:
    halaman_pilih_mode()

elif st.session_state.mode == "guru":
    menu = sidebar_guru()
    if menu == "🏠 Dashboard":
        dashboard_guru()
    elif menu == "📄 Perangkat Pembelajaran":
        tampilkan_perangkat_guru()
    elif menu == "✏️ Latihan":
        halaman_latihan_guru()
    elif menu == "🔄 Remedial":
        tampilkan_file_txt(FOLDER_REMEDIAL, "Remedial", "🔄")
    elif menu == "⭐ Pengayaan":
        tampilkan_file_txt(FOLDER_PENGAYAAN, "Pengayaan", "⭐")
    elif menu == "📊 Hasil Siswa":
        halaman_hasil_guru()
    elif menu == "❔ Petunjuk Penggunaan":
        halaman_petunjuk("guru")

elif st.session_state.mode == "siswa":
    if not st.session_state.nama_siswa:
        login_siswa()
    else:
        menu = sidebar_siswa()
        if menu == "🏠 Beranda":
            halaman_beranda_siswa()
        elif menu == "📚 Materi":
            halaman_materi_siswa()
        elif menu == "🤖 Tanya AI":
            halaman_tanya_ai()
        elif menu == "✏️ Latihan":
            halaman_latihan_siswa()
        elif menu == "🎬 Media/Evaluasi":
            halaman_media()
        elif menu == "❔ Petunjuk Penggunaan":
            halaman_petunjuk("siswa")
