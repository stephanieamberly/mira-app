import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import base64
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- App Configuration ---
st.set_page_config(page_title="MIRA Assistant", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
        .main { background-color: #f9f5ff; }
        .stButton>button { background-color: #a047fa; color: white; }
        .stTextInput>div>div>input { border: 1px solid #a047fa; }
        .css-18e3th9 { padding: 2rem; }
        .mira-header {
            display: flex;
            align-items: center;
            gap: 12px;
            justify-content: flex-start;
        }
        .mira-header img {
            width: 48px;
            height: 48px;
            object-fit: cover;
            border-radius: 50%;
            border: 2px solid #d9a125;
        }
        .mira-header h3 {
            color: #a047fa;
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- Load MIRA Image ---
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

mira_img_base64 = get_base64_image("mira.png")

# --- Header ---
st.markdown(f"""
    <div class="mira-header">
        <img src="data:image/png;base64,{mira_img_base64}" />
        <h3>MIRA: Your AI Recruiting Assistant</h3>
    </div>
""", unsafe_allow_html=True)

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect("mira_resumes.db")
    cur = conn.cursor()
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
            salary REAL,
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
    conn.commit()
    conn.close()

init_db()

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

# --- Import Tab Logic ---
from mira_tab_logic import render_tabs
render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7)
