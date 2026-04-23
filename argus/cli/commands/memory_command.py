"""message"""

from rich.panel import Panel
from rich import get_console
from.base_command import BaseCommand

class MemoryCommand(BaseCommand):
    def __init__(self):
        super().__init__("memory", "Commands for interacting with memory.")
        self.console = get_console()
    
    async def execute(self, context, args: str) -> dict:
        """message"""
        if not args:
            self._show_memory_help()
            return {"result": False, "message": "no arguments provided"}

        subcommand = args.split()[0].lower()
        
        if subcommand == "show":
            await self._show_memory(context)
        elif subcommand == "add":
            await self._add_memory(context, args)
        elif subcommand == "refresh":
            await self._refresh_memory(context)
        else:
            self._show_memory_help()
        
        return {"result": True, "message": "success"}
    
    def _show_memory_help(self):
        """message"""
        help_content = """[bold cyan]Memory Commands:[/bold cyan]

[purple]/memory show[/purple] - Show the current memory contents
[purple]/memory add <content>[/purple] - Add content to the memory
[purple]/memory refresh[/purple] - Refresh the memory from the source"""
        
        panel = Panel(help_content, title="Memory Help", border_style="blue")
        self.console.print(panel)
    
    async def _show_memory(self, context):
        """message"""
        # TODO: message
        self.console.print("[yellow]Memory contents will be displayed here[/yellow]")
    
    async def _add_memory(self, context, args):
        """message"""
        # TODO: message
        content = " ".join(args.split()[1:])
        self.console.print(f"[green]Added to memory: {content}[/green]")
    
    async def _refresh_memory(self, context):
        """message"""
        # TODO: message
        self.console.print("[green]Memory refreshed[/green]")
