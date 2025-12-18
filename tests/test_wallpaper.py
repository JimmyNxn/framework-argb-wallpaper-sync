import os
from types import SimpleNamespace

import pytest

from framework_argb_wallpaper_sync.wallpaper import (
    WallpaperLookupError,
    resolve_wallpaper_path,
)


def test_resolve_wallpaper_path_accepts_file(tmp_path):
    wallpaper = tmp_path / "custom.png"
    wallpaper.write_bytes(b"fake")
    resolved = resolve_wallpaper_path(wallpaper)
    assert resolved == wallpaper


def test_resolve_wallpaper_path_accepts_jpg_file(tmp_path):
    wallpaper = tmp_path / "custom.jpg"
    wallpaper.write_bytes(b"fake")
    resolved = resolve_wallpaper_path(wallpaper)
    assert resolved == wallpaper


def test_resolve_wallpaper_path_accepts_jpeg_file(tmp_path):
    wallpaper = tmp_path / "custom.jpeg"
    wallpaper.write_bytes(b"fake")
    resolved = resolve_wallpaper_path(wallpaper)
    assert resolved == wallpaper


def test_resolve_wallpaper_path_handles_directory(tmp_path):
    directory = tmp_path / "backgrounds"
    directory.mkdir()
    wallpaper = directory / "1.png"
    wallpaper.write_bytes(b"fake")
    resolved = resolve_wallpaper_path(directory)
    assert resolved == wallpaper


def test_resolve_wallpaper_path_handles_directory_with_jpg(tmp_path):
    directory = tmp_path / "backgrounds"
    directory.mkdir()
    wallpaper = directory / "1.jpg"
    wallpaper.write_bytes(b"fake")
    resolved = resolve_wallpaper_path(directory)
    assert resolved == wallpaper


def test_resolve_wallpaper_path_picks_latest_when_multiple(tmp_path):
    directory = tmp_path / "backgrounds"
    directory.mkdir()
    first = directory / "1.png"
    second = directory / "2.png"
    third = directory / "3.png"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    third.write_bytes(b"third")
    os.utime(first, (1, 1))
    os.utime(second, (2, 2))
    os.utime(third, (3, 3))

    resolved = resolve_wallpaper_path(directory)
    assert resolved == third


def test_resolve_wallpaper_path_raises_when_missing(tmp_path):
    directory = tmp_path / "backgrounds"
    with pytest.raises(WallpaperLookupError):
        resolve_wallpaper_path(directory)


def test_resolve_wallpaper_path_honours_sudo_user(monkeypatch, tmp_path):
    home_dir = tmp_path / "userhome"
    wallpapers_dir = home_dir / ".config/omarchy/current/theme/backgrounds"
    wallpapers_dir.mkdir(parents=True)
    wallpaper = wallpapers_dir / "wall.png"
    wallpaper.write_bytes(b"fake")

    monkeypatch.setenv("SUDO_USER", "omarchy")
    monkeypatch.setattr(
        "framework_argb_wallpaper_sync.wallpaper.pwd.getpwnam",
        lambda _: SimpleNamespace(pw_dir=str(home_dir)),
    )

    resolved = resolve_wallpaper_path()
    assert resolved == wallpaper
