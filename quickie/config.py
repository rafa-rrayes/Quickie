"""Configuration management for Quickie."""

from pathlib import Path
from typing import Literal
import json

BorderTitleAlign = Literal["left", "center", "right"]
EditorTheme = Literal["monokai", "dracula", "github_light", "vscode_dark"]

class Config:
    """Application configuration."""

    def __init__(self) -> None:
        """Initialize configuration with defaults."""
        # Appearance
        self.border_title_align: BorderTitleAlign = "right"
        self.background_color: str = "#1e1e2e"
        self.textarea_bg_color: str = "#2b2b3b"
        self.terminal_bg_color: str = "#1a1a28"
        self.accent_color: str = "#89b4fa"

        # Editor settings
        self.editor_theme: EditorTheme = "monokai"
        self.show_line_numbers: bool = True
        self.soft_wrap: bool = False

        # Terminal settings
        self.clear_terminal_on_run: bool = False

        # Behavior
        self.auto_save_on_run: bool = True

        self.config_file = Path.home() / ".quickie" / "config.json"
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    # Appearance
                    self.border_title_align = data.get("border_title_align", "right")
                    self.background_color = data.get("background_color", "#1e1e2e")
                    self.textarea_bg_color = data.get("textarea_bg_color", "#2b2b3b")
                    self.terminal_bg_color = data.get("terminal_bg_color", "#1a1a28")
                    self.accent_color = data.get("accent_color", "#89b4fa")
                    # Editor
                    self.editor_theme = data.get("editor_theme", "monokai")
                    self.show_line_numbers = data.get("show_line_numbers", True)
                    self.soft_wrap = data.get("soft_wrap", False)
                    # Terminal
                    self.clear_terminal_on_run = data.get("clear_terminal_on_run", False)
                    # Behavior
                    self.auto_save_on_run = data.get("auto_save_on_run", True)
            except (json.JSONDecodeError, IOError):
                # If config is corrupted, use defaults
                pass

    def save(self) -> None:
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump({
                "border_title_align": self.border_title_align,
                "background_color": self.background_color,
                "textarea_bg_color": self.textarea_bg_color,
                "terminal_bg_color": self.terminal_bg_color,
                "accent_color": self.accent_color,
                "editor_theme": self.editor_theme,
                "show_line_numbers": self.show_line_numbers,
                "soft_wrap": self.soft_wrap,
                "clear_terminal_on_run": self.clear_terminal_on_run,
                "auto_save_on_run": self.auto_save_on_run,
            }, f, indent=2)

    def set_border_title_align(self, align: BorderTitleAlign) -> None:
        """Set border title alignment and save."""
        self.border_title_align = align
        self.save()
    
    def set_color(self, color_type: str, color: str) -> None:
        """Set a color configuration and save."""
        if color_type == "background":
            self.background_color = color
        elif color_type == "textarea_bg":
            self.textarea_bg_color = color
        elif color_type == "terminal_bg":
            self.terminal_bg_color = color
        elif color_type == "accent":
            self.accent_color = color
        self.save()


# Global config instance
config = Config()
