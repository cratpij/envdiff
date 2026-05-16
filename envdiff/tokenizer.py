"""Tokenize .env file content into structured tokens for analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    COMMENT = auto()
    BLANK = auto()
    ASSIGNMENT = auto()
    MALFORMED = auto()


@dataclass
class Token:
    line_number: int
    token_type: TokenType
    raw: str
    key: str = ""
    value: str = ""

    @property
    def is_comment(self) -> bool:
        return self.token_type == TokenType.COMMENT

    @property
    def is_assignment(self) -> bool:
        return self.token_type == TokenType.ASSIGNMENT

    @property
    def is_malformed(self) -> bool:
        return self.token_type == TokenType.MALFORMED


@dataclass
class TokenizeResult:
    tokens: List[Token] = field(default_factory=list)
    source: str = ""

    @property
    def assignments(self) -> List[Token]:
        return [t for t in self.tokens if t.is_assignment]

    @property
    def comments(self) -> List[Token]:
        return [t for t in self.tokens if t.is_comment]

    @property
    def malformed(self) -> List[Token]:
        return [t for t in self.tokens if t.is_malformed]

    def summary(self) -> str:
        return (
            f"{len(self.assignments)} assignments, "
            f"{len(self.comments)} comments, "
            f"{len(self.malformed)} malformed"
        )


def _strip_quotes(value: str) -> str:
    for q in ('"', "'"):
        if value.startswith(q) and value.endswith(q) and len(value) >= 2:
            return value[1:-1]
    return value


def tokenize(content: str, source: str = "") -> TokenizeResult:
    """Tokenize raw .env file content into a TokenizeResult."""
    tokens: List[Token] = []
    for lineno, raw in enumerate(content.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            tokens.append(Token(lineno, TokenType.BLANK, raw))
        elif stripped.startswith("#"):
            tokens.append(Token(lineno, TokenType.COMMENT, raw))
        elif "=" in stripped:
            key, _, val = stripped.partition("=")
            key = key.strip()
            val = _strip_quotes(val.strip())
            tokens.append(Token(lineno, TokenType.ASSIGNMENT, raw, key=key, value=val))
        else:
            tokens.append(Token(lineno, TokenType.MALFORMED, raw))
    return TokenizeResult(tokens=tokens, source=source)


def tokenize_file(path: str) -> TokenizeResult:
    """Read a file and return its TokenizeResult."""
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    return tokenize(content, source=path)
