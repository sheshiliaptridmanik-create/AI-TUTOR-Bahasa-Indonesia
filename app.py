import streamlit as st
import os
import re
import json
from collections import Counter
from datetime import datetime

st.set_page_config(
    page_title="AI Tutor Bahasa Indonesia",
    page_icon="📚",
    layout="wide"
)
