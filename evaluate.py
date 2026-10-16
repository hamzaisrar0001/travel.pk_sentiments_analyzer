"""
evaluate.py — CLI Evaluation Script
══════════════════════════════════════
Runs sentiment + theme evaluation on the 25 held-out test reviews
and prints a detailed report to the terminal.

Usage:
    python evaluate.py
    python evaluate.py --dataset data/reviews_dataset.csv
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from backend.sentiment_analyzer import SentimentAnalyzer
from backend.theme_detector import ThemeDetector
from backend.evaluator import Evaluator


def main():
    parser = argparse.ArgumentParser(description="Travel.pk Sentiment Analyzer — Evaluation")
    parser.add_argument(
        "--dataset",
        default=os.path.join("data", "reviews_dataset.csv"),
        help="Path to reviews_dataset.csv (default: data/reviews_dataset.csv)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(
            f"❌  Dataset not found: {args.dataset}\n"
            "    Run first:  python data/generate_dataset.py"
        )
        sys.exit(1)

    print("🔄 Loading models …")
    sa = SentimentAnalyzer()
    td = ThemeDetector()
    ev = Evaluator(sa, td)

    print(f"📊 Evaluating on held-out test set in: {args.dataset}\n")
    report = ev.evaluate(args.dataset)
    print(report["summary"])

    # Optionally save raw results
    out_path = "data/evaluation_results.csv"
    report["raw_results"].to_csv(out_path, index=False)
    print(f"\n📁 Raw results saved → {out_path}")


if __name__ == "__main__":
    main()
