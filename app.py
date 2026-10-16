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
