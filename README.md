# Quickie

A minimal Python scratchpad for quick, throwaway scripts. Open it, write code, run it, close it.

![Python](https://img.shields.io/badge/python-3.13+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Install

```bash
curl -LsSf https://raw.githubusercontent.com/rafa-rrayes/quickie/main/install.sh | sh
```

Or manually with uv or pipx:

```bash
uv tool install "quickie @ git+https://github.com/rafa-rrayes/quickie.git"
pipx install "git+https://github.com/rafa-rrayes/quickie.git"
```

## Usage

```bash
quickie
```

That's it. Enter a project name, write your code, hit `Ctrl+R` to run.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+S` | Save file |
| `Ctrl+R` | Run code |
| `Ctrl+E` | Open file |
| `Ctrl+O` | Switch focus (editor/terminal) |
| `Ctrl+Q` | Quit |
| `Ctrl+P` | Command palette |
| `Escape` | Settings |

## What It Does

- Creates a minimal Python project in `~/Code/Quickies/<name>` using `uv init --bare`
- Gives you a split-pane editor + terminal
- Runs your code with `uv run`

## What It Doesn't Do

- Project management, git integration, debugging, or anything complex
- This is for code you'll write today and never look at again

## License

MIT
