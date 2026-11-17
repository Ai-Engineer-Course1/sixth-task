"""Small text helpers used as sample source code for the code explorer."""

from __future__ import annotations

import re
import unicodedata

_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_NON_SLUG_RE = re.compile(r"[^a-z0-9]+")


def word_count(text: str) -> int:
    """Return the number of words found in ``text``."""
    return len(_WORD_RE.findall(text))


def reverse(text: str) -> str:
    """Return ``text`` with its characters reversed."""
    return text[::-1]


def normalize(text: str) -> str:
    """Lowercase ``text`` and strip accents (e.g. ``café`` -> ``cafe``)."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


def is_palindrome(text: str) -> bool:
    """Return ``True`` if ``text`` reads the same forwards and backwards.

    Comparison ignores case, accents and non-alphanumeric characters.
    """
    cleaned = "".join(char for char in normalize(text) if char.isalnum())
    return cleaned == cleaned[::-1]


def slugify(text: str) -> str:
    """Convert ``text`` into a URL friendly ``kebab-case`` slug."""
    return _NON_SLUG_RE.sub("-", normalize(text)).strip("-")


def truncate(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """Shorten ``text`` to ``max_length`` characters, appending ``suffix``."""
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return suffix[:max_length]
    return text[: max_length - len(suffix)] + suffix
