# AI Resume Analyzer

A full-stack AI-powered resume analyzer built with Flask and Gemini AI.

## Features
- ATS Score with breakdown
- Skill detection across 100+ technologies
- Missing skills vs target role
- ML-based job role prediction
- Gemini AI-generated summary, feedback & interview tips
- Downloadable PDF report
- User authentication & history

## Quick Start

```bash
# 1. Clone / unzip the project
cd AI-Resume-Analyzer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env: add your GEMINI_API_KEY and a random SECRET_KEY

# 5. Train the ML model (one-time)
python model/train_model.py

# 6. Run the app
python app.py
```

Open https://resumeanalyzer.vinaysharmatech.xyz/ in your browser.

## Get a Gemini API Key
1. Go to https://aistudio.google.com/
2. Create a free API key
3. Paste it in your `.env` file as `GEMINI_API_KEY=...`

> **Note:** The app works without a Gemini key — it falls back to templated AI responses.

## Folder Structure
```
AI-Resume-Analyzer/
├── app.py                  # Flask application
├── requirements.txt
├── .env.example
├── database/               # SQLite DB (auto-created)
├── uploads/                # Uploaded PDFs
├── reports/                # Generated PDF reports
├── model/
│   ├── train_model.py      # Train ML model
│   └── job_role_model.pkl  # Saved model (after training)
├── utils/
│   ├── parser.py           # Resume text parsing
│   ├── ats.py              # ATS score calculation
│   ├── predictor.py        # Role prediction
│   ├── report_generator.py # PDF report (ReportLab)
│   └── gemini_helper.py    # Gemini AI integration
├── templates/              # Jinja2 HTML templates
├── static/css/style.css    # Dark premium CSS
├── static/js/app.js        # Frontend JavaScript
└── dataset/job_roles.csv   # Training data
```
