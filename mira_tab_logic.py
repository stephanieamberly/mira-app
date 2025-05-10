import streamlit as st
import sqlite3
from datetime import datetime
import dateparser
import re
import csv
from io import StringIO

DB_FILE = "mira_resumes.db"

def render_tabs(tab1, tab2, tab3, tab4, tab5, tab6, tab7):
    # --- 🧠 Ask MIRA ---
    with tab1:
        st.subheader("🧠 How can I help?")
        user_input = ""
        if st.button("🎤 Start Listening"):
            st.info("Voice input activated (simulated in web version)")

        typed_input = st.text_input("Type your command here:")
        if typed_input:
            user_input = typed_input

        if user_input:
            name_match = re.search(r"with ([A-Z][a-z]+(?: [A-Z][a-z]+)?)", user_input)
            position_match = re.search(r"for (the )?(.*?)( role| position)?( on| at| next| this|\.|$)", user_input)
            datetime_obj = dateparser.parse(user_input)
            name = name_match.group(1) if name_match else ""
            position = position_match.group(2).strip() if position_match else ""
            date = datetime_obj.date().strftime("%Y-%m-%d") if datetime_obj else ""
            time = datetime_obj.time().strftime("%H:%M") if datetime_obj else ""

            gpt_response = ask_gpt(user_input)
            st.success(f"MIRA says: {gpt_response}")
            log_mira_response(user_input, gpt_response)

    # --- 📄 Resumes Tab ---
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

        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader("Upload a resume (.pdf or .docx)", type=["pdf", "docx"])
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            raw_text = extract_text_from_pdf(uploaded_file) if ext == "pdf" else extract_text_from_docx(uploaded_file)
            name, email, phone, skills, experience = extract_details(raw_text)
            save_to_db(name, email, phone, skills, experience, uploaded_file.name)
            st.success(f"Saved: {name} | {email} | {phone}")

    # --- 📅 Calendar & Onboarding ---
    with tab3:
        st.subheader("📅 Schedule Interview")
        with st.form("calendar_form"):
            candidate_name = st.text_input("Candidate Name")
            candidate_email = st.text_input("Candidate Email")
            position_title = st.text_input("Position Title")
            interview_date = st.date_input("Date", value=datetime.today())
            interview_time = st.time_input("Time", value=datetime.now().time())
            submitted = st.form_submit_button("📅 Schedule Interview")
            if submitted:
                link = schedule_google_event(candidate_name, candidate_email, interview_date.strftime("%Y-%m-%d"), interview_time.strftime("%H:%M"), position_title)
                st.success(f"Scheduled: [View Interview]({link})")

    # --- 📁 Onboarding Docs Tab ---
    with tab4:
        st.subheader("📁 Sent Onboarding Docs")
        conn = sqlite3.connect(DB_FILE)
        docs = conn.execute("SELECT name, email, position, start_date, salary, filepath, timestamp FROM onboarding_logs ORDER BY timestamp DESC").fetchall()
        for d in docs:
            st.markdown(f"**{d[0]}** | {d[1]} | {d[2]} | {d[3]} | ${d[4]}")
            st.markdown(f"📄 [Download]({d[5]}) | 🕒 Sent: {d[6]}")
            st.markdown("---")

    # --- 📂 Job Descriptions Tab ---
    with tab5:
        st.subheader("📂 Job Descriptions")
        conn = sqlite3.connect(DB_FILE)
        jd_entries = conn.execute("SELECT id, content, timestamp FROM job_descriptions ORDER BY timestamp DESC").fetchall()
        for jd in jd_entries:
            st.markdown(f"📝 **Generated:** {jd[2]}")
            st.code(jd[1])
            st.markdown("---")

    # --- 📈 Upskilling & Coaching ---
    with tab6:
        st.subheader("📈 Upskilling & Manager Coaching")
        st.markdown("Coming soon: Automatically generate personalized growth plans and coaching tips for leadership.")

    # --- 📚 MIRA Q&A Log ---
    with tab7:
        st.subheader("📚 MIRA Q&A Log")
        conn = sqlite3.connect(DB_FILE)
        rows = conn.execute("SELECT question, answer, timestamp FROM mira_logs ORDER BY timestamp DESC").fetchall()
        for row in rows:
            st.markdown(f"**🕒 {row[2]}**")
            st.markdown(f"**Q:** {row[0]}")
            st.markdown(f"**A:** {row[1]}")
            st.markdown("---")
