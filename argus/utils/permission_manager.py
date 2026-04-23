from enum import Enum
from typing import Set, Dict, Any, Optional
from dataclasses import dataclass

class PermissionLevel(Enum):
    """Permission levels for tool execution."""
    LOCKED = "locked"           # message:message
    EDIT_ONLY = "edit_only"     # message:message,message
    PLANNING = "planning"       # message:message,message
    YOLO = "yolo"              # message:message

@dataclass
class PermissionRule:
    """Permission rule for specific tool categories."""
    tool_categories: Set[str]
    auto_approve: bool
    description: str

class PermissionManager:
    """Manages tool execution permissions based on permission levels."""
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.LOCKED):
        self.permission_level = permission_level
        self._setup_tool_categories()
        self._setup_permission_rules()
    
    def _setup_tool_categories(self):
        """Define tool categories for permission management."""
        self.tool_categories = {
            # message
            "file_edit": {
                "write_file", "edit_file", "edit", "apply_patch"
            },
            
            # message
            "file_read": {
                "read_file", "read_many_files"
            },
            
            # message
            "file_system": {
                "ls", "grep", "glob", "find"
            },
            
            # message
            "system_command": {
                "bash", "shell", "cmd"
            },
            
            # message
            "network": {
                "web_fetch", "web_search", "curl", "wget"
            },
            
            # message
            "memory": {
                "memory", "remember", "recall"
            },
            
            # message
            "agent": {
                "agent_tool", "architect_tool", "sub_agent", "update_plan"
            },
            
            # Git message
            "git": {
                "git_status", "git_log", "git_diff", "git_commit", "git_push"
            }
        }
    
    def _setup_permission_rules(self):
        """Setup permission rules for each permission level."""
        self.permission_rules = {
            PermissionLevel.LOCKED: {
                # message:message
                "file_edit": PermissionRule({"file_edit"}, False, "message"),
                "file_read": PermissionRule({"file_read"}, False, "message"),
                "file_system": PermissionRule({"file_system"}, False, "message"),
                "system_command": PermissionRule({"system_command"}, False, "message"),
                "network": PermissionRule({"network"}, False, "message"),
                "memory": PermissionRule({"memory"}, False, "message"),
                "agent": PermissionRule({"agent"}, False, "message"),
                "git": PermissionRule({"git"}, False, "Gitmessage"),
            },
            
            PermissionLevel.EDIT_ONLY: {
                # message:message,message
                "file_edit": PermissionRule({"file_edit"}, True, "message"),
                "file_read": PermissionRule({"file_read"}, False, "message"),
                "file_system": PermissionRule({"file_system"}, False, "message"),
                "system_command": PermissionRule({"system_command"}, False, "message"),
                "network": PermissionRule({"network"}, False, "message"),
                "memory": PermissionRule({"memory"}, False, "message"),
                "agent": PermissionRule({"agent"}, False, "message"),
                "git": PermissionRule({"git"}, False, "Gitmessage"),
            },
            
            PermissionLevel.PLANNING: {
                # message:message,message
                "file_edit": PermissionRule({"file_edit"}, False, "message"),
                "file_read": PermissionRule({"file_read"}, True, "message"),
                "file_system": PermissionRule({"file_system"}, True, "message"),
                "system_command": PermissionRule({"system_command"}, True, "message"),
                "network": PermissionRule({"network"}, True, "message"),
                "memory": PermissionRule({"memory"}, True, "message"),
                "agent": PermissionRule({"agent"}, True, "message"),
                "git": PermissionRule({"git"}, True, "Gitmessage"),
            },
            
            PermissionLevel.YOLO: {
                # message:message
                "file_edit": PermissionRule({"file_edit"}, True, "message"),
                "file_read": PermissionRule({"file_read"}, True, "message"),
                "file_system": PermissionRule({"file_system"}, True, "message"),
                "system_command": PermissionRule({"system_command"}, True, "message"),
                "network": PermissionRule({"network"}, True, "message"),
                "memory": PermissionRule({"memory"}, True, "message"),
                "agent": PermissionRule({"agent"}, True, "message"),
                "git": PermissionRule({"git"}, True, "Gitmessage"),
            }
        }
    
    def get_tool_category(self, tool_name: str) -> Optional[str]:
        """Get the category of a tool."""
        for category, tools in self.tool_categories.items():
            if tool_name in tools:
                return category
        return None
    
    def should_auto_approve(self, tool_name: str, **kwargs) -> bool:
        # message
        category = self.get_tool_category(tool_name)
        if not category:
            return False
        
        #message
        rules = self.permission_rules.get(self.permission_level, {})
        rule = rules.get(category)
        if not rule:
            return False
        
        # message,message
        if category == "system_command" and rule.auto_approve:
            return self._is_safe_system_command(tool_name, **kwargs)

        # message 
        return rule.auto_approve
    
    def _is_safe_system_command(self, tool_name: str, **kwargs) -> bool:
        """Check if a system command is safe for auto-approval."""
        if tool_name!= "bash":
            return True
        
        command = kwargs.get("command", "")
        if not command:
            return True
        
        # High risk commands that should always require confirmation
        high_risk_commands = [
            "rm -rf", "del /s", "format", "fdisk", "mkfs", "dd", 
            "shutdown", "reboot", "halt", "poweroff"
        ]
        
        command_lower = command.lower()
        for risk_cmd in high_risk_commands:
            if risk_cmd in command_lower:
                return False
        
        return True
    
    def get_permission_description(self) -> str:
        """Get description of current permission level."""
        descriptions = {
            PermissionLevel.LOCKED: "🔒 message:message",
            PermissionLevel.EDIT_ONLY: "✏️ message:message,message",
            PermissionLevel.PLANNING: "🧠 message:message,message",
            PermissionLevel.YOLO: "🚀 message:message"
        }
        return descriptions.get(self.permission_level, "message")
    
    def set_permission_level(self, level: PermissionLevel):
        """Set permission level."""
        self.permission_level = level
    
    def get_permission_level(self) -> PermissionLevel:
        """Get current permission level."""
        return self.permission_level
    
    def get_available_levels(self) -> Dict[str, str]:
        """Get all available permission levels with descriptions."""
        return {
            "locked": "🔒 message:message",
            "edit_only": "✏️ message:message,message", 
            "planning": "🧠 message:message,message",
            "yolo": "🚀 message:message"
        }
    
    def get_tool_permission_info(self, tool_name: str) -> Dict[str, Any]:
        """Get permission information for a specific tool."""
        category = self.get_tool_category(tool_name)
        auto_approve = self.should_auto_approve(tool_name)
        
        rules = self.permission_rules.get(self.permission_level, {})
        rule = rules.get(category) if category else None
        
        return {
            "tool_name": tool_name,
            "category": category or "unknown",
            "auto_approve": auto_approve,
            "permission_level": self.permission_level.value,
            "rule_description": rule.description if rule else "message,message"
        }
