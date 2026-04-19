CRITICAL_KEYWORDS = (
    "meaning incorrect",
    "meaning changed",
    "meaning distorted",
    "missing content",
    "missing information",
    "hallucinated",
    "invented",
    "not preserved",
    "empty",
    "upstream error",
    "malformed speaker",
)


def has_critical_issue(issues=None, critical_issues=None):
    if critical_issues:
        return True

    text = " ".join(str(issue or "").lower() for issue in (issues or []))
    return any(keyword in text for keyword in CRITICAL_KEYWORDS)


def decide_verdict(confidence_score, issues=None, critical_issues=None):
    score = max(0, min(100, int(confidence_score or 0)))

    if has_critical_issue(issues=issues, critical_issues=critical_issues):
        return "fail"
    if score >= 85:
        return "pass"
    if score >= 60:
        return "review"
    return "fail"


def is_valid_verdict(verdict):
    return verdict == "pass"
