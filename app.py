
import streamlit as st
import google.generativeai as genai
import os
import pdfkit
import markdown

# Set your Gemini API key
API_KEY = "AIzaSyCtv6LQWAUCj2ZxRUrkqICa_bZaH75SGUU"  # 🔁 Replace this with your Gemini API key
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

# Generate and show roadmap
if submit:
    with st.spinner("Generating roadmap..."):
        roadmap = generate_learning_roadmap(topic, level.lower(), hours, weeks)
        st.markdown("### ✨ Your Personalized Roadmap")
        st.markdown(roadmap)

        # --- Convert to PDF ---
        pdf_file_path = "study_plan.pdf"
        try:
            pdfkit.from_string(markdown.markdown(roadmap), pdf_file_path)
        except OSError as e:
            st.error("Make sure wkhtmltopdf is installed and available in PATH.")
            st.stop()

        # --- Download Button ---
        with open(pdf_file_path, "rb") as f:
            st.download_button(
                label="📥 Download Study Plan as PDF",
                data=f,
                file_name="Study_Plan.pdf",
                mime="application/pdf"
            )

# --- FOOTER ---
st.markdown("""
    <hr style='border:1px solid #ddd;'>
    <div style='text-align: center; color: grey; font-size: 0.9em;'>
        Made with ❤️ by <b>Mohsin Khan</b> | <a href='https://linkedin.com/in/k-mohsin' target='_blank'>LinkedIn</a> |
        <a href='mailto:kmohsinnadeem@gmail.com'>Email Me</a>
    </div>
""", unsafe_allow_html=True)
