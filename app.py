import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import docx
import io
import base64
from datetime import datetime

# Configure Gemini API
import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# 🔴 Replace with your actual key

# Extract text from PDF or DOCX
def extract_text(file):
    if file.type == "application/pdf":
        text = ""
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        doc = docx.Document(io.BytesIO(file.read()))
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

# Generate questions using Gemini
def generate_questions(prompt, num_questions, question_types):
    try:
        model = genai.GenerativeModel("gemini-pro")  # ✅ Corrected model name
        response = model.generate_content(prompt)
        return response.text.strip().split('\n')[:num_questions]
    except Exception as e:
        return [f"Error generating questions: {str(e)}"]

# Download helper
def download_file(data, filename, filetype="text/plain"):
    b64 = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:{filetype};base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

# UI Setup
st.set_page_config(page_title="AI Quiz Contest App", layout="wide")
st.markdown("## 🧠 AI Quiz Contest App")
st.sidebar.header("📁 Resources")

# Sidebar actions
if st.sidebar.button("📌 Create Custom Question"):
    st.info("Custom question creation coming soon...")

if st.sidebar.button("📁 Download Question Bank"):
    if "quiz_data" in st.session_state:
        content = "\n\n".join(st.session_state.quiz_data["questions"])
        st.sidebar.markdown(download_file(content, "question_bank.txt"), unsafe_allow_html=True)
    else:
        st.sidebar.warning("No quiz generated yet!")

if st.sidebar.button("📁 Download Flashcards"):
    if "quiz_data" in st.session_state:
        content = "\n".join([f"{q} - Answer" for q in st.session_state.quiz_data["questions"]])
        st.sidebar.markdown(download_file(content, "flashcards.txt"), unsafe_allow_html=True)
    else:
        st.sidebar.warning("No flashcards to download!")

# Inputs
grade = st.selectbox("Select Grade", ["6", "7", "8", "9", "10", "11", "12"])
subject = st.text_input("Subject", "Science")
topic = st.text_input("Topic", "Photosynthesis")
num_questions = st.slider("Number of Questions", 1, 10, 5)
question_types = st.multiselect("Choose Question Types", ["MCQ", "True/False", "Short Answer"])
quiz_duration = st.slider("Total Quiz Duration (minutes)", 1, 60, 10)
per_question_duration = st.slider("Time per Question (seconds)", 10, 120, 30)
evaluation_points = st.number_input("Points per Question", 1, 10, 2)
uploaded_file = st.file_uploader("Upload Study Material (PDF/DOCX)", type=["pdf", "docx"])
use_uploaded = st.checkbox("Generate questions from uploaded material")

# Generate button
if st.button("🧪 Generate Quiz"):
    if not question_types:
        st.error("⚠️ Please select at least one question type.")
        st.stop()

    base_text = extract_text(uploaded_file) if (uploaded_file and use_uploaded) else \
        f"Generate {num_questions} {question_types[0]} questions for grade {grade}, subject {subject}, topic {topic}."

    quiz = generate_questions(base_text, num_questions, question_types)

    st.session_state.quiz_data = {
        "questions": quiz,
        "duration": quiz_duration,
        "per_question_duration": per_question_duration,
        "evaluation_points": evaluation_points,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.success("✅ Quiz generated successfully!")
    st.rerun()

# Display quiz
if "quiz_data" in st.session_state:
    st.markdown("### 📝 Quiz Preview")
    score = 0
    for i, q in enumerate(st.session_state.quiz_data["questions"]):
        with st.expander(f"Q{i+1}: {q}"):
            st.radio("Choose one:", ["Option A", "Option B", "Option C", "Option D"], key=f"q{i}")

    if st.button("🚀 Submit Quiz"):
        st.success(f"Score: {score}/{len(st.session_state.quiz_data['questions'])}")
        st.info(f"🎯 Accuracy: {(score / len(st.session_state.quiz_data['questions'])) * 100:.2f}%")
