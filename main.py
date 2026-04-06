import streamlit as st
import PyPDF2 
import io
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Resume Critiquer", page_icon="", layout="centered")

st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI powered feedback tailored to your needs")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

uploaded_file = st.file_uploader("Upload Resume Here (PDF or TXT)", type=["pdf", 'txt'])
job_role = st.text_input("Enter the job position you are targetting (optional)")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("ERROR! File does not have any content")
            st.stop()
        
        prompt = f"""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience description
        4. Specific improvements for {job_role if job_role else "general job application"}

        Resume content:
        {file_content}

        Please provide your analysis in a clear, structured format with specific recommendations on what could be improved"""

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction="You are an expert resume reviewer with years of experience in HR and recruitment for companies like Microsoft, Meta, Google, Netflix, and Salesforce."
        )
        response = model.generate_content(prompt)
        st.markdown("### Analysis Results")
        st.markdown(response.text)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
