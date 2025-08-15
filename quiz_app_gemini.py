# quiz_app.py
import streamlit as st
import fitz  # PyMuPDF for PDF
import docx2txt
import pytesseract
from PIL import Image
import json
from datetime import datetime
import base64
import random

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

# Extract text from uploaded file
def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()
    elif file.name.endswith(".docx"):
        text = docx2txt.process(file)
    elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
    elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            import pytesseract
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        except Exception:
            st.warning("OCR for image is not supported in this deployment.")

    return text

# Generate Quiz
if st.button("🧪 Generate Quiz"):
    if not question_types:
        st.error("⚠️ Please select at least one question type.")
        st.stop()

    with st.spinner("⚙️ Generating quiz using Gemini AI..."):
        # Create base prompt from uploaded content or topic info
        base_text = extract_text(uploaded_file) if (uploaded_file and use_uploaded) else \
            f"Generate {num_questions} {', '.join(question_types)} questions for grade {grade}, subject {subject}, topic {topic}."

        # Generate quiz using Gemini
        quiz = generate_questions(base_text, num_questions, question_types)

        # Handle errors
        if not quiz or "Error" in quiz[0]:
            st.error("❌ Failed to generate quiz questions. Check your API key or input.")
            st.stop()

        # Save quiz to session and rerun
        st.session_state.quiz_data = {
            "questions": quiz,
            "duration": quiz_duration,
            "per_question_duration": per_question_duration,
            "evaluation_points": evaluation_points
        }
        st.success("✅ Quiz generated successfully!")
        st.rerun()
import google.generativeai as genai

# Configure your Gemini API key
genai.configure(api_key=•••••••••••••••••••••••••••••••••••••••)

def generate_questions(prompt, num_questions=5, question_types=None):
    try:
        model = genai.GenerativeModel("gemini-pro")
        question_type_str = ", ".join(question_types or [])
        full_prompt = f"Generate {num_questions} {question_type_str} questions based on the following:\n\n{prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text.strip().split("\n\n")
    except Exception as e:
        return [f"Error generating questions: {str(e)}"]

# Quiz Interface
if st.session_state.quiz_data:
    st.subheader("📝 Quiz Preview")
    questions = st.session_state.quiz_data['questions']
    user_answers = []

    for idx, q in enumerate(questions):
        with st.expander(f"Q{idx+1}: {q['question']}", expanded=True):
            choice = st.radio("Choose one:", q['options'], key=f"q_{idx}")
            questions[idx]['user_answer'] = choice

    if st.button("🚀 Submit Quiz"):
        right, wrong = 0, 0
        incorrect_topics = []
        for q in questions:
            if q['user_answer'] == q['answer']:
                right += 1
            else:
                wrong += 1
                incorrect_topics.append(q['question'])

        accuracy = right / len(questions) * 100
        grade_score = round((accuracy / 100) * 10, 2)

        st.success(f"✅ Score: {right}/{len(questions)}")
        st.info(f"🎯 Accuracy: {accuracy:.2f}%")
        st.warning(f"📉 Mistakes: {wrong}")
        st.success(f"🏅 Grade: {grade_score}/10")

        st.subheader("🧩 Weak Areas")
        for t in incorrect_topics:
            st.write(f"❌ {t}")

        st.subheader("🧠 Recap Flashcards")
        for idx, q in enumerate(questions):
            if q['user_answer'] != q['answer']:
                card = {
                    "topic": topic,
                    "front": q['question'],
                    "back": q['answer'],
                    "created_at": datetime.now().isoformat()
                }
                st.session_state.flashcards[f"card_{idx}"] = card
                with st.expander(f"📇 Flashcard {idx+1}"):
                    st.write(f"**Q:** {card['front']}")
                    st.write(f"**A:** {card['back']}")

# Create Flashcards & Question Bank
st.sidebar.header("📁 Resources")
if st.sidebar.button("📌 Create Custom Question"):
    with st.sidebar.form("create_q"):
        q_text = st.text_input("Enter Question")
        q_ans = st.text_input("Correct Answer")
        q_type = st.selectbox("Question Type", question_types)
        submitted = st.form_submit_button("Add to Bank")
        if submitted:
            uid = f"q_{random.randint(1000,9999)}"
            st.session_state.question_bank[uid] = {
                "question": q_text,
                "answer": q_ans,
                "type": q_type
            }
            st.success("Question added!")

if st.sidebar.button("📂 Download Question Bank"):
    content = json.dumps(st.session_state.question_bank, indent=2)
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="question_bank.json">📥 Download JSON</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

if st.sidebar.button("📂 Download Flashcards"):
    content = json.dumps(st.session_state.flashcards, indent=2)
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="flashcards.json">📥 Download Flashcards</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)
