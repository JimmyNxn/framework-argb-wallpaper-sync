from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable, List

from PIL import Image


class PaletteExtractionError(Exception):
    """Raised when palette extraction fails."""


def _normalize_hex(color: Iterable[int]) -> str:
    r, g, b = (int(channel) for channel in color)
    return f"{r:02x}{g:02x}{b:02x}"


def extract_palette(path: Path, size: int = 8) -> List[str]:
    if size <= 0:
        raise ValueError("Palette size must be positive")

    resolved_path = path.expanduser()
    if not resolved_path.exists():
        raise PaletteExtractionError(f"Wallpaper not found: {resolved_path}")

    try:
        with Image.open(resolved_path) as image:
            image = image.convert("RGB")
            quantized = image.convert("P", palette=Image.ADAPTIVE, colors=size)
            palette = quantized.getpalette()
            if not palette:
                raise PaletteExtractionError("Unable to derive palette from wallpaper")
            color_counts = Counter(quantized.getdata())
            ordered_indices = [index for index, _ in color_counts.most_common(size)]
            result = []
            for index in ordered_indices:
                base = index * 3
                result.append(_normalize_hex(palette[base : base + 3]))
            while len(result) < size:
                result.append(result[-1])
            return result[:size]
    except PaletteExtractionError:
        raise
    except Exception as exc:  # pragma: no cover - Pillow-specific failures
        raise PaletteExtractionError(str(exc)) from exc
