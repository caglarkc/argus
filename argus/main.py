from __future__ import annotations
import argparse
import asyncio
import uuid
from argus import get_version
from argus.utils.permission_manager import PermissionLevel, PermissionManager
from argus.config.manager import ConfigManager
from argus.agents.agent_manager import AgentManager
from argus.cli.cli_console import CLIConsole
from argus.hooks.config import load_hooks_config
from argus.hooks.manager import HookManager
from argus.hooks.models import HookEvent
from argus.tools.tool_manager import ToolManager 
from argus.cli.runtime import HeadlessRunner, InteractiveSession

async def async_main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Argus Python Agent")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {get_version()}")
    parser.add_argument("--config", type=str, default=None, help="Config file path (default: ~/.argus/argus/argus_config.json)")
    parser.add_argument("--model", type=str, help="Override model name")
    parser.add_argument("--api_key", help="Qwen API key", default=None)
    parser.add_argument("--base_url", help="Qwen base URL", default=None)
    parser.add_argument("--temperature", type=float, help="Override temperature")
    parser.add_argument("--max-tokens", type=int, help="Override max tokens")
    parser.add_argument("--session-id", type=str, help="Use specific session ID")
    parser.add_argument("--permission-mode", type=str, help="Set permission mode (yolo, planning, edit-only, locked)", default="locked")
    parser.add_argument("--agent", type=str, help="Use specific agent: argus|claude|codex", default="argus")
    parser.add_argument("-p", "--prompt", nargs="?", help="Prompt to execute")
    args = parser.parse_args()

    cfg_mgr = ConfigManager(args.config)
    config = cfg_mgr.get_app_config(args)

    perm_level = PermissionLevel(config.permission_level)
    perm_mgr = PermissionManager(perm_level)

    cli = CLIConsole(perm_mgr)

    session_id = args.session_id or str(uuid.uuid4())[:8]

    hooks_cfg = load_hooks_config(cfg_mgr.get_default_hooks_path())
    hook_mgr = HookManager(hooks_cfg)

    tool_mgr = ToolManager(perm_mgr=perm_mgr, hook_mgr=hook_mgr, cli=cli)
    tool_mgr.autodiscover()

    await hook_mgr.emit(HookEvent.SessionStart,
        base_payload={"session_id": session_id, "source": "startup"},)

    agent_mgr = AgentManager(cfg_mgr, cli, tool_mgr)
    await agent_mgr.init(args.agent.lower())

    ok, msg, _ = await hook_mgr.emit(HookEvent.UserPromptSubmit,
        base_payload={"session_id": session_id, "prompt": args.prompt or ""},)
    if not ok:
        cli.print(f"⛔ {msg or 'Prompt blocked by hook'}", "yellow")
        return

    # message 
    if args.prompt:
        runner = HeadlessRunner(agent_mgr=agent_mgr, hook_mgr=hook_mgr, cli=cli, perm_mgr=perm_mgr)
        await runner.run(prompt=args.prompt, session_id=session_id, set_yolo=True)
        await agent_mgr.close()
        return

    # message 
    session = InteractiveSession(cli=cli,
        agent_mgr=agent_mgr,
        hook_mgr=hook_mgr,
        config_mgr=cfg_mgr,
        tool_mgr=tool_mgr,
        perm_mgr=perm_mgr,
        session_id=session_id,)
    await session.run()
    await agent_mgr.close()

def main() -> None:
    """Synchronous wrapper for the main CLI entry point."""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
