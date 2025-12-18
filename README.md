# Framework ARGB Wallpaper Sync

Sync the Framework Desktop ARGB Fan lighting to match the dominant colors of your current wallpaper. The tool targets Omarchy (an Arch-based distro) where the active wallpaper lives inside `~/.config/omarchy/current/theme/backgrounds` and typically only a single image is present.

## Features

- Reads the Omarchy wallpaper PNG and extracts an adaptive color palette using Pillow.
- Applies the palette to the eight RGB zones exposed by `framework_tool --rgbkbd`.
- Optional watch mode to monitor the wallpaper PNG for changes.
- Dry-run support to preview the exact command before applying it.

## Prerequisites

- A Framework Desktop fitted with the official ARGB Fan accessory.
- Omarchy Linux with wallpapers stored in `~/.config/omarchy/current/theme/backgrounds`.
- Python 3.9 or newer (used to run the CLI).
- `framework_tool` installed and available on your `PATH`.
- Ability to run `framework_tool` with elevated privileges (the CLI defaults to prepending `sudo`).

## Installation

### Using `uv` (recommended)

[`uv`](https://github.com/astral-sh/uv) can install the CLI directly onto your PATH while keeping the environment isolated.

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
uv tool install --from path/to/framework-argb-wallpaper-sync colour-sync
```

Replace the path with this directory or a VCS URL. To work inside a project checkout instead, create a local environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install .
```

### Using `pipx`

```bash
pipx install path/to/framework-argb-wallpaper-sync
```

`pipx` likewise exposes `colour-sync` on your PATH while keeping dependencies isolated.

### Using `pip`

```bash
pip install .
```

This method installs into the current Python environment.

## Usage

Once installed, a `colour-sync` command becomes available.

### Apply once

```bash
colour-sync
```

> The tool automatically honours `SUDO_USER`, so even when run via `sudo` it reads the wallpaper from your Omarchy profile instead of `/root`.

By default the CLI invokes `framework_tool` using `sudo`. Disable that behaviour with `colour-sync --no-sudo` if your setup does not require elevated access.

This command:

1. Resolves the Omarchy wallpaper PNG (defaults to `~/.config/omarchy/current/theme/backgrounds`).
2. Extracts eight dominant colors.
3. Runs `sudo framework_tool --rgbkbd 0 <colors...>` to update the RGB zones.

Key flags:

- `--wallpaper` – override the wallpaper path or directory if you customise Omarchy.
- `--tool-path /usr/bin/framework_tool` – override the executable path.
- `--sudo` / `--no-sudo` – control whether `sudo` is prepended when calling `framework_tool` (defaults to on).
- `--dry-run` – print the command without running it.

### Watch for changes

```bash
colour-sync --watch 5
```

This polls the wallpaper PNG every 5 seconds, reapplying colors whenever the file changes (by timestamp or palette). Use `Ctrl+C` to stop.

### Hooking into Omarchy theme changes

If you have a script that updates Omarchy wallpapers, append the CLI afterwards so the lighting stays in sync:

```bash
framework-theme-switcher --set my-theme
colour-sync
```

For long-running daemons, prefer the `--watch` mode.

## Development

Set up a local environment with `uv` and run the tests:

```bash
uv venv
source .venv/bin/activate
uv pip install .[test]
uv run pytest
```

Feel free to adjust palette sampling (`--palette-size`) or LED zone count (`--led-count`) to experiment with different mappings.
