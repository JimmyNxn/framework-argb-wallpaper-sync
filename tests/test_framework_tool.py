from unittest import mock

import pytest

from framework_argb_wallpaper_sync.framework_tool import build_rgb_command


@mock.patch("shutil.which", return_value="/usr/bin/framework_tool")
def test_build_rgb_command_generates_expected_args(mock_which):
    colors = [
        "ff0000",
        "ff8000",
        "ffff00",
        "00ff00",
        "00ffff",
        "0000ff",
        "8000ff",
        "ff00ff",
    ]
    command = build_rgb_command(colors, zone_index=0)
    assert command == [
        "framework_tool",
        "--rgbkbd",
        "0",
        "0xff0000",
        "0xff8000",
        "0xffff00",
        "0x00ff00",
        "0x00ffff",
        "0x0000ff",
        "0x8000ff",
        "0xff00ff",
    ]
    mock_which.assert_called_once_with("framework_tool")


def test_build_rgb_command_requires_eight_colors():
    with pytest.raises(ValueError):
        build_rgb_command(["ff0000"], zone_index=0)
