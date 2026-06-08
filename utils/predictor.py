"""
Job role predictor using the pre-trained sklearn pipeline.
Falls back to a rule-based heuristic if the model file is missing.
"""

import os
import pickle

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model', 'job_role_model.pkl')

_model = None


def _load_model():
    global _model
    if _model is None and os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            _model = pickle.load(f)
    return _model


# Rule-based fallback scores per role
ROLE_KEYWORDS = {
    "Frontend Developer":  ["html", "css", "javascript", "react", "angular", "vue", "figma", "svelte"],
    "Backend Developer":   ["django", "flask", "fastapi", "spring", "express", "laravel", "rails",
                            "postgresql", "mysql", "redis", "rest api"],
    "Full Stack Developer":["react", "node.js", "django", "flask", "javascript", "python",
                            "postgresql", "mongodb", "docker"],
    "Data Scientist":      ["pandas", "numpy", "matplotlib", "scikit-learn", "machine learning",
                            "statistics", "sql", "tableau", "r", "data analysis"],
    "AI Engineer":         ["pytorch", "tensorflow", "nlp", "deep learning", "langchain",
                            "transformers", "llm", "bert", "gpt", "embedding"],
}


def _rule_based(skills: list) -> str:
    lower = {s.lower() for s in skills}
    scores = {
        role: sum(1 for kw in kws if kw in lower)
        for role, kws in ROLE_KEYWORDS.items()
    }
    return max(scores, key=scores.get)


def predict_role(skills: list) -> dict:
    text  = " ".join(skills).lower()
    model = _load_model()

    if model:
        predicted = model.predict([text])[0]
        proba     = model.predict_proba([text])[0]
        classes   = model.classes_
        confidence = round(float(max(proba)) * 100, 1)
        top3 = sorted(
            [(cls, round(float(p)*100, 1)) for cls, p in zip(classes, proba)],
            key=lambda x: -x[1]
        )[:3]
    else:
        # Fallback: rule-based
        predicted  = _rule_based(skills)
        confidence = 75.0
        top3 = [(predicted, 75.0)]

    return {
        "predicted_role": predicted,
        "confidence":     confidence,
        "top_predictions": top3,
    }
