"""
app.py — Travel.pk Sentiment & Theme Analyzer
═══════════════════════════════════════════════
Streamlit web app.

Run:
    streamlit run app.py
"""

import os
import sys
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Ensure project root is in path ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from backend.sentiment_analyzer import SentimentAnalyzer
from backend.theme_detector import ThemeDetector

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Travel.pk Sentiment Analyzer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a6e3c;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        margin-top: 0;
    }
    .sentiment-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 4px;
    }
    .positive  { background-color: #d4edda; color: #155724; }
    .negative  { background-color: #f8d7da; color: #721c24; }
    .neutral   { background-color: #fff3cd; color: #856404; }
    .theme-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        background-color: #e8f4fd;
        color: #1565c0;
        font-size: 0.88rem;
        margin: 2px;
        border: 1px solid #90caf9;
    }
    .metric-box {
        background: #f8f9fa;
        border-left: 4px solid #1a6e3c;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Cached model loading ───────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🔄 Loading AI models — first run takes ~1 min …")
def load_models():
    sa = SentimentAnalyzer()
    td = ThemeDetector()
    return sa, td


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/"
        "Flag_of_Pakistan.svg/320px-Flag_of_Pakistan.svg.png",
        width=80,
    )
    st.markdown("## ✈️ Travel.pk Analyzer")
    st.markdown("*Hotel & Destination Review Intelligence*")
    st.divider()

    page = st.radio(
        "Navigate",
        ["🔍 Single Review", "📊 Bulk CSV Analysis", "📋 About & Evaluation"],
        index=0,
    )

    st.divider()
    st.markdown("**Themes Detected:**")
    themes_list = ["🍽️ Food", "🧹 Cleanliness", "👤 Staff", "📍 Location", "💰 Value for Money"]
    for t in themes_list:
        st.markdown(f"- {t}")

    st.divider()
    st.caption("Travel.pk — TechAbout's OTA for Pakistan")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="main-header">✈️ Travel.pk Review Sentiment & Theme Analyzer</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-header">AI-powered analysis of hotel and travel destination reviews in Pakistan</p>',
    unsafe_allow_html=True,
)
st.divider()

# ── Load models ───────────────────────────────────────────────────────────────
try:
    sa, td = load_models()
    model_ok = True
except Exception as e:
    st.error(f"Model loading failed: {e}")
    model_ok = False


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 1 — Single Review Analysis                            ║
# ╚══════════════════════════════════════════════════════════════╝
if page == "🔍 Single Review":
    st.subheader("🔍 Analyze a Single Review")

    review_text = st.text_area(
        "Paste your review below",
        height=160,
        placeholder=(
            "e.g. The Pearl Continental Lahore exceeded all expectations. "
            "The room was spotless, staff incredibly helpful and the food at the "
            "rooftop restaurant was outstanding …"
        ),
    )

    col_btn, col_clear = st.columns([1, 4])
    with col_btn:
        analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear"):
            st.rerun()

    if analyze_btn:
        if not review_text.strip():
            st.warning("⚠️ Please enter a review text first.")
        elif not model_ok:
            st.error("Models not loaded — check installation.")
        else:
            with st.spinner("Analyzing …"):
                s_result = sa.analyze(review_text)
                t_result = td.detect_themes(review_text)

            # ── Sentiment result ───────────────────────────────────────────────
            label = s_result["label"]
            conf  = s_result["confidence"]
            scores = s_result.get("scores", {})

            emoji_map = {"positive": "😊", "negative": "😟", "neutral": "😐"}
            st.markdown("---")
            st.markdown("### 📌 Sentiment Analysis Result")

            r1, r2 = st.columns([1, 2])
            with r1:
                badge_html = (
                    f'<span class="sentiment-badge {label}">'
                    f'{emoji_map.get(label, "")} {label.upper()}</span>'
                )
                st.markdown(badge_html, unsafe_allow_html=True)
                st.metric("Confidence Score", f"{conf*100:.1f}%")

            with r2:
                if scores:
                    score_df = pd.DataFrame(
                        [{"Sentiment": k.capitalize(), "Score": v}
                         for k, v in scores.items()]
                    )
                    fig = px.bar(
                        score_df,
                        x="Sentiment", y="Score",
                        color="Sentiment",
                        color_discrete_map={
                            "Positive": "#28a745",
                            "Negative": "#dc3545",
                            "Neutral":  "#ffc107",
                        },
                        title="Confidence Scores",
                        height=250,
                    )
                    fig.update_layout(showlegend=False, margin=dict(t=40, b=0))
                    fig.update_yaxes(range=[0, 1])
                    st.plotly_chart(fig, use_container_width=True)

            # ── Theme result ───────────────────────────────────────────────────
            st.markdown("### 🏷️ Themes Detected")
            if t_result:
                theme_html = ""
                for t in t_result:
                    theme_html += (
                        f'<span class="theme-pill">'
                        f'{t["theme"]} ({t["confidence"]*100:.0f}%)</span> '
                    )
                st.markdown(theme_html, unsafe_allow_html=True)

                # Theme confidence bar chart
                theme_df = pd.DataFrame(t_result)
                fig2 = px.bar(
                    theme_df,
                    x="confidence", y="theme",
                    orientation="h",
                    color="confidence",
                    color_continuous_scale="teal",
                    title="Theme Confidence Scores",
                    height=max(200, len(t_result) * 55),
                    labels={"confidence": "Confidence", "theme": "Theme"},
                )
                fig2.update_layout(
                    margin=dict(t=40, b=0),
                    coloraxis_showscale=False,
                )
                fig2.update_xaxes(range=[0, 1])
                st.plotly_chart(fig2, use_container_width=True)

                # Keywords
                with st.expander("🔎 Keywords that triggered each theme"):
                    for t in t_result:
                        kws = t.get("matched_keywords", [])
                        st.markdown(
                            f"**{t['theme']}**: `{'`, `'.join(kws) if kws else 'N/A'}`"
                        )
            else:
                st.info("No specific themes detected in this review.")


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 2 — Bulk CSV Analysis                                 ║
# ╚══════════════════════════════════════════════════════════════╝
elif page == "📊 Bulk CSV Analysis":
    st.subheader("📊 Bulk CSV Review Analysis")

    st.info(
        "Upload a CSV file with a column named **`review_text`** "
        "(or any column — you can choose it below). "
        "The app will add `pred_sentiment`, `confidence`, and `pred_themes` columns."
    )

    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        try:
            df_raw = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
            st.stop()

        st.success(f"✅ Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns.")
        st.dataframe(df_raw.head(5), use_container_width=True)

        # Column selection
        text_col = st.selectbox(
            "Which column contains the review text?",
            options=df_raw.columns.tolist(),
            index=df_raw.columns.tolist().index("review_text")
            if "review_text" in df_raw.columns
            else 0,
        )

        if st.button("🚀 Analyze All Reviews", type="primary"):
            if not model_ok:
                st.error("Models not loaded.")
            else:
                texts = df_raw[text_col].fillna("").astype(str).tolist()
                progress = st.progress(0, text="Analyzing reviews …")
                sentiments, confidences, themes_list_out = [], [], []

                for i, text in enumerate(texts):
                    s = sa.analyze(text)
                    t = td.detect_themes(text)
                    sentiments.append(s["label"])
                    confidences.append(round(s["confidence"], 3))
                    themes_list_out.append(", ".join(x["theme"] for x in t))
                    progress.progress((i + 1) / len(texts),
                                      text=f"Analyzing {i+1}/{len(texts)} …")

                progress.empty()
                df_out = df_raw.copy()
                df_out["pred_sentiment"] = sentiments
                df_out["confidence"] = confidences
                df_out["pred_themes"] = themes_list_out

                st.success("✅ Analysis complete!")

                # ── Summary charts ─────────────────────────────────────────────
                c1, c2 = st.columns(2)
                with c1:
                    sent_counts = pd.Series(sentiments).value_counts().reset_index()
                    sent_counts.columns = ["Sentiment", "Count"]
                    fig_pie = px.pie(
                        sent_counts, names="Sentiment", values="Count",
                        color="Sentiment",
                        color_discrete_map={
                            "positive": "#28a745",
                            "negative": "#dc3545",
                            "neutral":  "#ffc107",
                        },
                        title="Sentiment Distribution",
                        hole=0.4,
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with c2:
                    theme_counter = {}
                    for t_str in themes_list_out:
                        for t in t_str.split(", "):
                            t = t.strip()
                            if t:
                                theme_counter[t] = theme_counter.get(t, 0) + 1
                    if theme_counter:
                        t_df = pd.DataFrame(
                            sorted(theme_counter.items(), key=lambda x: -x[1]),
                            columns=["Theme", "Count"]
                        )
                        fig_bar = px.bar(
                            t_df, x="Count", y="Theme", orientation="h",
                            color="Count", color_continuous_scale="teal",
                            title="Theme Frequency",
                        )
                        fig_bar.update_layout(coloraxis_showscale=False)
                        st.plotly_chart(fig_bar, use_container_width=True)

                # ── Results table ──────────────────────────────────────────────
                st.markdown("### 📋 Detailed Results")

                def _color_sentiment(val):
                    colors = {
                        "positive": "background-color: #d4edda",
                        "negative": "background-color: #f8d7da",
                        "neutral":  "background-color: #fff3cd",
                    }
                    return colors.get(val, "")

                st.dataframe(
                    df_out.style.map(_color_sentiment, subset=["pred_sentiment"]),
                    use_container_width=True,
                    height=400,
                )

                # ── Download button ────────────────────────────────────────────
                csv_bytes = df_out.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Results CSV",
                    data=csv_bytes,
                    file_name="sentiment_results.csv",
                    mime="text/csv",
                )


# ╔══════════════════════════════════════════════════════════════╗
# ║  PAGE 3 — About & Evaluation                                ║
# ╚══════════════════════════════════════════════════════════════╝
elif page == "📋 About & Evaluation":
    st.subheader("📋 About This Project")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
**Project:** Travel.pk Review Sentiment & Theme Analyzer

**Task:** ZR-26-00753 (TechAbout-Tasks) — AI/ML Engineer, Task 6

**Objective:** Build a tool that reads hotel or destination reviews
and reports whether each review is positive, negative, or neutral,
along with the main themes (Food, Cleanliness, Staff, Location, Value for Money).

**Dataset:**
- 125 reviews (100 train + 25 held-out test)
- Simulated, original text, fully documented
- See `data/data_sources.md` for full details

**Sentiment Model:**
- Primary: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- Fallback: VADER (offline, no internet needed)

**Theme Detection:**
- Keyword-weighted scoring with sigmoid normalisation
- 5 themes: Food, Cleanliness, Staff, Location, Value for Money
""")
    with col2:
        st.markdown("""
**Architecture:**
```
review_text
    │
    ├─→ SentimentAnalyzer
    │       └─→ {label, confidence, scores}
    │
    └─→ ThemeDetector
            └─→ [{theme, confidence, keywords}, ...]
```

**Files:**
```
travel.pk_sentiment_analyser/
├── app.py              ← Streamlit UI
├── evaluate.py         ← CLI evaluation script
├── backend/
│   ├── sentiment_analyzer.py
│   ├── theme_detector.py
│   └── evaluator.py
├── data/
│   ├── reviews_dataset.csv
│   └── data_sources.md
├── requirements.txt
└── README.md
```
""")

    st.divider()
    st.subheader("🧪 Run Evaluation on 25 Held-Out Reviews")
    st.markdown(
        "Click the button to evaluate the model on the **25 held-out test reviews** "
        "(not used during model selection or tuning)."
    )

    dataset_path = os.path.join(os.path.dirname(__file__), "data", "reviews_dataset.csv")

    if st.button("▶️ Run Evaluation", type="primary"):
        if not os.path.exists(dataset_path):
            st.error(
                f"Dataset not found at `{dataset_path}`. "
                "Run `python data/generate_dataset.py` first."
            )
        elif not model_ok:
            st.error("Models not loaded.")
        else:
            with st.spinner("Evaluating on held-out test set …"):
                from backend.evaluator import Evaluator
                ev = Evaluator(sa, td)
                report = ev.evaluate(dataset_path)

            st.success(
                f"✅ Sentiment Accuracy: **{report['sentiment_accuracy']*100:.1f}%** | "
                f"Theme Jaccard: **{report['theme_jaccard']:.3f}**"
            )

            # Summary text
            st.code(report["summary"], language="text")

            # Results table
            st.markdown("#### 📄 Full Test Results")
            raw = report["raw_results"]

            def _color_correct(val):
                return "background-color: #d4edda" if val else "background-color: #f8d7da"

            display_cols = [
                "id", "review_text", "sentiment", "pred_sentiment",
                "pred_confidence", "pred_themes", "theme_jaccard", "sentiment_correct"
            ]
            display_cols = [c for c in display_cols if c in raw.columns]
            st.dataframe(
                raw[display_cols].style.map(
                    _color_correct, subset=["sentiment_correct"]
                ),
                use_container_width=True,
                height=500,
            )

            # Failure cases
            if report["failure_cases"]:
                st.markdown("#### ❌ Failure Cases")
                for fc in report["failure_cases"]:
                    st.markdown(
                        f"**[ID {fc['id']}]** True: `{fc['true_sentiment']}` → "
                        f"Predicted: `{fc['pred_sentiment']}` (conf: {fc['confidence']:.2f})  \n"
                        f"> {fc['review']}"
                    )
            else:
                st.balloons()
                st.success("🎉 No failure cases — perfect sentiment accuracy on the test set!")
