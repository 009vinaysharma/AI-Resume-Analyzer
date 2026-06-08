"""
Resume parser – extracts structured information from plain resume text.
"""

import re


# ── Skill taxonomy ─────────────────────────────────────────────────────────────
SKILL_DB = {
    "Programming Languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "c", "go",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
        "perl", "bash", "shell", "lua", "dart", "elixir", "haskell",
    ],
    "Frameworks & Libraries": [
        "react", "angular", "vue", "next.js", "nuxt", "svelte", "django",
        "flask", "fastapi", "express", "spring", "spring boot", "laravel",
        "rails", "asp.net", "tensorflow", "pytorch", "keras", "scikit-learn",
        "pandas", "numpy", "matplotlib", "seaborn", "langchain", "hugging face",
        "transformers", "opencv", "celery", "graphql", "rxjs", "tailwind",
        "bootstrap", "sass", "scss", "redux", "mobx", "jquery",
    ],
    "Databases": [
        "postgresql", "mysql", "sqlite", "mongodb", "redis", "cassandra",
        "elasticsearch", "firebase", "dynamodb", "oracle", "mssql",
        "neo4j", "influxdb", "vector database", "pinecone", "weaviate",
    ],
    "DevOps & Cloud": [
        "docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "ci/cd",
        "terraform", "ansible", "linux", "nginx", "apache", "git", "github",
        "gitlab", "bitbucket", "heroku", "vercel", "netlify", "pulumi",
    ],
    "AI / ML Concepts": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "llm", "rag", "embeddings", "fine-tuning", "bert", "gpt",
        "transformers", "langchain", "prompt engineering", "mlops",
        "data science", "statistics", "reinforcement learning",
    ],
    "Tools & Other": [
        "rest api", "grpc", "kafka", "rabbitmq", "spark", "hadoop",
        "tableau", "power bi", "figma", "jira", "confluence", "postman",
        "swagger", "webpack", "vite", "jest", "pytest", "selenium",
        "cucumber", "agile", "scrum", "microservices",
    ],
}

# Flat list for quick lookup
ALL_SKILLS = {s.lower() for skills in SKILL_DB.values() for s in skills}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def extract_email(text: str) -> str:
    match = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(
        r'(\+?[\d\s\-().]{10,15})', text
    )
    return _clean(match.group(0)) if match else ""


def extract_name(text: str) -> str:
    """
    Heuristic: the name is usually on the first non-empty line
    that looks like a real name (2-4 title-case words, no digits).
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip lines with email / phone / URL / too many words
        if re.search(r'[@|://|\d{3}]', line):
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return line
    return "Unknown"


def extract_skills(text: str) -> dict:
    """Return a dict of {category: [matched_skills]}."""
    lower = text.lower()
    result = {}
    for category, skills in SKILL_DB.items():
        found = []
        for skill in skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, lower):
                found.append(skill)
        if found:
            result[category] = found
    return result


def extract_education(text: str) -> list:
    edu_keywords = [
        "bachelor", "master", "phd", "b.sc", "m.sc", "b.tech", "m.tech",
        "b.e", "m.e", "mba", "diploma", "degree", "university", "college",
        "institute", "school of",
    ]
    lines, found = text.splitlines(), []
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in edu_keywords):
            snippet = " ".join(lines[max(0, i-1):i+3])
            found.append(_clean(snippet))
    return found[:5]


def extract_experience(text: str) -> list:
    exp_keywords = [
        "engineer", "developer", "analyst", "manager", "intern",
        "lead", "architect", "consultant", "specialist", "scientist",
        "worked at", "employed", "experience",
    ]
    lines, found = text.splitlines(), []
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in exp_keywords):
            snippet = " ".join(lines[max(0, i-1):i+2])
            found.append(_clean(snippet))
    return found[:6]


def extract_projects(text: str) -> list:
    proj_keywords = ["project", "built", "developed", "created", "implemented",
                     "designed", "deployed"]
    lines, found = text.splitlines(), []
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in proj_keywords):
            snippet = " ".join(lines[i:i+2])
            found.append(_clean(snippet))
    return found[:6]


# ── Main entry point ───────────────────────────────────────────────────────────

def parse_resume(text: str) -> dict:
    skills_by_cat = extract_skills(text)
    flat_skills = [s for lst in skills_by_cat.values() for s in lst]
    return {
        "name":       extract_name(text),
        "email":      extract_email(text),
        "phone":      extract_phone(text),
        "skills":     flat_skills,
        "skills_by_category": skills_by_cat,
        "education":  extract_education(text),
        "experience": extract_experience(text),
        "projects":   extract_projects(text),
        "raw_text":   text,
    }
