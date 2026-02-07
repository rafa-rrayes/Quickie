from pathlib import Path
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Input, Label, Select, Static
from .config import config

class SettingsScreen(Screen):
    """Settings screen showing project structure and keyboard shortcuts."""

    CSS = """
    SettingsScreen {
        background: $surface;
    }

    #settings-title {
        dock: top;
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        background: $primary;
        color: $background;
    }

    #settings-body {
        height: 1fr;
        padding: 2 4;
    }

    .settings-panel {
        width: 1fr;
        border: round $primary;
        padding: 1 2;
        margin-right: 1;
        height: 1fr;
    }

    .settings-panel:last-child {
        margin-right: 0;
    }
    
    .align-button, .color-input, .theme-select {
        width: 100%;
        margin-top: 1;
    }

    .color-label, .setting-label {
        margin-top: 1;
        color: $text-muted;
    }

    .setting-checkbox {
        margin-top: 1;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #border-section, #colors-section {
        margin-top: 2;
    }

    .tree-item {
        margin-left: 2;
    }

    .shortcut-row {
        margin-top: 1;
    }

    .shortcut-key {
        color: $primary;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("enter", "start_editing", "Start", show=True),
        Binding("escape", "go_back", "Back", show=True),
    ]

    def __init__(self, project_name: str, project_path: Path | None = None) -> None:
        """Initialize with project name and path."""
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path or Path.home() / "Code" / "Quickies" / project_name

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Settings", id="settings-title")
        with Horizontal(id="settings-body"):
            # Editor Settings Panel
            with VerticalScroll(classes="settings-panel"):
                yield Label("Editor", classes="section-title")
                yield Label("Theme", classes="setting-label")
                yield Select(
                    [(theme, theme) for theme in ["monokai", "dracula", "github_light", "vscode_dark"]],
                    value=config.editor_theme,
                    id="theme-select",
                    classes="theme-select",
                )
                yield Checkbox("Show line numbers", config.show_line_numbers, id="check-line-numbers", classes="setting-checkbox")
                yield Checkbox("Soft wrap", config.soft_wrap, id="check-soft-wrap", classes="setting-checkbox")

                yield Label("Border Title", classes="section-title", id="border-section")
                yield Static(f"Current: [b]{config.border_title_align}[/b]", id="current-align")
                yield Button("Left", id="align-left", classes="align-button")
                yield Button("Center", id="align-center", classes="align-button")
                yield Button("Right", id="align-right", classes="align-button")

            # Behavior & Terminal Panel
            with VerticalScroll(classes="settings-panel"):
                yield Label("Behavior", classes="section-title")
                yield Checkbox("Auto-save before run", config.auto_save_on_run, id="check-auto-save", classes="setting-checkbox")
                yield Checkbox("Clear terminal on run", config.clear_terminal_on_run, id="check-clear-terminal", classes="setting-checkbox")

                yield Label("Colors", classes="section-title", id="colors-section")
                yield Label("Background", classes="color-label")
                yield Input(value=config.background_color, placeholder="#1e1e2e", id="color-background", classes="color-input")
                yield Label("Editor Background", classes="color-label")
                yield Input(value=config.textarea_bg_color, placeholder="#2b2b3b", id="color-textarea", classes="color-input")
                yield Label("Terminal Background", classes="color-label")
                yield Input(value=config.terminal_bg_color, placeholder="#1a1a28", id="color-terminal", classes="color-input")
                yield Label("Accent Color", classes="color-label")
                yield Input(value=config.accent_color, placeholder="#89b4fa", id="color-accent", classes="color-input")
                yield Button("Apply Colors", id="apply-colors", classes="align-button")

            # Keyboard Shortcuts Panel
            with VerticalScroll(classes="settings-panel"):
                yield Label("Keyboard Shortcuts", classes="section-title")
                yield Static(self._get_shortcuts())
        yield Footer()

    def _get_shortcuts(self) -> str:
        """Generate keyboard shortcuts."""
        return """[b]QUICKIE[/b]

[b]Ctrl+S[/]   Save file
[b]Ctrl+R[/]   Run code
[b]Ctrl+E[/]   Open file
[b]Ctrl+O[/]   Switch focus
[b]Ctrl+Q[/]   Quit
[b]Ctrl+P[/]   Command palette
[b]Escape[/]   Settings

[b]EDITOR[/b]

[b]Ctrl+C[/]   Copy
[b]Ctrl+V[/]   Paste
[b]Ctrl+Z[/]   Undo
[b]Ctrl+X[/]   Cut

[b]TERMINAL[/b]

[b]Enter[/]    Run command
"""

    @on(Button.Pressed, "#align-left")
    def set_align_left(self) -> None:
        """Set border title alignment to left."""
        config.set_border_title_align("left")
        self.query_one("#current-align", Static).update(f"Current: [b]left[/b]")
        self.notify("Border alignment set to left")

    @on(Button.Pressed, "#align-center")
    def set_align_center(self) -> None:
        """Set border title alignment to center."""
        config.set_border_title_align("center")
        self.query_one("#current-align", Static).update(f"Current: [b]center[/b]")
        self.notify("Border alignment set to center")

    @on(Button.Pressed, "#align-right")
    def set_align_right(self) -> None:
        """Set border title alignment to right."""
        config.set_border_title_align("right")
        self.query_one("#current-align", Static).update(f"Current: [b]right[/b]")
        self.notify("Border alignment set to right")

    @on(Button.Pressed, "#apply-colors")
    def apply_colors(self) -> None:
        """Apply color settings."""
        bg_color = self.query_one("#color-background", Input).value
        textarea_color = self.query_one("#color-textarea", Input).value
        terminal_color = self.query_one("#color-terminal", Input).value
        accent_color = self.query_one("#color-accent", Input).value
        
        # Validate hex colors (basic validation)
        colors = [
            ("background", bg_color),
            ("textarea_bg", textarea_color),
            ("terminal_bg", terminal_color),
            ("accent", accent_color)
        ]
        
        for color_type, color_value in colors:
            if color_value and (color_value.startswith("#") and len(color_value) in [4, 7]):
                config.set_color(color_type, color_value)
        
        self.notify("Colors updated! Restart the app to see changes.", severity="information")

    @on(Select.Changed, "#theme-select")
    def on_theme_changed(self, event: Select.Changed) -> None:
        """Handle theme selection change."""
        if event.value:
            config.editor_theme = event.value
            config.save()
            self.notify(f"Theme set to {event.value}")

    @on(Checkbox.Changed, "#check-line-numbers")
    def on_line_numbers_changed(self, event: Checkbox.Changed) -> None:
        """Handle line numbers checkbox change."""
        config.show_line_numbers = event.value
        config.save()

    @on(Checkbox.Changed, "#check-soft-wrap")
    def on_soft_wrap_changed(self, event: Checkbox.Changed) -> None:
        """Handle soft wrap checkbox change."""
        config.soft_wrap = event.value
        config.save()

    @on(Checkbox.Changed, "#check-auto-save")
    def on_auto_save_changed(self, event: Checkbox.Changed) -> None:
        """Handle auto-save checkbox change."""
        config.auto_save_on_run = event.value
        config.save()

    @on(Checkbox.Changed, "#check-clear-terminal")
    def on_clear_terminal_changed(self, event: Checkbox.Changed) -> None:
        """Handle clear terminal checkbox change."""
        config.clear_terminal_on_run = event.value
        config.save()

    def action_start_editing(self) -> None:
        """Return to the editor (pop settings screen)."""
        self.app.pop_screen()

    def action_go_back(self) -> None:
        """Go back to welcome screen."""
        self.app.pop_screen()
