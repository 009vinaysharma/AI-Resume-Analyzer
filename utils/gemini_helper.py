"""
Gemini AI helper – generates resume summary, feedback and interview tips.
Falls back to templated responses when the API key is absent.
"""

import os
import re

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def _get_model():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or not GENAI_AVAILABLE:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


def _safe_generate(model, prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI generation temporarily unavailable: {e}"


# ── Fallback templates ──────────────────────────────────────────────────────────

def _fallback_summary(parsed: dict) -> str:
    name   = parsed.get("name", "The candidate")
    skills = parsed.get("skills", [])[:6]
    role   = parsed.get("predicted_role", "software professional")
    return (
        f"{name} is a motivated {role} with hands-on experience in "
        f"{', '.join(skills) if skills else 'various technologies'}. "
        "They demonstrate a strong technical foundation and a passion for building "
        "scalable software solutions."
    )


def _fallback_feedback(ats_score: float) -> list:
    tips = [
        "Add quantifiable achievements (e.g. 'Reduced load time by 40%').",
        "Include a concise professional summary at the top.",
        "Tailor your skills section to the job description.",
        "Ensure consistent formatting and use of action verbs.",
        "Add links to GitHub, portfolio, or LinkedIn.",
    ]
    if ats_score < 60:
        tips.insert(0, "Your resume needs significant improvements – focus on adding more relevant keywords.")
    return tips


def _fallback_interview_tips(role: str) -> list:
    common = [
        "Research the company mission and recent news before the interview.",
        "Use the STAR method (Situation, Task, Action, Result) for behavioural questions.",
        "Prepare 2-3 thoughtful questions to ask the interviewer.",
        "Practice explaining your most impactful projects concisely.",
    ]
    role_specific = {
        "Frontend Developer":  ["Be ready to code a UI component live.", "Know CSS specificity and box-model well."],
        "Backend Developer":   ["Brush up on REST principles and DB indexing.", "Expect a system-design round."],
        "Full Stack Developer":["Prepare for both frontend and backend coding rounds.", "Discuss trade-offs in architecture decisions."],
        "Data Scientist":      ["Review core ML algorithms and their assumptions.", "Be prepared to explain your model evaluation strategy."],
        "AI Engineer":         ["Understand transformer architecture in depth.", "Discuss fine-tuning vs RAG trade-offs."],
    }
    return common + role_specific.get(role, [])


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_summary(parsed: dict, predicted_role: str) -> str:
    model = _get_model()
    if not model:
        return _fallback_summary({**parsed, "predicted_role": predicted_role})

    prompt = f"""
You are a professional resume coach. Given the following resume details, write a compelling 3-4 sentence professional summary.

Name: {parsed.get('name')}
Predicted Role: {predicted_role}
Skills: {', '.join(parsed.get('skills', [])[:15])}
Experience Snippets: {'; '.join(parsed.get('experience', [])[:3])}
Education: {'; '.join(parsed.get('education', [])[:2])}

Write only the summary paragraph. No headings.
"""
    return _safe_generate(model, prompt)


def generate_feedback(parsed: dict, ats_result: dict, predicted_role: str) -> list:
    model = _get_model()
    if not model:
        return _fallback_feedback(ats_result.get("total_score", 50))

    prompt = f"""
You are an expert ATS resume reviewer. Analyse this resume and provide exactly 6 specific, actionable improvement suggestions as a numbered list.

Predicted Role: {predicted_role}
ATS Score: {ats_result.get('total_score')}
Detected Skills: {', '.join(parsed.get('skills', []))}
Missing Skills: {', '.join(ats_result.get('missing_skills', []))}
Sections Present: {[k for k,v in ats_result.get('sections_present',{}).items() if v]}

Return ONLY a numbered list 1-6. Each item should be one clear sentence.
"""
    raw = _safe_generate(model, prompt)
    lines = [re.sub(r'^\d+[\.\)]\s*', '', l).strip() for l in raw.splitlines() if l.strip()]
    return [l for l in lines if l][:6] or _fallback_feedback(ats_result.get("total_score", 50))


def generate_interview_tips(predicted_role: str, skills: list) -> list:
    model = _get_model()
    if not model:
        return _fallback_interview_tips(predicted_role)

    prompt = f"""
You are a career coach preparing a candidate for a {predicted_role} interview.
Their skills include: {', '.join(skills[:10])}.

Provide exactly 5 specific, practical interview preparation tips as a numbered list.
Return ONLY the numbered list. Each tip should be one or two sentences.
"""
    raw = _safe_generate(model, prompt)
    lines = [re.sub(r'^\d+[\.\)]\s*', '', l).strip() for l in raw.splitlines() if l.strip()]
    return [l for l in lines if l][:5] or _fallback_interview_tips(predicted_role)
