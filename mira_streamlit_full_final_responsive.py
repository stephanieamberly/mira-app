import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import re
import dateparser
import base64
from io import StringIO
import csv
import pdfplumber
from docx import Document
import os

DB_FILE = "mira_resumes.db"

def ensure_onboarding_table():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
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
    conn.commit()
    conn.close()

def ensure_job_descriptions_table():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def ensure_mira_logs_table():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mira_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def ask_gpt(prompt):
    import openai
    openai.api_key = st.secrets["openai"]["api_key"]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are MIRA, an intelligent, helpful, and friendly AI recruiting assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_details(text):
    name = text.split("\n")[0].strip() if text else ""
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone_match = re.search(r"(\+\d{1,2}\s)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    email = email_match.group() if email_match else ""
    phone = phone_match.group() if phone_match else ""
    skills = experience = ""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "skills" in line.lower():
            skills = "\n".join(lines[i+1:i+6])
        if "experience" in line.lower():
            experience = "\n".join(lines[i+1:i+10])
    return name, email, phone, skills, experience

def save_to_db(name, email, phone, skills, experience, filename):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes (name, email, phone, skills, experience, filename, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, phone, skills, experience, filename, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_mira_response(question, answer):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO mira_logs (question, answer, timestamp)
        VALUES (?, ?, ?)
    """, (question, answer, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def generate_onboarding_doc(name, email, position, start_date, salary):
    doc = Document()
    doc.add_heading("Offer of Employment", 0)
    doc.add_paragraph(f"Dear {name},\n\nWe are pleased to offer you the position of {position} at our company.")
    doc.add_paragraph(f"Your start date will be {start_date}, and your salary will be ${salary:,.2f} per year.")
    doc.add_paragraph("We look forward to welcoming you aboard!\n\nSincerely,\nMIRA Team")
    filepath = f"onboarding_{name.replace(' ', '_')}.docx"
    doc.save(filepath)
    return filepath

def fetch_resumes(query=""):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    if query:
        cur.execute("""
            SELECT * FROM resumes
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
            OR skills LIKE ? OR experience LIKE ?
        """, (f"%{query}%",)*5)
    else:
        cur.execute("SELECT * FROM resumes")
    rows = cur.fetchall()
    conn.close()
    return rows

def export_csv():
    rows = fetch_resumes()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "Phone", "Skills", "Experience", "Filename", "Timestamp"])
    writer.writerows(rows)
    return output.getvalue()

def render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7):
    ensure_onboarding_table()
    ensure_job_descriptions_table()
    ensure_mira_logs_table()

    with tab1:
        st.subheader("🧠 How can I help?")
        typed_input = st.text_input("Type your command here:")
        if typed_input:
            gpt_response = ask_gpt(typed_input)
            st.success(f"MIRA says: {gpt_response}")
            log_mira_response(typed_input, gpt_response)

    with tab2:
        st.subheader("📂 View Resumes")
        filter = st.text_input("Search resumes by name, email, skill, etc.")
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        if filter:
            cur.execute("""
                SELECT * FROM resumes
                WHERE name LIKE ? OR email LIKE ? OR skills LIKE ? OR experience LIKE ?
            """, (f"%{filter}%",)*4)
        else:
            cur.execute("SELECT * FROM resumes")
        rows = cur.fetchall()

        for r in rows:
            st.markdown(f"**{r[1]}** | {r[2]} | {r[3]}")
            st.markdown(f"**Skills:** {r[4][:150]}...")
            st.markdown(f"**Experience:** {r[5][:200]}...")
            st.markdown("---")

        csv_output = StringIO()
        writer = csv.writer(csv_output)
        writer.writerow(["ID", "Name", "Email", "Phone", "Skills", "Experience", "Filename", "Timestamp"])
        writer.writerows(rows)
        st.download_button("⬇️ Export Resumes Log", data=csv_output.getvalue(), file_name="resumes_log.csv", mime="text/csv")

    with tab3:
        st.subheader("📅 Schedule Interview + Generate Onboarding")
        with st.form("calendar_form"):
            candidate_name = st.text_input("Candidate Name")
            candidate_email = st.text_input("Candidate Email")
            position_title = st.text_input("Position Title")
            interview_date = st.date_input("Interview Date", value=datetime.today())
            interview_time = st.time_input("Interview Time", value=datetime.now().time())
            start_date = st.date_input("Start Date")
            salary = st.number_input("Salary Offered", min_value=30000, step=1000)
            generate_button = st.form_submit_button("Generate Offer Letter")

        if generate_button:
            filepath = generate_onboarding_doc(candidate_name, candidate_email, position_title, start_date, salary)
            st.success("Offer letter generated!")
            with open(filepath, "rb") as f:
                st.download_button("📄 Review Offer Letter", data=f.read(), file_name=filepath)

            if st.button("📨 Approve and Send"):
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO onboarding_logs (name, email, position, start_date, salary, filepath, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (candidate_name, candidate_email, position_title, start_date.isoformat(), salary, filepath, datetime.now().isoformat()))
                conn.commit()
                conn.close()
                st.success("Offer sent and logged!")

    with tab4:
        st.subheader("📁 Sent Onboarding Docs")
        conn = sqlite3.connect(DB_FILE)
        docs = conn.execute("SELECT name, email, position, start_date, salary, filepath, timestamp FROM onboarding_logs ORDER BY timestamp DESC").fetchall()
        for d in docs:
            st.markdown(f"**{d[0]}** | {d[1]} | {d[2]} | {d[3]} | ${d[4]}")
            st.markdown(f"📄 [Download]({d[5]}) | 🕒 Sent: {d[6]}")
            st.markdown("---")

    with tab5:
        st.subheader("📂 Job Descriptions")
        conn = sqlite3.connect(DB_FILE)
        jd_entries = conn.execute("SELECT id, content, timestamp FROM job_descriptions ORDER BY timestamp DESC").fetchall()
        for jd in jd_entries:
            st.markdown(f"📝 **Generated:** {jd[2]}")
            st.code(jd[1])
            st.markdown("---")

    with tab6:
        st.subheader("📈 Upskilling & Manager Coaching")
        st.markdown("Coming soon: Automatically generate personalized growth plans and coaching tips for leadership.")

    with tab7:
        st.subheader("📚 MIRA Q&A Log")
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("SELECT question, answer, timestamp FROM mira_logs ORDER BY timestamp DESC").fetchall()
        for row in rows:
            st.markdown(f"**🕒 {row[2]}**")
            st.markdown(f"**Q:** {row[0]}")
            st.markdown(f"**A:** {row[1]}")
            st.markdown("---")

from mira_tab_logic import render_tabs

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

render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7)
