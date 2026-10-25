from pathlib import Path

import typer

from src.chunkers import (
    chunk_by_characters,
    chunk_by_markdown,
    chunk_by_recursive,
    chunk_by_sentences,
)
from src.visualizer import render_chunks, render_comparison_table

STRATEGIES = ["character", "sentence", "markdown", "recursive"]

app = typer.Typer(add_completion=False)


@app.command()
def main(
    path: Path = typer.Option(
        ..., "--path", "-f", exists=True, dir_okay=False, readable=True, help="Input .md, .py or .txt file."
    ),
    strategy: str = typer.Option(
        "all", "--strategy", "-s", help="character, sentence, markdown, recursive or all."
    ),
    size: int = typer.Option(300, "--size", min=1, help="Target max characters per chunk."),
    overlap: int = typer.Option(50, "--overlap", min=0, help="Character overlap for window chunking."),
    limit: int = typer.Option(5, "--limit", min=0, help="Max chunk panels to render per strategy."),
):
    if strategy not in STRATEGIES + ["all"]:
        raise typer.BadParameter(f"choose from {', '.join(STRATEGIES)} or all", param_hint="--strategy")
    if overlap >= size:
        raise typer.BadParameter("must be smaller than --size", param_hint="--overlap")

    text = path.read_text(encoding="utf-8")
    runners = {
        "character": lambda: chunk_by_characters(text, chunk_size=size, overlap=overlap),
        "sentence": lambda: chunk_by_sentences(text, max_chars=size),
        "markdown": lambda: chunk_by_markdown(text, max_chars=size),
        "recursive": lambda: chunk_by_recursive(text, chunk_size=size, overlap=overlap),
    }
    picked = STRATEGIES if strategy == "all" else [strategy]
    results = {name: runners[name]() for name in picked}

    for name, chunks in results.items():
        render_chunks(chunks, name, limit=limit)
    render_comparison_table(text, results)


if __name__ == "__main__":
    app()
