"""Modelmessage"""

from rich import get_console
from.base_command import BaseCommand
from argus.config.manager import ConfigManager
from typing import Dict, Any

class ModelCommand(BaseCommand):
    def __init__(self):
        super().__init__("model", "switch between different model providers")
        self.console = get_console()
    
    async def execute(self, context: Dict[str, Any], args: str) -> dict:
        """messagemodelmessage"""
        parts = args.strip().split() if args.strip() else []
        
        if len(parts) == 0:
            # messagemodelmessage
            self._show_available_models(context)
        elif len(parts) == 1:
            # messagemodel
            await self._switch_model(context, parts[0])
        else:
            self.console.print("[red]Usage: /model [provider_name][/red]")
            self.console.print("")
        
        return {"result": True, "message": "success"}
    
    def _show_available_models(self, context: Dict[str, Any]):
        """messagemodelmessage"""
        config = context.get('config')
        if not config:
            self.console.print("[red]No config available[/red]")
            return
        
        # messagemodels
        config_mgr = ConfigManager()
        try:
            # message
            config_data = ConfigManager._read_yaml(config_mgr.config_path)
            models = config_data.get("models", [])
            default_agent = config_data.get("default_agent", "argus")
        except Exception as e:
            self.console.print(f"[red]Failed to read config: {e}[/red]")
            return
        
        if not models:
            self.console.print("[yellow]No models configured[/yellow]")
            return
        
        self.console.print("[bold]Available Models:[/bold]")
        for model in models:
            agent_name = model.get("agent_name", "unknown")
            model_name = model.get("model", "N/A")
            provider = model.get("provider", "N/A")
            status = "[green]✓ Current[/green]" if agent_name == default_agent else ""
            self.console.print(f"  • [cyan]{agent_name}[/cyan] ({provider}): {model_name} {status}")
        self.console.print(f"\n[dim]Usage: /agent <agent_name> to switch[/dim]")
    
    async def _switch_model(self, context: Dict[str, Any], new_provider: str):
        """message /agent message"""
        # message,message agent message,message /agent message
        self.console.print("[yellow]Model switching is now done through agents.[/yellow]")
        self.console.print(f"[dim]Please use: /agent {new_provider}[/dim]")
        
        # message agents
        config_mgr = ConfigManager()
        try:
            config_data = ConfigManager._read_yaml(config_mgr.config_path)
            models = config_data.get("models", [])
            if models:
                agent_names = [m.get("agent_name", "") for m in models if m.get("agent_name")]
                if agent_names:
                    self.console.print(f"\n[dim]Available agents: {', '.join(agent_names)}[/dim]")
        except Exception:
            pass
