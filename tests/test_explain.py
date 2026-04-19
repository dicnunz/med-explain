import explain


def test_build_plain_language_prompt_truncates_input():
    text = "abcde" * 3_000
    prompt = explain.build_plain_language_prompt(text)
    assert "curious 12-year-old" in prompt
    assert len(prompt) < len(text)


def test_extract_repeated_medical_terms_prefers_repeated_rare_words(monkeypatch):
    scores = {
        "tachycardia": 2.0,
        "hemoglobin": 3.0,
        "patient": 5.0,
    }
    monkeypatch.setattr(
        explain,
        "zipf_frequency",
        lambda word, language: scores.get(word, 5.0),
    )

    text = "tachycardia tachycardia hemoglobin hemoglobin patient patient"
    assert explain.extract_repeated_medical_terms(text) == ["hemoglobin", "tachycardia"]


def test_normalize_definition_snippet_returns_first_sentence():
    snippet = "Triglycerides are a type of fat in the blood. More detail follows."
    assert explain.normalize_definition_snippet(snippet) == (
        "Triglycerides are a type of fat in the blood..."
    )


def test_render_summary_html_escapes_input_and_adds_tooltips():
    html = explain.render_summary_html(
        "A1c < 6 is better. Hemoglobin matters.",
        {"hemoglobin": 'Oxygen-carrying protein in red blood cells "RBCs"...'},
    )
    assert "A1c &lt; 6 is better." in html
    assert (
        'title="Oxygen-carrying protein in red blood cells &quot;RBCs&quot;..."' in html
    )
    assert "<span" in html
