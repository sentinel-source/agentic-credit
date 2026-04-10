"""Transcript accumulator for the evidence model."""

from __future__ import annotations

class TranscriptAccumulator:
    """Records conversation turns and produces transcript text for broker submissions."""

    def __init__(self) -> None:
        self._all_entries: list[str] = []
        self._pending: list[str] = []

    def add_user(self, text: str) -> None:
        entry = f"[User] {text}"
        self._all_entries.append(entry)
        self._pending.append(entry)

    def add_assistant(self, text: str) -> None:
        entry = f"[Assistant] {text}"
        self._all_entries.append(entry)
        self._pending.append(entry)

    def add_regulated_display(self, action_type: str, content: str, response: str) -> None:
        entry = (
            f"[Regulated {action_type}] Content displayed verbatim:\n"
            f"{content}\n"
            f"[User response] {response}"
        )
        self._all_entries.append(entry)
        self._pending.append(entry)

    def flush(self, challenge_token: str | None = None) -> str:
        """Return transcript text since last flush, with challenge token embedded."""
        if not self._pending:
            text = "(no new conversation since last submission)"
        else:
            text = "\n\n".join(self._pending)
        if challenge_token:
            text += f"\n\n[challenge_token: {challenge_token}]"
        self._pending = []
        return text

    def full_transcript(self) -> str:
        """Return the complete conversation transcript."""
        return "\n\n".join(self._all_entries)
