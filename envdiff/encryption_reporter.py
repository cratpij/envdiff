"""Format and print encryption/decryption reports."""

from __future__ import annotations

from typing import Optional

from envdiff.encryptor import EncryptionResult


def _colorize(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_encryption_report(
    result: EncryptionResult,
    *,
    color: bool = True,
    filename: Optional[str] = None,
) -> str:
    lines: list[str] = []
    header = f"Encryption report"
    if filename:
        header += f" — {filename}"
    lines.append(_colorize(header, "1") if color else header)
    lines.append("")

    if result.encrypted:
        label = _colorize("Encrypted:", "32") if color else "Encrypted:"
        lines.append(f"  {label}")
        for k in sorted(result.encrypted):
            lines.append(f"    {k}")

    if result.skipped:
        label = _colorize("Skipped (non-sensitive):", "33") if color else "Skipped (non-sensitive):"
        lines.append(f"  {label}")
        for k in sorted(result.skipped):
            lines.append(f"    {k}")

    if result.errors:
        label = _colorize("Errors:", "31") if color else "Errors:"
        lines.append(f"  {label}")
        for msg in result.errors:
            lines.append(f"    {msg}")

    lines.append("")
    summary_text = result.summary()
    if result.has_errors():
        lines.append(_colorize(summary_text, "31") if color else summary_text)
    else:
        lines.append(_colorize(summary_text, "32") if color else summary_text)

    return "\n".join(lines)


def print_encryption_report(
    result: EncryptionResult,
    *,
    color: bool = True,
    filename: Optional[str] = None,
) -> None:
    print(format_encryption_report(result, color=color, filename=filename))
