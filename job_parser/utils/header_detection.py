"""Heuristics to detect and normalize section headers within job postings."""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Tuple


HEADER_PATTERN = re.compile(
    r"^(?P<prefix>[◆■□●★☆◇▼▶▶︎]+)?\s*[\[【]?(?P<core>[^\]】]+)[\]】]?\s*[：:]*\s*(?P<inline>.+)?$"
)
INLINE_SPLIT_PATTERN = re.compile(r"(?P<header>[^：:]+)[：:]\s*(?P<body>.+)")
PUNCTUATION_TRIMMER = re.compile(r"^[\-‐−―・\s]+|[\-‐−―・\s]+$")

# Target fields to map high-confidence headers when building the top-level JSON
CANONICAL_FIELDS = {
    "job_title": ["職種", "募集職種", "ポジション", "タイトル"],
    "company": ["会社名", "企業名", "社名", "運営"],
    "salary": ["給与", "給料", "報酬", "年収", "月給", "時給"],
}


@dataclass
class HeaderCandidate:
    index: int
    title: str
    inline_content: str = ""
    score: float = 0.0


def _normalize_title(title: str) -> str:
    title = title.strip()
    title = PUNCTUATION_TRIMMER.sub("", title)
    return title


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _looks_like_header(line: str) -> Tuple[bool, float, str, str]:
    """Return whether line is a header and include a heuristic score."""
    stripped = line.strip()
    if not stripped:
        return False, 0.0, "", ""
    if len(stripped) > 50:
        return False, 0.0, "", ""

    inline_match = INLINE_SPLIT_PATTERN.match(stripped)
    if inline_match:
        header = _normalize_title(inline_match.group("header"))
        # Avoid mistaking time notations (e.g., "10:00") for headers
        if re.fullmatch(r"\d+(\.\d+)?", header):
            return False, 0.0, "", ""
        return True, 0.9, header, inline_match.group("body").strip()

    match = HEADER_PATTERN.match(stripped)
    if match:
        header = _normalize_title(match.group("core"))
        inline = match.group("inline") or ""
        has_marker = bool(
            match.group("prefix")
            or "[" in stripped
            or "【" in stripped
            or "]" in stripped
            or "】" in stripped
            or inline
        )
        if has_marker:
            # Score is boosted when the line is short and stylized
            base_score = 0.6 if match.group("prefix") else 0.5
            if inline:
                base_score += 0.1
            return True, base_score, header, inline.strip()

    # fallback: heading-like lines with trailing colon
    if stripped.endswith(":") or stripped.endswith("："):
        header = _normalize_title(stripped[:-1])
        return True, 0.55, header, ""

    return False, 0.0, "", ""


def identify_headers(lines: Iterable[str]) -> List[HeaderCandidate]:
    """Identify potential headers from lines."""
    candidates: List[HeaderCandidate] = []
    for idx, line in enumerate(lines):
        is_header, score, header, inline = _looks_like_header(line)
        if is_header:
            candidates.append(HeaderCandidate(index=idx, title=header, inline_content=inline, score=score))
    return candidates


def find_best_field_match(title: str) -> Optional[str]:
    """Map a header title to a top-level field if similarity is high enough."""
    best_field: Optional[str] = None
    best_score = 0.0
    for field, synonyms in CANONICAL_FIELDS.items():
        for synonym in synonyms:
            sim = _similarity(title, synonym)
            if sim > best_score:
                best_score = sim
                best_field = field
    return best_field if best_score >= 0.55 else None


def group_sections(lines: List[str]) -> Dict[str, str]:
    """Group text blocks under detected headers.

    Unknown headers are preserved. Inline content is appended to the section body
    so that ``"勤務地：東京"`` remains useful even when no subsequent lines exist.
    """
    headers = identify_headers(lines)
    sections: Dict[str, str] = {}

    if not headers:
        sections["本文"] = "\n".join(lines).strip()
        return sections

    for i, candidate in enumerate(headers):
        start = candidate.index + 1
        end = headers[i + 1].index if i + 1 < len(headers) else len(lines)
        body_lines = []
        if candidate.inline_content:
            body_lines.append(candidate.inline_content)
        body_lines.extend(line.strip() for line in lines[start:end] if line.strip())
        sections[candidate.title] = "\n".join(body_lines).strip()
    return sections
