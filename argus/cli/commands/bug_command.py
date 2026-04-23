"""GitHub issue message"""

import aiohttp
import os
import sys
import platform
from typing import Dict, Any
from rich import get_console
from.base_command import BaseCommand

class BugCommand(BaseCommand):
    def __init__(self):
        super().__init__("bug", "create a GitHub issue for bug reports")
        self.console = get_console()
    
    async def execute(self, context: Dict[str, Any], args: str) -> dict:
        """message GitHub issue"""
        if not args.strip():
            self.console.print("[red]Usage: /bug <bug_description>[/red]")
            self.console.print("[dim]Example: /bug Found a memory leak in agent execution[/dim]")
            return {"result": True, "message": "success"} 
        
        description = args.strip()
        
        # message GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            self.console.print("[red]❌ GITHUB_TOKEN environment variable not set[/red]")
            self.console.print("[dim]Please create a GitHub Personal Access Token with 'repo' scope:[/dim]")
            self.console.print("[dim]1. Go to https://github.com/settings/tokens/ [dim]")
            self.console.print("[dim]2. Generate new token with 'repo' permissions[/dim]")
            self.console.print("[dim]3. Set: export GITHUB_TOKEN=your_token[/dim]")
            return {"result": True, "message": "success"} 
        
        # message
        self.console.print("[yellow]🔄 Creating GitHub issue...[/yellow]")
        
        try:
            issue_url = await self._create_github_issue(description, github_token)
            self.console.print(f"[green]✅ Issue created successfully: {issue_url}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to create issue: {str(e)}[/red]")
            self.console.print("[dim]Please ensure your GitHub token has 'repo' permissions[/dim]")
        
        return {"result": True, "message": "success"} 
    
    async def _create_github_issue(self, description: str, github_token: str) -> str:
        """message GitHub API message issue"""
        # message token message
        repo_owner = "Ali Çağlar Koçer"
        repo_name = "Argus"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Argus-CLI"
        }
        
        # message
        repo_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        
        async with aiohttp.ClientSession() as session:
            # message
            async with session.get(repo_url, headers=headers) as response:
                if response.status == 404:
                    raise Exception("Repository not found or no access permission")
                elif response.status == 401:
                    raise Exception("Invalid GitHub token or insufficient permissions")
                elif response.status!= 200:
                    error_text = await response.text()
                    raise Exception(f"Repository access error ({response.status}): {error_text}")
            
            # message
            env_info = self._get_environment_info()
            
            issue_data = {
                "title": f"Bug Report: {description[:50]}{'...' if len(description) > 50 else ''}",
                "body": f"""## Bug Description
{description}

## Environment Information
{env_info}

---
_This issue was created automatically via Argus `/bug` command._
""",
                "labels": ["bug", "argus-report", "auto-generated"]
            }
            
            # message issue
            issues_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
            async with session.post(issues_url, headers=headers, json=issue_data) as response:
                if response.status == 201:
                    result = await response.json()
                    return result["html_url"]
                else:
                    error_text = await response.text()
                    raise Exception(f"GitHub API error ({response.status}): {error_text}")
    
    def _get_environment_info(self) -> str:
        """message"""
        try:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            platform_info = platform.platform()
            architecture = platform.machine()
            
            return f"""- **Argus Version**: 1.0.0
- **Python Version**: {python_version}
- **Platform**: {platform_info}
- **Architecture**: {architecture}"""
        except Exception:
            return "- **Environment**: Unable to detect"
