import streamlit as st
from mira_tab_logic import init_db, render_tabs

# MUST BE FIRST Streamlit command
st.set_page_config(page_title="MIRA Assistant", layout="wide")

# Initialize database
init_db()

# Tab layout
TABS = [
    "🤖 Ask MIRA", 
    "📄 Resumes", 
    "📅 Calendar & Interview Scheduling", 
    "📁 Onboarding Documents", 
    "📂 Job Description Hub", 
    "🎨 Employer Branding",
    "📊 Analytics & Feedback",
    "📈 Upskilling & Coaching"
]

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(TABS)

# Render content
render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8)