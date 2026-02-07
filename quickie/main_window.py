import asyncio
import shlex
from dataclasses import dataclass
from pathlib import Path
from rich.style import Style
from textual import events, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Input, Label, OptionList, RichLog, TextArea
from textual.widgets.option_list import Option
from textual.widgets.text_area import TextAreaTheme
from .config import config


@dataclass
class OpenFile:
    """Represents an open file."""
    path: Path
    content: str = ""
    modified: bool = False

class TerminalWidget(RichLog):
    """A scrollable terminal widget."""

    DEFAULT_CSS = """
    TerminalWidget {
        height: 1fr;
        background: $panel;
        border: none;
        padding: 0 1;
        scrollbar-size: 1 1;
    }
    """

    def __init__(self, project_name: str, project_path: Path) -> None:
        """Initialize terminal."""
        super().__init__(wrap=True, highlight=False, markup=False)
        self.project_name = project_name
        self.project_path = project_path
        self.command_history: list[str] = []

    def on_mount(self) -> None:
        """Initialize terminal output."""
        self.write("$ ")

    def on_click(self, event: events.Click) -> None:
        """Focus terminal input when clicked."""
        self.screen.query_one("#terminal-input").focus()
        if hasattr(self.screen, "current_focus"):
            self.screen.current_focus = "terminal"

    def run_command(self, command: str) -> None:
        """Run a command in the terminal."""
        self.command_history.append(command)
        # Show the command being run (replace the prompt line)
        self.write(command)
        # Execute asynchronously
        self.execute_command(command)

    @work(exclusive=True)
    async def execute_command(self, command: str) -> None:
        """Execute command asynchronously."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=self.project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await process.communicate()
            output = stdout.decode().strip()
            if output:
                for line in output.split("\n"):
                    self.write(line)
        except Exception as e:
            self.write(f"Error: {e}")

        self.write("$ ")


class TerminalInput(Input):
    """Terminal command input."""

    DEFAULT_CSS = """
    TerminalInput {
        dock: bottom;
        height: 1;
        background: $panel;
        border: none;
        padding: 0 2;
    }

    TerminalInput:focus {
        background: $panel;
        border: none;
    }
    """


class QuickOpenModal(ModalScreen):
    """Modal for quickly opening files."""

    DEFAULT_CSS = """
    QuickOpenModal {
        align: center middle;
    }

    #quick-open-container {
        width: 60;
        height: auto;
        max-height: 20;
        background: $surface;
        border: round $primary;
        padding: 1;
    }

    #quick-open-input {
        width: 100%;
        margin-bottom: 1;
    }

    #file-list {
        height: auto;
        max-height: 15;
        background: $surface;
    }

    #file-list > .option-list--option-highlighted {
        background: $primary;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
        Binding("enter", "select_file", "Select", show=False),
    ]

    def __init__(self, project_path: Path) -> None:
        super().__init__()
        self.project_path = project_path
        self.all_files: list[Path] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="quick-open-container"):
            yield Input(placeholder="Search files...", id="quick-open-input")
            yield OptionList(id="file-list")

    def on_mount(self) -> None:
        """Load files on mount."""
        self.all_files = self._get_project_files()
        self._update_file_list("")
        self.query_one("#quick-open-input", Input).focus()
        # Highlight first option
        file_list = self.query_one("#file-list", OptionList)
        if file_list.option_count > 0:
            file_list.highlighted = 0

    def _get_project_files(self) -> list[Path]:
        """Get all files in the project."""
        files = []
        for path in self.project_path.rglob("*"):
            if path.is_file() and not any(part.startswith(".") for part in path.parts):
                # Skip hidden files and common non-code directories
                if not any(skip in str(path) for skip in [".git", "__pycache__", ".venv", "node_modules"]):
                    files.append(path)
        return sorted(files, key=lambda p: p.name)

    def _update_file_list(self, query: str) -> None:
        """Update file list based on search query."""
        file_list = self.query_one("#file-list", OptionList)
        file_list.clear_options()

        query_lower = query.lower()
        for file_path in self.all_files:
            name = file_path.name.lower()
            rel_path = str(file_path.relative_to(self.project_path))
            if not query or query_lower in name or query_lower in rel_path.lower():
                file_list.add_option(Option(rel_path, id=str(file_path)))

        # Highlight first option after update
        if file_list.option_count > 0:
            file_list.highlighted = 0

    @on(Input.Changed, "#quick-open-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input change."""
        self._update_file_list(event.value)

    @on(OptionList.OptionSelected, "#file-list")
    def on_file_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle file selection."""
        if event.option.id:
            self.dismiss(Path(event.option.id))

    def action_cursor_up(self) -> None:
        """Move cursor up in file list."""
        file_list = self.query_one("#file-list", OptionList)
        if file_list.highlighted is not None and file_list.highlighted > 0:
            file_list.highlighted -= 1
        elif file_list.option_count > 0:
            file_list.highlighted = file_list.option_count - 1

    def action_cursor_down(self) -> None:
        """Move cursor down in file list."""
        file_list = self.query_one("#file-list", OptionList)
        if file_list.highlighted is not None and file_list.highlighted < file_list.option_count - 1:
            file_list.highlighted += 1
        elif file_list.option_count > 0:
            file_list.highlighted = 0

    def action_select_file(self) -> None:
        """Select the highlighted file."""
        file_list = self.query_one("#file-list", OptionList)
        if file_list.highlighted is not None and file_list.option_count > 0:
            option = file_list.get_option_at_index(file_list.highlighted)
            if option.id:
                self.dismiss(Path(option.id))

    def action_close(self) -> None:
        """Close the modal."""
        self.dismiss(None)


class MainScreen(Screen):
    """Main editor screen with code editor and terminal."""

    DEFAULT_CSS = """
    MainScreen {
        background: $surface;
    }

    #app-title {
        text-style: bold;
        margin-left: 2;
        width: 1fr;
    }

    #project-menu {
        width: 1fr;
        margin-right: 2;
        content-align: right middle;
    }

    #main-header {
        dock: top;
        width: 100%;
        height: auto;
    }

    #editor-container {
        height: 3fr;
    }

    #main-body {
        height: 1fr;
        width: 100%;
    }

    #code-editor {
        height: 100%;
        border: round $primary;
    }

    #code-editor:focus {
        border: round $secondary;
    }

    #code-editor .text-area--gutter {
        background: $surface;
    }

    #code-editor{
        scrollbar-size: 0 1;
    }

    #terminal-container {
        height: 2fr;
        border: round $primary;
    }

    #terminal-container:focus-within {
        border: round $secondary;
    }

    TerminalWidget {
        height: 1fr;
    }

    TerminalInput {
        height: auto;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit_app", "Quit", show=True),
        Binding("ctrl+s", "save_file", "Save", show=True),
        Binding("ctrl+r", "run_code", "Run", show=True),
        Binding("ctrl+e", "quick_open", "Open", show=True),
        Binding("ctrl+o", "toggle_focus", "Switch Focus", show=True),
        Binding("escape", "back_to_settings", "Settings", show=True),
    ]

    def __init__(self, project_name: str, project_path: Path) -> None:
        """Initialize with project name and path."""
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path
        self.current_focus = "editor"  # "editor" or "terminal"
        self.open_files: dict[Path, OpenFile] = {}
        self.active_file: Path | None = None

    def on_mount(self) -> None:
        """Apply color settings and focus editor on mount."""
        # Apply custom colors from config
        self.styles.background = config.background_color

        editor = self.query_one("#code-editor", TextArea)

        # Create custom theme based on selected theme with our custom colors
        theme_base = TextAreaTheme.get_builtin_theme(config.editor_theme)
        custom_theme = TextAreaTheme(
            name="quickie_custom",
            base_style=Style(bgcolor=config.textarea_bg_color),
            gutter_style=Style(bgcolor=config.textarea_bg_color),
            cursor_style=theme_base.cursor_style,
            cursor_line_style=theme_base.cursor_line_style,
            selection_style=theme_base.selection_style,
            syntax_styles=theme_base.syntax_styles,
        )

        # Register and apply custom theme
        editor.register_theme(custom_theme)
        editor.theme = "quickie_custom"

        editor.styles.border = ("round", config.accent_color)

        terminal_container = self.query_one("#terminal-container")
        terminal_container.styles.border = ("round", config.accent_color)

        terminal = self.query_one(TerminalWidget)
        terminal.styles.background = config.terminal_bg_color

        # Open main.py by default
        main_py = self.project_path / "main.py"
        if not main_py.exists():
            main_py.write_text(self._get_default_code())
        self.open_file(main_py)
        editor.focus()


    def compose(self) -> ComposeResult:
        """Create child widgets."""
        with Horizontal(id="main-header"):
            yield Label("Quickie", id="app-title")
            yield Label(f"[dim]{self.project_name}[/]", id="project-menu")

        with Vertical(id="main-body"):
            with Vertical(id="editor-container"):
                editor = TextArea(
                    soft_wrap=config.soft_wrap,
                    text="",
                    language="python",
                    theme=config.editor_theme,
                    show_line_numbers=config.show_line_numbers,
                    id="code-editor"
                )
                editor.border_title = "main.py"
                editor.styles.border_title_align = config.border_title_align
                yield editor
            with Vertical(id="terminal-container"):
                yield TerminalWidget(self.project_name, self.project_path)
                yield TerminalInput(
                    placeholder="Type command...",
                    id="terminal-input"
                )

    def _get_default_code(self) -> str:
        """Get default code template."""
        return '''def main():
    print("Hello, World!")


if __name__ == "__main__":
    main()
'''

    def _get_language_for_file(self, path: Path) -> str | None:
        """Get language identifier for syntax highlighting."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".json": "json",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
            ".toml": "toml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".sh": "bash",
            ".rs": "rust",
            ".go": "go",
        }
        return ext_map.get(path.suffix.lower())

    def open_file(self, file_path: Path) -> None:
        """Open a file in the editor."""
        editor = self.query_one("#code-editor", TextArea)

        # Persist current editor state before switching
        if self.active_file and self.active_file in self.open_files:
            self.open_files[self.active_file].content = editor.text

        # Load file content (reuse cached content if already open)
        if file_path in self.open_files:
            content = self.open_files[file_path].content
        else:
            content = ""
            if file_path.exists():
                try:
                    content = file_path.read_text()
                except Exception:
                    content = ""
            self.open_files[file_path] = OpenFile(path=file_path, content=content)

        self.active_file = file_path

        # Update editor
        editor.text = content
        editor.border_title = file_path.name
        editor.language = self._get_language_for_file(file_path)

    @on(Input.Submitted, "#terminal-input")
    def handle_terminal_command(self, event: Input.Submitted) -> None:
        """Handle terminal command submission."""
        command = event.value.strip()
        if command:
            terminal = self.query_one(TerminalWidget)
            terminal.run_command(command)
            event.input.value = ""

    def action_toggle_focus(self) -> None:
        """Toggle focus between editor and terminal."""
        if self.current_focus == "editor":
            self.query_one("#terminal-input", TerminalInput).focus()
            self.current_focus = "terminal"
        else:
            self.query_one("#code-editor", TextArea).focus()
            self.current_focus = "editor"

    def action_save_file(self) -> None:
        """Save the current file."""
        if not self.active_file:
            self.notify("No file to save", severity="warning")
            return

        editor = self.query_one("#code-editor", TextArea)
        try:
            self.active_file.write_text(editor.text)
            self.open_files[self.active_file].content = editor.text
            self.open_files[self.active_file].modified = False
            self.notify(f"Saved {self.active_file.name}", severity="information")
        except Exception as e:
            self.notify(f"Save failed: {e}", severity="error")

    def action_run_code(self) -> None:
        """Run the Python code with uv."""
        if not self.active_file:
            self.notify("No file to run", severity="warning")
            return

        # Auto-save if enabled
        if config.auto_save_on_run:
            self.action_save_file()

        terminal = self.query_one(TerminalWidget)

        # Clear terminal if enabled
        if config.clear_terminal_on_run:
            terminal.clear()
            terminal.write("$ ")

        # Run the active file
        rel_path = self.active_file.relative_to(self.project_path)
        terminal.run_command(f"uv run {shlex.quote(str(rel_path))}")

    def action_quick_open(self) -> None:
        """Open the quick open modal."""
        def handle_result(file_path: Path | None) -> None:
            if file_path:
                self.open_file(file_path)

        self.app.push_screen(QuickOpenModal(self.project_path), handle_result)

    def action_back_to_settings(self) -> None:
        """Go back to settings screen."""
        self.app.pop_screen()

    def action_quit_app(self) -> None:
        """Quit the application."""
        self.app.exit()