import streamlit as st
st.set_page_config(
    page_title="AI Mock Interviewer",
    page_icon="🎤",
    layout="wide"
)
st.title("🎤 AI Mock Interviewer")
st.write("Upload your resume and let AI identify the most suitable interview role.")

st.divider()

st.subheader("📄 Upload Your Resume")

resume = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "txt"]
)
candidate_name = st.text_input("Enter your name")
if st.button("Analyze Resume 🚀"):
    if not candidate_name:
        st.warning("Please enter your name.")

    elif not resume:
        st.warning("Please upload your resume.")

    else:
        st.success("Resume uploaded successfully!")

        st.info(
            "Your resume is ready for AI analysis. "
            "The AI agent will identify your suitable job role "
            "based on your skills, education, projects and experience."
        )
        st.write("### 📋 Resume Details")
        st.write("Candidate:", candidate_name)
        st.write("File:", resume.name)