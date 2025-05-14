import streamlit as st
from mira_tab_logic import init_db, render_tabs
import base64

# MUST BE FIRST Streamlit command
st.set_page_config(page_title="MIRA Assistant", layout="wide")

# Initialize database
init_db()

import os
import base64

def ask_gpt(prompt):
    openai.api_key = st.secrets["openai"]["api_key"]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are MIRA, an intelligent, helpful, and friendly AI recruiting assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# --- MIRA Branding (Logo + Header) ---
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_path = "mira.png"
if os.path.exists(image_path):
mira_img_path = "mira.png"
if os.path.exists(mira_img_path):
    with open(mira_img_path, "rb") as f:
        encoded_img = base64.b64encode(f.read()).decode()

    st.markdown(f"""
        <style>
            .mira-header {{
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 30px;
            }}
            .mira-header img {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid #d9a125;
            }}
            .mira-header h1 {{
                font-size: 1.8em;
                color: #a047fa;
                margin: 0;
            }}
        </style>
        <div class="mira-header">
            <img src="data:image/png;base64,{encoded_img}" />
            <h1>MIRA: Your AI Recruiting Assistant</h1>
        </div>
    """, unsafe_allow_html=True)

from mira_tab_logic import init_db, render_tabs, show_header

# Initialize database
init_db()

# Show MIRA logo + header
show_header()

# --- Tab layout ---
TABS = [
    "🧠  Ask MIRA", 
    "📄 Resumes", 
    "📅 Calendar & Interview Scheduling", 
    "📁 Onboarding Documents", 
    "📂 Job Description Hub", 
    "🎨 Employer Branding",
    "📊 Analytics & Feedback",
    "📈 Upskilling & Coaching"
]

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(TABS)

# --- Render content ---
render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8)