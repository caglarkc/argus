"""message"""

from rich.panel import Panel
from rich import get_console
from.base_command import BaseCommand
import sys
import platform

class AboutCommand(BaseCommand):
    def __init__(self):
        super().__init__("about", "show version info")
        self.console = get_console()
    
    async def execute(self, context, args: str) -> dict:
        """message"""
        version_info = self._build_version_info()
        
        panel = Panel(version_info,
            title="Argus Version Info",
            border_style="blue",
            padding=(1, 2))
        
        self.console.print(panel)
        return {"result": True, "message": "success"} #
    
    def _build_version_info(self) -> str:
        """message"""
        content = []
        content.append(f"[bold cyan]Argus CLI Version:[/bold cyan] 1.0.0")
        content.append(f"[bold cyan]Python Version:[/bold cyan] {sys.version}")
        content.append(f"[bold cyan]Platform:[/bold cyan] {platform.platform()}")
        content.append(f"[bold cyan]Architecture:[/bold cyan] {platform.machine()}")
        return "\n".join(content)
