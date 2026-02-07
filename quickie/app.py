"""Main Quickie application."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Input, Label
from .main_window import MainScreen

class WelcomeScreen(Screen):
    """Welcome screen where user enters project name."""

    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        """Create child widgets."""

        yield Label("Quickie", id="quickie-title")
        with Container(id="welcome-container"):
            yield Input(
                placeholder="Enter project name...",
                id="project-input"
            )
            yield Label("", id="status-label")

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#project-input", Input).focus()

    @on(Input.Submitted, "#project-input")
    def handle_project_input(self, event: Input.Submitted) -> None:
        """Handle project name submission."""
        project_name = event.value.strip()
        status_label = self.query_one("#status-label", Label)
        if not project_name:
            status_label.update("Please enter a project name")
            return
        if not re.match(r'^[\w\-]+$', project_name):
            status_label.update("Name can only contain letters, numbers, hyphens, underscores")
            return
        self.setup_project(project_name)

    @work(exclusive=True)
    async def setup_project(self, project_name: str) -> None:
        """Create project directory and run uv init."""
        status_label = self.query_one("#status-label", Label)
        project_input = self.query_one("#project-input", Input)
        project_input.disabled = True

        # Create project directory
        project_path = Path.home() / "Code" / "Quickies" / project_name
        status_label.update(f"Creating {project_path}...")

        try:
            is_new = not project_path.exists()
            project_path.mkdir(parents=True, exist_ok=True)

            if is_new:
                # Only run uv init for new projects
                status_label.update("Running uv init...")
                process = await asyncio.create_subprocess_exec(
                    "uv", "init", "--bare",
                    cwd=project_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await process.wait()

                if process.returncode != 0:
                    stderr = await process.stderr.read()
                    status_label.update(f"Error: {stderr.decode()}")
                    project_input.disabled = False
                    return
            else:
                status_label.update("Opening existing project...")

            self.app.push_screen(MainScreen(project_name, project_path))
        except Exception as e:
            status_label.update(f"Error: {e}")
            project_input.disabled = False

class QuickieApp(App):
    """The main Quickie application."""

    CSS = """
    QuickieApp {
        background: $background;
    }
    """

    TITLE = "Quickie"
    
    def get_system_commands(self, screen: Screen):
        """Get system commands including custom settings command."""
        # Get default system commands (but filter out screenshot)
        for command in super().get_system_commands(screen):
            if "screenshot" not in command.title.lower():
                yield command

        # Add settings command
        yield SystemCommand(
            "Settings",
            "Open application settings",
            self.action_open_settings,
        )

        # Add MainScreen-specific commands
        if hasattr(screen, 'action_save_file'):
            yield SystemCommand(
                "Save File",
                "Save the current file (Ctrl+S)",
                screen.action_save_file,
            )
        if hasattr(screen, 'action_run_code'):
            yield SystemCommand(
                "Run Code",
                "Run the current file (Ctrl+R)",
                screen.action_run_code,
            )
        if hasattr(screen, 'action_quick_open'):
            yield SystemCommand(
                "Open File",
                "Quick open a file (Ctrl+E)",
                screen.action_quick_open,
            )
        if hasattr(screen, 'action_toggle_focus'):
            yield SystemCommand(
                "Toggle Focus",
                "Switch between editor and terminal (Ctrl+O)",
                screen.action_toggle_focus,
            )
    
    def action_open_settings(self) -> None:
        """Open settings screen."""
        from .settings_screen import SettingsScreen
        # Get the current project name and path from the active screen if available
        project_name = "default"
        project_path = None
        if hasattr(self.screen, 'project_name'):
            project_name = self.screen.project_name
        if hasattr(self.screen, 'project_path'):
            project_path = self.screen.project_path
        self.push_screen(SettingsScreen(project_name, project_path))
    
    def on_mount(self) -> None:
        """Push the welcome screen on mount."""
        self.push_screen(WelcomeScreen())


def main() -> None:
    """Run the Quickie application."""
    app = QuickieApp()
    app.run()


if __name__ == "__main__":
    main()
