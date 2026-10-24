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
