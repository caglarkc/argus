"""command processor"""

import subprocess
import os
from typing import Dict
from.commands.base_command import BaseCommand
from.commands.help_command import HelpCommand
from.commands.about_command import AboutCommand
from.commands.clear_command import ClearCommand
from.commands.quit_command import QuitCommand
from.commands.memory_command import MemoryCommand
from.commands.stats_command import StatsCommand
from.commands.agent_command import AgentCommand
from.commands.bug_command import BugCommand
from.commands.tools_command import ToolsCommand
from.commands.model_command import ModelCommand
from.commands.placeholder_commands import (PrivacyCommand, ThemeCommand, DocsCommand,
    EditorCommand, McpCommand, ExtensionsCommand,
    ChatCommand, CompressCommand)

class CommandProcessor:
    def __init__(self):
        self.commands: Dict[str, BaseCommand] = {}
        self._register_commands()
    
    def _register_commands(self):
        """message"""
        # message
        commands = [
            HelpCommand(),
            AboutCommand(),
            ClearCommand(),
            QuitCommand(),
            MemoryCommand(),
            StatsCommand(),
            AgentCommand(),
            BugCommand(),
            ToolsCommand(),
            ModelCommand(),
            # message
            PrivacyCommand(),
            ThemeCommand(),
            DocsCommand(),
            EditorCommand(),
            McpCommand(),
            ExtensionsCommand(),
            ChatCommand(),
            CompressCommand(),
        ]
        
        for cmd in commands:
            self.commands[cmd.name] = cmd
            if cmd.alt_name:
                self.commands[cmd.alt_name] = cmd
    
    async def process_command(self, user_input: str, context: Dict) -> dict:
        """message"""
        # message, messageshellmessage
        if user_input.startswith('!'):
            return await self._handle_shell_command(user_input, context)
        
        # message, message
        if not user_input.startswith('/'):
            return {"result": False, "message": "continue"} #
        
        # message
        parts = user_input[1:].split(' ', 1)
        command_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # message
        if command_name in self.commands:
            command = self.commands[command_name]
            return await command.execute(context, args)
        
        # message
        console = context.get('console')
        if console:
            console.print(f"Unknown command: /{command_name}", "red")
            console.print("Type '/help' to see available commands.","dim")
        
        # messageTruemessage(message)
        return {"result": True, "message": "success"} #
    
    async def _handle_shell_command(self, user_input: str, context: Dict) -> dict:
        """messageshellmessage"""
        console = context.get('console')
        
        # message(message)
        shell_command = user_input[1:].strip()
        
        if not shell_command:
            if console:
                console.print("No command specified after '!'","red")
            return {"result": False, "message": "no command specified"} 
        
        # message cd message
        if shell_command.startswith('cd ') or shell_command == 'cd':
            return await self._handle_cd_command(shell_command, console)
        
        if console:
            console.print(f"Executing shell command:{shell_command}","cyan")
        
        try:
            # messageshellmessage
            result = subprocess.run(shell_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # 30message
                cwd=os.getcwd()  # message)
            
            # message
            if result.stdout:
                if console:
                    console.print(f"Output:\n{result.stdout}", "orange3")
                    console.print("")  # message
            
            if result.stderr:
                if console:
                    console.print(f"Error output:\n{result.stderr}", "orange3")
                    console.print("")  # message
            
            if result.returncode!= 0:
                if console:
                    console.print(f"Command exited with code: {result.returncode}", "orange3")
                    console.print("")  # message
            else:
                if console and not result.stdout and not result.stderr:
                    console.print("Command completed successfully (no output)", "orange3")
                    console.print("")  # message
                    
        except subprocess.TimeoutExpired:
            if console:
                console.print("Command timed out after 30 seconds", "red")
                console.print("")  # message
        except Exception as e:
            if console:
                console.print(f"Error executing command: {e}", "red")
                console.print("")  # message
        
        return {"result": True, "message": "success"} 

    async def _handle_cd_command(self, command: str, console) -> dict:
        """message cd message"""
        
        # message cd message
        parts = command.split(' ', 1)
        if len(parts) == 1:
            # message cd,message
            target_dir = os.path.expanduser('~')
        else:
            # cd message
            target_dir = parts[1].strip()
            
            # message
            if target_dir == '~':
                target_dir = os.path.expanduser('~')
            elif target_dir == '-':
                # cd - message,message
                if console:
                    console.print("cd - not supported, use absolute path","yellow")
                return {"result": True, "message": "success"} 
            else:
                # message
                target_dir = os.path.expanduser(target_dir)
                if not os.path.isabs(target_dir):
                    target_dir = os.path.join(os.getcwd(), target_dir)
        
        try:
            # message
            target_dir = os.path.abspath(target_dir)
            
            # message
            if not os.path.exists(target_dir):
                if console:
                    console.print(f"Directory does not exist: {target_dir}","red")
                return {"result": False, "message": "directory does not exist"} 
            
            if not os.path.isdir(target_dir):
                if console:
                    console.print(f"Not a directory: {target_dir}","red")
                return {"result": False, "message": "not a directory"} 
            
            # message
            old_dir = os.getcwd()
            os.chdir(target_dir)
            
            if console:
                console.print(f"Changed directory from {old_dir} to {os.getcwd()}", "orange3")
                console.print("")  # message
            
        except PermissionError:
            if console:
                console.print(f"Permission denied: {target_dir}", "red")
                console.print("")  # message
        except Exception as e:
            if console:
                console.print(f"Error changing directory: {e}", "red")
                console.print("")  # message
        
        return {"result": True, "message": "success"} 
