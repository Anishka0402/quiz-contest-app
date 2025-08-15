
import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import docx
import io

# Configure Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your actual Gemini API key

# Extract text from PDF or DOCX files
def extract_text(file):
    if file.type == "AIzaSyC7KKh5QQxwWuOLDaC1wsmQjDLOcgDMHR4":
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

# Generate questions using Gemini API
def generate_questions(prompt, num_questions, question_types):
    try:
        model = genai.GenerativeModel(model_name="models/gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip().split('\n')[:num_questions]
    except Exception as e:
        return [f"Error generating questions: {str(e)}"]

# Streamlit UI
st.set_page_config(page_title="AI Quiz Contest App", layout="wide")
st.markdown("## 🧠 AI Quiz Contest App")
st.sidebar.header("📁 Resources")

# Sidebar options
st.sidebar.button("📌 Create Custom Question")
st.sidebar.button("📁 Download Question Bank")
st.sidebar.button("📁 Download Flashcards")

# User input section
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

# Generate Quiz
if st.button("🧪 Generate Quiz"):
    if not question_types:
        st.error("⚠️ Please select at least one question type.")
        st.stop()

    base_text = extract_text(uploaded_file) if (uploaded_file and use_uploaded) else         f"Generate {num_questions} {question_types[0]} questions for grade {grade}, subject {subject}, topic {topic}."

    quiz = generate_questions(base_text, num_questions, question_types)

    st.session_state.quiz_data = {
        "questions": quiz,
        "duration": quiz_duration,
        "per_question_duration": per_question_duration,
        "evaluation_points": evaluation_points
    }
    st.rerun()

# Display Quiz
if "quiz_data" in st.session_state:
    st.markdown("### 📝 Quiz Preview")
    score = 0
    for i, q in enumerate(st.session_state.quiz_data["questions"]):
        with st.expander(f"Q{i+1}: {q}"):
            answer = st.radio("Choose one:", ["Option A", "Option B", "Option C", "Option D"], key=f"q{i}")
    if st.button("🚀 Submit Quiz"):
        st.success(f"Score: {score}/{len(st.session_state.quiz_data['questions'])}")
        st.info(f"🎯 Accuracy: {(score / len(st.session_state.quiz_data['questions'])) * 100:.2f}%")
