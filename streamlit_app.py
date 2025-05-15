import streamlit as st
from mira_tab_logic import init_db, render_tabs
import base64
import os

# MUST BE FIRST Streamlit command
st.set_page_config(page_title="MIRA Assistant", layout="wide")

# Initialize database
init_db()

# --- MIRA Branding Header ---
if os.path.exists("mira.png"):
    mira_img_path = "mira.png"
    with open(mira_img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 12px; margin: 1rem 0 2.5rem 0;'>
                <img src="data:image/png;base64,{encoded}" style="width:60px;height:60px;border-radius:50%;border:2px solid #a047fa;" />
                <h1 style="font-size: 1.8em; color: #a047fa; margin: 0;'>MIRA: Your AI Recruiting Assistant</h1>
            </div>
        """.replace("<h1", "<h1").replace(";'>", "'>"), unsafe_allow_html=True)
else:
    st.title("MIRA: Your AI Recruiting Assistant")


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