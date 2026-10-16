"""
backend/evaluator.py
─────────────────────
Evaluates sentiment and theme predictions against the held-out test set
(reviews with split == 'test').

Metrics produced
────────────────
Sentiment:
  • Accuracy
  • Per-class Precision / Recall / F1
  • Confusion matrix

Themes (per review, multi-label):
  • Exact-match accuracy
  • Average Jaccard similarity (intersection-over-union per review)
  • Failure cases (reviews where prediction diverges from ground truth)

Usage (standalone):
    python evaluate.py
    (see evaluate.py for the entry point)

Or programmatically:
    from backend.evaluator import Evaluator
    ev = Evaluator()
    report = ev.evaluate("data/reviews_dataset.csv")
    print(report["summary"])
"""

import os
import pandas as pd
from typing import Dict, List, Any

from .sentiment_analyzer import SentimentAnalyzer
from .theme_detector import ThemeDetector


class Evaluator:
    def __init__(
        self,
        sentiment_analyzer: SentimentAnalyzer = None,
        theme_detector: ThemeDetector = None,
    ):
        self.sa = sentiment_analyzer or SentimentAnalyzer()
        self.td = theme_detector or ThemeDetector()

    # ──────────────────────────────────────────────────────────────────────────
    def evaluate(self, dataset_path: str) -> Dict[str, Any]:
        """
        Run full evaluation on held-out test reviews.

        Parameters
        ----------
        dataset_path : path to reviews_dataset.csv

        Returns
        -------
        dict with keys:
            summary           : str (pretty-printed report)
            sentiment_accuracy: float
            sentiment_f1      : dict per class
            theme_jaccard     : float (mean Jaccard over test reviews)
            failure_cases     : list of dicts describing wrong predictions
            raw_results       : DataFrame with all predictions
        """
        df = pd.read_csv(dataset_path)
        test_df = df[df["split"] == "test"].copy().reset_index(drop=True)

        if test_df.empty:
            raise ValueError("No test reviews found (split == 'test').")

        # ── Run predictions ────────────────────────────────────────────────────
        sent_preds, sent_confidences, theme_preds = [], [], []
        for _, row in test_df.iterrows():
            text = row["review_text"]
            s_result = self.sa.analyze(text)
            t_result = self.td.detect_themes(text)
            sent_preds.append(s_result["label"])
            sent_confidences.append(s_result["confidence"])
            theme_preds.append([t["theme"] for t in t_result])

        test_df["pred_sentiment"] = sent_preds
        test_df["pred_confidence"] = sent_confidences
        test_df["pred_themes"] = [",".join(t) for t in theme_preds]
        test_df["sentiment_correct"] = (
            test_df["sentiment"] == test_df["pred_sentiment"]
        )

        # ── Sentiment metrics ──────────────────────────────────────────────────
        sent_accuracy = round(test_df["sentiment_correct"].mean(), 4)
        classes = ["positive", "negative", "neutral"]
        sent_f1 = self._per_class_metrics(
            test_df["sentiment"].tolist(),
            test_df["pred_sentiment"].tolist(),
            classes,
        )
        confusion = self._confusion_matrix(
            test_df["sentiment"].tolist(),
            test_df["pred_sentiment"].tolist(),
            classes,
        )

        # ── Theme metrics ──────────────────────────────────────────────────────
        jaccard_scores = []
        for _, row in test_df.iterrows():
            true_themes = set(t.strip() for t in row["themes"].split(","))
            pred_themes = set(row["pred_themes"].split(",")) if row["pred_themes"] else set()
            jaccard_scores.append(self._jaccard(true_themes, pred_themes))
        test_df["theme_jaccard"] = jaccard_scores
        mean_jaccard = round(sum(jaccard_scores) / len(jaccard_scores), 4)

        # ── Failure cases ──────────────────────────────────────────────────────
        failures = []
        for _, row in test_df.iterrows():
            if not row["sentiment_correct"]:
                failures.append({
                    "id": int(row["id"]),
                    "review": row["review_text"][:120] + "…",
                    "true_sentiment": row["sentiment"],
                    "pred_sentiment": row["pred_sentiment"],
                    "confidence": row["pred_confidence"],
                })

        # ── Build summary string ───────────────────────────────────────────────
        summary = self._build_summary(
            len(test_df), sent_accuracy, sent_f1, confusion,
            mean_jaccard, failures
        )

        return {
            "summary": summary,
            "sentiment_accuracy": sent_accuracy,
            "sentiment_f1": sent_f1,
            "theme_jaccard": mean_jaccard,
            "failure_cases": failures,
            "raw_results": test_df,
        }

    # ── Metrics helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _jaccard(set_a: set, set_b: set) -> float:
        if not set_a and not set_b:
            return 1.0
        union = set_a | set_b
        if not union:
            return 0.0
        return round(len(set_a & set_b) / len(union), 4)

    @staticmethod
    def _per_class_metrics(true: List, pred: List, classes: List) -> Dict:
        metrics = {}
        for cls in classes:
            tp = sum(1 for t, p in zip(true, pred) if t == cls and p == cls)
            fp = sum(1 for t, p in zip(true, pred) if t != cls and p == cls)
            fn = sum(1 for t, p in zip(true, pred) if t == cls and p != cls)
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1        = (2 * precision * recall / (precision + recall)
                         if (precision + recall) > 0 else 0.0)
            metrics[cls] = {
                "precision": round(precision, 3),
                "recall":    round(recall, 3),
                "f1":        round(f1, 3),
            }
        return metrics

    @staticmethod
    def _confusion_matrix(true: List, pred: List, classes: List) -> Dict:
        matrix = {c: {c2: 0 for c2 in classes} for c in classes}
        for t, p in zip(true, pred):
            if t in matrix and p in classes:
                matrix[t][p] += 1
        return matrix

    # ── Pretty print ───────────────────────────────────────────────────────────
    @staticmethod
    def _build_summary(
        n_test, accuracy, f1_dict, confusion, jaccard, failures
    ) -> str:
        lines = [
            "=" * 60,
            "  TRAVEL.PK SENTIMENT ANALYZER — EVALUATION REPORT",
            "=" * 60,
            f"\nTest set size : {n_test} reviews",
            f"Sentiment Accuracy : {accuracy*100:.1f}%",
            "",
            "Per-class Sentiment Metrics:",
            f"  {'Class':<12} {'Precision':>10} {'Recall':>8} {'F1':>6}",
            "  " + "-" * 38,
        ]
        for cls, m in f1_dict.items():
            lines.append(
                f"  {cls:<12} {m['precision']:>10.3f} {m['recall']:>8.3f} {m['f1']:>6.3f}"
            )

        lines += [
            "",
            "Confusion Matrix (rows=true, cols=pred):",
            f"  {'':10} {'positive':>10} {'negative':>10} {'neutral':>8}",
            "  " + "-" * 40,
        ]
        for true_cls in ["positive", "negative", "neutral"]:
            row = confusion.get(true_cls, {})
            lines.append(
                f"  {true_cls:<10} "
                f"{row.get('positive',0):>10} "
                f"{row.get('negative',0):>10} "
                f"{row.get('neutral',0):>8}"
            )

        lines += [
            "",
            f"Theme Detection — Mean Jaccard Similarity: {jaccard:.3f}",
            f"  (1.0 = perfect match, 0.0 = no overlap)",
            "",
            f"Failure Cases ({len(failures)} of {n_test}):",
        ]
        if failures:
            for fc in failures:
                lines.append(
                    f"  [ID {fc['id']}] True={fc['true_sentiment']} | "
                    f"Pred={fc['pred_sentiment']} (conf={fc['confidence']:.2f})"
                )
                lines.append(f"    \"{fc['review']}\"")
        else:
            lines.append("  None — perfect sentiment accuracy!")

        lines.append("=" * 60)
        return "\n".join(lines)
