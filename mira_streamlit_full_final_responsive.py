import streamlit as st
from datetime import datetime, timedelta
import os
import re
import csv
import sqlite3
from io import StringIO
import pdfplumber
from docx import Document
import dateparser
import speech_recognition as sr
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64

DB_FILE = "mira_resumes.db"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

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
    conn.commit()
    conn.close()

def authenticate_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def schedule_google_event(candidate_name, candidate_email, interview_date, interview_time, position_title):
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)
    start_datetime = datetime.strptime(f"{interview_date} {interview_time}", "%Y-%m-%d %H:%M")
    end_datetime = start_datetime + timedelta(hours=1)
    event = {
        'summary': f'Interview with {candidate_name} - {position_title}',
        'location': 'Google Meet',
        'description': f'Scheduled interview for {position_title} with {candidate_name}.',
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'America/Phoenix'},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'America/Phoenix'},
        'attendees': [{'email': candidate_email}],
        'reminders': {'useDefault': True},
        'conferenceData': {
            'createRequest': {
                'requestId': f"{candidate_email.replace('@', '_')}_interview",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        }
    }
    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    return event.get('htmlLink')

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

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Streamlit UI ---
init_db()
st.set_page_config(page_title="MIRA Assistant", layout="wide")

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

# Ask MIRA
st.subheader("🧠 How can I help?")
if st.button("🎤 Start Listening"):
    try:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            audio = recognizer.listen(source, phrase_time_limit=5)
            transcription = recognizer.recognize_google(audio)
            st.session_state["user_input"] = transcription
            st.success(f"You said: {transcription}")
    except:
        st.warning("Audio not captured.")

typed_input = st.text_input("Or type your command here:")
if typed_input:
    st.session_state["user_input"] = typed_input

user_input = st.session_state.get("user_input", "")
name = email = position = date = time = ""
if user_input:
    st.markdown(f"**You said:** {user_input}")
    name_match = re.search(r"with ([A-Z][a-z]+(?: [A-Z][a-z]+)?)", user_input)
    position_match = re.search(r"for (the )?(.*?)( role| position)?( on| at| next| this|\.|$)", user_input)
    datetime_obj = dateparser.parse(user_input)
    name = name_match.group(1) if name_match else ""
    position = position_match.group(2).strip() if position_match else ""
    date = datetime_obj.date().strftime("%Y-%m-%d") if datetime_obj else ""
    time = datetime_obj.time().strftime("%H:%M") if datetime_obj else ""

# Resume Viewer
st.divider()
st.subheader("📂 View Stored Resumes")
search_query = st.text_input("Search stored resumes:")
resumes = fetch_resumes(search_query)
for r in resumes:
    st.markdown(f"**{r[1]}** | {r[2]} | {r[3]}")
    st.markdown(f"**Skills:** {r[4][:150]}...")
    st.markdown(f"**Experience:** {r[5][:200]}...")
    st.markdown("---")

st.download_button("📁 Export All Resumes to CSV", export_csv(), file_name="resumes_export.csv", mime="text/csv")

# Resume Upload
st.divider()
st.subheader("📄 Upload a Resume")
uploaded_file = st.file_uploader("Upload a resume (.pdf or .docx)", type=["pdf", "docx"])
if uploaded_file:
    try:
        ext = uploaded_file.name.split(".")[-1].lower()
        raw_text = extract_text_from_pdf(uploaded_file) if ext == "pdf" else extract_text_from_docx(uploaded_file)
        resume_name, resume_email, resume_phone, resume_skills, resume_experience = extract_details(raw_text)
        save_to_db(resume_name, resume_email, resume_phone, resume_skills, resume_experience, uploaded_file.name)
        st.success(f"Parsed and saved: {resume_name} | {resume_email} | {resume_phone}")
        summary = f"Name: {resume_name}\nEmail: {resume_email}\nPhone: {resume_phone}\n\nSkills:\n{resume_skills}\n\nExperience:\n{resume_experience}"
        st.download_button("⬇️ Download Parsed Summary", data=summary, file_name="parsed_resume.txt")
    except Exception as e:
        st.error(f"Error parsing resume: {e}")

# Calendar Form (Always Visible)
st.divider()
st.subheader("📅 Schedule an Interview")
with st.form("calendar_form_bottom"):
    candidate_name = st.text_input("Candidate Name", value=name)
    candidate_email = st.text_input("Candidate Email")
    position_title = st.text_input("Position Title", value=position)
    interview_date = st.date_input("Interview Date", value=datetime.strptime(date, "%Y-%m-%d") if date else datetime.today())
    interview_time = st.time_input("Interview Time", value=datetime.strptime(time, "%H:%M").time() if time else datetime.now().time())
    submitted = st.form_submit_button("📅 Schedule Interview")
    if submitted:
        try:
            link = schedule_google_event(candidate_name, candidate_email, interview_date.strftime("%Y-%m-%d"), interview_time.strftime("%H:%M"), position_title)
            st.success(f"Scheduled! [View Interview]({link})")
        except Exception as e:
            st.error(f"Failed to schedule interview: {e}")
