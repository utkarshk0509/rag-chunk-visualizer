from src.chunkers import (
    chunk_by_characters,
    chunk_by_markdown,
    chunk_by_sentences,
    count_tokens,
)


def test_count_tokens():
    assert count_tokens("") == 0
    assert count_tokens("hello world") == 2


def test_character_overlap_matches_previous_tail():
    text = "".join(chr(97 + i % 26) for i in range(500))
    chunks = chunk_by_characters(text, chunk_size=100, overlap=20)
    assert chunks[1].overlap_prefix == chunks[0].text[-20:]
    assert chunks[1].text.startswith(chunks[1].overlap_prefix)
    assert chunks[-1].text == text[-len(chunks[-1].text) :]


def test_sentence_boundaries():
    text = "First one here. Second one here! Third one here? Fourth one here."
    chunks = chunk_by_sentences(text, max_chars=35, overlap_sentences=1)
    assert chunks[0].text == "First one here. Second one here!"
    assert chunks[1].overlap_prefix == "Second one here!"
    assert all(c.text.rstrip()[-1] in ".!?" for c in chunks)


def test_markdown_header_split():
    text = "# Intro\nSome text.\n\n## Setup\nMore text.\n\n### Usage\nEven more."
    chunks = chunk_by_markdown(text, max_chars=400)
    assert [c.text.splitlines()[0] for c in chunks] == ["# Intro", "## Setup", "### Usage"]
    assert all(c.overlap_prefix == "" for c in chunks)
