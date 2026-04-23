import asyncio
from asyncio import TimerHandle
from typing import Callable, Optional, Dict, Any
from prompt_toolkit.key_binding import KeyBindings
from argus.cli.cli_console import CLIConsole
from argus.utils.permission_manager import PermissionLevel,PermissionManager

def create_key_bindings(console_getter: Callable[[], CLIConsole], 
    perm_mgr_getter: Callable[[], PermissionManager], 
    cancel_event_getter: Optional[Callable[[], Optional[Any]]] = None, 
    current_task_getter: Optional[Callable] = None,
    *,
    exit_sentinel: str = "__ARGUS_QUIT__",) -> KeyBindings:
    """message"""
    bindings = KeyBindings()
    loop = asyncio.get_event_loop()
    
    # Ctrl+J - message
    @bindings.add('c-j')
    def _(event):
        """Insert a newline."""
        event.app.current_buffer.insert_text('\n')
    
    # Alt+Enter - message (messageLinuxmessage)
    @bindings.add('escape', 'enter')
    def _(event):
        """Insert a newline (Alt+Enter)."""
        event.app.current_buffer.insert_text('\n')
    
    # Ctrl+Y - Cycle through permission levels
    @bindings.add('c-y')
    def _(event):
        """Cycle through permission levels: LOCKED -> EDIT_ONLY -> PLANNING -> YOLO -> LOCKED"""
        perm_mgr = perm_mgr_getter()
        console = console_getter()
        try:
            current_level = perm_mgr.get_permission_level()

            # Define the cycle order
            cycle_order = [
                PermissionLevel.LOCKED,
                PermissionLevel.EDIT_ONLY,
                PermissionLevel.PLANNING,
                PermissionLevel.YOLO
            ]

            # Find current index and get next level
            try:
                current_index = cycle_order.index(current_level)
                next_index = (current_index + 1) % len(cycle_order)
                next_level = cycle_order[next_index]
            except ValueError:
                # If current level not in cycle, start from LOCKED
                next_level = PermissionLevel.LOCKED

            # Set new permission level
            perm_mgr.set_permission_level(next_level)

            # Display status with appropriate color and icon
            level_info = {
                PermissionLevel.LOCKED: ("🔒 LOCKED", "message:message","red"),
                PermissionLevel.EDIT_ONLY: ("✏️ EDIT_ONLY", "message:message,message","yellow"),
                PermissionLevel.PLANNING: ("📝 PLANNING", "message:message,message","blue"),
                PermissionLevel.YOLO: ("🚀 YOLO", "message:message","green")
            }

            icon_text, description, color= level_info[next_level]
            console.print(f"{icon_text} - {description}",color)

        except Exception as e:
            console.print(f"Error switching permission level: {e}","red")
    
    # Shift+Tab - Toggle auto-accepting edits (placeholder)
    @bindings.add('s-tab')
    def _(event):
        """Toggle auto-accepting edits."""
        console = console_getter()
        console.print("Auto-accepting edits toggled (not implemented yet)","yellow")
    
    # ESC - message
    # message,message ESC message
    @bindings.add('escape')
    def _(event):
        """Cancel current operation."""
        cancel_event = cancel_event_getter() if cancel_event_getter else None
        current_task = current_task_getter() if current_task_getter else None
        try:
            if current_task:
                current_task.cancel()
        except Exception:
            pass
        try:
            if cancel_event and hasattr(cancel_event, "set"):
                cancel_event.set()
        except Exception:
            pass
    # Ctrl+C - message:message,message
    ctrl_c_count = {"n": 0}
    reset_handle: Dict[str, Optional[TimerHandle]] = {"h": None}
    def schedule_reset():
        if reset_handle["h"] is not None:
            reset_handle["h"].cancel()
        reset_handle["h"] = loop.call_later(3.0, lambda: ctrl_c_count.__setitem__("n", 0))

    @bindings.add('c-c')
    def _(event):
        console = console_getter()
        cancel_event = cancel_event_getter() if cancel_event_getter else None
        current_task = current_task_getter() if current_task_getter else None
        running = bool(current_task and not current_task.done())

        if running:
            console.print("\nCancelling current operation... (Press Ctrl+C again to quit)", "yellow")
            if cancel_event and not cancel_event.is_set():
                cancel_event.set()
            try:
                if current_task and not current_task.done():
                    current_task.cancel()
            finally:
                ctrl_c_count["n"] = 1
                schedule_reset()
            return

        # message:message 3 message
        ctrl_c_count["n"] += 1
        if ctrl_c_count["n"] == 1:
            console.print("Press Ctrl+C again to quit", "yellow")
            schedule_reset()
        else:
            console.print("Force quitting...", "red")
            if reset_handle["h"] is not None:
                reset_handle["h"].cancel()
                reset_handle["h"] = None
            event.app.exit(result=exit_sentinel)
    
    # Alt+Left - Jump word left
    @bindings.add('escape', 'left')
    def _(event):
        """Jump to previous word."""
        buffer = event.app.current_buffer
        pos = buffer.document.find_previous_word_beginning()
        if pos:
            buffer.cursor_position += pos
    
    # Alt+Right - Jump word right  
    @bindings.add('escape', 'right')
    def _(event):
        """Jump to next word."""
        buffer = event.app.current_buffer
        pos = buffer.document.find_next_word_ending()
        if pos:
            buffer.cursor_position += pos
    
    return bindings
