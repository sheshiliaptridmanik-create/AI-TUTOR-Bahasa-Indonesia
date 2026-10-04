import streamlit as st
import os
import re
import json
from collections import Counter
from datetime import datetime


# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# KONFIGURASI FOLDER
# =========================================================

FOLDER_DATABASE = "database"

FOLDER_MATERI = os.path.join(FOLDER_DATABASE, "materi")
FOLDER_PERANGKAT = os.path.join(FOLDER_DATABASE, "perangkat")
FOLDER_LATIHAN = os.path.join(FOLDER_DATABASE, "latihan")
FOLDER_REMEDIAL = os.path.join(FOLDER_DATABASE, "remedial")
FOLDER_PENGAYAAN = os.path.join(FOLDER_DATABASE, "pengayaan")
FOLDER_HASIL = os.path.join(FOLDER_DATABASE, "hasil_siswa")

FILE_HASIL = os.path.join(
    FOLDER_HASIL,
    "hasil_siswa.json"
)

FILE_CONFIG = os.path.join(
    "config",
    "pembelajaran.json"
)

# =========================================================
# SESSION STATE
# =========================================================

if "mode" not in st.session_state:
    st.session_state.mode = None

if "nama_siswa" not in st.session_state:
    st.session_state.nama_siswa = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================================================
# FUNGSI MEMBACA FILE TXT
# =========================================================

