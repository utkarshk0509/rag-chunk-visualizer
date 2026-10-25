import re
from dataclasses import dataclass

import tiktoken

SPLIT_RE = re.compile(r"(?m)^(?=#{1,6}\s+|(?:def |class ))")


@dataclass
class Chunk:
    index: int
    text: str
    overlap_prefix: str
    token_count: int
    char_count: int


def count_tokens(text: str) -> int:
    return len(tiktoken.get_encoding("o200k_base").encode(text))


def _chunk(i: int, text: str, prefix: str = "") -> Chunk:
    return Chunk(i, text, prefix, count_tokens(text), len(text))


def chunk_by_characters(text: str, chunk_size: int = 300, overlap: int = 50) -> list[Chunk]:
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")
    step = chunk_size - overlap
    out = []
    for start in range(0, len(text), step):
        buf = text[start : start + chunk_size]
        # first `overlap` chars of this window are the last `overlap` chars of the previous one
        out.append(_chunk(len(out), buf, buf[:overlap] if out else ""))
        if start + chunk_size >= len(text):
            break
    return out


def chunk_by_sentences(text: str, max_chars: int = 300, overlap_sentences: int = 1) -> list[Chunk]:
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]
    out = []
    carry: list[str] = []
    buf: list[str] = []
    for s in sents:
        if buf and len(" ".join(carry + buf + [s])) > max_chars:
            out.append(_chunk(len(out), " ".join(carry + buf), " ".join(carry)))
            # [-0:] would keep everything, so guard the no-overlap case
            carry = (carry + buf)[-overlap_sentences:] if overlap_sentences else []
            buf = []
        buf.append(s)
    if buf:
        out.append(_chunk(len(out), " ".join(carry + buf), " ".join(carry)))
    return out


def chunk_by_markdown(text: str, max_chars: int = 400) -> list[Chunk]:
    out = []
    for block in SPLIT_RE.split(text):
        block = block.strip()
        if not block:
            continue
        if len(block) <= max_chars:
            out.append(_chunk(len(out), block))
            continue
        # ponytail: a single paragraph longer than max_chars stays whole
        buf = ""
        for para in (p.strip() for p in block.split("\n\n")):
            if not para:
                continue
            if buf and len(buf) + len(para) + 2 > max_chars:
                out.append(_chunk(len(out), buf))
                buf = ""
            buf = f"{buf}\n\n{para}" if buf else para
        if buf:
            out.append(_chunk(len(out), buf))
    return out


def _split_text_recursively(text: str, separators: list[str], chunk_size: int) -> list[str]:
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chosen_sep = None
    remaining_seps = []
    for idx, sep in enumerate(separators):
        if sep == "" or sep in text:
            chosen_sep = sep
            remaining_seps = separators[idx + 1 :]
            break

    if chosen_sep is None or chosen_sep == "":
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    parts = text.split(chosen_sep)
    raw_pieces = []
    for i, part in enumerate(parts):
        if i < len(parts) - 1:
            raw_pieces.append(part + chosen_sep)
        elif part:
            raw_pieces.append(part)

    final_pieces = []
    for piece in raw_pieces:
        if len(piece) <= chunk_size:
            final_pieces.append(piece)
        else:
            if remaining_seps:
                final_pieces.extend(_split_text_recursively(piece, remaining_seps, chunk_size))
            else:
                final_pieces.extend([piece[i : i + chunk_size] for i in range(0, len(piece), chunk_size)])

    return final_pieces


def chunk_by_recursive(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50,
    separators: list[str] | None = None,
) -> list[Chunk]:
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")
    if not text:
        return []

    if separators is None:
        separators = ["\n\n", "\n", " ", ""]

    pieces = _split_text_recursively(text, separators, chunk_size)
    if not pieces:
        return []

    chunks: list[Chunk] = []
    current_pieces: list[str] = []
    current_len = 0
    overlap_prefix = ""

    for piece in pieces:
        if current_pieces and (current_len + len(piece) > chunk_size):
            chunk_text = "".join(current_pieces)
            chunks.append(_chunk(len(chunks), chunk_text, overlap_prefix))

            while current_pieces and (current_len > overlap or current_len + len(piece) > chunk_size):
                popped = current_pieces.pop(0)
                current_len -= len(popped)

            overlap_prefix = "".join(current_pieces)

        current_pieces.append(piece)
        current_len += len(piece)

    if current_pieces:
        chunk_text = "".join(current_pieces)
        chunks.append(_chunk(len(chunks), chunk_text, overlap_prefix))

    return chunks

