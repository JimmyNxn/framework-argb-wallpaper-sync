from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Iterable, List, cast

from framework_argb_wallpaper_sync.framework_tool import (
    FrameworkToolError,
    apply_rgb_palette,
)
from framework_argb_wallpaper_sync.palette import (
    PaletteExtractionError,
    extract_palette,
)
from framework_argb_wallpaper_sync.wallpaper import (
    WallpaperLookupError,
    resolve_wallpaper_path,
)


def _prepare_colors(palette: Iterable[str], led_count: int) -> List[str]:
    colors = list(palette)
    if not colors:
        raise PaletteExtractionError("Palette extraction returned no colors")

    if len(colors) < led_count:
        colors.extend([colors[-1]] * (led_count - len(colors)))
    return colors[:led_count]


def _apply_once(
    *,
    wallpaper: str | None,
    palette_size: int,
    led_count: int,
    zone_index: int,
    sudo: bool,
    tool_path: str,
    dry_run: bool,
) -> bool:
    try:
        wallpaper_path = resolve_wallpaper_path(wallpaper)
    except WallpaperLookupError as error:
        print(f"Error locating wallpaper: {error}", file=sys.stderr)
        return False

    try:
        palette = extract_palette(wallpaper_path, size=max(palette_size, led_count))
        colors = _prepare_colors(palette, led_count)
    except PaletteExtractionError as error:
        print(f"Error extracting palette from {wallpaper_path}: {error}", file=sys.stderr)
        return False

    try:
        result = apply_rgb_palette(
            colors,
            zone_index=zone_index,
            sudo=sudo,
            tool_path=tool_path,
            dry_run=dry_run,
        )
    except FrameworkToolError as error:
        print(f"Error applying colors: {error}", file=sys.stderr)
        return False

    if dry_run:
        command = cast(List[str], result)
        print("Dry run command:", " ".join(command))
    else:
        print(f"Applied palette from {wallpaper_path}")

    return True


def _run_watch_mode(
    *,
    wallpaper: str | None,
    palette_size: int,
    led_count: int,
    zone_index: int,
    sudo: bool,
    tool_path: str,
    dry_run: bool,
    poll_interval: float,
) -> None:
    last_signature: tuple[str, int, tuple[str, ...]] | None = None
    while True:
        try:
            wallpaper_path = resolve_wallpaper_path(wallpaper)
        except WallpaperLookupError as error:
            print(f"Error locating wallpaper: {error}", file=sys.stderr)
            time.sleep(poll_interval)
            continue

        try:
            stat_result = wallpaper_path.stat()
        except OSError as error:
            print(f"Error accessing wallpaper metadata: {error}", file=sys.stderr)
            time.sleep(poll_interval)
            continue

        try:
            palette = extract_palette(wallpaper_path, size=max(palette_size, led_count))
            colors = _prepare_colors(palette, led_count)
        except PaletteExtractionError as error:
            print(f"Error extracting palette from {wallpaper_path}: {error}", file=sys.stderr)
            time.sleep(poll_interval)
            continue

        signature = (
            wallpaper_path.expanduser().as_posix(),
            int(stat_result.st_mtime_ns),
            tuple(colors),
        )
        if signature != last_signature:
            try:
                result = apply_rgb_palette(
                    colors,
                    zone_index=zone_index,
                    sudo=sudo,
                    tool_path=tool_path,
                    dry_run=dry_run,
                )
            except FrameworkToolError as error:
                print(f"Error applying colors: {error}", file=sys.stderr)
            else:
                last_signature = signature
                if dry_run:
                    command = cast(List[str], result)
                    print("Dry run command:", " ".join(command))
                else:
                    print(f"Applied palette from {wallpaper_path}")
        time.sleep(poll_interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Sync Framework RGB keyboard/fan colors to the dominant colors of the current wallpaper"
        )
    )
    parser.add_argument(
        "--wallpaper",
        help=(
            "Wallpaper PNG or directory (default: Omarchy wallpapers in ~/.config/omarchy/current/theme/backgrounds)"
        ),
    )
    parser.add_argument(
        "--palette-size",
        type=int,
        default=8,
        help="Number of colors to sample from the wallpaper before fitting to LEDs (default: 8)",
    )
    parser.add_argument(
        "--led-count",
        type=int,
        default=8,
        help="Number of LED zones to fill (default: 8 for framework_tool --rgbkbd)",
    )
    parser.add_argument(
        "--zone-index",
        type=int,
        default=0,
        help="framework_tool zone index to target (default: 0)",
    )
    parser.add_argument(
        "--sudo",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Invoke framework_tool via sudo (default: enabled)",
    )
    parser.add_argument(
        "--tool-path",
        default="framework_tool",
        help="Path to the framework_tool executable (default: framework_tool)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the framework_tool command without executing it",
    )
    parser.add_argument(
        "--watch",
        type=float,
        metavar="SECONDS",
        help="Poll the Omarchy wallpaper file every N seconds",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.palette_size <= 0:
        parser.error("--palette-size must be positive")
    if args.led_count <= 0:
        parser.error("--led-count must be positive")
    if args.watch is not None and args.watch <= 0:
        parser.error("--watch interval must be positive")

    if args.sudo and hasattr(os, "geteuid") and os.geteuid() == 0:
        args.sudo = False

    if args.watch is None:
        success = _apply_once(
            wallpaper=args.wallpaper,
            palette_size=args.palette_size,
            led_count=args.led_count,
            zone_index=args.zone_index,
            sudo=args.sudo,
            tool_path=args.tool_path,
            dry_run=args.dry_run,
        )
        return 0 if success else 1

    try:
        _run_watch_mode(
            wallpaper=args.wallpaper,
            palette_size=args.palette_size,
            led_count=args.led_count,
            zone_index=args.zone_index,
            sudo=args.sudo,
            tool_path=args.tool_path,
            dry_run=args.dry_run,
            poll_interval=args.watch,
        )
    except KeyboardInterrupt:
        print("Stopped watching for wallpaper changes")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
