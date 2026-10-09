import html
import json
import os
import re
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

import streamlit as st


# =========================================================
# KONFIGURASI
# =========================================================

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

FOLDER_DATABASE = "database"
FOLDER_MATERI = os.path.join(FOLDER_DATABASE, "materi")
FOLDER_PERANGKAT = os.path.join(FOLDER_DATABASE, "perangkat")
FOLDER_LATIHAN = os.path.join(FOLDER_DATABASE, "latihan")
FOLDER_REMEDIAL = os.path.join(FOLDER_DATABASE, "remedial")
FOLDER_PENGAYAAN = os.path.join(FOLDER_DATABASE, "pengayaan")
FOLDER_HASIL = os.path.join(FOLDER_DATABASE, "hasil_siswa")
FOLDER_ASSETS = "assets"
FOLDER_GAMBAR = os.path.join(FOLDER_ASSETS, "gambar")
FOLDER_VIDEO = os.path.join(FOLDER_ASSETS, "video")
FOLDER_MEDIA = os.path.join(FOLDER_ASSETS, "media")
FOLDER_CONFIG = "config"

FILE_HASIL = os.path.join(FOLDER_HASIL, "hasil_siswa.json")
FILE_CONFIG = os.path.join(FOLDER_CONFIG, "pembelajaran.json")
FILE_PERANGKAT_DATA = os.path.join(
    FOLDER_PERANGKAT, "perangkat_pembelajaran.json"
)
FILE_LATIHAN_LAMA = os.path.join(FOLDER_LATIHAN, "latihan_lho.txt")


# =========================================================
# STYLE: LAYOUT + GESTURE + MICRO INTERACTION
# =========================================================

