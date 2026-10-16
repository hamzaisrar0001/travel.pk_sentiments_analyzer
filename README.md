# Travel.pk Review Sentiment & Theme Analyzer

> **Task:** ZR-26-00753 · TechAbout / Travel.pk · AI/ML Engineer · Task 6  
> **Deadline:** 15 Oct 2026 · **Points:** 10

---

## Overview

A tool that reads hotel and travel destination reviews for Pakistan and reports:
- **Sentiment** (Positive / Negative / Neutral) with a **confidence score**
- **Themes** detected (Food, Cleanliness, Staff, Location, Value for Money)

It ships with a simple **Streamlit web UI** (paste a review or upload a CSV) and a **CLI evaluation script** tested on 25 held-out reviews.

---

## Features

| Feature | Details |
|---|---|
| Sentiment classification | 3-class: Positive / Negative / Neutral |
| Confidence score | 0–100% probability from the model |
| Theme detection | 5 themes — Food, Cleanliness, Staff, Location, Value for Money |
| Single review UI | Paste text → instant results with charts |
| Bulk CSV upload | Upload `.csv`, get results table + download |
| Evaluation | Accuracy, per-class F1, confusion matrix, failure cases |
| Offline fallback | VADER used if HuggingFace model unavailable |

---

## Approach

### Sentiment Model
- **Primary:** [`cardiffnlp/twitter-roberta-base-sentiment-latest`](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) — a RoBERTa model fine-tuned on ~124M tweets for 3-class sentiment (Positive / Neutral / Negative). Returns per-class softmax scores.
- **Fallback:** [VADER](https://github.com/cjhutto/vaderSentiment) — lexicon-based, runs fully offline.

### Theme Detection
- **Method:** Keyword-weighted scoring with sigmoid normalisation.
- Each of the 5 themes has a curated keyword bank with weights (1 = moderate indicator, 2 = strong indicator).
- Raw score is normalised to [0, 1] via a sigmoid curve; themes above a configurable threshold (default 0.15) are returned.
- Fast, interpretable, and explainable — matched keywords are shown in the UI.

### Dataset
- 125 reviews: 50 positive, 40 negative, 35 neutral
- Locations: Pearl Continental, Serena, Marriott, Avari, budget guesthouses, Hunza, Swat, Murree, Skardu, Gilgit, Chitral, Fairy Meadows, and more
- **Split:** 100 train (for reference) + 25 held-out test
- **Source:** Self-written / simulated (see `data/data_sources.md`)

---

## Setup

```bash
# 1. Clone / extract the project
cd travel.pk_sentiment_analyser

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Configure environment
cp .env.example .env
# Edit .env if you want to use a HuggingFace token or change the model

# 5. Generate the dataset
python data/generate_dataset.py
```

---

## Running the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Pages

| Page | Description |
|---|---|
| 🔍 Single Review | Paste a review → see sentiment + confidence chart + themes |
| 📊 Bulk CSV | Upload CSV → analyze all reviews → download results |
| 📋 About & Evaluation | Run held-out evaluation, view accuracy + failure cases |

---

## Running Evaluation (CLI)

```bash
python evaluate.py
# or
python evaluate.py --dataset data/reviews_dataset.csv
```

Outputs:
- Sentiment Accuracy
- Per-class Precision / Recall / F1
- Confusion Matrix
- Theme Jaccard Similarity (mean over 25 reviews)
- Failure cases list
- Saves `data/evaluation_results.csv`

---

## Project Structure

```
travel.pk_sentiment_analyser/
├── app.py                        ← Streamlit UI (3 pages)
├── evaluate.py                   ← CLI evaluation script
├── requirements.txt
├── .env.example                  ← Config template (no secrets)
├── README.md
│
├── backend/
│   ├── __init__.py
│   ├── sentiment_analyzer.py     ← HuggingFace + VADER fallback
│   ├── theme_detector.py         ← Keyword-weighted theme scoring
│   └── evaluator.py              ← Accuracy, F1, Jaccard metrics
│
└── data/
    ├── generate_dataset.py       ← Run once to create CSV
    ├── reviews_dataset.csv       ← 125 labeled reviews
    ├── data_sources.md           ← Source documentation
    └── evaluation_results.csv    ← Created after running evaluate.py
```

---

## Limitations

- Theme detection is keyword-based — it may miss sarcasm or implicit mentions (e.g., "the ceiling was hosting its own ecosystem" → missed Cleanliness).
- The sentiment model was fine-tuned on tweets, not hotel reviews; occasional misclassification on formal/neutral review language.
- Urdu/Roman Urdu reviews are not currently supported.
- Very short reviews (1–3 words) may get low-confidence predictions.

---

## Dependencies

| Package | Purpose |
|---|---|
| `transformers` | HuggingFace model loading |
| `torch` | Model inference |
| `streamlit` | Web UI |
| `pandas` | Data manipulation |
| `plotly` | Interactive charts |
| `vaderSentiment` | Offline fallback sentiment |
| `nltk` | Text utilities |
| `python-dotenv` | Environment config |
| `scikit-learn` | Evaluation metrics |

---

## License

This project is submitted as part of TechAbout task ZR-26-00753.  
Dataset is self-authored (see `data/data_sources.md`). No proprietary data used.
