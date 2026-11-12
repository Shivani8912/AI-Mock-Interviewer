# 🎤 AI Mock Interviewer

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Author](https://img.shields.io/badge/Author-Shivani%20PR-purple.svg)](https://github.com/Shivani8912)

An intelligent, interactive AI-powered Mock Interviewer web application that analyzes candidate resumes, recommends best-fit job roles, conducts adaptive live mock interviews with voice narration, and generates comprehensive performance scorecards with personalized study roadmaps.

---

## 🌟 Key Features

- **📄 Multi-Format Resume Parser:** Seamlessly parses resumes in **PDF**, **DOCX**, and **TXT** formats. Automatically extracts candidate information, contact links, and categorizes technical skills (Languages, Frameworks, Databases, Cloud & DevOps, AI/ML, and Methodologies).
- **🎯 AI Job Role Matching:** Computes algorithmic compatibility scores across high-demand industry roles (Full Stack Developer, Backend Developer, Frontend Developer, ML Engineer, Data Scientist, DevOps Engineer, etc.) highlighting matched skills and recommended focus areas.
- **🎤 Adaptive Mock Interview Engine:** Dynamic multi-turn interview flow tailored to your chosen role, seniority level (Junior to Lead), and interview category (Technical, Behavioral / STAR method, System Design).
- **🔊 Browser Voice Narration:** Integrated with the HTML5 Web Speech API allowing the AI interviewer to speak questions aloud directly in the browser with zero external audio dependencies.
- **💡 In-Session Interviewer Hints:** Get gentle contextual hints when tackling difficult architectural questions without spoiling the full answer.
- **📊 360° Evaluation & Scorecards:** Evaluates answers across four key dimensions:
  - *Overall Score* (0–100)
  - *Technical Depth*
  - *Communication & Clarity*
  - *Problem Solving & Analytical Logic*
- **🔍 Model Answers & Feedback:** Inspect question-by-question critiques paired with gold-standard model answers.
- **🗺️ Personalized Preparation Roadmap:** Tailored study recommendations targeting specific knowledge gaps detected during the interview.
- **📥 Exportable Reports:** One-click download of the complete interview transcript and performance report in Markdown format.
- **⚡ Dual-Mode AI Execution:**
  - **Built-in Intelligent Engine:** 100% functional out of the box with zero external API keys required.
  - **Live LLM Integration:** Connect your Google Gemini API key or OpenAI/Groq key in the sidebar for live model inference.

---

## 🏗️ Project Architecture

```
AI-Mock-Interviewer/
├── app.py                      # Main Streamlit web application & UI workflow
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
└── utils/
    ├── __init__.py             # Package initializer
    ├── resume_parser.py        # PDF/DOCX/TXT text extractor & skill classifier
    ├── interview_engine.py     # Question generator, adaptive progression & rubrics
    ├── ai_client.py            # Gemini, OpenAI, & offline heuristic AI engine
    └── audio_utils.py          # Browser Web Speech API audio widget generator
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Shivani8912/AI-Mock-Interviewer.git
cd AI-Mock-Interviewer
```

### 2. Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 💻 How to Use

1. **Step 1: Upload Resume & Profile Setup**
   - Upload your resume (`.pdf`, `.docx`, or `.txt`) or click **"Load Sample Profile"** for an instant test run.
   - Review the extracted candidate profile, categorized skills, and AI role match percentages.
2. **Step 2: Configure Interview Session**
   - Select your target job role and seniority level (Entry-Level, Mid-Level, Senior, Lead).
   - Choose your interview focus: **Technical**, **Behavioral (STAR)**, or **System Design**.
   - Configure session length (3 to 10 questions) and toggle browser voice narration.
3. **Step 3: Live Interview Arena**
   - Listen to or read the AI interviewer's question.
   - Type your detailed response. Use the **"💡 Need a hint"** dropdown if you get stuck.
   - Click **"Submit Answer"** to advance through adaptive follow-ups.
4. **Step 4: Scorecard & Feedback Report**
   - Review your multi-dimensional KPI scores.
   - Study question-by-question feedback alongside model answers.
   - Download the full Markdown report (`.md`) to guide your interview preparation.

---

## 🛠️ Tech Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
- **Document Processing:** [pypdf](https://pypi.org/project/pypdf/), [python-docx](https://python-docx.readthedocs.io/)
- **AI / LLM Integration:** [Google Generative AI](https://pypi.org/project/google-generativeai/), REST APIs
- **Audio / TTS:** Browser Web Speech API (HTML5 SpeechSynthesis)
- **Language:** Python 3.10+

---

## 👤 Author

**Shivani PR**
- GitHub: [@Shivani8912](https://github.com/Shivani8912)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
