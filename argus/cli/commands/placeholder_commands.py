"""message - message"""

from rich import get_console
from.base_command import BaseCommand

class PlaceholderCommand(BaseCommand):
    """message"""
    
    def __init__(self, name: str, description: str, alt_name: str = None):
        super().__init__(name, description, alt_name)
        self.console = get_console()
    
    async def execute(self, context, args: str) -> dict:
        """message"""
        self.console.print(f"[yellow]Command '/{self.name}' is not yet implemented.[/yellow]")
        self.console.print(f"[dim]Description: {self.description}[/dim]")
        return {"result": True, "message": "success"}

class PrivacyCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("privacy", "display the privacy notice")

class ThemeCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("theme", "change the theme")

class DocsCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("docs", "open full Argus documentation in your browser")

class EditorCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("editor", "set external editor preference")


class McpCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("mcp", "list configured MCP servers and tools")

class ExtensionsCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("extensions", "list active extensions")

class ChatCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("chat", "Manage conversation history. Usage: /chat <list|save|resume> <tag>")

class CompressCommand(PlaceholderCommand):
    def __init__(self):
        super().__init__("compress", "Compresses the context by replacing it with a summary.")