def baca_file_txt(folder):

    data = []

    if not os.path.exists(folder):
        return data

    for nama_file in sorted(os.listdir(folder)):

        if nama_file.lower().endswith(".txt"):

            path = os.path.join(folder, nama_file)

            try:
                with open(
                    path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    isi = file.read().strip()

                if isi:
                    data.append({
                        "nama_file": nama_file,
                        "isi": isi
                    })

            except Exception:
                pass

    return data


# =========================================================
# MEMBACA MATERI
# =========================================================

def baca_materi():
    return baca_file_txt(FOLDER_MATERI)


# =========================================================
# MEMBACA LATIHAN / REMEDIAL / PENGAYAAN
# =========================================================

def baca_latihan():
    return baca_file_txt(FOLDER_LATIHAN)


def baca_remedial():
    return baca_file_txt(FOLDER_REMEDIAL)


def baca_pengayaan():
    return baca_file_txt(FOLDER_PENGAYAAN)


# =========================================================
# MEMBACA CONFIG
# =========================================================

def baca_config():

    if not os.path.exists(FILE_CONFIG):
        return {}

    try:

        with open(
            FILE_CONFIG,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:
        return {}


# =========================================================
# HASIL SISWA
# =========================================================

def baca_hasil():

    if not os.path.exists(FILE_HASIL):
        return []

    try:

        with open(
            FILE_HASIL,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def simpan_hasil(data):

    os.makedirs(FOLDER_HASIL, exist_ok=True)

    with open(
        FILE_HASIL,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# MENCARI MATERI YANG RELEVAN
# =========================================================

def bersihkan_teks(teks):

    teks = teks.lower()

    teks = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        teks
    )

    return teks


def cari_materi(pertanyaan, database):

    kata_tanya = bersihkan_teks(
        pertanyaan
    ).split()

    stopwords = {
        "apa",
        "itu",
        "yang",
        "dan",
        "atau",
        "adalah",
        "dari",
        "pada",
        "dalam",
        "untuk",
        "dengan",
        "ke",
        "di",
        "jelaskan",
        "jelaskanlah",
        "sebutkan",
        "bagaimana",
        "mengapa",
        "apakah",
        "saya",
        "mau",
        "ingin",
        "tahu"
    }

    kata_penting = [
        kata
        for kata in kata_tanya
        if kata not in stopwords
        and len(kata) > 2
    ]

    hasil = []

    for data in database:

        isi_bersih = bersihkan_teks(
            data["isi"]
        )

        kata_isi = isi_bersih.split()

        counter = Counter(kata_isi)

        skor = 0

        for kata in kata_penting:

            if kata in counter:
                skor += counter[kata]

        if skor > 0:

            hasil.append({
                "isi": data["isi"],
                "skor": skor
            })

    hasil.sort(
        key=lambda x: x["skor"],
        reverse=True
    )

    return hasil


# =========================================================
# MEMBUAT JAWABAN AI
# =========================================================

def ambil_potongan_relevan(isi, pertanyaan):

    paragraf = re.split(
        r"\n\s*\n|\r\n\s*\r\n",
        isi
    )

    pertanyaan_bersih = bersihkan_teks(
        pertanyaan
    )

    kata_pertanyaan = set(
        pertanyaan_bersih.split()
    )

    kandidat = []

    for p in paragraf:

        if not p.strip():
            continue

        p_bersih = bersihkan_teks(p)

        kata_p = set(
            p_bersih.split()
        )

        skor = len(
            kata_pertanyaan.intersection(kata_p)
        )

        kandidat.append(
            (skor, p.strip())
        )

    kandidat.sort(
        key=lambda x: x[0],
        reverse=True
    )

    hasil = [
        teks
        for skor, teks in kandidat[:3]
        if teks
    ]

    if hasil:
        return "\n\n".join(hasil)

    return isi[:2000]


def jawab_ai(pertanyaan):

    database = baca_materi()

    if not database:

        return (
            "Maaf, materi pembelajaran belum tersedia "
            "di dalam database. Silakan minta guru "
            "menambahkan materi terlebih dahulu."
        )

    hasil = cari_materi(
        pertanyaan,
        database
    )

    if not hasil:

        return (
            "Maaf, saya belum menemukan informasi "
            "yang sesuai dengan pertanyaan tersebut "
            "di materi pembelajaran yang tersedia."
        )

    isi = hasil[0]["isi"]

    jawaban = ambil_potongan_relevan(
        isi,
        pertanyaan
    )

    return jawaban


# =========================================================
# MEMBUAT SOAL DARI FILE TXT
# =========================================================
#
# FORMAT YANG DISARANKAN:
#
# SOAL 1: Apa yang dimaksud teks laporan hasil observasi?
# A. ...
# B. ...
# C. ...
# D. ...
# JAWABAN: A
# PEMBAHASAN: ...
#
# SOAL 2: ...
#
# =========================================================

def parse_soal(isi):

    soal_list = []

    blok_soal = re.split(
        r"(?=SOAL\s*\d+\s*:)",
        isi,
        flags=re.IGNORECASE
    )

    for blok in blok_soal:

        blok = blok.strip()

        if not blok:
            continue

        match_soal = re.search(
            r"SOAL\s*\d+\s*:\s*(.*?)(?=\nA\.)",
            blok,
            flags=re.IGNORECASE | re.DOTALL
        )

        if not match_soal:
            continue

        pertanyaan = match_soal.group(1).strip()

        pilihan = {}

        for huruf in ["A", "B", "C", "D"]:

            pattern = (
                rf"{huruf}\.\s*(.*?)(?=\n[A-D]\.|\nJAWABAN:|\Z)"
            )

            match = re.search(
                pattern,
                blok,
                flags=re.IGNORECASE | re.DOTALL
            )

            if match:
                pilihan[huruf] = (
                    match.group(1)
                    .strip()
                )

        match_jawaban = re.search(
            r"JAWABAN\s*:\s*([A-D])",
            blok,
            flags=re.IGNORECASE
        )

        if not match_jawaban:
            continue

        jawaban = (
            match_jawaban.group(1)
            .upper()
        )

        match_pembahasan = re.search(
            r"PEMBAHASAN\s*:\s*(.*)",
            blok,
            flags=re.IGNORECASE | re.DOTALL
        )

        pembahasan = ""

        if match_pembahasan:
            pembahasan = (
                match_pembahasan.group(1)
                .strip()
            )

        soal_list.append({
            "pertanyaan": pertanyaan,
            "pilihan": pilihan,
            "jawaban": jawaban,
            "pembahasan": pembahasan
        })

    return soal_list


# =========================================================
# MENGAMBIL SEMUA SOAL
# =========================================================

def ambil_semua_soal(folder):

    semua_soal = []

    data = baca_file_txt(folder)

    for item in data:

        soal = parse_soal(
            item["isi"]
        )

        for s in soal:

            s["sumber_internal"] = item["nama_file"]

            semua_soal.append(s)

    return semua_soal


# =========================================================
# MENU LOGIN / PILIH MODE
# =========================================================

def halaman_pilih_mode():

    st.title("📚 AI Tutor Bahasa Indonesia")

    st.markdown(
        "### Selamat datang di AI Tutor Bahasa Indonesia"
    )

    st.write(
        "Silakan pilih mode penggunaan aplikasi."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🧑‍🏫 Guru")

        st.write(
            "Mengelola pembelajaran dan melihat "
            "hasil pekerjaan siswa."
        )

        if st.button(
            "Masuk sebagai Guru",
            use_container_width=True
        ):

            st.session_state.mode = "guru"
            st.rerun()

    with col2:

        st.subheader("👩‍🎓 Siswa")

        st.write(
            "Belajar, bertanya kepada AI, dan "
            "mengerjakan latihan."
        )

        if st.button(
            "Masuk sebagai Siswa",
            use_container_width=True
        ):

            st.session_state.mode = "siswa"
            st.rerun()


# =========================================================
# SIDEBAR GURU
# =========================================================

def sidebar_guru():

    st.sidebar.title("🧑‍🏫 MODE GURU")

    menu = st.sidebar.radio(
        "Menu",
        [
            "🏠 Dashboard",
            "📚 Materi",
            "📄 Perangkat Pembelajaran",
            "✏️ Latihan",
            "🔄 Remedial",
            "⭐ Pengayaan",
            "📊 Hasil Siswa",
            "🔗 Media/Evaluasi"
        ]
    )

    if st.sidebar.button(
        "🚪 Keluar",
        use_container_width=True
    ):

        st.session_state.mode = None
        st.rerun()

    return menu


# =========================================================
# SIDEBAR SISWA
# =========================================================

def sidebar_siswa():

    st.sidebar.title("👩‍🎓 MODE SISWA")

    if st.session_state.nama_siswa:

        st.sidebar.write(
            f"👤 {st.session_state.nama_siswa}"
        )

    menu = st.sidebar.radio(
        "Menu",
        [
            "🏠 Beranda",
            "🤖 Tanya AI",
            "✏️ Latihan",
            "🔗 Media/Evaluasi"
        ]
    )

    if st.sidebar.button(
        "🚪 Keluar",
        use_container_width=True
    ):

        st.session_state.mode = None
        st.session_state.nama_siswa = ""
        st.session_state.chat_history = []

        st.rerun()

    return menu


# =========================================================
# DASHBOARD GURU
# =========================================================

def dashboard_guru():

    st.title("🏠 Dashboard Guru")

    materi = baca_materi()
    latihan = baca_latihan()
    remedial = baca_remedial()
    pengayaan = baca_pengayaan()
    hasil = baca_hasil()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📚 Materi",
            len(materi)
        )

    with col2:
        st.metric(
            "✏️ File Latihan",
            len(latihan)
        )

    with col3:
        st.metric(
            "🔄 Remedial",
            len(remedial)
        )

    with col4:
        st.metric(
            "👩‍🎓 Hasil Siswa",
            len(hasil)
        )

    st.divider()

    st.info(
        "Gunakan menu di sebelah kiri untuk "
        "mengelola materi, latihan, remedial, "
        "pengayaan, dan melihat hasil pekerjaan siswa."
    )


# =========================================================
# TAMPILKAN FILE MATERI GURU
# =========================================================

def tampilkan_file_txt(folder, judul):

    st.title(judul)

    data = baca_file_txt(folder)

    if not data:

        st.warning(
            "Belum ada file tersedia."
        )

        return

    for item in data:

        with st.expander(
            item["nama_file"]
        ):

            st.text(
                item["isi"]
            )


# =========================================================
# PERANGKAT PEMBELAJARAN
# =========================================================

def tampilkan_perangkat():

    st.title(
        "📄 Perangkat Pembelajaran"
    )

    if not os.path.exists(FOLDER_PERANGKAT):

        st.warning(
            "Folder perangkat belum tersedia."
        )

        return

    daftar_file = sorted(
        os.listdir(FOLDER_PERANGKAT)
    )

    if not daftar_file:

        st.info(
            "Belum ada perangkat pembelajaran."
        )

        return

    for nama_file in daftar_file:

        path = os.path.join(
            FOLDER_PERANGKAT,
            nama_file
        )

        if os.path.isfile(path):

            st.write(
                f"📄 **{nama_file}**"
            )

            try:

                with open(
                    path,
                    "rb"
                ) as file:

                    data = file.read()

                st.download_button(
                    "⬇️ Buka/Unduh",
                    data=data,
                    file_name=nama_file,
                    key=f"download_{nama_file}",
                    use_container_width=True
                )

            except Exception:

                st.error(
                    "File tidak dapat dibaca."
                )


# =========================================================
# HALAMAN LATIHAN GURU
# =========================================================

def halaman_latihan_guru():

    tampilkan_file_txt(
        FOLDER_LATIHAN,
        "✏️ Latihan"
    )

    st.info(
        "Format soal yang digunakan harus mengikuti "
        "format SOAL, pilihan A-D, JAWABAN, dan PEMBAHASAN."
    )


# =========================================================
# HASIL SISWA GURU
# =========================================================

def halaman_hasil_guru():

    st.title(
        "📊 Hasil Pekerjaan Siswa"
    )

    hasil = baca_hasil()

    if not hasil:

        st.info(
            "Belum ada siswa yang mengerjakan latihan."
        )

        return

    st.write(
        f"Jumlah pengerjaan: **{len(hasil)}**"
    )

    st.divider()

    for nomor, data in enumerate(
        reversed(hasil),
        start=1
    ):

        nama = data.get(
            "nama_siswa",
            "Tanpa Nama"
        )

        nilai = data.get(
            "nilai",
            0
        )

        waktu = data.get(
            "waktu",
            "-"
        )

        with st.expander(
            f"👤 {nama} — Nilai {nilai}"
        ):

            st.write(
                f"**Waktu:** {waktu}"
            )

            st.write(
                f"**Benar:** {data.get('benar', 0)}"
            )

            st.write(
                f"**Salah:** {data.get('salah', 0)}"
            )

            st.divider()

            jawaban_siswa = data.get(
                "jawaban",
                []
            )

            for i, item in enumerate(
                jawaban_siswa,
                start=1
            ):

                st.write(
                    f"**Soal {i}:** "
                    f"{item.get('pertanyaan', '')}"
                )

                st.write(
                    f"Jawaban siswa: "
                    f"**{item.get('jawaban_siswa', '-') }**"
                )

                st.write(
                    f"Jawaban benar: "
                    f"**{item.get('jawaban_benar', '-') }**"
                )

                if item.get("status") == "Benar":

                    st.success("✓ Benar")

                else:

                    st.error("✗ Salah")

                    if item.get("pembahasan"):

                        st.caption(
                            "Pembahasan: "
                            + item["pembahasan"]
                        )

                st.divider()


# =========================================================
# MEDIA / EVALUASI
# =========================================================

def halaman_media():

    st.title(
        "🔗 Media / Evaluasi"
    )

    config = baca_config()

    if not config:

        st.info(
            "Belum ada konfigurasi media/evaluasi."
        )

        return

    if isinstance(config, dict):

        for nama, link in config.items():

            if isinstance(link, str):

                st.markdown(
                    f"### 🔗 {nama}"
                )

                st.link_button(
                    "Buka Media",
                    link,
                    use_container_width=True
                )

            elif isinstance(link, list):

                for index, url in enumerate(
                    link,
                    start=1
                ):

                    st.link_button(
                        f"Buka Media {index}",
                        url,
                        use_container_width=True
                    )


# =========================================================
# BERANDA SISWA
# =========================================================

def halaman_beranda_siswa():

    st.title(
        "🏠 AI Tutor Bahasa Indonesia"
    )

    st.subheader(
        f"Halo, {st.session_state.nama_siswa}! 👋"
    )

    st.write(
        "Selamat belajar Bahasa Indonesia."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.info(
            "🤖 **Tanya AI**\n\n"
            "Ajukan pertanyaan mengenai "
            "materi pembelajaran."
        )

    with col2:

        st.info(
            "✏️ **Latihan**\n\n"
            "Kerjakan latihan dan lihat "
            "hasil serta jawaban yang benar."
        )

    with col3:

        st.info(
            "🔗 **Media/Evaluasi**\n\n"
            "Akses media dan evaluasi "
            "yang disediakan guru."
        )


# =========================================================
# TANYA AI SISWA
# =========================================================

def halaman_tanya_ai():

    st.title(
        "🤖 Tanya AI"
    )

    st.write(
        "Tanyakan sesuatu mengenai pembelajaran "
        "Bahasa Indonesia."
    )

    # Tampilkan percakapan
    for chat in st.session_state.chat_history:

        with st.chat_message(
            chat["role"]
        ):

            st.write(
                chat["content"]
            )

    pertanyaan = st.chat_input(
        "Tulis pertanyaanmu di sini..."
    )

    if pertanyaan:

        st.session_state.chat_history.append({
            "role": "user",
            "content": pertanyaan
        })

        jawaban = jawab_ai(
            pertanyaan
        )

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": jawaban
        })

        st.rerun()


# =========================================================
# LATIHAN SISWA
# =========================================================

def halaman_latihan_siswa():

    st.title(
        "✏️ Latihan"
    )

    st.write(
        f"Nama siswa: **{st.session_state.nama_siswa}**"
    )

    semua_soal = ambil_semua_soal(
        FOLDER_LATIHAN
    )

    if not semua_soal:

        st.warning(
            "Belum ada soal latihan."
        )

        st.info(
            "Guru perlu memasukkan soal ke "
            "database/latihan/latihan_lho.txt"
        )

        return

    st.write(
        f"Jumlah soal: **{len(semua_soal)}**"
    )

    st.divider()

    jawaban_siswa = {}

    for i, soal in enumerate(
        semua_soal
    ):

        st.write(
            f"### Soal {i + 1}"
        )

        st.write(
            soal["pertanyaan"]
        )

        pilihan = soal["pilihan"]

        if pilihan:

            opsi = []

            for huruf in ["A", "B", "C", "D"]:

                if huruf in pilihan:

                    opsi.append(
                        f"{huruf}. {pilihan[huruf]}"
                    )

            jawaban_siswa[i] = st.radio(
                "Pilih jawaban:",
                opsi,
                key=f"soal_{i}"
            )

        st.divider()

    if st.button(
        "📤 Kirim Jawaban",
        use_container_width=True
    ):

        benar = 0
        salah = 0

        detail_jawaban = []

        for i, soal in enumerate(
            semua_soal
        ):

            jawaban = jawaban_siswa.get(
                i,
                ""
            )

            huruf_siswa = ""

            if jawaban:

                match = re.match(
                    r"([A-D])\.",
                    jawaban
                )

                if match:
                    huruf_siswa = (
                        match.group(1)
                    )

            huruf_benar = soal[
                "jawaban"
            ]

            if huruf_siswa == huruf_benar:

                status = "Benar"
                benar += 1

            else:

                status = "Salah"
                salah += 1

            detail_jawaban.append({

                "pertanyaan":
                    soal["pertanyaan"],

                "jawaban_siswa":
                    huruf_siswa if huruf_siswa
                    else "Tidak dijawab",

                "jawaban_benar":
                    huruf_benar,

                "status":
                    status,

                "pembahasan":
                    soal.get(
                        "pembahasan",
                        ""
                    )
            })

        total = len(
            semua_soal
        )

        nilai = round(
            (benar / total) * 100,
            2
        ) if total > 0 else 0

        data_hasil = baca_hasil()

        hasil_baru = {

            "nama_siswa":
                st.session_state.nama_siswa,

            "nilai":
                nilai,

            "benar":
                benar,

            "salah":
                salah,

            "total":
                total,

            "waktu":
                datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),

            "jawaban":
                detail_jawaban
        }

        data_hasil.append(
            hasil_baru
        )

        simpan_hasil(
            data_hasil
        )

        st.session_state[
            "hasil_terakhir"
        ] = hasil_baru

        st.success(
            "Jawaban berhasil dikirim!"
        )

    # =====================================================
    # HASIL TERAKHIR SISWA
    # =====================================================

    if "hasil_terakhir" in st.session_state:

        hasil = st.session_state[
            "hasil_terakhir"
        ]

        st.divider()

        st.header(
            "📊 Hasil Latihan"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Nilai",
                hasil["nilai"]
            )

        with col2:

            st.metric(
                "Benar",
                hasil["benar"]
            )

        with col3:

            st.metric(
                "Salah",
                hasil["salah"]
            )

        st.divider()

        st.subheader(
            "📝 Pemeriksaan Jawaban"
        )

        for i, item in enumerate(
            hasil["jawaban"],
            start=1
        ):

            st.write(
                f"**Soal {i}**"
            )

            st.write(
                item["pertanyaan"]
            )

            st.write(
                "Jawaban kamu: "
                f"**{item['jawaban_siswa']}**"
            )

            if item["status"] == "Benar":

                st.success(
                    "✓ Jawaban kamu benar."
                )

            else:

                st.error(
                    "✗ Jawaban kamu salah."
                )

                st.info(
                    "✅ Jawaban yang benar: "
                    f"**{item['jawaban_benar']}**"
                )

                if item["pembahasan"]:

                    st.write(
                        "**Pembahasan:**"
                    )

                    st.write(
                        item["pembahasan"]
                    )

            st.divider()


# =========================================================
# LOGIN SISWA
# =========================================================

def login_siswa():

    st.title(
        "👩‍🎓 Masuk sebagai Siswa"
    )

    nama = st.text_input(
        "Nama siswa",
        placeholder="Masukkan nama lengkap"
    )

    if st.button(
        "Masuk",
        use_container_width=True
    ):

        if not nama.strip():

            st.warning(
                "Silakan masukkan nama terlebih dahulu."
            )

        else:

            st.session_state.nama_siswa = (
                nama.strip()
            )

            st.session_state.mode = "siswa"

            st.rerun()


# =========================================================
# APLIKASI UTAMA
# =========================================================

if st.session_state.mode is None:

    halaman_pilih_mode()


elif st.session_state.mode == "guru":

    menu_guru = sidebar_guru()

    if menu_guru == "🏠 Dashboard":

        dashboard_guru()

    elif menu_guru == "📚 Materi":

        tampilkan_file_txt(
            FOLDER_MATERI,
            "📚 Materi Pembelajaran"
        )

    elif menu_guru == "📄 Perangkat Pembelajaran":

        tampilkan_perangkat()

    elif menu_guru == "✏️ Latihan":

        halaman_latihan_guru()

    elif menu_guru == "🔄 Remedial":

        tampilkan_file_txt(
            FOLDER_REMEDIAL,
            "🔄 Remedial"
        )

    elif menu_guru == "⭐ Pengayaan":

        tampilkan_file_txt(
            FOLDER_PENGAYAAN,
            "⭐ Pengayaan"
        )

    elif menu_guru == "📊 Hasil Siswa":

        halaman_hasil_guru()

    elif menu_guru == "🔗 Media/Evaluasi":

        halaman_media()


elif st.session_state.mode == "siswa":

    # Jika belum ada nama, minta nama
    if not st.session_state.nama_siswa:

        login_siswa()

    else:

        menu_siswa = sidebar_siswa()

        if menu_siswa == "🏠 Beranda":

            halaman_beranda_siswa()

        elif menu_siswa == "🤖 Tanya AI":

            halaman_tanya_ai()

        elif menu_siswa == "✏️ Latihan":

            halaman_latihan_siswa()

        elif menu_siswa == "🔗 Media/Evaluasi":

            halaman_media()
