"""
Resume Parser Utility for AI Mock Interviewer.
Extracts text from PDF, DOCX, and TXT files, extracts contact info,
categorizes technical & soft skills, and recommends tailored job roles.
"""

import io
import re
from typing import Any, Dict, List, Optional

# Attempt imports for PDF and DOCX
try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


# Known skill catalogs
SKILL_TAXONOMY = {
    "Programming Languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "golang", "go",
        "rust", "ruby", "php", "swift", "kotlin", "sql", "html", "css", "bash", "shell", "r"
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "vue.js", "next.js", "node.js", "express", "django",
        "flask", "fastapi", "spring", "spring boot", "asp.net", ".net", "flutter",
        "pytorch", "tensorflow", "scikit-learn", "sklearn", "pandas", "numpy", "keras"
    ],
    "Databases & Storage": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "sqlite",
        "cassandra", "dynamodb", "elasticsearch", "firebase", "supabase", "oracle"
    ],
    "Cloud & DevOps": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
        "ci/cd", "github actions", "gitlab ci", "terraform", "linux", "nginx", "helm"
    ],
    "AI, ML & Data": [
        "machine learning", "deep learning", "nlp", "natural language processing",
        "computer vision", "llms", "large language models", "rag", "langchain",
        "generative ai", "transformers", "data science", "data analysis", "data engineering", "tableau", "power bi"
    ],
    "Concepts & Practices": [
        "rest api", "graphql", "microservices", "system design", "distributed systems",
        "oop", "data structures", "algorithms", "agile", "scrum", "unit testing",
        "tdd", "git", "version control", "problem solving", "leadership", "communication"
    ]
}

