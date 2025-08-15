# quiz_app.py
import streamlit as st
import fitz  # PyMuPDF for PDF
import docx2txt
import pytesseract
from PIL import Image
import json
from datetime import datetime

st.set_page_config(page_title="AI Quiz Contest App", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        body { background-color: #0f0f1a; color: white; }
        .stApp { background-color: #0f0f1a; }
    </style>
""", unsafe_allow_html=True)

# Session init
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = {}
if "question_bank" not in st.session_state:
    st.session_state.question_bank = {}
if "flashcards" not in st.session_state:
    st.session_state.flashcards = {}

# Input Section
st.title("🧠 AI Quiz Generator & Study Buddy")
st.subheader("Enter Quiz Specifications")

grade = st.selectbox("Select Grade", ["6", "7", "8", "9", "10", "11", "12"])
subject = st.text_input("Subject")
topic = st.text_input("Topic")
num_questions = st.number_input("Number of Questions", min_value=1, max_value=50)
question_types = st.multiselect("Types of Questions", ["MCQ", "True/False", "Fill in the blanks", "Short Answer"])
duration_per_question = st.number_input("Duration per Question (seconds)", min_value=10, max_value=300)
total_duration = st.number_input("Total Quiz Duration (seconds)", min_value=60, max_value=3600)
eval_points = st.slider("Evaluation strictness (1=Easy, 5=Strict)", 1, 5, 3)

st.subheader("📤 Upload Study Material (PDF, DOCX, Image)")
uploaded_file = st.file_uploader("Upload file", type=["pdf", "docx", "png", "jpg", "jpeg"])

use_uploaded = False
if uploaded_file:
    use_uploaded = st.radio("Generate questions from:", ["Uploaded Material", "Gemini AI"], horizontal=True) == "Uploaded Material"

if st.button("🧪 Generate Quiz"):
    st.success("Generating Quiz... (mock implementation)")
    # Placeholder for Gemini API / material parsing logic
    questions = []
    for i in range(int(num_questions)):
        questions.append({
            "question": f"Sample {question_types[0]} Question {i+1} on {topic}",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        })

    st.session_state.quiz_data = {
        "questions": questions,
        "meta": {
            "grade": grade,
            "subject": subject,
            "topic": topic,
            "types": question_types,
            "duration": total_duration,
            "eval_points": eval_points,
            "timestamp": datetime.now().isoformat()
        }
    }
    st.experimental_rerun()

# Display Quiz
if st.session_state.quiz_data:
    st.subheader("📝 Quiz Preview")
    for idx, q in enumerate(st.session_state.quiz_data['questions']):
        st.markdown(f"**Q{idx+1}:** {q['question']}")
        if "MCQ" in q['question']:
            st.radio("Choose one:", q['options'], key=f"q_{idx}")

    st.button("🚀 Submit Quiz", key="submit_quiz")

# Placeholder for evaluation, flashcards, download features, etc.
# Will be implemented in next steps.
