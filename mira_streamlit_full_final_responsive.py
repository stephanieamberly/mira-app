# mira_streamlit_full_final_responsive.py
import streamlit as st
import os
import base64
from datetime import datetime
from mira_tab_logic import render_tabs

# --- Database Initialization ---
from mira_tab_logic import DB_FILE
if not os.path.exists(DB_FILE):
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT,
            skills TEXT, experience TEXT,
            filename TEXT, timestamp TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mira_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT, answer TEXT, timestamp TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, position TEXT,
            start_date TEXT, salary TEXT, filepath TEXT, timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Theme + Config ---
st.set_page_config(page_title="MIRA Assistant", layout="wide")

# --- Header Branding ---
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

mira_img_base64 = get_base64_image("mira.png")
st.markdown(f'''
    <style>
        .mira-header {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
        }}
        .mira-header img {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid #d9a125;
        }}
        .mira-header h1 {{
            color: #a047fa;
            font-size: 1.8rem;
        }}
    </style>
    <div class="mira-header">
        <img src="data:image/png;base64,{mira_img_base64}" />
        <h1>MIRA: Your AI Recruiting Assistant</h1>
    </div>
''', unsafe_allow_html=True)

# --- Tab Setup ---
TABS = [
    "🤖 Ask MIRA", 
    "📄 Resumes", 
    "🗕 Calendar & Onboarding", 
    "📁 Onboarding Docs", 
    "📂 Job Descriptions", 
    "📈 Upskilling & Coaching",
    "📚 MIRA Q&A Log"
]

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(TABS)

# --- Render all tabs ---
render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7)