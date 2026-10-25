import pytest

from src.chunkers import (
    chunk_by_characters,
    chunk_by_markdown,
    chunk_by_recursive,
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


def test_recursive_splits_on_paragraph_boundaries():
    p1 = "First paragraph here."
    p2 = "Second paragraph here."
    p3 = "Third paragraph here."
    text = f"{p1}\n\n{p2}\n\n{p3}"
    chunks = chunk_by_recursive(text, chunk_size=30, overlap=10)
    # Each chunk shouldn't exceed chunk_size
    assert all(len(c.text) <= 30 for c in chunks)
    assert len(chunks) >= 3


def test_recursive_overlap_matches_prefix_and_tail():
    sample = (
        "Retrieval-augmented generation (RAG) is a powerful architecture for question answering. "
        "It combines information retrieval with language modeling.\n\n"
        "Document chunking is a critical step in the pipeline. It defines retrieval units.\n\n"
        "Choosing the right boundaries avoids incomplete answers and reduces re-embedding cost."
    )
    chunks = chunk_by_recursive(sample, chunk_size=120, overlap=40)
    assert len(chunks) > 1
    assert chunks[0].overlap_prefix == ""
    for idx, c in enumerate(chunks):
        assert len(c.text) <= 120
        if idx > 0 and c.overlap_prefix:
            assert c.text.startswith(c.overlap_prefix)
            assert chunks[idx - 1].text.endswith(c.overlap_prefix)
            assert len(c.overlap_prefix) <= 40


def test_recursive_fallback_to_words_and_chars():
    # Long paragraph with no newlines
    words = "word " * 50
    chunks = chunk_by_recursive(words, chunk_size=50, overlap=15)
    assert all(len(c.text) <= 50 for c in chunks)
    assert len(chunks) > 1

    # Unbroken continuous sequence with no whitespace
    unbroken = "x" * 250
    chunks_unbroken = chunk_by_recursive(unbroken, chunk_size=60, overlap=10)
    assert all(len(c.text) <= 60 for c in chunks_unbroken)
    assert len(chunks_unbroken) == 5


def test_recursive_empty_and_invalid():
    assert chunk_by_recursive("", chunk_size=100, overlap=20) == []

    with pytest.raises(ValueError, match="overlap must be >= 0 and smaller than chunk_size"):
        chunk_by_recursive("hello", chunk_size=50, overlap=50)

    with pytest.raises(ValueError, match="overlap must be >= 0 and smaller than chunk_size"):
        chunk_by_recursive("hello", chunk_size=50, overlap=-1)


def test_recursive_custom_separators():
    text = "sectionA---sectionB---sectionC---sectionD"
    chunks = chunk_by_recursive(text, chunk_size=20, overlap=5, separators=["---", ""])
    assert len(chunks) > 1
    assert all(len(c.text) <= 20 for c in chunks)

