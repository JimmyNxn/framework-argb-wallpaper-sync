from pathlib import Path

from PIL import Image

from framework_argb_wallpaper_sync.palette import extract_palette


def create_test_image(path: Path) -> None:
    image = Image.new("RGB", (4, 2))
    pixels = [
        (255, 0, 0),
        (255, 128, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 255, 255),
        (0, 0, 255),
        (128, 0, 255),
        (255, 0, 255),
    ]
    image.putdata(pixels)
    image.save(path)


def test_extract_palette_returns_expected_color_count(tmp_path):
    wallpaper_path = tmp_path / "wallpaper.png"
    create_test_image(wallpaper_path)

    colors = extract_palette(wallpaper_path, size=8)

    assert len(colors) == 8
    # Ensure colors generate valid hex strings
    assert all(len(color) == 6 for color in colors)
