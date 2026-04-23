"""message"""
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from.base_command import BaseCommand

class ClearCommand(BaseCommand):
    def __init__(self):
        super().__init__("clear", "clear the screen and conversation history")
    
    async def execute(self, context, args: str) -> dict:
        """message"""
        console = context.get('console')
        
        # message --force message -f message
        if args and ('-f' in args or '--force' in args):
            await self._perform_clear(context)
            return {"result": True, "message": "success"} 
        
        # message
        if console:
            console.print("[yellow]This will clear the screen and reset conversation history.[/yellow]")
            try:
                
                session = PromptSession()
                response = await session.prompt_async(HTML('<ansiblue>Are you sure you want to continue? (y/N): </ansiblue>'))
                
                if response.lower().strip() in ['y', 'yes']:
                    await self._perform_clear(context)
                else:
                    console.print("[dim]Clear operation cancelled.[/dim]")
                    console.print("")
            except KeyboardInterrupt:
                console.print("\n[dim]Clear operation cancelled.[/dim]")
                console.print("")
            except Exception as e:
                console.print(f"[dim]Clear operation cancelled: {e}[/dim]")
                console.print("")
        
        return {"result": True, "message": "success"} 
    
    async def _perform_clear(self, context):
        """message"""
        # message
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # message
        agent_mgr = context.get('agent_mgr')
        if agent_mgr and hasattr(agent_mgr.current, 'reset_conversation'):
            agent_mgr.current.reset_conversation()
        
        console = context.get('console')
        if console:
            console.show_interactive_banner()
            console.show_status_bar()
            console.print("[green]Screen cleared and conversation history reset.[/green]")
            console.print("")
