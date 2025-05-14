import streamlit as st
from openai import OpenAI
from datetime import datetime, timedelta
import sqlite3
import os
import base64
import dateparser
import re
import csv
from io import StringIO
import pdfplumber
from docx import Document
from docx.shared import Pt

DB_FILE = "mira_resumes.db"

# --- HELPER FUNCTIONS ---
def ask_gpt(prompt):
    client = OpenAI(api_key=st.secrets["openai"]["api_key"])
    response = client.chat.completions.create(
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

def schedule_google_event(candidate_name, candidate_email, interview_date, interview_time, position_title, teams_link="https://teams.microsoft.com/l/meetup-join/abc123"):
    return teams_link or "https://teams.microsoft.com/l/meetup-join/abc123"

def generate_onboarding_doc(name, email, position, start_date, salary):
    doc = Document()
    doc.add_heading('Offer Letter', 0)
    doc.add_paragraph(f"Dear {name},")
    doc.add_paragraph(f"We are excited to offer you the position of {position}. Your start date will be {start_date}, with a starting salary of ${salary}.")
    doc.add_paragraph("Please let us know if you have any questions.")
    doc.add_paragraph("Sincerely,\nHR Team")

    for para in doc.paragraphs:
        for run in para.runs:
            run.font.size = Pt(11)

    filepath = f"onboarding_docs/{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
    os.makedirs("onboarding_docs", exist_ok=True)
    doc.save(filepath)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO onboarding_logs (name, email, position, start_date, salary, filepath, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, position, start_date, salary, filepath, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return filepath

# --- DB SETUP ---
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
        timestamp TEXT,
        job_title TEXT DEFAULT '',
        status TEXT DEFAULT 'New',
        score INTEGER DEFAULT 0
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS branding_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        content TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback_surveys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT,
        rating INTEGER,
        comments TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS coaching_materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        notes TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric TEXT,
        value INTEGER,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS voice_assistant_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transcript TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()