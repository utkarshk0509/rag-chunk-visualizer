from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.chunkers import Chunk, count_tokens

COLORS = ["cyan", "green", "magenta", "yellow"]

console = Console()


def render_chunks(chunks: list[Chunk], strategy_name: str, limit: int = 5):
    console.rule(f"[bold]{strategy_name}[/bold] ({len(chunks)} chunks)")
    for c in chunks[:limit]:
        body = Text()
        body.append(c.overlap_prefix, style="bold black on yellow")
        body.append(c.text[len(c.overlap_prefix) :])
        console.print(
            Panel(
                body,
                title=f"chunk {c.index}",
                subtitle=f"tokens: {c.token_count} | chars: {c.char_count} | overlap_chars: {len(c.overlap_prefix)}",
                border_style=COLORS[c.index % len(COLORS)],
            )
        )
    if len(chunks) > limit:
        console.print(f"[dim]... {len(chunks) - limit} more chunks not shown[/dim]")


def render_comparison_table(raw_text: str, results: dict[str, list[Chunk]]):
    src_toks = count_tokens(raw_text)
    table = Table(title="Strategy comparison", caption=f"source file: {src_toks} tokens")
    for col in ["Strategy", "Chunks", "Avg Tokens", "Min/Max Tokens", "Total Tokens", "Overlap Overhead %"]:
        table.add_column(col, justify="left" if col == "Strategy" else "right")

    for name, chunks in results.items():
        if not chunks:
            table.add_row(name, "0", "-", "-", "0", "-")
            continue
        toks = [c.token_count for c in chunks]
        overlap_toks = sum(count_tokens(c.overlap_prefix) for c in chunks if c.overlap_prefix)
        pct = overlap_toks / src_toks * 100 if src_toks else 0.0
        table.add_row(
            name,
            str(len(chunks)),
            f"{sum(toks) / len(toks):.1f}",
            f"{min(toks)}/{max(toks)}",
            str(sum(toks)),
            f"{pct:.1f}%",
        )
    console.print(table)
