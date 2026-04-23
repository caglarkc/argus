import tempfile
import yaml
import pytest

from argus.config.manager import ConfigManager

@pytest.fixture
def sample_yaml_config():
    """
    message YAML message,message ConfigManager.
    """
    data = {
        "default_agent": "argus",
        "permission_level": "locked",
        "agents": [
            {
                "agent_name": "argus",
                "api_key": "yaml_qwen_key",
                "base_url": "https://qwen.com",
                "model": "qwen3-coder",
            },
            {
                "agent_name": "claude",
                "api_key": "yaml_claude_key",
                "base_url": "https://claude.com",
                "model": "claude-4.5",
            }
        ],
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w") as f:
        yaml.safe_dump(data, f, allow_unicode=True)
        return f.name


class DummyArgs:
    """
    message CLI message
    """
    def __init__(self,
        config=None,
        agent=None,
        api_key=None,
        base_url=None,
        model=None,
        temperature=None,
        max_tokens=None,
        permission_mode=None,):
        self.config = config
        self.agent = agent
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.permission_mode = permission_mode


def test_load_default_agent(sample_yaml_config):
    """
    message:message default_agent message argus
    """
    args = DummyArgs(config=sample_yaml_config)
    mgr = ConfigManager(args.config)

    cfg = mgr.get_app_config(args)

    assert cfg.active_agent_name == "argus"
    assert cfg.active_agent.model == "qwen3-coder"


def test_switch_agent(sample_yaml_config):
    """
    message:message agent message
    """
    args = DummyArgs(config=sample_yaml_config)
    mgr = ConfigManager(args.config)

    mgr.get_app_config(args)
    cfg2 = mgr.switch_active_agent("claude", args)

    assert cfg2.active_agent_name == "claude"
    assert cfg2.active_agent.model == "claude-4.5"


def test_cli_override(sample_yaml_config):
    """
    message:CLI message YAML message
    """
    args = DummyArgs(config=sample_yaml_config,
        api_key="cli_api_key",
        model="cli_model",)
    mgr = ConfigManager(args.config)
    cfg = mgr.get_app_config(args)

    assert cfg.active_agent.api_key == "cli_api_key"
    assert cfg.active_agent.model == "cli_model"


def test_env_fallback(sample_yaml_config, monkeypatch):
    """
    message:YAML message,ENV message
    """
    # message YAML:message argus message api_key
    data = yaml.safe_load(open(sample_yaml_config))
    data["agents"][0]["api_key"] = None

    new_file = tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode="w")
    yaml.safe_dump(data, new_file)
    new_file.close()

    # message
    monkeypatch.setenv("ARGUS_ARGUS_API_KEY", "env_api_key")

    args = DummyArgs(config=new_file.name)

    mgr = ConfigManager(args.config)
    cfg = mgr.get_app_config(args)

    assert cfg.active_agent.api_key == "env_api_key"

