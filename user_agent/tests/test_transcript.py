from user_agent.transcript import TranscriptAccumulator


def test_add_user_and_assistant():
    t = TranscriptAccumulator()
    t.add_user("I earn 35 grand")
    t.add_assistant("Thanks, I'll note that down.")
    text = t.flush()
    assert "[User] I earn 35 grand" in text
    assert "[Assistant] Thanks, I'll note that down." in text


def test_flush_clears_pending():
    t = TranscriptAccumulator()
    t.add_user("Hello")
    t.flush()
    text = t.flush()
    assert "no new conversation" in text


def test_challenge_token_embedded():
    t = TranscriptAccumulator()
    t.add_user("Yes, I consent")
    text = t.flush(challenge_token="abc123def456")
    assert "[challenge_token: abc123def456]" in text


def test_full_transcript_preserves_all():
    t = TranscriptAccumulator()
    t.add_user("First message")
    t.flush()
    t.add_user("Second message")
    full = t.full_transcript()
    assert "First message" in full
    assert "Second message" in full


def test_regulated_display_recorded():
    t = TranscriptAccumulator()
    t.add_regulated_display("disclosure", "Important broker info", "acknowledged")
    text = t.flush()
    assert "Regulated disclosure" in text
    assert "Important broker info" in text
    assert "acknowledged" in text
