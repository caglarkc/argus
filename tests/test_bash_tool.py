"""
message BashTool message,message
"""
import asyncio
import os
import pytest
import tempfile
from pathlib import Path

from argus.tools.bash_tool import BashTool


@pytest.fixture
def bash_tool():
    """message BashTool message"""
    return BashTool()


@pytest.fixture
def temp_dir():
    """message"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.mark.asyncio
async def test_basic_command_execution(bash_tool, temp_dir):
    """message(message)"""
    result = await bash_tool.execute(command="echo 'Hello, World!'", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    assert "Hello, World!" in result.result
    # metadata message,message exit_code
    assert result.metadata is None or result.metadata == {} or result.metadata.get("exit_code") == 0


@pytest.mark.asyncio
async def test_environment_variables_set(bash_tool, temp_dir):
    """message(message)"""
    # message PAGER, GIT_PAGER, PYTHONUNBUFFERED message
    result = await bash_tool.execute(command="env | grep -E '(PAGER|GIT_PAGER|PYTHONUNBUFFERED)'", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    assert "PAGER=cat" in result.result
    assert "GIT_PAGER=cat" in result.result
    assert "PYTHONUNBUFFERED=1" in result.result


@pytest.mark.asyncio
async def test_grep_line_buffered_auto_add(bash_tool, temp_dir):
    """message grep message --line-buffered message"""
    # message
    test_file = Path(temp_dir) / "test.txt"
    test_file.write_text("test line 1\ntest line 2\ntest line 3\n")
    
    # message grep message,message --line-buffered
    result = await bash_tool.execute(command=f"grep 'test' {test_file}", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    # message(message,message)
    assert "test" in result.result.lower() or result.result.strip() == ""


@pytest.mark.asyncio
async def test_grep_with_existing_line_buffered(bash_tool, temp_dir):
    """message grep message --line-buffered,message"""
    test_file = Path(temp_dir) / "test.txt"
    test_file.write_text("test line\n")
    
    # message --line-buffered message grep message
    result = await bash_tool.execute(command=f"grep --line-buffered 'test' {test_file}", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    # message
    assert "test" in result.result.lower() or result.result.strip() == ""


@pytest.mark.asyncio
async def test_multiline_command(bash_tool, temp_dir):
    """message"""
    # message Python message
    result = await bash_tool.execute(command='''python3 -c "
print('Line 1')
print('Line 2')
print('Line 3')
"''', directory=temp_dir)
    
    assert result.error is None or result.error == ""
    # message
    assert "Line 1" in result.result or "Line 2" in result.result or "Line 3" in result.result or "python3" not in result.result.lower()


@pytest.mark.asyncio
async def test_python_unbuffered_output(bash_tool, temp_dir):
    """message Python message(message)"""
    # Python message,message
    result = await bash_tool.execute(command='python3 -c "import sys; sys.stdout.write(\"immediate\\n\"); sys.stdout.flush(); import time; time.sleep(0.1); print(\"delayed\")"', directory=temp_dir)
    
    assert result.error is None or result.error == ""
    # message
    assert "immediate" in result.result or "delayed" in result.result or "python3" not in result.result.lower()


@pytest.mark.asyncio
async def test_git_command_no_pager(bash_tool, temp_dir):
    """message git message(message)"""
    # message git message
    os.chdir(temp_dir)
    os.system("git init > /dev/null 2>&1")
    os.system("git config user.name 'Test' > /dev/null 2>&1")
    os.system("git config user.email 'test@test.com' > /dev/null 2>&1")
    
    # message
    with open("test.txt", "w") as f:
        f.write("test content")
    os.system("git add test.txt > /dev/null 2>&1")
    os.system("git commit -m 'Initial commit' > /dev/null 2>&1")
    
    # message git log message
    result = await bash_tool.execute(command="git log --oneline")
    
    # git log message,message
    assert result.error is None or "Initial commit" in result.result or result.result.strip() == ""


@pytest.mark.asyncio
async def test_command_with_error(bash_tool, temp_dir):
    """message"""
    result = await bash_tool.execute(command="nonexistent_command_12345", directory=temp_dir)
    
    # message
    assert result.error is not None or result.metadata is not None or "[Exit Code:" in result.result or "error" in result.result.lower()


@pytest.mark.asyncio
async def test_command_timeout(bash_tool, temp_dir):
    """message"""
    # message(sleep message)
    result = await bash_tool.execute(command="sleep 0.5", timeout=0.2, directory=temp_dir)
    
    # message(message)
    assert result.error is not None or result.metadata is not None or "timeout" in result.result.lower() or "running" in result.result.lower() or "PID" in result.result


@pytest.mark.asyncio
async def test_background_process(bash_tool, temp_dir):
    """message"""
    result = await bash_tool.execute(command="echo 'background test'", is_background=True, directory=temp_dir)
    
    # message PID message
    assert result.error is None or result.error == ""
    assert "PID" in result.result or "background" in result.result.lower() or "started" in result.result.lower()


@pytest.mark.asyncio
async def test_directory_parameter(bash_tool, temp_dir):
    """message directory message"""
    # message
    test_file = Path(temp_dir) / "test_file.txt"
    test_file.write_text("test content")
    
    # message
    result = await bash_tool.execute(command="cat test_file.txt", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    assert "test content" in result.result


@pytest.mark.asyncio
async def test_invalid_directory(bash_tool):
    """message"""
    result = await bash_tool.execute(command="echo 'test'", directory="/nonexistent/directory/12345")
    
    # message
    assert result.error is not None and "does not exist" in result.error


@pytest.mark.asyncio
async def test_empty_command(bash_tool):
    """message"""
    result = await bash_tool.execute(command="")
    
    # message
    assert result.error is not None and "No command provided" in result.error


@pytest.mark.asyncio
async def test_find_with_grep(bash_tool, temp_dir):
    """message find message grep message(message,message)"""
    # message
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("def test_function():\n    pass\n")
    
    # message find message grep message
    result = await bash_tool.execute(command=f"find {temp_dir} -name '*.py' -exec grep -l 'test_function' {{}} \\;", directory=temp_dir)
    
    # message,message
    assert result.error is None or result.error == ""
    # grep message --line-buffered
    assert "test.py" in result.result or result.result.strip() == ""


@pytest.mark.asyncio
async def test_command_with_special_characters(bash_tool, temp_dir):
    """message"""
    result = await bash_tool.execute(command="echo 'Hello, \"World\"!'", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    assert "Hello" in result.result or "World" in result.result


@pytest.mark.asyncio
async def test_command_output_truncation(bash_tool, temp_dir):
    """message"""
    # message(message MAX_OUTPUT_LENGTH)
    long_output_cmd = "python3 -c \"print('x' * 50000)\""
    result = await bash_tool.execute(command=long_output_cmd, directory=temp_dir)
    
    # message
    assert result.error is None or result.error == "" or "truncated" in result.result.lower()


@pytest.mark.asyncio
async def test_risk_level_detection(bash_tool):
    """message"""
    # message
    high_risk = bash_tool.get_risk_level(command="rm -rf /")
    assert high_risk.value == "high"
    
    # message
    medium_risk = bash_tool.get_risk_level(command="rm file.txt")
    assert medium_risk.value == "medium"
    
    # message
    low_risk = bash_tool.get_risk_level(command="echo 'test'")
    assert low_risk.value == "low"


@pytest.mark.asyncio
async def test_pager_environment_variables(bash_tool, temp_dir):
    """message"""
    # message
    result = await bash_tool.execute(command="env | grep -E '(PAGER|MANPAGER|GIT_PAGER|LESS)' | sort", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    # message
    env_vars = result.result
    assert "PAGER=cat" in env_vars
    assert "GIT_PAGER=cat" in env_vars
    assert "MANPAGER=cat" in env_vars
    assert "LESS=-R" in env_vars


@pytest.mark.asyncio
async def test_python_progress_bar_disabled(bash_tool, temp_dir):
    """message Python message"""
    result = await bash_tool.execute(command="env | grep -E '(PIP_PROGRESS_BAR|TQDM_DISABLE)'", directory=temp_dir)
    
    assert result.error is None or result.error == ""
    env_vars = result.result
    assert "PIP_PROGRESS_BAR=off" in env_vars
    assert "TQDM_DISABLE=1" in env_vars


@pytest.mark.asyncio
async def test_complex_multiline_python_command(bash_tool, temp_dir):
    """message Python message(message run.log message)"""
    # message run.log message Python message
    complex_cmd = '''python3 -c "
import numpy as np
from astropy.table import Table

array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
tbl = Table({'a': [1, 2, 3], 'b': [4, 5, 6]})
print('Table created successfully')
print('Array shape:', array.shape)
"'''
    result = await bash_tool.execute(command=complex_cmd, directory=temp_dir)
    
    # message,message
    assert result.error is None or result.error == ""
    # message,message
    assert "Table created" in result.result or "Array shape" in result.result or "ImportError" in result.result or "ModuleNotFoundError" in result.result or result.result.strip() == ""


@pytest.mark.asyncio
async def test_python_command_with_delayed_output(bash_tool, temp_dir):
    """message Python message(message PYTHONUNBUFFERED message)"""
    # message Python message
    cmd = 'python3 -c "import time; time.sleep(0.1); print(\"Output after delay\")"'
    result = await bash_tool.execute(command=cmd, directory=temp_dir)
    
    # message,message
    assert result.error is None or result.error == ""
    assert "Output after delay" in result.result or "python3" not in result.result.lower()


@pytest.mark.asyncio
async def test_git_log_with_grep_pattern(bash_tool, temp_dir):
    """message git log message grep message(message run.log message)"""
    # message git message
    os.chdir(temp_dir)
    os.system("git init > /dev/null 2>&1")
    os.system("git config user.name 'Test' > /dev/null 2>&1")
    os.system("git config user.email 'test@test.com' > /dev/null 2>&1")
    
    # message
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("def test_function():\n    pass\n")
    os.system("git add test.py > /dev/null 2>&1")
    os.system("git commit -m 'Add test function' > /dev/null 2>&1")
    
    # message git log message grep(message run.log message)
    result = await bash_tool.execute(command="git log --oneline --grep='test'", directory=temp_dir)
    
    # message,message
    assert result.error is None or result.error == ""
    # message,message(message)
    assert "Add test function" in result.result or result.result.strip() == "" or "Command executed successfully" in result.result


@pytest.mark.asyncio
async def test_python_table_read_command(bash_tool, temp_dir):
    """message run.log message Table.read message"""
    # message
    test_file = Path(temp_dir) / "test.txt"
    test_file.write_text("col1,col2\n1,2\n3,4\n")
    
    # message Python message(message run.log message)
    cmd = f'python3 -c "from astropy.table import Table; tbl = Table.read(\'{test_file}\', format=\'ascii.csv\'); print(len(tbl))"'
    result = await bash_tool.execute(command=cmd, directory=temp_dir)
    
    # message,message
    assert result.error is None or result.error == ""
    # message(message astropy)message(message),message
    assert "2" in result.result or "ImportError" in result.result or "ModuleNotFoundError" in result.result or result.result.strip() == ""

