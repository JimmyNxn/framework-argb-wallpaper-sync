from __future__ import annotations

import shutil
import subprocess
from typing import Iterable, List


class FrameworkToolError(Exception):
    """Raised when invoking framework_tool fails."""


def build_rgb_command(
    colors: Iterable[str],
    *,
    zone_index: int = 0,
    tool_path: str = "framework_tool",
    sudo: bool = False,
) -> List[str]:
    color_list = list(colors)
    if len(color_list) != 8:
        raise ValueError("framework_tool expects exactly 8 colors for --rgbkbd")

    if zone_index < 0:
        raise ValueError("zone_index must be non-negative")

    if not shutil.which(tool_path):
        raise FrameworkToolError(
            f"framework_tool executable '{tool_path}' was not found in PATH"
        )

    command = [tool_path, "--rgbkbd", str(zone_index)]
    command.extend(f"0x{color.lower()}" for color in color_list)

    if sudo:
        command.insert(0, "sudo")

    return command


def apply_rgb_palette(
    colors: Iterable[str],
    *,
    zone_index: int = 0,
    tool_path: str = "framework_tool",
    sudo: bool = False,
    dry_run: bool = False,
) -> subprocess.CompletedProcess[str] | List[str]:
    command = build_rgb_command(
        colors, zone_index=zone_index, tool_path=tool_path, sudo=sudo
    )

    if dry_run:
        return command

    try:
        return subprocess.run(command, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - runtime failure
        raise FrameworkToolError(exc.stderr or str(exc)) from exc
