"""
backend/theme_detector.py
──────────────────────────
Keyword-weighted theme detection for travel / hotel reviews.

Detects 5 themes:
    • Food
    • Cleanliness
    • Staff
    • Location
    • Value for Money

Each keyword carries a weight (1 = standard, 2 = strong indicator).
A theme score is the sum of matched keyword weights, normalised to [0, 1].
Themes above THRESHOLD are returned, sorted by confidence descending.

Usage:
    from backend.theme_detector import ThemeDetector
    td = ThemeDetector()
    themes = td.detect_themes("The food was great but the room was dirty.")
    # → [{'theme': 'Food', 'confidence': 0.82}, {'theme': 'Cleanliness', 'confidence': 0.74}]
"""

import re
import math
import os
from typing import List, Dict

# ── Default confidence threshold ──────────────────────────────────────────────
_DEFAULT_THRESHOLD = float(os.getenv("THEME_THRESHOLD", "0.15"))

# ── Keyword bank ──────────────────────────────────────────────────────────────
# Format: (keyword/phrase, weight)
# Phrases are matched as whole words / sequences.
THEME_KEYWORDS: Dict[str, List] = {
    "Food": [
        ("food", 2), ("meal", 2), ("breakfast", 2), ("lunch", 2), ("dinner", 2),
        ("buffet", 2), ("menu", 2), ("cuisine", 2), ("restaurant", 2),
        ("taste", 1), ("tasty", 2), ("delicious", 2), ("bland", 2), ("stale", 2),
        ("fresh", 1), ("cooked", 1), ("cooking", 1), ("chef", 2), ("dish", 1),
        ("dishes", 1), ("overcooked", 2), ("undercooked", 2), ("spicy", 1),
        ("flavour", 1), ("flavor", 1), ("portion", 1), ("portions", 1),
        ("inedible", 2), ("edible", 1), ("coffee", 1), ("tea", 1), ("juice", 1),
        ("snack", 1), ("halwa puri", 2), ("chapshuro", 2), ("biryani", 2),
        ("kebab", 2), ("kebabs", 2), ("naan", 2), ("roti", 2), ("curry", 2),
        ("bread", 1), ("eggs", 1), ("pastry", 1), ("pastries", 1), ("apricot", 1),
        ("dal", 2), ("rice", 1), ("water", 1), ("drinks", 1), ("bar", 1),
        ("dining", 2), ("cafe", 1), ("cafeteria", 1), ("snacks", 1),
        ("poisoning", 2), ("food poisoning", 2),
    ],
    "Cleanliness": [
        ("clean", 2), ("dirty", 2), ("filthy", 2), ("hygiene", 2), ("hygienic", 2),
        ("spotless", 2), ("immaculate", 2), ("tidy", 2), ("messy", 2),
        ("dust", 1), ("dusty", 2), ("mold", 2), ("mould", 2), ("stain", 2),
        ("stains", 2), ("stained", 2), ("smell", 1), ("smelly", 2), ("odour", 2),
        ("odor", 2), ("bathroom", 2), ("restroom", 1), ("toilet", 2), ("shower", 1),
        ("cockroach", 2), ("cockroaches", 2), ("insects", 2), ("bugs", 2),
        ("rats", 2), ("pest", 2), ("pests", 2), ("sewage", 2), ("mop", 1),
        ("swept", 1), ("linen", 1), ("sheets", 2), ("towels", 2), ("maintained", 1),
        ("maintenance", 1), ("algae", 2), ("damp", 2), ("dampness", 2),
        ("wet", 1), ("hair", 1), ("used toiletries", 2), ("cracked", 1),
        ("broken tiles", 1), ("fresh sheets", 2), ("well-maintained", 2),
        ("pool", 1), ("garbage", 2), ("rubbish", 2), ("trash", 2),
        ("room", 1), ("rooms", 1), ("dirty room", 2), ("clean room", 2),
        ("not cleaned", 2), ("unclean", 2), ("sanitized", 2), ("sanitised", 2),
        ("spotlessly", 2), ("immaculately", 2), ("well maintained", 2),
        ("poorly maintained", 2), ("unhygienic", 2),
    ],
    "Staff": [
        ("staff", 2), ("service", 2), ("receptionist", 2), ("front desk", 2),
        ("manager", 1), ("waiter", 2), ("waitress", 2), ("host", 1), ("hosts", 1),
        ("caretaker", 2), ("helpful", 2), ("rude", 2), ("friendly", 2),
        ("polite", 2), ("courteous", 2), ("professional", 2), ("attentive", 2),
        ("dismissive", 2), ("ignored", 2), ("unprofessional", 2), ("knowledgeable", 2),
        ("hospitable", 2), ("warm", 1), ("welcoming", 2), ("responsive", 2),
        ("check-in", 2), ("check in", 2), ("checkout", 2), ("check out", 2),
        ("room service", 2), ("concierge", 2), ("guide", 1), ("guides", 1),
        ("personnel", 2), ("team", 1), ("crew", 1), ("unresponsive", 2),
        ("assistance", 1), ("helped", 1), ("unhelpful", 2), ("kind", 1),
        ("unkind", 2), ("aggressive", 2), ("slow service", 2), ("quick service", 2),
        ("trained", 1), ("untrained", 2), ("personal touch", 2),
    ],
    "Location": [
        ("location", 2), ("located", 2), ("situated", 2), ("central", 2),
        ("nearby", 1), ("access", 1), ("transport", 1), ("view", 1), ("views", 1),
        ("surroundings", 1), ("area", 1), ("distance", 1), ("proximity", 2),
        ("airport", 1), ("highway", 1), ("road", 1), ("street", 1),
        ("city center", 2), ("city centre", 2), ("downtown", 2),
        ("safe", 1), ("unsafe", 2), ("dangerous", 2), ("noisy", 1), ("quiet", 1),
        ("peaceful", 1), ("valley", 1), ("river", 1), ("mountain", 1),
        ("hill", 1), ("sea view", 2), ("seaview", 2), ("panoramic", 2),
        ("scenic", 2), ("remote", 1), ("far from", 2), ("near to", 1),
        ("walking distance", 2), ("diplomatic enclave", 2), ("mall road", 2),
        ("clifton", 2), ("gulberg", 2), ("blue area", 2), ("f-6", 2),
        ("mm alam road", 2), ("johar town", 2), ("dha", 2), ("saddar", 2),
    ],
    "Value for Money": [
        ("price", 2), ("prices", 2), ("expensive", 2), ("affordable", 2),
        ("value", 2), ("overpriced", 2), ("cheap", 2), ("cost", 1), ("fee", 1),
        ("worth", 2), ("not worth", 2), ("money", 1), ("budget", 1),
        ("luxury", 1), ("premium", 1), ("reasonable", 2), ("unreasonable", 2),
        ("rip-off", 2), ("rip off", 2), ("robbery", 2), ("hidden fees", 2),
        ("charged", 1), ("overcharged", 2), ("pricing", 2), ("rate", 1),
        ("rates", 1), ("tariff", 1), ("per night", 2), ("value for money", 2),
        ("good deal", 2), ("bad deal", 2), ("recommend", 1), ("refund", 2),
        ("bang for", 2), ("five stars", 1), ("5 stars", 1), ("mediocre", 1),
    ],
}

