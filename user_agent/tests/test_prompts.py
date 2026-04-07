from user_agent.prompts import build_system_prompt


def test_prompt_includes_vocabulary(sample_vocabulary):
    prompt = build_system_prompt(sample_vocabulary)
    assert "gross_annual_income" in prompt
    assert "full_name" in prompt
    assert "debt_consolidation" in prompt


def test_prompt_includes_protocol_rules(sample_vocabulary):
    prompt = build_system_prompt(sample_vocabulary)
    assert "MUST present the content EXACTLY" in prompt
    assert "Do NOT infer consent" in prompt
    assert "challenge_token" in prompt


def test_prompt_includes_british_english(sample_vocabulary):
    prompt = build_system_prompt(sample_vocabulary)
    assert "British English" in prompt
