# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Quickie is a minimal Python scratchpad application built with Textual for quick, throwaway scripts and experimentation. It's designed for code you'll write in a day and never come back to - testing ideas, running one-off tasks, or trying things out.

**Core Philosophy:**
- **Extremely minimal**: No clutter, just editor + terminal
- **Quick workflow**: Open Quickie → create project → work → close
- **Not for complex projects**: Single-session, throwaway code
- **UV-powered**: Leverages `uv init --bare` for minimal project setup without extra files (.git, etc.)

The interface is split-pane: code editor (top) and terminal (bottom). Projects are created in `~/Code/Quickies/<project-name>` and users manually clean them up when done.

## Commands

```bash
quickie                         # Run the installed CLI
uv run -m quickie.app           # Run during development (calls main())
uv sync                         # Install/sync dependencies
uv build                        # Build distribution package
uv publish                      # Publish to PyPI
```

### Development

The project has no test suite. When making changes:
- Install locally with `uv pip install -e .` and run `quickie`
- Verify settings persistence by checking `~/.quickie/config.json`
- Test terminal commands by running Python files with `Ctrl+R`

## Architecture

### Application Flow

1. **WelcomeScreen** (app.py): Initial screen for project name input
   - Creates project directory at `~/Code/Quickies/<project-name>`
   - Runs `uv init --bare` to initialize the project
   - Transitions to MainScreen on success

2. **MainScreen** (main_window.py): Main editor interface
   - Top pane: TextArea widget for code editing (3fr height)
   - Bottom pane: TerminalWidget + TerminalInput (2fr height)
   - Supports multiple file editing via quick-open modal
   - Tracks open files in `self.open_files` dict with `OpenFile` dataclass
   - Auto-creates `main.py` with default template on project creation

3. **SettingsScreen** (settings_screen.py): Configuration UI
   - Organized in three vertical panels: Editor, Behavior/Colors, Keyboard Shortcuts
   - Settings are persisted via Config singleton
   - Philosophy: Minimal settings focused on key bindings and UI style, avoiding clutter

4. **QuickOpenModal** (main_window.py): File picker modal
   - Fuzzy search through project files (excludes .git, __pycache__, .venv, node_modules)
   - Vim-like navigation (up/down arrows, enter to select)
   - Primary use is single `main.py`, but essential for when users need multiple files

### Configuration System

**config.py** provides a global `config` singleton that loads/saves to `~/.quickie/config.json`.

Configuration categories:
- **Appearance**: border_title_align, background_color, textarea_bg_color, terminal_bg_color, accent_color
- **Editor**: editor_theme (monokai/dracula/github_light/vscode_dark), show_line_numbers, soft_wrap
- **Terminal**: clear_terminal_on_run
- **Behavior**: auto_save_on_run

Colors are applied in MainScreen.on_mount() by creating a custom TextAreaTheme based on the selected theme.

### Terminal Widget

**TerminalWidget** extends RichLog and executes commands via `asyncio.create_subprocess_shell`. Commands run with `cwd=project_path` and output streams to the widget. The TerminalInput widget handles command entry.

## Key Bindings

**MainScreen**:
- `Ctrl+S`: Save file (action_save_file)
- `Ctrl+R`: Run code with `uv run <file>` (action_run_code)
- `Ctrl+E`: Quick open file picker (action_quick_open)
- `Ctrl+O`: Toggle focus between editor and terminal (action_toggle_focus)
- `Ctrl+Q`: Quit application (action_quit_app)
- `Escape`: Return to settings/previous screen
- `Ctrl+P`: Command palette (Textual builtin)

**SettingsScreen**:
- `Enter`: Start editing (push MainScreen)
- `Escape`: Go back to WelcomeScreen

## Dependencies

- **textual[syntax]**: TUI framework (>=6.6.0)
- **uv**: Package manager (runtime dependency, assumes system install)

## Code Patterns

### Async Workers

The codebase uses Textual's `@work` decorator for async operations:
```python
@work(exclusive=True)
async def setup_project(self, project_name: str) -> None:
    # Long-running operations
```

### Event Handlers

Textual's `@on` decorator for event handling:
```python
@on(Input.Submitted, "#terminal-input")
def handle_terminal_command(self, event: Input.Submitted) -> None:
```

### System Commands

Custom system commands are added via `QuickieApp.get_system_commands()`, which filters out the default screenshot command and adds custom entries for Save, Run, Open File, and Settings.

## File Structure

```
quickie/
├── __init__.py         # Package init, version
├── app.py              # Main app, WelcomeScreen, QuickieApp, main() entry point
├── main_window.py      # MainScreen, TerminalWidget, QuickOpenModal
├── settings_screen.py  # SettingsScreen configuration UI
├── config.py           # Global config singleton
└── style.tcss          # WelcomeScreen styles (MainScreen styles inline)
```

## Design Principles

When developing Quickie, prioritize:
1. **Minimal friction**: Users should go from idea to running code in seconds
2. **Single-session focus**: Typical workflow is one project per Quickie session
3. **Essential features only**: Avoid feature creep; this isn't a full IDE
4. **Customizable but not complex**: Settings for key bindings and UI style, but keep it simple

## Future Enhancements

- **View Old Quickies page**: Browse, reopen, or delete projects in `~/Code/Quickies/`

## Important Notes

- The `textual/` directory is a cloned copy of the Textual library repository for reference (not part of the app)
- Projects are always created in `~/Code/Quickies/` directory
- Terminal commands execute with `project_path` as cwd
- Config changes requiring widget recreation (colors, theme) need app restart
- The app uses `uv run` for Python execution in the terminal
- `uv init --bare` is used intentionally: gets UV's power without extra files like .git
- Users are expected to manually delete old projects when done
