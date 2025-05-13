import streamlit as st
from mira_tab_logic import render_tabs
from datetime import datetime
import sqlite3
import os
import base64

DB_FILE = "mira_resumes.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        skills TEXT,
        experience TEXT,
        filename TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS mira_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS onboarding_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        position TEXT,
        start_date TEXT,
        salary TEXT,
        filepath TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Streamlit Config & Setup ---
st.set_page_config(page_title="MIRA Assistant", layout="wide")
init_db()

# --- MIRA Branding ---
mira_img_base64 = get_base64_image("mira.png")
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    st.markdown(f'''
        <style>
            .mira-header {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                justify-content: center;
                gap: 16px;
                text-align: center;
            }}
            .mira-header img {{
                width: 80px;
                height: 80px;
                object-fit: cover;
                border-radius: 50%;
                border: 3px solid #d9a125;
            }}
            .mira-header h1 {{
                font-size: 1.8em;
                color: #a047fa;
                margin: 0;
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