"""
AI Mock Interviewer - Production Web Application
Built with Streamlit.
Author: Shivani PR (github.com/Shivani8912)
"""

import time
import streamlit as st
import streamlit.components.v1 as components

from utils.resume_parser import parse_resume
from utils.ai_client import AIClient, get_ai_client
from utils.interview_engine import InterviewEngine
from utils.audio_utils import get_speech_html

# Page configuration
st.set_page_config(
    page_title="AI Mock Interviewer | Smart Career Prep",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Global accents */
    .main-header {
        background: linear-gradient(135deg, #4338CA 0%, #6366F1 50%, #8B5CF6 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.15);
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
    }
    .main-header p {
        color: #E0E7FF !important;
        margin: 6px 0 0 0;
        font-size: 1.05rem;
    }

    /* Cards */
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4F46E5;
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
        opacity: 0.8;
    }

    /* Skill badges */
    .skill-badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.12);
        color: #4F46E5;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Question Bubble */
    .question-box {
        background: rgba(79, 70, 229, 0.05);
        border-left: 5px solid #6366F1;
        padding: 20px;
        border-radius: 8px;
        margin: 16px 0;
    }

    .step-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
def init_state():
    defaults = {
        "stage": 1,  # 1: Upload, 2: Setup, 3: Interview, 4: Report
        "resume_data": None,
        "candidate_name": "",
        "target_role": "Full Stack Developer",
        "target_level": "Mid-Level",
        "interview_type": "Technical",
        "total_questions": 5,
        "enable_voice": True,
        "current_question_idx": 0,
        "current_question_data": None,
        "qa_history": [],
        "evaluation_results": None,
        "api_provider": "Built-in Intelligent Engine",
        "api_key": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# Sidebar Configuration
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=64)
    st.title("Interview Hub")
    st.markdown("---")

    st.subheader("⚙️ AI Engine Settings")
    provider = st.selectbox(
        "AI Provider",
        ["Built-in Intelligent Engine", "Google Gemini", "OpenAI / Compatible"],
        index=0,
        help="Built-in works immediately without any external API keys. Or connect Gemini / OpenAI."
    )
    st.session_state.api_provider = provider

    api_key = ""
    if provider != "Built-in Intelligent Engine":
        api_key = st.text_input(
            f"Enter {provider} API Key",
            type="password",
            value=st.session_state.api_key,
            help="Your key is only kept in local browser memory and never stored."
        )
        st.session_state.api_key = api_key

    st.markdown("---")
    st.subheader("📍 Workflow Progress")
    stages = [
        ("1. Resume & Profile", 1),
        ("2. Role Setup", 2),
        ("3. Live Interview", 3),
        ("4. Feedback & Scorecard", 4)
    ]
    for label, s in stages:
        if st.session_state.stage == s:
            st.markdown(f"**👉 <span style='color: #4F46E5;'>{label} (Active)</span>**", unsafe_allow_html=True)
        elif st.session_state.stage > s:
            st.markdown(f"✅ ~{label}~")
        else:
            st.markdown(f"⚪ {label}")

    st.markdown("---")
    if st.button("🔄 Restart / New Interview", use_container_width=True):
        st.session_state.stage = 1
        st.session_state.resume_data = None
        st.session_state.qa_history = []
        st.session_state.current_question_idx = 0
        st.session_state.current_question_data = None
        st.session_state.evaluation_results = None
        st.rerun()

    st.markdown("---")
    st.caption("Developed by [Shivani PR](https://github.com/Shivani8912)")
    st.caption("AI-Mock-Interviewer v1.0.0")


# Get AI Client & Engine
def get_engine():
    provider_key = "auto"
    if st.session_state.api_provider == "Google Gemini":
        provider_key = "gemini"
    elif st.session_state.api_provider == "OpenAI / Compatible":
        provider_key = "openai"

    client = get_ai_client(provider=provider_key, api_key=st.session_state.api_key)
    return InterviewEngine(ai_client=client)


