"""
Train a job role prediction model using TF-IDF + Logistic Regression.
Run this script once to generate job_role_model.pkl
"""

import pandas as pd
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Load dataset ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(BASE, '..', 'dataset', 'job_roles.csv')

df = pd.read_csv(DATASET, header=None,
                 names=[f'skill_{i}' for i in range(9)] + ['role'])

# Combine skill columns into one text blob
df['text'] = df[[c for c in df.columns if c != 'role']].apply(
    lambda r: ' '.join(r.dropna().astype(str)), axis=1
)

X = df['text']
y = df['role']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Build pipeline ────────────────────────────────────────────────────────────
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
    ('clf',   LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
])

pipeline.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────
preds = pipeline.predict(X_test)
print("=== Classification Report ===")
print(classification_report(y_test, preds))

# ── Save model ────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(BASE, 'job_role_model.pkl')
with open(MODEL_PATH, 'wb') as f:
    pickle.dump(pipeline, f)

print(f"\n✅ Model saved to {MODEL_PATH}")
