import re


FILLER_TERMS = (
    "um",
    "uh",
    "erm",
    "ah",
    "like",
    "actually",
    "basically",
    "you know",
    "sort of",
    "kind of",
    "i mean",
)

FILLER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(term) for term in FILLER_TERMS) + r")\b",
    re.IGNORECASE,
)


def detect_fillers(text):
    matches = FILLER_PATTERN.findall(text or "")
    counts = {}
    for match in matches:
        key = match.lower()
        counts[key] = counts.get(key, 0) + 1
    return {"filler_count": len(matches), "fillers": counts}