# App Header Banner
st.markdown("""
<div class="main-header">
    <h1>🎤 AI Mock Interviewer</h1>
    <p>Prepare, practice, and excel in technical and behavioral interviews with adaptive AI guidance.</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# STAGE 1: RESUME & PROFILE HUB
# ==============================================================================
if st.session_state.stage == 1:
    st.subheader("📄 Step 1: Upload Your Resume")
    st.write("Upload your resume to extract skills and match tailored interview job roles.")

    col1, col2 = st.columns([3, 2])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            help="Accepts .pdf, .docx, or .txt format"
        )

        candidate_name_input = st.text_input(
            "Candidate Name",
            value=st.session_state.candidate_name,
            placeholder="e.g. Shivani PR"
        )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            analyze_clicked = st.button("Analyze Resume 🚀", type="primary", use_container_width=True)
        with col_b2:
            sample_clicked = st.button("Load Sample Profile 💡", use_container_width=True)

    with col2:
        st.info(
            "**What this AI does:**\n"
            "- Extracts programming languages, frameworks, cloud tools & databases\n"
            "- Matches your background against industry roles\n"
            "- Generates adaptive interview questions matching your skill depth"
        )

    # Handle sample load
    if sample_clicked:
        sample_resume_text = """
        Shivani PR
        Bengaluru, India | shivani@example.com | https://linkedin.com/in/shivani-pr | https://github.com/Shivani8912
        SUMMARY:
        Full Stack Software Engineer with experience developing scalable web applications, microservices, and AI integrations.
        SKILLS:
        Languages: Python, JavaScript, TypeScript, SQL, HTML, CSS
        Frameworks: React, Node.js, FastAPI, Django, Flask, Express
        Databases: PostgreSQL, MongoDB, Redis
        Cloud & Tools: AWS, Docker, Git, CI/CD, REST APIs, Microservices, System Design
        EXPERIENCE:
        Software Engineer - Engineered responsive React frontends and high-performance Python FastAPI services.
        Reduced API latency by 35% through Redis caching and PostgreSQL query optimization.
        EDUCATION:
        B.Tech in Computer Science and Engineering
        """
        st.session_state.resume_data = parse_resume(sample_resume_text, "sample_resume.txt")
        st.session_state.candidate_name = st.session_state.resume_data["candidate_name"]
        st.success("Sample candidate profile loaded successfully!")
        st.rerun()

    # Handle user upload analysis
    if analyze_clicked:
        if not uploaded_file:
            st.warning("Please upload a resume file (PDF, DOCX, TXT) or click 'Load Sample Profile'.")
        else:
            with st.spinner("Extracting resume contents and matching job roles..."):
                parsed = parse_resume(uploaded_file, uploaded_file.name)
                if not parsed.get("success"):
                    st.error(parsed.get("error", "Error parsing resume."))
                else:
                    st.session_state.resume_data = parsed
                    if candidate_name_input.strip():
                        st.session_state.candidate_name = candidate_name_input.strip()
                    elif parsed.get("candidate_name") and parsed["candidate_name"] != "Candidate":
                        st.session_state.candidate_name = parsed["candidate_name"]
                    else:
                        st.session_state.candidate_name = "Candidate"
                    st.success("Resume parsed successfully!")
                    st.rerun()

    # Display Parsed Results if available
    if st.session_state.resume_data and st.session_state.resume_data.get("success"):
        data = st.session_state.resume_data
        st.divider()

        st.markdown(f"### 👤 Profile: **{st.session_state.candidate_name}**")

        # Contact info chips
        contact = data.get("contact_info", {})
        contact_items = []
        if contact.get("email"):
            contact_items.append(f"📧 {contact['email']}")
        if contact.get("phone"):
            contact_items.append(f"📱 {contact['phone']}")
        if contact.get("links"):
            for l in contact["links"][:2]:
                contact_items.append(f"🔗 [{l}]({l})")
        if contact_items:
            st.markdown(" | ".join(contact_items))

        # Extracted Skills
        st.markdown("#### 🛠️ Extracted Skills")
        skills_by_cat = data.get("skills_by_category", {})
        if skills_by_cat:
            cat_cols = st.columns(min(len(skills_by_cat), 3))
            for i, (cat, skills) in enumerate(skills_by_cat.items()):
                with cat_cols[i % 3]:
                    st.markdown(f"**{cat}**")
                    badges_html = " ".join([f"<span class='skill-badge'>{s}</span>" for s in skills])
                    st.markdown(badges_html, unsafe_allow_html=True)
                    st.write("")
        else:
            st.info("No specific technical keywords detected. You can still proceed by selecting any role.")

        # Recommended Roles
        st.divider()
        st.markdown("### 🎯 AI Job Role Match Recommendations")
        recs = data.get("recommended_roles", [])

        for rec in recs[:4]:
            score = rec["match_score"]
            role_name = rec["role"]
            col_r1, col_r2 = st.columns([4, 1])

            with col_r1:
                st.markdown(f"**{role_name}** — Match: **{score}%**")
                st.progress(score / 100.0)
                st.caption(f"{rec['description']}")
                matched = rec.get("matched_skills", [])
                if matched:
                    st.caption(f"✓ Matched: {', '.join(matched[:6])}")

            with col_r2:
                st.write("")
                if st.button(f"Choose {role_name}", key=f"btn_role_{role_name}", use_container_width=True):
                    st.session_state.target_role = role_name
                    st.session_state.stage = 2
                    st.rerun()

        st.markdown("---")
        if st.button("Continue to Interview Setup ➡️", type="primary", use_container_width=True):
            if recs:
                st.session_state.target_role = recs[0]["role"]
            st.session_state.stage = 2
            st.rerun()


# ==============================================================================
# STAGE 2: INTERVIEW CONFIGURATION
# ==============================================================================
elif st.session_state.stage == 2:
    st.subheader("🎯 Step 2: Configure Your Interview Session")
    st.write(f"Tailor the mock interview parameters for **{st.session_state.candidate_name or 'Candidate'}**.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💼 Target Role & Level")
        default_roles = [
            "Full Stack Developer", "Backend Developer", "Frontend Developer",
            "Machine Learning Engineer", "Data Scientist", "DevOps & Cloud Engineer",
            "Mobile Developer", "QA & Automation Engineer"
        ]
        curr_idx = default_roles.index(st.session_state.target_role) if st.session_state.target_role in default_roles else 0

        target_role = st.selectbox("Job Role", default_roles, index=curr_idx)
        st.session_state.target_role = target_role

        levels = ["Entry-Level / Junior (0-2 yrs)", "Mid-Level (2-5 yrs)", "Senior Engineer (5-8 yrs)", "Lead / Principal (8+ yrs)"]
        target_level = st.selectbox("Seniority Level", levels, index=1)
        st.session_state.target_level = target_level

    with col2:
        st.markdown("#### 📋 Interview Format")
        itypes = ["Technical", "Behavioral", "System Design"]
        interview_type = st.selectbox("Interview Focus", itypes, index=0)
        st.session_state.interview_type = interview_type

        num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
        st.session_state.total_questions = num_questions

        enable_voice = st.checkbox("Enable Browser Voice Narration (Web Speech)", value=st.session_state.enable_voice)
        st.session_state.enable_voice = enable_voice

    st.divider()

    st.markdown("#### 📌 Session Summary")
    st.markdown(
        f"- **Candidate:** {st.session_state.candidate_name or 'Candidate'}\n"
        f"- **Role:** {st.session_state.target_level} {st.session_state.target_role}\n"
        f"- **Format:** {st.session_state.interview_type} Interview ({st.session_state.total_questions} Questions)\n"
        f"- **AI Engine:** {st.session_state.api_provider}"
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("⬅️ Back"):
            st.session_state.stage = 1
            st.rerun()
    with col_btn2:
        if st.button("🚀 Start Interview Now", type="primary", use_container_width=True):
            engine = get_engine()
            skills = st.session_state.resume_data.get("top_skills", []) if st.session_state.resume_data else []
            with st.spinner("Generating opening interview question..."):
                q_data = engine.generate_opening_question(
                    candidate_name=st.session_state.candidate_name or "Candidate",
                    role=st.session_state.target_role,
                    level=st.session_state.target_level,
                    interview_type=st.session_state.interview_type,
                    skills=skills
                )
                st.session_state.current_question_data = q_data
                st.session_state.current_question_idx = 0
                st.session_state.qa_history = []
                st.session_state.stage = 3
                st.rerun()


# ==============================================================================
# STAGE 3: LIVE MOCK INTERVIEW ARENA
# ==============================================================================
elif st.session_state.stage == 3:
    curr_idx = st.session_state.current_question_idx
    total = st.session_state.total_questions
    q_data = st.session_state.current_question_data

    # Top metrics bar
    col_m1, col_m2, col_m3, col_m4 = st.columns([2, 2, 2, 2])
    with col_m1:
        st.metric("Progress", f"Question {curr_idx + 1} of {total}")
    with col_m2:
        st.metric("Role", st.session_state.target_role)
    with col_m3:
        st.metric("Level", st.session_state.target_level.split()[0])
    with col_m4:
        st.metric("Focus", st.session_state.interview_type)

    progress_val = min(1.0, (curr_idx + 1) / float(total))
    st.progress(progress_val)

    st.markdown("---")

    # Interviewer Question Display
    st.markdown("### 🤖 AI Interviewer")
    question_text = q_data.get("question", "Could you walk through your technical experience?")

    st.markdown(
        f"""
        <div class="question-box">
            <h4 style="margin: 0; color: #1E1B4B; font-weight: 600;">{question_text}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Optional Speech button
    if st.session_state.enable_voice:
        speech_html = get_speech_html(question_text)
        components.html(speech_html, height=45)

    # Candidate Answer Form
    st.markdown("### ✍️ Your Answer")
    answer_text = st.text_area(
        "Type your response below (explain your reasoning, trade-offs, and examples):",
        height=180,
        placeholder="Structure your answer clearly: Explain the concept, why you chose that approach, trade-offs, and any real-world project context..."
    )

    # Hint expander
    hint = q_data.get("hint")
    if hint:
        with st.expander("💡 Need a hint or guidance?"):
            st.info(f"**Interviewer Tip:** {hint}")

    st.markdown("")
    col_a1, col_a2, col_a3 = st.columns([2, 1, 1])

    with col_a1:
        submit_clicked = st.button("Submit Answer ➡️", type="primary", use_container_width=True)
    with col_a2:
        skip_clicked = st.button("Skip Question ⏭️", use_container_width=True)
    with col_a3:
        finish_clicked = st.button("Finish Interview 🏁", use_container_width=True)

    engine = get_engine()
    skills = st.session_state.resume_data.get("top_skills", []) if st.session_state.resume_data else []

    # Handle Answer Submission or Skip
    if submit_clicked or skip_clicked:
        final_answer = answer_text.strip() if submit_clicked else "Question skipped by candidate."
        if submit_clicked and not final_answer:
            st.warning("Please type your answer before submitting, or click 'Skip Question'.")
        else:
            # Record turn
            st.session_state.qa_history.append({
                "question": question_text,
                "answer": final_answer,
                "hint": hint or "",
                "ideal_answer": q_data.get("ideal_answer", "")
            })

            next_idx = curr_idx + 1
            if next_idx >= total:
                # Complete interview
                with st.spinner("Generating comprehensive scorecard and evaluation report..."):
                    eval_results = engine.evaluate_interview_session(
                        candidate_name=st.session_state.candidate_name or "Candidate",
                        role=st.session_state.target_role,
                        level=st.session_state.target_level,
                        interview_type=st.session_state.interview_type,
                        qa_history=st.session_state.qa_history
                    )
                    st.session_state.evaluation_results = eval_results
                    st.session_state.stage = 4
                    st.rerun()
            else:
                with st.spinner("Preparing next adaptive question..."):
                    next_q = engine.generate_next_question(
                        role=st.session_state.target_role,
                        level=st.session_state.target_level,
                        interview_type=st.session_state.interview_type,
                        question_index=next_idx,
                        total_questions=total,
                        skills=skills,
                        previous_qa=st.session_state.qa_history
                    )
                    st.session_state.current_question_data = next_q
                    st.session_state.current_question_idx = next_idx
                    st.rerun()

    # Handle early finish
    if finish_clicked:
        if answer_text.strip():
            st.session_state.qa_history.append({
                "question": question_text,
                "answer": answer_text.strip(),
                "hint": hint or "",
                "ideal_answer": q_data.get("ideal_answer", "")
            })
        with st.spinner("Compiling evaluation report for completed questions..."):
            eval_results = engine.evaluate_interview_session(
                candidate_name=st.session_state.candidate_name or "Candidate",
                role=st.session_state.target_role,
                level=st.session_state.target_level,
                interview_type=st.session_state.interview_type,
                qa_history=st.session_state.qa_history
            )
            st.session_state.evaluation_results = eval_results
            st.session_state.stage = 4
            st.rerun()

    # Show conversation history if any questions were answered
    if st.session_state.qa_history:
        st.markdown("---")
        with st.expander(f"📝 Review Previous Questions & Answers ({len(st.session_state.qa_history)})"):
            for i, item in enumerate(st.session_state.qa_history, 1):
                st.markdown(f"**Q{i}:** {item['question']}")
                st.markdown(f"**Your Answer:** {item['answer']}")
                st.markdown("---")


# ==============================================================================
# STAGE 4: PERFORMANCE REPORT & ANALYTICS
# ==============================================================================
elif st.session_state.stage == 4:
    st.subheader("📊 Performance Scorecard & Evaluation Report")
    st.write(f"Interview summary for **{st.session_state.candidate_name or 'Candidate'}** ({st.session_state.target_level} {st.session_state.target_role}).")

    results = st.session_state.evaluation_results or {}
    overall = results.get("overall_score", 75)
    tech = results.get("technical_score", 75)
    comm = results.get("communication_score", 80)
    prob = results.get("problem_solving_score", 75)

    # Big Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{overall}/100</div>
            <div class="metric-label">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{tech}/100</div>
            <div class="metric-label">Technical Depth</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{comm}/100</div>
            <div class="metric-label">Communication & Clarity</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{prob}/100</div>
            <div class="metric-label">Problem Solving</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive Assessment
    summary_text = results.get("summary", "Solid performance demonstrating good core foundational knowledge.")
    st.markdown("### 📋 Executive Assessment")
    st.info(summary_text)

    # Strengths and Areas of Growth side by side
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown("#### ✅ Demonstrated Strengths")
        strengths = results.get("strengths", ["Clear explanation of core technical principles.", "Logical approach to problem solving."])
        for s in strengths:
            st.markdown(f"- {s}")

    with col_s2:
        st.markdown("#### 🎯 Areas for Growth")
        growth = results.get("growth_areas", ["Provide deeper trade-off discussions.", "Elaborate more on edge case management."])
        for g in growth:
            st.markdown(f"- {g}")

    # Question-by-Question Deep Dive
    st.divider()
    st.markdown("### 🔍 Question-by-Question Breakdown")
    q_evals = results.get("question_evaluations", [])

    if not q_evals:
        # Fallback build from qa_history
        for i, turn in enumerate(st.session_state.qa_history, 1):
            with st.expander(f"Question {i}: {turn['question'][:80]}..."):
                st.markdown(f"**Full Question:** {turn['question']}")
                st.markdown(f"**Your Answer:** {turn['answer']}")
                if turn.get("ideal_answer"):
                    st.markdown(f"**Ideal / Model Answer:**\n> {turn['ideal_answer']}")
    else:
        for i, item in enumerate(q_evals, 1):
            q_score = item.get("score", 75)
            with st.expander(f"Q{i} (Score: {q_score}/100): {item.get('question', '')[:75]}..."):
                st.markdown(f"**Question:** {item.get('question', '')}")
                # Locate answer from history
                ans = st.session_state.qa_history[i - 1]["answer"] if i - 1 < len(st.session_state.qa_history) else "N/A"
                st.markdown(f"**Your Answer:** {ans}")
                st.markdown(f"**Feedback:** {item.get('feedback', '')}")
                st.markdown(f"**Ideal / Model Answer:**\n> {item.get('model_answer', '')}")

    # Personalized Study Roadmap
    st.divider()
    st.markdown("### 🗺️ Recommended Study & Preparation Roadmap")
    roadmap = results.get("study_roadmap", [
        "Review distributed caching and replication strategies.",
        "Deep dive into concurrency, race conditions, and locking.",
        "Structure behavioral answers using the STAR method (Situation, Task, Action, Result)."
    ])
    for step in roadmap:
        st.markdown(f"1. **{step}**")

    # Downloadable Report
    st.divider()
    report_content = f"""# AI Mock Interview Performance Report
Candidate: {st.session_state.candidate_name or 'Candidate'}
Target Role: {st.session_state.target_level} {st.session_state.target_role}
Interview Focus: {st.session_state.interview_type}
Date Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Overall Scores
- Overall Score: {overall}/100
- Technical Depth: {tech}/100
- Communication & Clarity: {comm}/100
- Problem Solving: {prob}/100

## Executive Assessment
{summary_text}

## Strengths
{chr(10).join(['- ' + s for s in strengths])}

## Areas for Growth
{chr(10).join(['- ' + g for g in growth])}

## Transcript & Question Breakdown
"""
    for i, item in enumerate(q_evals if q_evals else st.session_state.qa_history, 1):
        q_txt = item.get("question", "")
        a_txt = item.get("answer", st.session_state.qa_history[i - 1]["answer"] if i - 1 < len(st.session_state.qa_history) else "")
        fb_txt = item.get("feedback", "Completed.")
        ideal = item.get("model_answer", item.get("ideal_answer", ""))
        report_content += f"\n### Question {i}: {q_txt}\nCandidate Answer: {a_txt}\nFeedback: {fb_txt}\nIdeal Answer: {ideal}\n"

    report_content += f"\n## Actionable Study Roadmap\n{chr(10).join(['- ' + r for r in roadmap])}\n"

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 Download Full Report (.md)",
            data=report_content,
            file_name=f"mock_interview_report_{st.session_state.candidate_name or 'candidate'}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_d2:
        if st.button("🔄 Start New Practice Session", type="primary", use_container_width=True):
            st.session_state.stage = 1
            st.session_state.qa_history = []
            st.session_state.current_question_idx = 0
            st.session_state.current_question_data = None
            st.session_state.evaluation_results = None
            st.rerun()
