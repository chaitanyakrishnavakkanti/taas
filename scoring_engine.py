CRITERIA_WEIGHTS = {
    "grammar_correctness": 30,
    "clarity_readability": 25,
    "sentence_structure": 20,
    "completeness": 15,
    "noise_reduction": 10,
}


CRITERIA_LABELS = {
    "grammar_correctness": "Grammar Correctness",
    "clarity_readability": "Clarity & Readability",
    "sentence_structure": "Sentence Structure",
    "completeness": "Completeness",
    "noise_reduction": "Noise Reduction",
}


_ALIASES = {
    "grammar": "grammar_correctness",
    "grammar_correctness": "grammar_correctness",
    "grammarCorrectness": "grammar_correctness",
    "clarity": "clarity_readability",
    "clarity_readability": "clarity_readability",
    "clarityReadability": "clarity_readability",
    "readability": "clarity_readability",
    "sentence_structure": "sentence_structure",
    "sentenceStructure": "sentence_structure",
    "structure": "sentence_structure",
    "completeness": "completeness",
    "meaning_preservation": "completeness",
    "meaningPreservation": "completeness",
    "noise_reduction": "noise_reduction",
    "noiseReduction": "noise_reduction",
    "filler_removal": "noise_reduction",
    "fillerRemoval": "noise_reduction",
}


def clamp_score(value, default=0):
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = default
    return max(0, min(100, score))


def normalize_metric_scores(raw_scores):
    raw_scores = raw_scores if isinstance(raw_scores, dict) else {}
    normalized = {key: 0 for key in CRITERIA_WEIGHTS}

    for raw_key, value in raw_scores.items():
        key = _ALIASES.get(str(raw_key).strip())
        if key:
            normalized[key] = clamp_score(value)

    return normalized


def calculate_confidence_score(metric_scores):
    normalized = normalize_metric_scores(metric_scores)
    weighted_total = 0.0

    for key, weight in CRITERIA_WEIGHTS.items():
        weighted_total += normalized[key] * (weight / 100.0)

    return clamp_score(weighted_total)


def missing_metric_issues(metric_scores):
    provided = set((metric_scores or {}).keys()) if isinstance(metric_scores, dict) else set()
    missing = []

    for key, label in CRITERIA_LABELS.items():
        aliases_for_key = {alias for alias, target in _ALIASES.items() if target == key}
        if key not in provided and not aliases_for_key.intersection(provided):
            missing.append(f"Validation model did not provide a {label} score.")

    return missing
