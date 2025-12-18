from __future__ import annotations

import os
import pwd
from pathlib import Path

OMARCHY_SUBPATH = Path(".config/omarchy/current/theme/backgrounds")
SUPPORTED_WALLPAPER_SUFFIXES = {".png", ".jpg", ".jpeg"}


class WallpaperLookupError(Exception):
    """Raised when the Omarchy wallpaper cannot be located."""


def _default_omarchy_directory() -> Path:
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            home_dir = Path(pwd.getpwnam(sudo_user).pw_dir)
        except KeyError:
            home_dir = Path.home()
    else:
        home_dir = Path.home()
    return home_dir / OMARCHY_SUBPATH


def _find_supported_wallpaper_files(directory: Path) -> list[Path]:
    return [
        path
        for path in directory.iterdir()
        if path.suffix.lower() in SUPPORTED_WALLPAPER_SUFFIXES
    ]


def resolve_wallpaper_path(target: str | Path | None = None) -> Path:
    """Return the Omarchy wallpaper path, ensuring it exists.

    ``target`` may be an explicit image path or a directory containing the
    wallpaper image. If omitted, the default Omarchy location is based on the
    invoking user's home directory. When run via ``sudo``, the ``SUDO_USER``
    environment variable is honoured so that the original user's wallpaper is
    detected instead of root's.
    """

    candidate = Path(target).expanduser() if target else _default_omarchy_directory()

    if not candidate.exists():
        if candidate.suffix.lower() in SUPPORTED_WALLPAPER_SUFFIXES:
            raise WallpaperLookupError(f"Wallpaper not found at {candidate}")
        raise WallpaperLookupError(f"Wallpaper directory not found: {candidate}")

    if candidate.is_dir():
        wallpaper_files = _find_supported_wallpaper_files(candidate)
        if not wallpaper_files:
            supported = ", ".join(sorted(SUPPORTED_WALLPAPER_SUFFIXES))
            raise WallpaperLookupError(
                f"No supported image files ({supported}) found in {candidate}"
            )
        if len(wallpaper_files) == 1:
            return wallpaper_files[0]
        latest = max(wallpaper_files, key=lambda path: path.stat().st_mtime_ns)
        return latest

    if candidate.suffix.lower() in SUPPORTED_WALLPAPER_SUFFIXES:
        return candidate

    raise WallpaperLookupError(f"Wallpaper not found at {candidate}")
