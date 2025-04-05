
import streamlit as st
import google.generativeai as genai
import os
import pdfkit
import markdown
import boto3
from io import BytesIO
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

# Function to generate roadmap
def generate_learning_roadmap(topic, level, hours, weeks):
    prompt = f"""
    Create a personalized {weeks}-week learning roadmap for someone who wants to learn "{topic}".
    They are currently at a {level} level and can dedicate {hours} hours per week.
    Break it down week-by-week with:
    - Learning goals
    - Key topics
    - Recommended resources
    - Optional practice/projects
    Format everything using Markdown.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.set_page_config(page_title="🎯 AI Learning Roadmap Generator")
st.title("📘 AI-Powered Learning Roadmap")
st.markdown("Generate a customized study plan using AI.")

# Input form
with st.form("roadmap_form"):
    topic = st.text_input("Enter the topic you want to learn")
    level = st.selectbox("Your current level", ["Beginner", "Intermediate", "Advanced"])
    hours = st.number_input("How many hours per week can you dedicate?", min_value=1, max_value=40, value=5)
    weeks = st.number_input("Number of weeks", min_value=1, max_value=52, value=4)
    submit = st.form_submit_button("Generate Roadmap")

# --- Upload to S3 ---
def upload_pdf_to_s3(pdf_bytes, filename):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )
    try:
        s3.upload_fileobj(BytesIO(pdf_bytes), BUCKET_NAME, filename)
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        return url
    except Exception as e:
        return str(e)


# Generate and show roadmap
if submit:
    with st.spinner("Generating roadmap..."):
        roadmap = generate_learning_roadmap(topic, level.lower(), hours, weeks)
        st.markdown("### ✨ Your Personalized Roadmap")
        st.markdown(roadmap)

        # --- Convert to PDF ---
        pdf_file_path = "study_plan.pdf"
        try:
            pdf_bytes = pdfkit.from_string(markdown.markdown(roadmap), False)
        except OSError as e:
            st.error("Make sure wkhtmltopdf is installed.")
            st.stop()

        filename = f"{topic}_Study_Plan.pdf".replace(" ", "_")
        url = upload_pdf_to_s3(pdf_bytes, filename)

        # --- Download Button using S3 URL ---
        if url.startswith("http"):
            response = requests.get(url)
            if response.status_code == 200:
                st.download_button(
                    label="📥 Download Study Plan as PDF",
                    data=response.content,
                    file_name=filename,
                    mime="application/pdf"
                )

        else:
            st.error(f"❌ Upload to S3 failed: {url}")

# --- FOOTER ---
st.markdown("""
    <hr style='border:1px solid #ddd;'>
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        Made with ❤️ by <b>Mohsin Khan</b> | <a href='https://linkedin.com/in/k-mohsin' target='_blank'>LinkedIn</a> |
        <a href='mailto:kmohsinnadeem@gmail.com'>Email Me</a>
    </div>
""", unsafe_allow_html=True)
