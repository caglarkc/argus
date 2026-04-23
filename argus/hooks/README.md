# Hooks English **Argus** English Hook English.

---

## English

* English:`~/.argus/argus_hooks.json`
* English:`HookManager.emit(event,...)`
* English:
  * English matcher:`UserPromptSubmit`, `Stop` English
  * English matcher(English):`PreToolUse`, `PostToolUse`
* I/O English:Hook English **stdin** English JSON；English **stdout/stderr + exit code** English **JSON stdout** English
* English:`transcript_path`, `ARGUS_PROJECT_DIR`(English)

---

## English

### 1) EnglishargusEnglish `argus_hooks.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "./.argus/hooks/prompt_guard.py" } ] }
    ],
    "PreToolUse": [
      {
        "matcher": "bash|write_file|edit",
        "hooks": [ { "type": "command", "command": "./.argus/hooks/pre_check.py", "timeout": 5 } ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "write_file|edit|bash",
        "hooks": [ { "type": "command", "command": "./.argus/hooks/post_audit.py" } ]
      }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "./.argus/hooks/stop_test.py" } ] }
    ]
  }
}
```

> `matcher`:English `PreToolUse`/`PostToolUse` English；English.English, English, `*`/English(English).

### 2) English

```bash
chmod +x./.argus/hooks/*.py
```

### 3) Qwen Agent English

* English:English `PreToolUse`(English)
* English:English `PostToolUse`(English, English)
* English:English `UserPromptSubmit`(English)
* English:English `Stop`(English“English”English)

---

## Hook English(stdin JSON)

English:

```json
{
  "session_id": "abc123",
  "cwd": "/current/working/dir",
  "hook_event_name": "PreToolUse" // or PostToolUse / UserPromptSubmit / Stop...
}
```

English:

* **PreToolUse**:`tool_name: str`, `tool_input: dict`
* **PostToolUse**:`tool_name: str`, `tool_input: dict`, `tool_response: dict`
* **UserPromptSubmit**:`prompt: str`
* **Stop**:`stop_hook_active: bool`

---

## Hook English(English)

### A. English:English + English

* `exit 0`:English(English).`stdout` English；`stderr` English UI English(English,English **English**).
* `exit 2`:**English**.`stderr` English/English.
* English 0:English,English `stderr` English(“English”).

### B. English:JSON English `stdout`

* English:

  ```json
  {
    "continue": true,                // English false English
    "stopReason": "string",          // English
    "systemMessage": "string"        // English UI English/English
  }
  ```
* **PreToolUse** English:

  ```json
  {
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "allow" | "deny" | "ask",
      "permissionDecisionReason": "string"
    }
  }
  ```
* **PostToolUse** English:

  ```json
  {
    "decision": "block",             // English(English)
    "reason": "string",
    "hookSpecificOutput": {
      "hookEventName": "PostToolUse",
      "additionalContext": "string"  // English system English
    }
  }
  ```
* **UserPromptSubmit**:

  ```json
  {
    "decision": "block",
    "reason": "string",
    "hookSpecificOutput": {
      "hookEventName": "UserPromptSubmit",
      "additionalContext": "string"
    }
  }
  ```
* **Stop**:

  ```json
  { "decision": "block", "reason": "string" }
  ```

---

## English

### 1) UserPromptSubmit(English + English)

`./.argus/hooks/prompt_guard.py`

```python
#!/usr/bin/env python3
import json, re, sys, datetime
d = json.load(sys.stdin)
p = d.get("prompt","")

if re.search(r"(?i)\b(password|api[_-]?key|secret|token)\s*[:=]", p):
    print(json.dumps({"decision":"block","reason":"Prompt contains potential secrets. Please remove them."}))
    sys.exit(0)

print(json.dumps({
  "systemMessage": "🛈 Prompt checked by hook.",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": f"[HOOK] Time={datetime.datetime.now().isoformat()}"
  }
}))
sys.exit(0)
```

### 2) PreToolUse(English)

`./.argus/hooks/pre_check.py`

```python
#!/usr/bin/env python3
import json, sys
d = json.load(sys.stdin)
tool = d.get("tool_name")
inp  = d.get("tool_input", {})
print(f"✅ [PreToolUse] {tool} about to run, input={inp}", file=sys.stderr)
sys.exit(1)  # English 0 English!= 2 => English,English
```

> English,English:
>
> ```python
> print(json.dumps({
>   "hookSpecificOutput":{
>     "hookEventName":"PreToolUse",
>     "permissionDecision":"deny",
>     "permissionDecisionReason":"Dangerous command detected."
>   }
> }))
> sys.exit(0)
> ```

### 3) PostToolUse(English + English,English)

`./.argus/hooks/post_audit.py`

```python
#!/usr/bin/env python3
import json
d = json.load(sys.stdin)
tool = d.get("tool_name")
print(json.dumps({
  "systemMessage": f"📣 [PostToolUse] {tool} finished.",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": f"[HOOK] {tool} completed successfully."
  }
}))
sys.exit(0)
```

> English“English”(English),English:
>
> ```python
> print(json.dumps({"decision":"block","reason":"Lint failed: please fix format"}))
> sys.exit(0)
> ```

### 4) Stop(English)

`./.argus/hooks/stop_test.py`

```python
#!/usr/bin/env python3
import sys
print("✅ [Stop] hook executed (non-blocking).", file=sys.stderr)
sys.exit(1)
```

> English(English):
>
> ```python
> print(json.dumps({"decision":"block","reason":"Please continue with a short summary."}))
> sys.exit(0)
> ```

---

## English

* English Qwen agent English `PreToolUse`/`PostToolUse`,English hook English `msg`；English“English/English”,English.
* `UserPromptSubmit` English agent English；`systemMessage`/`stderr` English；`additionalContext` English **system** English.
* `Stop` English；`stderr` English `systemMessage` English；`block` English(English).

---

## matcher English

* English `PreToolUse`/`PostToolUse`:English `tool_name` English(English)
* English:

  * English:`"write_file"`
  * English:`"edit|write_file"`
  * English:`"*"`, `""`, English (English `"bash"`, `"write_file"`, `"edit"` …).

---

## English

1. **English hook English**

   * English agent English `ok=True` English `msg`(English).
   * English, English.
   * English `matcher` English `tool_name`.

2. **PreToolUse English**

   * English agent English `pre_ok=False` English `continue` English(English).
   * English `exit 2` English JSON English `permissionDecision: "deny"`.

3. **PostToolUse English**

   * English `{"decision":"block","reason":"..."}`；agent English(English).

4. **English `126`**(English)

   * English `python script.py` English；English shebang `#!/usr/bin/env python3`.

---

## English(English LLM)

```python
ok, msg, extra = hook_mgr.emit(HookEvent.PreToolUse,
    base_payload={"session_id":"test","cwd":os.getcwd()},
    tool_name="bash",
    tool_input={"command":"echo ok"})
print("PRE:", ok, msg)

ok, msg, extra = hook_mgr.emit(HookEvent.PostToolUse,
    base_payload={"session_id":"test","cwd":os.getcwd()},
    tool_name="bash",
    tool_input={"command":"echo ok"},
    tool_response={"success": True, "result":"ok", "error": None})
print("POST:", ok, msg, extra)
```
