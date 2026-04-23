# Argus English

```
Argus/
├── agents/                             # English
|   └── qwen/                           # Qwen English
|       ├── qwen_agent.py               # Qwen English
|       ├── turn.py                     # Qwen English
|       ├── task_continuation_checker.py    # English
|       └── loop_detection_service.py   # Qwen English
|   base_agent.py                       # English
├── config/                             # English
│   ├── config.py                       # English,English
|   └── loader.py                       # English
├── core/                               # English
│   ├── client.py                       # EnglishLLM English,English
│   ├── tool_scheduler.py               # English
│   ├── tool_executor.py                # English
│   ├── tool_registry.py                # English
|   └── trajectory_recorder.py          # English
├── tools/                              # English
│   ├── base.py                         # English,English
│   ├── bash_tool.py                    # Shell English
│   ├── edit_tool.py                    # English
│   ├── file_tools.py                   # English(English, English)
│   ├── glob_tool.py                    # English glob English
│   ├── grep_tool.py                    # English grep English
│   ├── ls_tool.py                      # English ls English
│   ├── memory_tool.py                  # English
│   ├── read_many_files_tool.py         # English
│   ├── web_fetch_tool.py               # English
│   └── web_search_tool.py              # English(English Serper API)
├── docs/                               # English
│   └── project-structure.md            # English
├── trajectories/                       # English(English)
│   └── trajectory_xxxxxx.json          # English,English LLM English
├── ui/                                 # CLI English
|   ├── commands/                       # English  
|   |   ├── __init__.py                 # English
|   |   ├── about_command.py            # English
|   |   ├── auth_command.py             # English
|   |   ├── base_command.py             # English
|   |   ├── clear_command.py            # English
|   |   ├── help_command.py             # English
|   |   ├── memory_command.py           # English
|   |   ├── quit_command.py             # English
|   |   └──...
|   |── utils/                          # English
|   |   └── keyboard.py                 # English
│   ├── cli_console.py                  # CLI English
│   ├── command_processor.py            # English
|   └── config_wizard.py                # English│   
├── utils                               # English
|   ├── __init__.py
|   ├── base_content_generator.py       # English,English
|   ├── qwen_content_generator.py       # Qwen English
|   ├── llm_basics.py                   # LLM English
|   ├── llm_client.py                   # LLM English
|   ├── llm_config.py                   # LLM English
|   └── token_limits.py                 # Token English
├── cli.py                              # CLI English,English `argus` English
├── pyproject.toml                      # English(English, English, English)
├── README.md                           # English(English)
├── README_ch.md                        # English(English)
└── argus_config.json                   # English(API English, English, English)
```