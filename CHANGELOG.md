# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.1.0] - 2024-10-24

### Added
- `Chunk` dataclass with `index`, `text`, `overlap_prefix`, `token_count`, `char_count` fields
- `chunk_by_characters()` – fixed-size sliding window with configurable overlap
- `chunk_by_sentences()` – sentence-boundary-aware chunker with sentence-level overlap
- `chunk_by_markdown()` – splits on Markdown headings (`#`–`######`) and code blocks
- `count_tokens()` – tiktoken-based token counter using the `o200k_base` encoding
- Rich terminal visualizer with color-coded panels per chunk strategy
- Strategy comparison table (chunks, avg tokens, min/max tokens, overlap overhead %)
- Typer CLI (`chunk-viz`) with `--path`, `--strategy`, `--size`, `--overlap`, `--limit` flags
- GitHub Actions CI workflow (ruff lint + pytest)
- Comprehensive unit test suite
