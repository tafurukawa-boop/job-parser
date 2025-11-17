"""Text cleaning utilities for job posting parsing."""

import html
import re
from typing import Iterable


_RE_MULTI_NEWLINE = re.compile(r"\n{2,}")
_RE_MULTI_NEWLINE_LONG = re.compile(r"\n{4,}")
_RE_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_RE_QUOTES = re.compile(r'["]|[“”]')


FULL_WIDTH_SPACE = "\u3000"
NON_BREAKING_SPACE = "\u00a0"


def _strip_html_entities(text: str) -> str:
    """Convert HTML entities and replace non-breaking spaces with regular spaces."""
    unescaped = html.unescape(text)
    # Explicitly catch literal ``&nbsp;`` artifacts before and after unescaping
    unescaped = unescaped.replace("&nbsp;", " ")
    return unescaped.replace(NON_BREAKING_SPACE, " ")


def _standardize_spaces(text: str) -> str:
    """Collapse repeated spaces and normalize full-width spaces to half-width."""
    normalized = text.replace(FULL_WIDTH_SPACE, " ")
    normalized = _RE_MULTI_SPACE.sub(" ", normalized)
    return normalized


def _remove_quotes(text: str) -> str:
    """Drop decorative straight and smart quotes that can mislead header detection."""
    return _RE_QUOTES.sub("", text)


def _collapse_newlines(text: str) -> str:
    """Reduce excessive blank lines while keeping paragraph intent."""
    text = _RE_MULTI_NEWLINE.sub("\n\n", text)
    # Bound extremely long blank sequences to at most three newlines
    return _RE_MULTI_NEWLINE_LONG.sub("\n\n\n", text)


def normalize_lines(lines: Iterable[str]) -> str:
    """Normalize each line and return a single cleaned text block."""
    cleaned_lines = []
    for line in lines:
        line = _strip_html_entities(line)
        line = _remove_quotes(line)
        line = _standardize_spaces(line)
        # preserve intentional indentation for bullets but trim trailing whitespace
        cleaned_lines.append(line.rstrip())
    text = "\n".join(cleaned_lines)
    text = _collapse_newlines(text)
    return text.strip()


def clean_text(raw_text: str) -> str:
    """Perform end-to-end cleaning for raw job posting text."""
    # Unify line breaks
    normalized_newlines = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized_newlines.split("\n")
    return normalize_lines(lines)