def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 5% 5%, rgba(99,102,241,.08), transparent 25%),
                radial-gradient(circle at 95% 8%, rgba(14,165,233,.07), transparent 23%),
                #f8fafc;
        }

        [data-testid="stSidebar"] {
            background: #0b1220;
            border-right: 1px solid rgba(255,255,255,.06);
        }
        [data-testid="stSidebar"] * { color: #eef2ff !important; }
        [data-testid="stSidebar"] .stRadio label {
            border-radius: 14px;
            padding: 9px 11px;
            transition: transform .18s ease, background .18s ease;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            transform: translateX(4px);
            background: rgba(255,255,255,.07);
        }

        .hero {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 30px 32px;
            margin-bottom: 22px;
            color: white;
            background: linear-gradient(135deg, #111827 0%, #312e81 55%, #6d28d9 100%);
            box-shadow: 0 22px 55px rgba(15,23,42,.14);
            animation: fadeUp .4s ease both;
        }
        .hero:before, .hero:after {
            content: "";
            position: absolute;
            border-radius: 50%;
            pointer-events: none;
        }
        .hero:before {
            width: 260px; height: 260px;
            right: -95px; top: -115px;
            background: rgba(255,255,255,.08);
        }
        .hero:after {
            width: 140px; height: 140px;
            right: 180px; bottom: -100px;
            background: rgba(56,189,248,.08);
        }
        .hero h1 {
            position: relative; z-index: 2;
            margin: 0 0 7px;
            font-size: 2.15rem;
            letter-spacing: -.035em;
        }
        .hero p {
            position: relative; z-index: 2;
            margin: 0;
            color: rgba(255,255,255,.86);
            max-width: 900px;
            line-height: 1.6;
        }

        .card {
            background: rgba(255,255,255,.9);
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            padding: 21px;
            margin-bottom: 16px;
            box-shadow: 0 9px 28px rgba(15,23,42,.06);
            transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
            min-height: 140px;
            animation: fadeUp .35s ease both;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 18px 38px rgba(15,23,42,.10);
            border-color: #c7d2fe;
        }
        .card-icon {
            width: 46px; height: 46px;
            display: inline-flex;
            align-items: center; justify-content: center;
            border-radius: 15px;
            background: #eef2ff;
            font-size: 1.35rem;
            margin-bottom: 11px;
        }
        .card-kicker {
            font-size: .73rem;
            font-weight: 850;
            color: #4338ca;
            text-transform: uppercase;
            letter-spacing: .08em;
            margin-bottom: 7px;
        }
        .card-title {
            color: #152033;
            font-weight: 850;
            font-size: 1.08rem;
            margin-bottom: 7px;
        }
        .card-text {
            color: #64748b;
            font-size: .9rem;
            line-height: 1.58;
        }

        .welcome-box {
            position: relative;
            overflow: hidden;
            border: 1px solid #dbeafe;
            background: linear-gradient(135deg, rgba(239,246,255,.92), rgba(245,243,255,.92));
            border-radius: 20px;
            padding: 18px 20px;
            margin: 12px 0 18px;
        }
        .section-title {
            color: #152033;
            font-size: 1.25rem;
            font-weight: 850;
            margin: 20px 0 10px;
        }
        .subtle { color: #64748b; font-size: .9rem; }

        .stepper {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 12px 0 18px;
        }
        .step {
            flex: 1 1 120px;
            min-width: 118px;
            border: 1px solid #e2e8f0;
            border-radius: 15px;
            padding: 10px 12px;
            background: white;
            color: #64748b;
            font-size: .8rem;
            transition: .2s ease;
        }
        .step.active {
            border-color: #c7d2fe;
            background: #eef2ff;
            color: #312e81;
            font-weight: 800;
            transform: translateY(-2px);
        }

        .content-box {
            background: rgba(255,255,255,.94);
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            padding: 22px;
            box-shadow: 0 8px 25px rgba(15,23,42,.05);
            animation: fadeUp .28s ease both;
        }
        .media-box {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 14px;
            margin-bottom: 15px;
            overflow: hidden;
        }
        .ai-answer {
            background: linear-gradient(135deg, #ffffff, #f8fbff);
            border: 1px solid #dbeafe;
            border-radius: 20px;
            padding: 18px 20px;
            line-height: 1.78;
            box-shadow: 0 7px 22px rgba(15,23,42,.045);
            animation: fadeUp .25s ease both;
        }
        .empty-state {
            border: 1px dashed #cbd5e1;
            border-radius: 20px;
            padding: 32px;
            text-align: center;
            color: #64748b;
            background: rgba(255,255,255,.67);
        }
        .footer-note {
            text-align: center;
            color: #94a3b8;
            font-size: .78rem;
            padding: 24px 0 6px;
        }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,.91);
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            box-shadow: 0 6px 20px rgba(15,23,42,.04);
        }
        .stButton > button, .stLinkButton > a, .stDownloadButton > button {
            border-radius: 13px !important;
            font-weight: 750 !important;
            min-height: 42px !important;
            transition: transform .15s ease, box-shadow .15s ease !important;
        }
        .stButton > button:hover, .stLinkButton > a:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 9px 20px rgba(79,70,229,.15) !important;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 850px) {
            .hero { padding: 23px 22px; }
            .hero h1 { font-size: 1.65rem; }
            .card { padding: 16px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# =========================================================
# FOLDER & SESSION
# =========================================================

def buat_folder():
    folders = [
        FOLDER_DATABASE,
        FOLDER_MATERI,
        FOLDER_PERANGKAT,
        FOLDER_LATIHAN,
        FOLDER_REMEDIAL,
        FOLDER_PENGAYAAN,
        FOLDER_GAMBAR,
        FOLDER_VIDEO,
        FOLDER_MEDIA,
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)


buat_folder()

DEFAULT_STATE = {
    "mode": None,
    "nama_siswa": "",
    "chat_history": [],
    "selected_topic": None,
    "student_material_view": "catalog",
    "student_material_section": "gambaran",
    "student_exercise_topic_id": None,
    "selected_teacher_topic": None,
    "teacher_view": "catalog",
    "teacher_section": "identitas",
    "hasil_terakhir": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# FILE UTILITY
# =========================================================

def baca_file_txt(folder):
    data = []
    if not os.path.exists(folder):
        return data
    for nama_file in sorted(os.listdir(folder)):
        if not nama_file.lower().endswith(".txt"):
            continue
        path = os.path.join(folder, nama_file)
        try:
            with open(path, "r", encoding="utf-8") as file:
                isi = file.read().strip()
            if isi:
                data.append({"nama_file": nama_file, "isi": isi})
        except Exception:
            continue
    return data


def baca_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return default


def simpan_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def baca_hasil():
    data = baca_json(FILE_HASIL, [])
    return data if isinstance(data, list) else []


def simpan_hasil(data):
    simpan_json(FILE_HASIL, data)


# =========================================================
# DATA PERANGKAT PEMBELAJARAN
# =========================================================

def template_materi(judul="Materi Bahasa Indonesia", data=None):
    data = data or {}
    return {
        "id": str(data.get("id", "")),
        "judul": str(data.get("judul", judul)),
        "deskripsi": str(data.get("deskripsi", "")),
        "cp": str(data.get("cp", "")),
        "tp": str(data.get("tp", "")),
        "modul": str(data.get("modul", "")),
        "materi": str(data.get("materi", "")),
        "media": data.get("media", []),
        "penilaian": str(data.get("penilaian", "")),
        "latihan": data.get("latihan", []),
    }


def snapshot_demo_lama():
    return {
        "materi": [
            {
                "id": "lho",
                "judul": "Teks Laporan Hasil Observasi",
                "deskripsi": "Materi untuk memahami, menganalisis, dan menyusun teks laporan hasil observasi.",
                "cp": "Siswa memahami, menganalisis, dan menyusun teks faktual berdasarkan data hasil pengamatan.",
                "tp": "Siswa mampu mengidentifikasi informasi, struktur, kaidah kebahasaan, serta menyusun teks laporan hasil observasi berdasarkan data pengamatan.",
                "modul": "Modul pembelajaran dapat disiapkan guru pada bagian ini. Gunakan ruang ini untuk merangkum modul atau memberikan petunjuk akses modul pembelajaran.",
                "materi": "",
                "media": ["Flipbook", "Video pembelajaran", "LKPD digital"],
                "penilaian": "Penilaian dapat mencakup pemahaman materi, hasil latihan, dan produk teks laporan hasil observasi.",
                "latihan": [],
            }
        ]
    }


def id_baru(judul, data):
    base = re.sub(r"[^a-z0-9]+", "-", str(judul).lower()).strip("-") or "materi"
    existing = {str(x.get("id", "")) for x in data.get("materi", [])}
    candidate = base
    n = 2
    while candidate in existing:
        candidate = f"{base}-{n}"
        n += 1
    return candidate


def normalisasi_perangkat(data):
    if not isinstance(data, dict):
        data = {"materi": []}

    # Versi sebelumnya menampilkan data demo otomatis. Hapus hanya bila persis sama.
    if data == snapshot_demo_lama():
        data = {"materi": []}

    if not isinstance(data.get("materi"), list):
        data["materi"] = []

    hasil = []
    for item in data["materi"]:
        if not isinstance(item, dict):
            continue
        bersih = template_materi(data=item)
        if not bersih["id"]:
            bersih["id"] = id_baru(bersih["judul"], {"materi": hasil})

        media = bersih["media"]
        if not isinstance(media, list):
            media = [media]
        bersih["media"] = media

        soal_bersih = []
        latihan = bersih["latihan"] if isinstance(bersih["latihan"], list) else []
        for soal in latihan:
            if not isinstance(soal, dict):
                continue
            pilihan = soal.get("pilihan", {})
            if not isinstance(pilihan, dict):
                pilihan = {}
            jawaban = str(soal.get("jawaban", "A")).upper()
            jawaban = jawaban[0] if jawaban and jawaban[0] in "ABCD" else "A"
            soal_bersih.append(
                {
                    "pertanyaan": str(soal.get("pertanyaan", "")),
                    "pilihan": {
                        "A": str(pilihan.get("A", "")),
                        "B": str(pilihan.get("B", "")),
                        "C": str(pilihan.get("C", "")),
                        "D": str(pilihan.get("D", "")),
                    },
                    "jawaban": jawaban,
                    "pembahasan": str(soal.get("pembahasan", "")),
                }
            )
        bersih["latihan"] = soal_bersih
        hasil.append(bersih)

    data["materi"] = hasil
    return data


def buat_migrasi_materi_terpisah(materi_txt):
    """Setiap file TXT lama menjadi satu materi/topik tersendiri."""
    hasil = []
    for item in materi_txt:
        nama = os.path.splitext(item["nama_file"])[0]
        judul = re.sub(r"[_-]+", " ", nama).strip()
        judul = re.sub(r"\s+", " ", judul).title() or "Materi Bahasa Indonesia"
        hasil.append(
            template_materi(
                judul=judul,
                data={
                    "id": id_baru(judul, {"materi": hasil}),
                    "deskripsi": f"Materi pembelajaran {judul}.",
                    "materi": item["isi"],
                },
            )
        )
    return hasil


def pasang_latihan_lama(data):
    """Memindahkan latihan_lho.txt ke topik LHO, bukan ke semua materi."""
    if not os.path.exists(FILE_LATIHAN_LAMA) or not data.get("materi"):
        return
    try:
        with open(FILE_LATIHAN_LAMA, "r", encoding="utf-8") as file:
            latihan_lama = parse_soal(file.read())
        target = next(
            (
                x for x in data["materi"]
                if "laporan hasil observasi" in x.get("judul", "").lower()
                or re.search(r"\blho\b", x.get("judul", ""), flags=re.I)
            ),
            None,
        )
        if target is not None:
            target["latihan"] = latihan_lama
    except Exception:
        pass


def baca_perangkat_data():
    materi_txt = baca_file_txt(FOLDER_MATERI)

    if not os.path.exists(FILE_PERANGKAT_DATA):
        data = {"materi": buat_migrasi_materi_terpisah(materi_txt)}
        pasang_latihan_lama(data)
        simpan_json(FILE_PERANGKAT_DATA, data)
        return normalisasi_perangkat(data)

    data = baca_json(FILE_PERANGKAT_DATA, {"materi": []})
    if not isinstance(data, dict):
        data = {"materi": []}

    # Perbaikan database versi sebelumnya yang pernah menggabungkan
    # semua file TXT menjadi satu materi bernama "Materi Lanjutan".
    judul = [str(x.get("judul", "")).strip().lower() for x in data.get("materi", []) if isinstance(x, dict)]
    if materi_txt and len(judul) == 1 and judul[0] == "materi lanjutan":
        data["materi"] = buat_migrasi_materi_terpisah(materi_txt)
        pasang_latihan_lama(data)
        simpan_json(FILE_PERANGKAT_DATA, data)

    return normalisasi_perangkat(data)

def simpan_perangkat_data(data):
    simpan_json(FILE_PERANGKAT_DATA, normalisasi_perangkat(data))


def topic_by_id(data, topic_id):
    if not topic_id:
        return None
    for item in data.get("materi", []):
        if item.get("id") == topic_id:
            return item
    return None


# =========================================================
# MEDIA RENDERER
# =========================================================

def is_url(value):
    return bool(re.match(r"^https?://", str(value).strip(), re.IGNORECASE))


def is_youtube_url(url):
    try:
        host = urlparse(url).netloc.lower()
        return "youtube.com" in host or "youtu.be" in host
    except Exception:
        return False


def infer_media_type(url):
    clean = str(url).lower().split("?", 1)[0].split("#", 1)[0]
    if is_youtube_url(url):
        return "video"
    if clean.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg")):
        return "gambar"
    if clean.endswith((".mp4", ".webm", ".ogg", ".mov", ".m4v")):
        return "video"
    return "link"


def video_format(url):
    clean = str(url).lower().split("?", 1)[0].split("#", 1)[0]
    if clean.endswith(".webm"):
        return "video/webm"
    if clean.endswith(".ogg"):
        return "video/ogg"
    if clean.endswith(".mov"):
        return "video/quicktime"
    if clean.endswith(".m4v"):
        return "video/x-m4v"
    return "video/mp4"


def normalize_media(item):
    if isinstance(item, dict):
        return {
            "judul": str(item.get("judul", item.get("title", "Media"))).strip() or "Media",
            "tipe": str(item.get("tipe", item.get("type", "auto"))).lower().strip() or "auto",
            "url": str(item.get("url", item.get("source", ""))).strip(),
        }

    raw = str(item).strip()
    if not raw:
        return {"judul": "Media", "tipe": "auto", "url": ""}

    # Format: video|Judul|URL atau gambar|Judul|URL
    parts = raw.split("|", 2)
    if len(parts) == 3 and parts[0].strip().lower() in {"video", "gambar", "image", "foto"}:
        tipe = "gambar" if parts[0].strip().lower() in {"gambar", "image", "foto"} else "video"
        return {"judul": parts[1].strip() or tipe.title(), "tipe": tipe, "url": parts[2].strip()}

    for prefix, tipe in [("video:", "video"), ("gambar:", "gambar"), ("image:", "gambar")]:
        if raw.lower().startswith(prefix):
            return {"judul": tipe.title(), "tipe": tipe, "url": raw[len(prefix):].strip()}

    return {"judul": "Media", "tipe": "auto", "url": raw}


def local_media_path(value):
    text = str(value).strip()
    candidates = [
        text,
        os.path.join(FOLDER_GAMBAR, text),
        os.path.join(FOLDER_VIDEO, text),
        os.path.join(FOLDER_MEDIA, text),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def render_media(item, index=1):
    media = normalize_media(item)
    title = media["judul"] or f"Media {index}"
    source = media["url"]
    tipe = media["tipe"]

    if not source:
        return

    with st.container():
        st.markdown('<div class="media-box">', unsafe_allow_html=True)
        st.markdown(f"**{html.escape(title)}**", unsafe_allow_html=True)

        if not is_url(source):
            path = local_media_path(source)
            if path:
                detected = infer_media_type(path)
                try:
                    if tipe == "gambar" or detected == "gambar":
                        st.image(path, width="stretch")
                    elif tipe == "video" or detected == "video":
                        st.video(path, format=video_format(path))
                    else:
                        st.code(path)
                except Exception:
                    st.info("Media tersedia di folder assets/media.")
            else:
                st.info(f"File media belum ditemukan: {source}")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        detected = infer_media_type(source) if tipe == "auto" else tipe
        try:
            if detected == "video":
                # st.video mendukung URL hosted video termasuk URL YouTube.
                st.video(source, format=video_format(source))
            elif detected in {"gambar", "image"}:
                st.image(source, caption=title, width="stretch")
            else:
                st.link_button("🔗 Buka media", source, use_container_width=True)
        except Exception:
            st.link_button("🔗 Buka media", source, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# AI TUTOR: RETRIEVAL TERARAH, TANPA NAMA FILE
# =========================================================

def bersihkan_teks(teks):
    teks = str(teks).lower()
    teks = re.sub(r"[^a-z0-9\s]", " ", teks)
    return re.sub(r"\s+", " ", teks).strip()


def token_pertanyaan(pertanyaan):
    stopwords = {
        "apa", "apakah", "itu", "yang", "dan", "atau", "adalah", "dari", "pada",
        "dalam", "untuk", "dengan", "ke", "di", "sebutkan", "jelaskan", "jelaskanlah",
        "bagaimana", "mengapa", "kapan", "siapa", "dimana", "mana", "saya", "aku",
        "mau", "ingin", "tahu", "tentang", "mengenai", "tolong", "bisa", "boleh",
        "dong", "ya", "kah", "nya", "sebuah", "suatu", "secara", "lebih", "beri",
        "berikan", "contoh",
    }
    tokens = [
        x for x in bersihkan_teks(pertanyaan).split()
        if x not in stopwords and len(x) > 2
    ]
    sinonim = {
        "pengertian": {"definisi", "maksud"},
        "definisi": {"pengertian", "maksud"},
        "tujuan": {"fungsi", "manfaat"},
        "fungsi": {"tujuan", "manfaat"},
        "manfaat": {"tujuan", "fungsi"},
        "ciri": {"karakteristik"},
        "karakteristik": {"ciri"},
        "struktur": {"bagian", "susunan"},
        "kaidah": {"kebahasaan"},
        "langkah": {"tahapan", "cara", "prosedur"},
    }
    extra = set()
    for token in tokens:
        extra.update(sinonim.get(token, set()))
    return tokens + sorted(extra)


def ai_documents():
    documents = []

    # TXT lama. Nama file hanya dipakai sebagai metadata internal, bukan output.
    for item in baca_file_txt(FOLDER_MATERI):
        documents.append(
            {
                "judul": os.path.splitext(item["nama_file"])[0],
                "bagian": "Materi",
                "isi": item["isi"],
            }
        )

    data = baca_perangkat_data()
    fields = [
        ("cp", "Capaian Pembelajaran"),
        ("tp", "Tujuan Pembelajaran"),
        ("modul", "Modul"),
        ("materi", "Materi"),
        ("penilaian", "Penilaian"),
    ]
    for topik in data.get("materi", []):
        for key, label in fields:
            isi = str(topik.get(key, "")).strip()
            if isi:
                documents.append(
                    {
                        "judul": topik.get("judul", "Materi Bahasa Indonesia"),
                        "bagian": label,
                        "isi": isi,
                    }
                )
    return documents


def bersihkan_jawaban(teks):
    text = str(teks).strip()

    # Hilangkan metadata teknis / nama file dari materi lama.
    text = re.sub(r"^\s*(sumber|nama file|filename)\s*:\s*.*$", "", text, flags=re.I | re.M)
    text = re.sub(r"^\s*Perangkat\s*-\s*.*$", "", text, flags=re.I | re.M)
    text = re.sub(r"^\s*##+\s*[^\n]+\s*$", "", text, flags=re.M)

    # Hindari label teknis menjadi pembuka jawaban.
    text = re.sub(
        r"^\s*(capaian pembelajaran|tujuan pembelajaran|modul|materi|penilaian)\s*:?\s*",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def cari_materi_ai(pertanyaan, documents, konteks_judul=None):
    tokens = token_pertanyaan(pertanyaan)
    if not tokens:
        return []

    query_clean = bersihkan_teks(pertanyaan)
    query_set = set(tokens)
    results = []

    for doc in documents:
        if konteks_judul and doc.get("judul") != konteks_judul:
            continue

        body = bersihkan_teks(doc.get("isi", ""))
        if not body:
            continue
        counter = Counter(body.split())
        unique_matches = sum(1 for token in query_set if token in counter)
        freq_score = sum(min(counter[token], 3) for token in query_set)

        title_clean = bersihkan_teks(doc.get("judul", ""))
        title_matches = sum(1 for token in query_set if token in set(title_clean.split()))

        phrase_bonus = 8 if len(query_clean.split()) >= 2 and query_clean in body else 0
        score = unique_matches * 6 + freq_score + title_matches * 4 + phrase_bonus
        coverage = unique_matches / max(1, len(query_set))

        if score > 0:
            results.append(
                {
                    "judul": doc.get("judul", ""),
                    "bagian": doc.get("bagian", ""),
                    "isi": doc.get("isi", ""),
                    "score": score,
                    "coverage": coverage,
                }
            )

    results.sort(key=lambda x: (x["coverage"], x["score"]), reverse=True)
    return results


def ambil_jawaban_relevan(isi, pertanyaan):
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n+", str(isi))
        if p.strip()
    ]
    if not paragraphs:
        return ""

    tokens = set(token_pertanyaan(pertanyaan))
    ranked = []
    for no, paragraph in enumerate(paragraphs):
        clean = bersihkan_teks(paragraph)
        words = set(clean.split())
        overlap = len(tokens.intersection(words))
        if overlap == 0:
            continue
        score = overlap * 7
        if len(paragraph.split()) >= 10:
            score += 2
        ranked.append((score, -no, paragraph))

    ranked.sort(reverse=True)
    chosen = [x[2] for x in ranked[:2]]
    chosen = [bersihkan_jawaban(x) for x in chosen if bersihkan_jawaban(x)]
    return "\n\n".join(chosen).strip()


def jawab_ai(pertanyaan, konteks_judul=None):
    documents = ai_documents()
    if not documents:
        return "Materi pembelajaran belum tersedia."

    results = cari_materi_ai(pertanyaan, documents, konteks_judul)

    # Jangan memberi jawaban dari materi lain secara diam-diam bila siswa telah memilih konteks.
    if konteks_judul and not results:
        return "Jawaban yang cukup spesifik belum ditemukan pada materi yang dipilih."
    if not results:
        return "Jawaban yang cukup spesifik belum ditemukan dalam materi pembelajaran yang tersedia."

    best = results[0]
    token_count = len(set(token_pertanyaan(pertanyaan)))
    minimum_coverage = 0.25 if token_count <= 3 else 0.20
    if best["coverage"] < minimum_coverage:
        return "Jawaban yang cukup spesifik belum ditemukan dalam materi pembelajaran yang tersedia."

    answer = ambil_jawaban_relevan(best["isi"], pertanyaan)
    return answer or "Jawaban yang cukup spesifik belum ditemukan dalam materi pembelajaran yang tersedia."


# =========================================================
# PARSER LATIHAN TXT LAMA
# =========================================================

def parse_soal(isi):
    soal_list = []
    blocks = re.split(r"(?=SOAL\s*\d+\s*:)", str(isi), flags=re.I)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        match_soal = re.search(
            r"SOAL\s*\d+\s*:\s*(.*?)(?=\nA\.)",
            block,
            flags=re.I | re.S,
        )
        if not match_soal:
            continue

        pilihan = {}
        for huruf in "ABCD":
            match = re.search(
                rf"{huruf}\.\s*(.*?)(?=\n[A-D]\.\s|\nJAWABAN:|\Z)",
                block,
                flags=re.I | re.S,
            )
            if match:
                pilihan[huruf] = match.group(1).strip()

        match_jawaban = re.search(r"JAWABAN\s*:\s*([A-D])", block, flags=re.I)
        if not match_jawaban:
            continue

        match_pembahasan = re.search(
            r"PEMBAHASAN\s*:\s*(.*)", block, flags=re.I | re.S
        )
        soal_list.append(
            {
                "pertanyaan": match_soal.group(1).strip(),
                "pilihan": {h: pilihan.get(h, "") for h in "ABCD"},
                "jawaban": match_jawaban.group(1).upper(),
                "pembahasan": match_pembahasan.group(1).strip() if match_pembahasan else "",
            }
        )

    return soal_list


def ambil_semua_soal(folder):
    semua = []
    for item in baca_file_txt(folder):
        semua.extend(parse_soal(item["isi"]))
    return semua


# =========================================================
# UI HELPERS
# =========================================================

def hero(judul, subjudul, emoji="📚"):
    st.markdown(
        f'<div class="hero"><h1>{html.escape(emoji)} {html.escape(judul)}</h1><p>{html.escape(subjudul)}</p></div>',
        unsafe_allow_html=True,
    )


def card(title, text, icon="📌", kicker=""):
    kicker_html = f'<div class="card-kicker">{html.escape(kicker)}</div>' if kicker else ""
    st.markdown(
        f'<div class="card"><div class="card-icon">{html.escape(icon)}</div>{kicker_html}<div class="card-title">{html.escape(str(title))}</div><div class="card-text">{html.escape(str(text))}</div></div>',
        unsafe_allow_html=True,
    )


def empty_state(text):
    st.markdown(f'<div class="empty-state">{html.escape(text)}</div>', unsafe_allow_html=True)


def footer():
    st.markdown('<div class="footer-note">AI Tutor Bahasa Indonesia • Ruang belajar digital Bahasa Indonesia</div>', unsafe_allow_html=True)


def daftar_dokumen_perangkat():
    result = []
    if not os.path.exists(FOLDER_PERANGKAT):
        return result
    for name in sorted(os.listdir(FOLDER_PERANGKAT)):
        if name == os.path.basename(FILE_PERANGKAT_DATA):
            continue
        path = os.path.join(FOLDER_PERANGKAT, name)
        if os.path.isfile(path):
            result.append((name, path))
    return result


# =========================================================
# LOGIN / MODE
# =========================================================

def halaman_pilih_mode():
    hero(
        "AI Tutor Bahasa Indonesia",
        "Pilih ruang sesuai peran: siswa belajar, guru mengelola perangkat pembelajaran.",
        "📚",
    )
    st.markdown(
        '<div class="welcome-box"><b>Selamat datang 👋</b><br>Materi siswa, perangkat guru, latihan, media, dan petunjuk sekarang dipisahkan agar alurnya tidak bercampur.</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        card("Mode Guru", "Buat beberapa materi dan kelola CP, TP, modul, materi, latihan, media, penilaian, serta hasil siswa.", "🧑‍🏫", "RUANG PENGELOLA")
        if st.button("Masuk sebagai Guru", use_container_width=True, key="mode_guru"):
            st.session_state.mode = "guru"
            st.session_state.teacher_view = "catalog"
            st.rerun()
    with c2:
        card("Mode Siswa", "Pilih materi terlebih dahulu, lalu buka bagian yang dibutuhkan tanpa menampilkan semua isi sekaligus.", "👩‍🎓", "RUANG BELAJAR")
        if st.button("Masuk sebagai Siswa", use_container_width=True, key="mode_siswa"):
            st.session_state.mode = "siswa"
            st.session_state.student_material_view = "catalog"
            st.rerun()
    footer()


def sidebar_guru():
    st.sidebar.markdown("## 🧑‍🏫 MODE GURU")
    st.sidebar.caption("Satu ruang untuk mengelola pembelajaran.")
    menu = st.sidebar.radio(
        "Navigasi",
        [
            "🏠 Dashboard",
            "📄 Perangkat Pembelajaran",
            "✏️ Latihan",
            "🔄 Remedial",
            "⭐ Pengayaan",
            "📊 Hasil Siswa",
            "❔ Petunjuk Penggunaan",
        ],
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    if st.sidebar.button("🚪 Keluar", use_container_width=True, key="guru_logout"):
        st.session_state.mode = None
        st.session_state.selected_teacher_topic = None
        st.rerun()
    return menu


def sidebar_siswa():
    st.sidebar.markdown("## 👩‍🎓 MODE SISWA")
    if st.session_state.nama_siswa:
        st.sidebar.success(f"👤 {st.session_state.nama_siswa}")
    menu = st.sidebar.radio(
        "Navigasi",
        [
            "🏠 Beranda",
            "📚 Materi",
            "🤖 Tanya AI",
            "✏️ Latihan",
            "🎬 Media/Evaluasi",
            "❔ Petunjuk Penggunaan",
        ],
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    if st.sidebar.button("🚪 Keluar", use_container_width=True, key="student_logout"):
        st.session_state.mode = None
        st.session_state.nama_siswa = ""
        st.session_state.chat_history = []
        st.session_state.selected_topic = None
        st.session_state.student_material_view = "catalog"
        st.rerun()
    return menu


# =========================================================
# DASHBOARD GURU
# =========================================================

def dashboard_guru():
    hero("Dashboard Guru", "Pantau struktur materi, latihan, dan hasil pengerjaan siswa.", "🧑‍🏫")
    data = baca_perangkat_data()
    materi = data.get("materi", [])
    hasil = baca_hasil()
    jumlah_soal = sum(len(x.get("latihan", [])) for x in materi)
    rata = round(sum(float(x.get("nilai", 0)) for x in hasil) / len(hasil), 1) if hasil else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Materi", len(materi))
    c2.metric("✏️ Soal", jumlah_soal)
    c3.metric("👩‍🎓 Pengerjaan", len(hasil))
    c4.metric("📈 Rata-rata", rata)

    st.markdown('<div class="section-title">Ruang kerja guru</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, item in zip(
        cols,
        [
            ("Perangkat", "Kelola CP, TP, modul, materi, media, penilaian.", "📄"),
            ("Latihan", "Tambah, ubah, atau hapus soal per materi.", "✏️"),
            ("Hasil", "Pantau nilai dan detail pengerjaan siswa.", "📊"),
        ],
    ):
        with col:
            card(item[0], item[1], item[2], "FITUR")

    st.markdown('<div class="section-title">Materi tersedia</div>', unsafe_allow_html=True)
    if not materi:
        empty_state("Belum ada materi. Buat materi melalui Perangkat Pembelajaran.")
    else:
        cols = st.columns(min(3, len(materi)))
        for i, topik in enumerate(materi):
            with cols[i % len(cols)]:
                card(topik.get("judul", "Materi"), topik.get("deskripsi", "Belum ada deskripsi."), "📘", "MATERI")
    footer()


# =========================================================
# PERANGKAT GURU
# =========================================================

def buat_materi_baru(data):
    judul = f"Materi Bahasa Indonesia {len(data.get('materi', [])) + 1}"
    baru = template_materi(
        judul=judul,
        data={"id": id_baru(judul, data)},
    )
    data["materi"].append(baru)
    return baru


def katalog_materi_guru(data):
    materi = data.get("materi", [])
    if not materi:
        empty_state("Belum ada materi pembelajaran. Klik “Buat Materi Baru”.")
        return
    st.markdown('<div class="section-title">Pilih materi yang ingin dikelola</div>', unsafe_allow_html=True)
    st.caption("Setelah memilih materi, bagian perangkat dibuka satu per satu — tidak semuanya sekaligus.")
    cols = st.columns(min(3, len(materi)))
    for i, topik in enumerate(materi):
        with cols[i % len(cols)]:
            card(topik.get("judul", "Materi"), topik.get("deskripsi", "Belum ada deskripsi."), "📘", f"{len(topik.get('latihan', []))} SOAL")
            if st.button("✏️ Kelola", use_container_width=True, key=f"open_guru_{topik.get('id', i)}"):
                st.session_state.selected_teacher_topic = topik.get("id")
                st.session_state.teacher_view = "editor"
                st.session_state.teacher_section = "identitas"
                st.rerun()


def editor_soal(topik, index, prefix):
    soal = topik["latihan"][index]
    pilihan = soal.setdefault("pilihan", {"A": "", "B": "", "C": "", "D": ""})
    soal["pertanyaan"] = st.text_area("Pertanyaan", soal.get("pertanyaan", ""), height=90, key=f"{prefix}_q_{index}")
    c1, c2 = st.columns(2)
    with c1:
        pilihan["A"] = st.text_input("Pilihan A", pilihan.get("A", ""), key=f"{prefix}_a_{index}")
        pilihan["C"] = st.text_input("Pilihan C", pilihan.get("C", ""), key=f"{prefix}_c_{index}")
    with c2:
        pilihan["B"] = st.text_input("Pilihan B", pilihan.get("B", ""), key=f"{prefix}_b_{index}")
        pilihan["D"] = st.text_input("Pilihan D", pilihan.get("D", ""), key=f"{prefix}_d_{index}")

    answer = soal.get("jawaban", "A") if soal.get("jawaban", "A") in "ABCD" else "A"
    soal["jawaban"] = st.selectbox("Jawaban benar", list("ABCD"), index=list("ABCD").index(answer), key=f"{prefix}_ans_{index}")
    soal["pembahasan"] = st.text_area("Pembahasan", soal.get("pembahasan", ""), height=85, key=f"{prefix}_exp_{index}")


def editor_media(topik):
    current = [normalize_media(x) for x in topik.get("media", [])]
    new_media = []

    st.caption("Pilih auto agar aplikasi mengenali URL video/gambar secara otomatis. URL YouTube dikenali sebagai video.")
    for i, item in enumerate(current):
        with st.expander(f"Media {i + 1} • {item.get('judul', 'Media')}"):
            c1, c2, c3 = st.columns([1, 1.1, 2])
            with c1:
                tipe = st.selectbox("Jenis", ["auto", "video", "gambar", "link"], index=["auto", "video", "gambar", "link"].index(item.get("tipe", "auto")) if item.get("tipe", "auto") in ["auto", "video", "gambar", "link"] else 0, key=f"mt_{topik['id']}_{i}")
            with c2:
                judul = st.text_input("Judul", item.get("judul", "Media"), key=f"mj_{topik['id']}_{i}")
            with c3:
                source = st.text_input("URL / nama file", item.get("url", ""), key=f"mu_{topik['id']}_{i}")
            new_media.append({"judul": judul, "tipe": tipe, "url": source})

    with st.form(f"new_media_form_{topik['id']}", clear_on_submit=True):
        st.markdown("**＋ Tambah media**")
        c1, c2, c3 = st.columns([1, 1.1, 2])
        with c1:
            tipe = st.selectbox("Jenis", ["auto", "video", "gambar", "link"])
        with c2:
            judul = st.text_input("Judul")
        with c3:
            source = st.text_input("URL / nama file")
        submit = st.form_submit_button("Tambahkan", use_container_width=True)

    if submit:
        if source.strip():
            new_media.append({"judul": judul.strip() or "Media", "tipe": tipe, "url": source.strip()})
            topik["media"] = new_media
            return True
    topik["media"] = new_media
    return False


def editor_perangkat_guru(data, topik):
    st.markdown(
        f'<div class="welcome-box"><b>📘 {html.escape(topik.get("judul", "Materi"))}</b><br><span class="subtle">Kelola satu bagian perangkat pada satu waktu.</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("← Kembali ke daftar materi", key="back_guru_catalog"):
        st.session_state.teacher_view = "catalog"
        st.session_state.selected_teacher_topic = None
        st.rerun()

    sections = [
        ("identitas", "🪪 Identitas"),
        ("cp_tp", "🎯 CP & TP"),
        ("modul", "📘 Modul"),
        ("materi", "📚 Materi"),
        ("latihan", "✏️ Latihan"),
        ("media", "🎬 Media"),
        ("penilaian", "📊 Penilaian"),
        ("dokumen", "📎 Dokumen"),
    ]
    current = st.radio(
        "Bagian perangkat",
        sections,
        index=[x[0] for x in sections].index(st.session_state.teacher_section) if st.session_state.teacher_section in [x[0] for x in sections] else 0,
        format_func=lambda x: x[1],
        horizontal=True,
        key=f"teacher_sections_{topik['id']}",
        label_visibility="collapsed",
    )
    st.session_state.teacher_section = current[0]
    section = current[0]

    if section == "identitas":
        topik["judul"] = st.text_input("Nama materi", topik.get("judul", ""), key=f"tg_title_{topik['id']}")
        topik["deskripsi"] = st.text_area("Deskripsi singkat", topik.get("deskripsi", ""), height=120, key=f"tg_desc_{topik['id']}")

    elif section == "cp_tp":
        topik["cp"] = st.text_area("Capaian Pembelajaran (CP)", topik.get("cp", ""), height=190, key=f"tg_cp_{topik['id']}")
        topik["tp"] = st.text_area("Tujuan Pembelajaran (TP)", topik.get("tp", ""), height=190, key=f"tg_tp_{topik['id']}")

    elif section == "modul":
        topik["modul"] = st.text_area("Modul Pembelajaran", topik.get("modul", ""), height=430, key=f"tg_modul_{topik['id']}")

    elif section == "materi":
        topik["materi"] = st.text_area("Materi Pembelajaran", topik.get("materi", ""), height=520, key=f"tg_material_{topik['id']}")

    elif section == "latihan":
        st.caption("Latihan ini tersimpan khusus untuk materi yang sedang dipilih.")
        if not topik["latihan"]:
            empty_state("Belum ada soal untuk materi ini.")
        for i in range(len(topik["latihan"])):
            with st.expander(f"Soal {i + 1}", expanded=(i == 0)):
                editor_soal(topik, i, f"tgq_{topik['id']}")
                if st.button("🗑️ Hapus soal", key=f"tg_delete_{topik['id']}_{i}"):
                    topik["latihan"].pop(i)
                    simpan_perangkat_data(data)
                    st.rerun()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("＋ Tambah soal", use_container_width=True, key=f"tg_add_{topik['id']}"):
                topik["latihan"].append({"pertanyaan": "", "pilihan": {"A": "", "B": "", "C": "", "D": ""}, "jawaban": "A", "pembahasan": ""})
                simpan_perangkat_data(data)
                st.rerun()
        with c2:
            if st.button("💾 Simpan latihan", use_container_width=True, key=f"tg_save_{topik['id']}"):
                simpan_perangkat_data(data)
                st.success("Latihan berhasil disimpan.")

    elif section == "media":
        editor_media(topik)
        if st.button("💾 Simpan media", use_container_width=True, key=f"tg_media_save_{topik['id']}"):
            simpan_perangkat_data(data)
            st.success("Media berhasil disimpan.")
        if topik.get("media"):
            st.markdown('<div class="section-title">Pratinjau</div>', unsafe_allow_html=True)
            for i, media in enumerate(topik["media"], start=1):
                if normalize_media(media).get("url"):
                    render_media(media, i)

    elif section == "penilaian":
        topik["penilaian"] = st.text_area("Penilaian", topik.get("penilaian", ""), height=350, key=f"tg_assess_{topik['id']}")

    elif section == "dokumen":
        docs = daftar_dokumen_perangkat()
        if not docs:
            empty_state("Belum ada PDF/DOCX pada database/perangkat/.")
        else:
            for name, path in docs:
                with open(path, "rb") as file:
                    raw = file.read()
                st.download_button(f"⬇️ {name}", raw, file_name=name, use_container_width=True, key=f"doc_{name}")

    st.divider()
    if st.button("💾 Simpan semua perubahan", use_container_width=True, key=f"tg_all_{topik['id']}"):
        simpan_perangkat_data(data)
        st.success("Semua perubahan perangkat berhasil disimpan.")


def tampilkan_perangkat_guru():
    hero("Perangkat Pembelajaran", "Buat beberapa materi. Pilih materi dahulu, kemudian kelola bagian perangkat secara terpisah.", "📄")
    data = baca_perangkat_data()
    materi = data.get("materi", [])

    c1, c2 = st.columns(2)
    with c1:
        if st.button("＋ Buat Materi Baru", use_container_width=True, key="new_material_teacher"):
            baru = buat_materi_baru(data)
            simpan_perangkat_data(data)
            st.session_state.selected_teacher_topic = baru["id"]
            st.session_state.teacher_view = "editor"
            st.session_state.teacher_section = "identitas"
            st.rerun()
    with c2:
        if st.session_state.teacher_view == "editor":
            if st.button("🗂️ Daftar Materi", use_container_width=True, key="teacher_catalog_button"):
                st.session_state.teacher_view = "catalog"
                st.session_state.selected_teacher_topic = None
                st.rerun()

    topik = topic_by_id(data, st.session_state.selected_teacher_topic)
    if st.session_state.teacher_view == "editor" and topik:
        editor_perangkat_guru(data, topik)
    else:
        st.session_state.teacher_view = "catalog"
        katalog_materi_guru(data)
    footer()


# =========================================================
# LATIHAN GURU
# =========================================================

def halaman_latihan_guru():
    hero("Kelola Latihan", "Ruang khusus untuk mengelola soal berdasarkan materi.", "✏️")
    data = baca_perangkat_data()
    materi = data.get("materi", [])
    if not materi:
        empty_state("Belum ada materi. Buat materi dahulu.")
        footer()
        return

    pilihan = st.selectbox("Pilih materi", materi, format_func=lambda x: x.get("judul", "Materi"), key="guru_quick_topic")
    topik = pilihan
    st.metric("Jumlah soal", len(topik.get("latihan", [])))

    if st.button("＋ Tambahkan Soal Baru", use_container_width=True, key="quick_add_question"):
        topik["latihan"].append({"pertanyaan": "", "pilihan": {"A": "", "B": "", "C": "", "D": ""}, "jawaban": "A", "pembahasan": ""})
        simpan_perangkat_data(data)
        st.rerun()

    for i in range(len(topik.get("latihan", []))):
        with st.expander(f"Soal {i + 1}"):
            editor_soal(topik, i, f"quick_{topik['id']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Simpan", use_container_width=True, key=f"quick_save_{topik['id']}_{i}"):
                    simpan_perangkat_data(data)
                    st.success("Soal tersimpan.")
            with c2:
                if st.button("🗑️ Hapus", use_container_width=True, key=f"quick_del_{topik['id']}_{i}"):
                    topik["latihan"].pop(i)
                    simpan_perangkat_data(data)
                    st.rerun()
    footer()


# =========================================================
# REMEDIAL / PENGAYAAN / HASIL
# =========================================================

def tampilkan_file_txt(folder, judul, emoji):
    hero(judul, "Materi pendamping yang disediakan guru.", emoji)
    data = baca_file_txt(folder)
    if not data:
        empty_state("Belum ada file tersedia.")
    else:
        for item in data:
            with st.expander(item["nama_file"]):
                st.markdown(item["isi"])
    footer()


def halaman_hasil_guru():
    hero("Hasil Siswa", "Lihat nilai dan detail pengerjaan siswa.", "📊")
    hasil = baca_hasil()
    if not hasil:
        empty_state("Belum ada siswa yang mengerjakan latihan.")
        footer()
        return

    rata = round(sum(float(x.get("nilai", 0)) for x in hasil) / len(hasil), 1)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total pengerjaan", len(hasil))
    c2.metric("Rata-rata", rata)
    c3.metric("Nilai tertinggi", max(float(x.get("nilai", 0)) for x in hasil))

    for item in reversed(hasil):
        nama = item.get("nama_siswa", "Tanpa Nama")
        with st.expander(f"👤 {nama} • {item.get('materi', '')} • Nilai {item.get('nilai', 0)}"):
            st.write(f"Waktu: {item.get('waktu', '-')}")
            st.write(f"Benar: {item.get('benar', 0)} • Salah: {item.get('salah', 0)}")
            for i, detail in enumerate(item.get("jawaban", []), start=1):
                st.markdown(f"**Soal {i}**")
                st.write(detail.get("pertanyaan", ""))
                st.write(f"Jawaban siswa: **{detail.get('jawaban_siswa', 'Tidak dijawab')}**")
                st.write(f"Jawaban benar: **{detail.get('jawaban_benar', '-')}**")
                if detail.get("status") == "Benar":
                    st.success("✓ Benar")
                else:
                    st.error("✗ Salah")
                if detail.get("pembahasan"):
                    st.caption(f"Pembahasan: {detail['pembahasan']}")
    footer()


# =========================================================
# KATALOG MATERI SISWA → DETAIL TERPISAH
# =========================================================

def katalog_materi_siswa(materi):
    st.markdown('<div class="section-title">📚 Pilih Materi Bahasa Indonesia</div>', unsafe_allow_html=True)
    st.caption("Setiap materi berdiri sendiri. Isi materi belum dibuka sampai kamu memilih satu materi.")
    if not materi:
        empty_state("Belum ada materi yang disediakan guru.")
        return

    # Satu kartu = satu topik. Tidak ada isi CP/TP/materi yang ditampilkan di katalog.
    for baris_mulai in range(0, len(materi), 2):
        cols = st.columns(2, gap="large")
        for offset, col in enumerate(cols):
            idx = baris_mulai + offset
            if idx >= len(materi):
                continue
            topik = materi[idx]
            with col:
                judul = topik.get("judul", "Materi Bahasa Indonesia")
                deskripsi = topik.get("deskripsi", "Belum ada deskripsi materi.")
                jumlah_soal = len(topik.get("latihan", []))
                jumlah_media = len(topik.get("media", []))
                st.markdown(
                    f"""<div class="card" style="min-height:190px;">
                        <div class="card-icon">📖</div>
                        <div class="card-kicker">MATERI {idx + 1:02d}</div>
                        <div class="card-title">{html.escape(judul)}</div>
                        <div class="card-text">{html.escape(deskripsi)}</div>
                        <div style="margin-top:14px;color:#64748b;font-size:.82rem;">
                            ✏️ {jumlah_soal} soal &nbsp; • &nbsp; 🎬 {jumlah_media} media
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                if st.button("Buka materi →", use_container_width=True, key=f"student_open_topic_{topik.get('id', idx)}"):
                    st.session_state.selected_topic = topik.get("id")
                    st.session_state.student_material_view = "detail"
                    st.session_state.student_material_section = "gambaran"
                    st.rerun()


def tampilkan_stepper(section):
    items = [
        ("gambaran", "01 • Gambaran"),
        ("cp_tp", "02 • CP & TP"),
        ("modul", "03 • Modul"),
        ("materi", "04 • Materi"),
        ("latihan", "05 • Latihan"),
        ("media", "06 • Media"),
        ("penilaian", "07 • Penilaian"),
    ]
    rendered = "".join(
        f'<div class="step {"active" if key == section else ""}">{label}</div>'
        for key, label in items
    )
    st.markdown(f'<div class="stepper">{rendered}</div>', unsafe_allow_html=True)


def detail_materi_siswa(topik):
    st.markdown(
        f'<div class="welcome-box"><b>📖 {html.escape(topik.get("judul", "Materi"))}</b><br><span class="subtle">Pilih satu bagian. Aplikasi tidak membuka seluruh isi sekaligus.</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("← Kembali ke daftar materi", key="student_back_catalog"):
        st.session_state.student_material_view = "catalog"
        st.session_state.selected_topic = None
        st.rerun()

    sections = [
        ("gambaran", "🪪 Gambaran"),
        ("cp_tp", "🎯 CP & TP"),
        ("modul", "📘 Modul"),
        ("materi", "📚 Materi"),
        ("latihan", "✏️ Latihan"),
        ("media", "🎬 Media"),
        ("penilaian", "📊 Penilaian"),
    ]
    selected = st.radio(
        "Pilih bagian",
        sections,
        index=[x[0] for x in sections].index(st.session_state.student_material_section) if st.session_state.student_material_section in [x[0] for x in sections] else 0,
        format_func=lambda x: x[1],
        horizontal=True,
        key=f"student_section_{topik['id']}",
        label_visibility="collapsed",
    )
    section = selected[0]
    st.session_state.student_material_section = section
    tampilkan_stepper(section)

    # Satu content box untuk satu bagian saja.
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    if section == "gambaran":
        st.subheader("Gambaran Materi")
        st.write(topik.get("deskripsi") or "Deskripsi materi belum diisi guru.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Soal", len(topik.get("latihan", [])))
        c2.metric("Media", len(topik.get("media", [])))
        c3.metric("Bagian", 7)

    elif section == "cp_tp":
        st.subheader("Capaian Pembelajaran")
        st.write(topik.get("cp") or "CP belum diisi oleh guru.")
        st.subheader("Tujuan Pembelajaran")
        st.write(topik.get("tp") or "TP belum diisi oleh guru.")

    elif section == "modul":
        st.subheader("Modul Pembelajaran")
        st.write(topik.get("modul") or "Modul belum diisi oleh guru.")

    elif section == "materi":
        st.subheader("Materi Pembelajaran")
        st.markdown(topik.get("materi", "").strip() or "Materi belum diisi oleh guru.")

    elif section == "latihan":
        st.subheader("Latihan")
        jumlah = len(topik.get("latihan", []))
        if jumlah == 0:
            st.info("Belum ada latihan untuk materi ini.")
        else:
            st.write(f"Tersedia {jumlah} soal latihan.")
            if st.button("✏️ Kerjakan latihan ini", use_container_width=True, key=f"student_go_exercise_{topik['id']}"):
                st.session_state.student_exercise_topic_id = topik["id"]
                st.rerun()

    elif section == "media":
        st.subheader("Media Pembelajaran")
        media = [x for x in topik.get("media", []) if normalize_media(x).get("url")]
        if not media:
            st.info("Belum ada media untuk materi ini.")
        else:
            for i, item in enumerate(media, start=1):
                render_media(item, i)

    elif section == "penilaian":
        st.subheader("Penilaian")
        st.write(topik.get("penilaian") or "Penilaian belum diisi oleh guru.")

    st.markdown('</div>', unsafe_allow_html=True)


def halaman_materi_siswa():
    hero("Materi Bahasa Indonesia", "Pilih materi terlebih dahulu, lalu pilih satu bagian materi.", "📚")
    data = baca_perangkat_data()
    materi = data.get("materi", [])
    topik = topic_by_id(data, st.session_state.selected_topic)

    if st.session_state.student_material_view == "detail" and topik:
        detail_materi_siswa(topik)
    else:
        st.session_state.student_material_view = "catalog"
        katalog_materi_siswa(materi)
    footer()


# =========================================================
# BERANDA SISWA
# =========================================================

def halaman_beranda_siswa():
    hero("AI Tutor Bahasa Indonesia", f"Selamat belajar, {st.session_state.nama_siswa}! 🌱", "👩‍🎓")
    data = baca_perangkat_data()
    materi = data.get("materi", [])
    jumlah_soal = sum(len(x.get("latihan", [])) for x in materi)

    c1, c2, c3 = st.columns(3)
    with c1:
        card("Materi", f"{len(materi)} materi tersedia.", "📚", "BELAJAR")
    with c2:
        card("Tanya AI", "Ajukan pertanyaan dengan konteks materi.", "🤖", "BERTANYA")
    with c3:
        card("Latihan", f"{jumlah_soal} soal tersedia.", "✏️", "BERLATIH")

    st.markdown('<div class="welcome-box"><b>Urutan yang disarankan ✨</b><br>Pilih materi → buka satu bagian → gunakan Tanya AI → kerjakan latihan.</div>', unsafe_allow_html=True)
    if st.button("📚 Buka daftar materi", use_container_width=True, key="student_start_material"):
        st.session_state.student_material_view = "catalog"
        st.rerun()
    footer()


# =========================================================
# TANYA AI SISWA
# =========================================================

def halaman_tanya_ai():
    hero("Tanya AI Tutor", "Pilih konteks agar jawaban lebih terarah pada materi yang sedang dipelajari.", "🤖")
    data = baca_perangkat_data()
    materi = data.get("materi", [])
    labels = ["Semua materi"] + [x.get("judul", "Materi") for x in materi]
    konteks = st.selectbox("Konteks materi", labels, key="ai_context")
    konteks_judul = None if konteks == "Semua materi" else konteks

    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                if chat["role"] == "assistant":
                    st.markdown(f'<div class="ai-answer">{html.escape(chat["content"]).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                else:
                    st.write(chat["content"])
    else:
        st.info("Contoh: “Apa pengertian teks laporan hasil observasi?”")

    pertanyaan = st.chat_input("Tulis pertanyaanmu di sini...")
    if pertanyaan:
        st.session_state.chat_history.append({"role": "user", "content": pertanyaan})
        jawaban = jawab_ai(pertanyaan, konteks_judul)
        st.session_state.chat_history.append({"role": "assistant", "content": jawaban})
        st.rerun()
    footer()


# =========================================================
# LATIHAN SISWA
# =========================================================

def ambil_soal_siswa(topik):
    if topik.get("latihan"):
        return topik["latihan"]
    if topik.get("id") == "lho":
        return ambil_semua_soal(FOLDER_LATIHAN)
    return []


def halaman_latihan_siswa():
    hero("Latihan Bahasa Indonesia", "Pilih materi lalu kerjakan soal.", "✏️")
    data = baca_perangkat_data()
    materi = data.get("materi", [])
    if not materi:
        empty_state("Belum ada materi latihan.")
        footer()
        return

    default = topic_by_id(data, st.session_state.student_exercise_topic_id) or materi[0]
    topik = st.selectbox(
        "Pilih materi latihan",
        materi,
        index=materi.index(default),
        format_func=lambda x: x.get("judul", "Materi"),
        key="student_exercise_select",
    )
    st.session_state.student_exercise_topic_id = topik.get("id")
    soal_list = ambil_soal_siswa(topik)

    if not soal_list:
        empty_state("Belum ada soal untuk materi ini. Guru dapat menambahkannya pada menu Kelola Latihan.")
        footer()
        return

    st.markdown(f'<div class="welcome-box"><b>📝 {html.escape(topik.get("judul", "Latihan"))}</b><br>Jumlah soal: <b>{len(soal_list)}</b></div>', unsafe_allow_html=True)
    jawaban_siswa = {}

    for i, soal in enumerate(soal_list):
        st.markdown(f"### Soal {i + 1}")
        st.write(soal.get("pertanyaan", ""))
        options = []
        for huruf in "ABCD":
            isi = soal.get("pilihan", {}).get(huruf, "")
            if isi:
                options.append(f"{huruf}. {isi}")
        jawaban_siswa[i] = st.radio(
            "Pilih jawaban",
            ["— Belum menjawab —"] + options,
            key=f"student_q_{topik.get('id', 'topic')}_{i}",
            label_visibility="collapsed",
        )
        st.divider()

    if st.button("📤 Kirim Jawaban", use_container_width=True, key=f"student_submit_{topik.get('id', 'topic')}"):
        benar = 0
        detail = []
        for i, soal in enumerate(soal_list):
            raw = jawaban_siswa.get(i, "")
            match = re.match(r"([A-D])\.", raw) if raw else None
            siswa = match.group(1) if match else ""
            benar_key = str(soal.get("jawaban", "")).upper()
            status = "Benar" if siswa and siswa == benar_key else "Salah"
            benar += status == "Benar"
            detail.append(
                {
                    "pertanyaan": soal.get("pertanyaan", ""),
                    "jawaban_siswa": siswa or "Tidak dijawab",
                    "jawaban_benar": benar_key,
                    "status": status,
                    "pembahasan": soal.get("pembahasan", ""),
                }
            )

        total = len(soal_list)
        nilai = round((benar / total) * 100, 2) if total else 0
        result = {
            "nama_siswa": st.session_state.nama_siswa,
            "materi": topik.get("judul", ""),
            "nilai": nilai,
            "benar": benar,
            "salah": total - benar,
            "total": total,
            "waktu": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "jawaban": detail,
        }
        all_results = baca_hasil()
        all_results.append(result)
        simpan_hasil(all_results)
        st.session_state.hasil_terakhir = result
        st.success("Jawaban berhasil dikirim.")

    result = st.session_state.get("hasil_terakhir")
    if result and result.get("materi") == topik.get("judul"):
        st.divider()
        st.subheader("Hasil Latihan")
        c1, c2, c3 = st.columns(3)
        c1.metric("Nilai", result["nilai"])
        c2.metric("Benar", result["benar"])
        c3.metric("Salah", result["salah"])
        for i, item in enumerate(result.get("jawaban", []), start=1):
            with st.expander(f"Soal {i}"):
                st.write(item.get("pertanyaan", ""))
                st.write(f"Jawaban kamu: **{item.get('jawaban_siswa', '-')}**")
                if item.get("status") == "Benar":
                    st.success("✓ Jawaban kamu benar.")
                else:
                    st.error("✗ Jawaban kamu salah.")
                    st.info(f"Jawaban yang benar: **{item.get('jawaban_benar', '-')}**")
                if item.get("pembahasan"):
                    st.write("Pembahasan:")
                    st.write(item["pembahasan"])
    footer()


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
    if isinstance(config, dict):
        for name, value in config.items():
            values = value if isinstance(value, list) else [value]
            for i, link in enumerate(values, start=1):
                if isinstance(link, str) and link.strip():
                    found = True
                    render_media({"judul": str(name) if len(values) == 1 else f"{name} {i}", "tipe": "auto", "url": link.strip()}, i)

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
