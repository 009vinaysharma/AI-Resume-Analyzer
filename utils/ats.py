"""
ATS (Applicant Tracking System) score calculator.
"""

from utils.parser import SKILL_DB

# Flat skill set
ALL_SKILLS = {s.lower() for cat in SKILL_DB.values() for s in cat}

# Important section keywords
SECTION_KEYWORDS = {
    "summary":    ["summary", "objective", "about", "profile"],
    "education":  ["education", "academic", "qualification", "degree"],
    "experience": ["experience", "employment", "work history", "career"],
    "skills":     ["skills", "technical skills", "competencies", "expertise"],
    "projects":   ["project", "portfolio", "work samples"],
    "certifications": ["certification", "certificate", "certified", "license"],
    "contact":    ["email", "phone", "linkedin", "github", "contact"],
}

# Target skills per role
ROLE_SKILLS = {
    "Frontend Developer": [
        "html", "css", "javascript", "react", "typescript", "git",
        "responsive design", "webpack", "figma", "rest api",
    ],
    "Backend Developer": [
        "python", "django", "flask", "postgresql", "docker", "rest api",
        "linux", "git", "redis", "kubernetes",
    ],
    "Full Stack Developer": [
        "javascript", "react", "node.js", "python", "postgresql",
        "docker", "git", "html", "css", "rest api",
    ],
    "Data Scientist": [
        "python", "pandas", "numpy", "scikit-learn", "machine learning",
        "sql", "matplotlib", "statistics", "tensorflow", "data analysis",
    ],
    "AI Engineer": [
        "python", "pytorch", "tensorflow", "nlp", "deep learning",
        "langchain", "transformers", "llm", "docker", "git",
    ],
}


def _detect_sections(text: str) -> dict:
    lower = text.lower()
    return {
        section: any(kw in lower for kw in kws)
        for section, kws in SECTION_KEYWORDS.items()
    }


def calculate_ats_score(parsed: dict, target_role: str = None) -> dict:
    text   = parsed.get("raw_text", "")
    skills = parsed.get("skills", [])

    sections = _detect_sections(text)
    words    = text.split()

    # ── Component scores (each 0-100) ─────────────────────────────────────────
    # 1. Skills breadth (25 pts)
    skill_score = min(len(skills) / 15 * 100, 100)

    # 2. Keywords (15 pts)  – ratio of known skills found vs total skill db size
    kw_score = min(len(skills) / 20 * 100, 100)

    # 3. Resume length (15 pts)
    if 300 <= len(words) <= 800:
        length_score = 100
    elif len(words) < 300:
        length_score = len(words) / 300 * 100
    else:
        length_score = max(100 - (len(words) - 800) / 20, 50)

    # 4. Sections present (25 pts)
    present = sum(1 for v in sections.values() if v)
    section_score = present / len(sections) * 100

    # 5. Projects (10 pts)
    proj_count = len(parsed.get("projects", []))
    project_score = min(proj_count / 4 * 100, 100)

    # 6. Contact completeness (10 pts)
    contact_score = (
        (50 if parsed.get("email") else 0) +
        (50 if parsed.get("phone") else 0)
    )

    # Weighted total
    total = (
        skill_score   * 0.25 +
        kw_score      * 0.15 +
        length_score  * 0.15 +
        section_score * 0.25 +
        project_score * 0.10 +
        contact_score * 0.10
    )
    total = round(min(max(total, 0), 100), 1)

    # Rating
    if total >= 80:
        rating = "Excellent"
    elif total >= 65:
        rating = "Good"
    elif total >= 50:
        rating = "Average"
    else:
        rating = "Needs Work"

    # Missing skills vs target role
    missing = []
    if target_role and target_role in ROLE_SKILLS:
        detected_lower = {s.lower() for s in skills}
        missing = [
            s for s in ROLE_SKILLS[target_role]
            if s.lower() not in detected_lower
        ]

    return {
        "total_score":    total,
        "rating":         rating,
        "components": {
            "skills":    round(skill_score,   1),
            "keywords":  round(kw_score,      1),
            "length":    round(length_score,  1),
            "sections":  round(section_score, 1),
            "projects":  round(project_score, 1),
            "contact":   round(contact_score, 1),
        },
        "sections_present": sections,
        "missing_skills":   missing,
        "target_role":      target_role,
    }