# Precompile max possible scores for normalisation
_MAX_SCORES: Dict[str, float] = {}
for _theme, _kws in THEME_KEYWORDS.items():
    # Take top-10 keywords (realistic upper bound)
    top10 = sorted([w for _, w in _kws], reverse=True)[:10]
    _MAX_SCORES[_theme] = float(sum(top10)) if top10 else 1.0


class ThemeDetector:
    """
    Keyword-weighted theme detector for hotel / travel reviews.
    Fast, offline, and interpretable.
    """

    def __init__(self, threshold: float = _DEFAULT_THRESHOLD):
        self.threshold = threshold
        self._patterns: Dict[str, List] = {}
        self._build_patterns()

    # ── Pattern building ───────────────────────────────────────────────────────
    def _build_patterns(self):
        for theme, keywords in THEME_KEYWORDS.items():
            compiled = []
            for kw, weight in keywords:
                # Word-boundary match, case-insensitive
                pattern = re.compile(
                    r"\b" + re.escape(kw) + r"\b", re.IGNORECASE
                )
                compiled.append((pattern, weight))
            self._patterns[theme] = compiled

    # ── Core API ───────────────────────────────────────────────────────────────
    def detect_themes(self, text: str) -> List[Dict]:
        """
        Detect themes present in review text.

        Returns
        -------
        list of dicts sorted by confidence descending:
            [{'theme': str, 'confidence': float, 'matched_keywords': list}, ...]
        """
        text = text.strip()
        results = []

        for theme, compiled_patterns in self._patterns.items():
            raw_score = 0.0
            matched = []
            for pattern, weight in compiled_patterns:
                matches = pattern.findall(text)
                if matches:
                    raw_score += weight * len(matches)
                    matched.append(matches[0].lower())

            # Sigmoid-like normalisation so score feels natural (0-1)
            normalised = self._normalise(raw_score, _MAX_SCORES[theme])

            if normalised >= self.threshold:
                results.append({
                    "theme": theme,
                    "confidence": round(normalised, 3),
                    "matched_keywords": list(set(matched)),
                })

        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

    def detect_themes_batch(self, texts: List[str]) -> List[List[Dict]]:
        """Detect themes for a list of texts."""
        return [self.detect_themes(t) for t in texts]

    # ── Helpers ────────────────────────────────────────────────────────────────
    @staticmethod
    def _normalise(raw: float, max_score: float) -> float:
        """
        Map raw keyword score to (0, 1).
        Uses sqrt normalisation so a single strong keyword still produces a
        meaningful score (avoids the sigmoid's harsh low-end compression).
        """
        if raw <= 0:
            return 0.0
        # sqrt normalisation: score = sqrt(raw / max_score), capped at 1.0
        return round(min(math.sqrt(raw / max_score), 1.0), 4)

    def theme_names(self) -> List[str]:
        """Return list of all supported theme names."""
        return list(THEME_KEYWORDS.keys())