# Role definitions for matching
ROLE_PROFILES = {
    "Full Stack Developer": {
        "core_skills": ["javascript", "typescript", "react", "node.js", "python", "sql", "html", "css", "rest api", "git", "docker"],
        "description": "Designs and builds responsive frontends, robust backend microservices, and database schemas."
    },
    "Backend Developer": {
        "core_skills": ["python", "java", "golang", "go", "c#", "node.js", "sql", "postgresql", "mysql", "redis", "docker", "microservices", "rest api", "system design"],
        "description": "Architects reliable backend APIs, handles server-side business logic, optimizations, and persistence."
    },
    "Frontend Developer": {
        "core_skills": ["javascript", "typescript", "react", "vue", "angular", "next.js", "html", "css", "git", "ui", "ux", "responsive"],
        "description": "Crafts accessible, performant, and interactive browser-based user experiences and UI systems."
    },
    "Machine Learning Engineer": {
        "core_skills": ["python", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "machine learning", "deep learning", "nlp", "llms", "docker"],
        "description": "Trains, fine-tunes, and deploys machine learning and deep learning models into production systems."
    },
    "Data Scientist": {
        "core_skills": ["python", "r", "sql", "pandas", "numpy", "scikit-learn", "data science", "data analysis", "tableau", "power bi", "statistics", "machine learning"],
        "description": "Extracts actionable insights, statistical patterns, and predictive intelligence from complex datasets."
    },
    "DevOps & Cloud Engineer": {
        "core_skills": ["aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "ci/cd", "linux", "bash", "nginx", "monitoring"],
        "description": "Automates cloud infrastructure, manages CI/CD deployment pipelines, and guarantees scalability."
    },
    "Mobile Developer": {
        "core_skills": ["swift", "kotlin", "flutter", "react native", "android", "ios", "mobile", "rest api", "git"],
        "description": "Builds high-performance native and cross-platform applications for iOS and Android platforms."
    },
    "QA & Automation Engineer": {
        "core_skills": ["python", "java", "selenium", "cypress", "unit testing", "automation", "ci/cd", "git", "agile", "api testing"],
        "description": "Ensures software quality, stability, and regression testing via automated test suites."
    }
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file bytes."""
    if not pypdf:
        return ""
    text_content = []
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
    except Exception as e:
        return f"[PDF Extraction Error: {str(e)}]"
    return "\n".join(text_content)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX file bytes."""
    if not docx:
        return ""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"[DOCX Extraction Error: {str(e)}]"


def extract_text(file_obj: Any, filename: str) -> str:
    """
    Extract text content from an uploaded file or file-like object.
    Supports .pdf, .docx, and .txt.
    """
    if file_obj is None:
        return ""

    if hasattr(file_obj, "read"):
        raw_bytes = file_obj.read()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
    elif isinstance(file_obj, bytes):
        raw_bytes = file_obj
    elif isinstance(file_obj, str):
        return file_obj
    else:
        return ""

    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext == "pdf":
        return extract_text_from_pdf(raw_bytes)
    elif ext in ["docx", "doc"]:
        return extract_text_from_docx(raw_bytes)
    else:
        # Default try utf-8 then latin-1
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return raw_bytes.decode("latin-1")
            except Exception:
                return ""


def extract_candidate_name(text: str) -> str:
    """Extract candidate name from header lines of resume."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    stop_words = {
        "resume", "curriculum", "vitae", "cv", "page", "contact",
        "email", "phone", "linkedin", "github", "summary", "profile", "education"
    }

    for line in lines[:8]:
        cleaned = re.sub(r"[^a-zA-Z\s]", "", line).strip()
        words = cleaned.split()
        if 2 <= len(words) <= 4:
            if not any(w.lower() in stop_words for w in words):
                # Ensure capitalized names
                if all(w[0].isupper() for w in words if w):
                    return cleaned
    return "Candidate"


def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract email, phone, and profile links from text."""
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    phone = phone_match.group(0) if phone_match else ""

    links = []
    for link_match in re.finditer(r"(https?://[^\s]+|www\.[^\s]+|linkedin\.com/in/[^\s]+|github\.com/[^\s]+)", text, re.IGNORECASE):
        l = link_match.group(0).rstrip(".,;")
        if l not in links:
            links.append(l)

    return {
        "email": email,
        "phone": phone,
        "links": links
    }


def extract_skills_from_text(text: str) -> tuple[Dict[str, List[str]], List[str]]:
    """Scan text for matching skills across technical categories."""
    lower_text = " " + re.sub(r"[,;:\(\)\[\]]", " ", text.lower()) + " "
    matched_skills = {}
    all_matched = []

    for category, skill_list in SKILL_TAXONOMY.items():
        found_in_cat = []
        for skill in skill_list:
            pattern = r"(?:\b|\s)" + re.escape(skill) + r"(?:\b|\s)"
            if re.search(pattern, lower_text):
                formatted = skill.title() if len(skill) > 3 else skill.upper()
                if skill == "sql":
                    formatted = "SQL"
                elif skill == "aws":
                    formatted = "AWS"
                elif skill == "gcp":
                    formatted = "GCP"
                elif skill == "ci/cd":
                    formatted = "CI/CD"
                elif skill == "rest api":
                    formatted = "REST API"
                elif skill == "node.js":
                    formatted = "Node.js"
                elif skill == "react":
                    formatted = "React"
                elif skill == "docker":
                    formatted = "Docker"
                elif skill == "kubernetes":
                    formatted = "Kubernetes"
                elif skill == "python":
                    formatted = "Python"

                if formatted not in found_in_cat:
                    found_in_cat.append(formatted)
                    all_matched.append(skill.lower())

        if found_in_cat:
            matched_skills[category] = found_in_cat

    return matched_skills, all_matched


def recommend_job_roles(all_matched_skills: List[str], text: str) -> List[Dict[str, Any]]:
    """Compute match scores for industry roles based on extracted skills and resume content."""
    skill_set = set(all_matched_skills)
    lower_text = text.lower()
    recommendations = []

    for role_name, profile in ROLE_PROFILES.items():
        core_skills = profile["core_skills"]
        matches = [s for s in core_skills if s in skill_set or s in lower_text]
        score = int(min(100, (len(matches) / max(len(core_skills) * 0.65, 1)) * 100))

        if role_name.lower() in lower_text:
            score = min(100, score + 15)

        missing = [s.title() for s in core_skills if s not in matches][:4]
        matched_display = [s.title() for s in matches]

        recommendations.append({
            "role": role_name,
            "match_score": max(25, min(100, score)),
            "description": profile["description"],
            "matched_skills": matched_display,
            "missing_skills": missing
        })

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations


def parse_resume(file_obj: Any, filename: str) -> Dict[str, Any]:
    """
    Main entry point for parsing resume files.
    Returns structured profile, contact info, skills, and role recommendations.
    """
    raw_text = extract_text(file_obj, filename)
    if not raw_text.strip():
        return {
            "success": False,
            "error": "Could not extract readable text from the uploaded file.",
            "raw_text": ""
        }

    candidate_name = extract_candidate_name(raw_text)
    contact_info = extract_contact_info(raw_text)
    categorized_skills, flat_skills = extract_skills_from_text(raw_text)
    recommended_roles = recommend_job_roles(flat_skills, raw_text)

    top_skills = []
    for cat_skills in categorized_skills.values():
        top_skills.extend(cat_skills)

    return {
        "success": True,
        "candidate_name": candidate_name,
        "contact_info": contact_info,
        "skills_by_category": categorized_skills,
        "top_skills": top_skills[:20],
        "recommended_roles": recommended_roles,
        "raw_text": raw_text,
        "word_count": len(raw_text.split())
    }
