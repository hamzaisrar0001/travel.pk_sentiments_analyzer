"""
backend/sentiment_analyzer.py
──────────────────────────────
Sentiment analysis module.

Primary  : cardiffnlp/twitter-roberta-base-sentiment-latest (HuggingFace)
           → labels: positive / neutral / negative + confidence score
Fallback  : VADER (vaderSentiment) – runs offline with no downloads needed

Usage:
    from backend.sentiment_analyzer import SentimentAnalyzer
    sa = SentimentAnalyzer()
    result = sa.analyze("The hotel was absolutely amazing!")
    # → {'label': 'positive', 'confidence': 0.97, 'scores': {...}}
"""

import os
import logging
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Label normalisation map ────────────────────────────────────────────────────
_LABEL_MAP = {
    # cardiffnlp model returns these
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    # some HF models return LABEL_0/1/2
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}


class SentimentAnalyzer:
    """
    Wraps a HuggingFace transformer model for 3-class sentiment analysis.
    Falls back to VADER if the transformer model cannot be loaded.
    """

    def __init__(self, model_name: str = None, use_gpu: bool = False):
        self.model_name = model_name or os.getenv(
            "SENTIMENT_MODEL",
            "cardiffnlp/twitter-roberta-base-sentiment-latest",
        )
        self.device = 0 if use_gpu else -1
        self._pipeline = None
        self._vader = None
        self._load_model()

    # ── Loading ────────────────────────────────────────────────────────────────
    def _load_model(self):
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            logger.info(f"Loading HuggingFace model: {self.model_name} …")
            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer,
                device=self.device,
                top_k=None,          # return all class scores
                truncation=True,
                max_length=512,
            )
            logger.info("✅  HuggingFace model loaded successfully.")
        except Exception as e:
            logger.warning(f"⚠️  Could not load transformer model ({e}). Using VADER fallback.")
            self._load_vader()

    def _load_vader(self):
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            self._vader = SentimentIntensityAnalyzer()
            logger.info("✅  VADER fallback loaded.")
        except ImportError:
            logger.error("❌  Neither transformers nor vaderSentiment available. Install one of them.")

    # ── Core API ───────────────────────────────────────────────────────────────
    def analyze(self, text: str) -> Dict:
        """
        Analyze the sentiment of a single review.

        Returns
        -------
        dict with keys:
            label      : 'positive' | 'neutral' | 'negative'
            confidence : float  (0.0 – 1.0)
            scores     : {'positive': float, 'neutral': float, 'negative': float}
        """
        text = text.strip()
        if not text:
            return {"label": "neutral", "confidence": 0.0, "scores": {}}

        if self._pipeline:
            return self._analyze_transformer(text)
        elif self._vader:
            return self._analyze_vader(text)
        else:
            raise RuntimeError("No sentiment model available. Check your installation.")

    def analyze_batch(self, texts: list) -> list:
        """Analyze a list of texts, returns list of result dicts."""
        return [self.analyze(t) for t in texts]

    # ── Internal helpers ───────────────────────────────────────────────────────
    def _analyze_transformer(self, text: str) -> Dict:
        try:
            results = self._pipeline(text)[0]   # list of {label, score} dicts
            # Normalise labels
            scores = {}
            for item in results:
                label = _LABEL_MAP.get(item["label"], item["label"].lower())
                scores[label] = round(item["score"], 4)

            # Ensure all three keys exist
            for k in ("positive", "neutral", "negative"):
                scores.setdefault(k, 0.0)

            best_label = max(scores, key=scores.__getitem__)
            confidence = round(scores[best_label], 4)

            # ── Ensemble correction for neutral reviews ────────────────────
            # RoBERTa (trained on tweets) over-predicts "positive" for mildly
            # positive neutral reviews. When the transformer says "positive"
            # with confidence < 0.90, cross-check with VADER compound score.
            # If VADER sees a near-neutral compound (-0.2 to 0.4) AND the
            # transformer neutral score is non-trivial, override to neutral.
            if best_label == "positive" and confidence < 0.90:
                vader_result = self._get_vader_scores(text)
                if vader_result is not None:
                    compound = vader_result["compound"]
                    transformer_neutral = scores.get("neutral", 0.0)
                    if -0.2 <= compound <= 0.35 and transformer_neutral > 0.08:
                        best_label = "neutral"
                        # blend confidence from both
                        confidence = round(
                            0.5 * scores["neutral"] + 0.5 * max(0.0, 1 - abs(compound)), 4
                        )

            return {"label": best_label, "confidence": confidence, "scores": scores}
        except Exception as e:
            logger.warning(f"Transformer inference failed ({e}), falling back to VADER.")
            if self._vader is None:
                self._load_vader()
            return self._analyze_vader(text)

    def _get_vader_scores(self, text: str):
        """Return raw VADER polarity scores dict, or None if VADER unavailable."""
        try:
            if self._vader is None:
                self._load_vader()
            if self._vader is None:
                return None
            return self._vader.polarity_scores(text)
        except Exception:
            return None

    def _analyze_vader(self, text: str) -> Dict:
        scores_raw = self._vader.polarity_scores(text)
        compound = scores_raw["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        # Map VADER pos/neg/neu to our confidence scale
        pos = round(scores_raw["pos"], 4)
        neg = round(scores_raw["neg"], 4)
        neu = round(scores_raw["neu"], 4)

        scores = {"positive": pos, "negative": neg, "neutral": neu}
        confidence = round(max(pos, neg, neu), 4)
        return {"label": label, "confidence": confidence, "scores": scores}

    # ── Convenience ───────────────────────────────────────────────────────────
    def is_ready(self) -> bool:
        return self._pipeline is not None or self._vader is not None
