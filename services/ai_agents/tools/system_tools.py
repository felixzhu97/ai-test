"""System command execution tools."""

from typing import List, Type
import subprocess
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from langchain_core.tools import tool


class CommandInput(BaseModel):
    command: str
    description: str = "Shell command to execute"


@tool("execute_command", args_schema=CommandInput)
def execute_command(command: str) -> str:
    """Execute a shell command and return the output.
    
    Use this tool to run system commands like kubectl, docker, git, etc.
    
    Examples:
    - kubectl get pods
    - docker ps
    - curl http://api/endpoint
    - git status
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout if result.stdout else result.stderr
        if result.returncode != 0 and not output:
            output = f"Command failed with return code {result.returncode}"
        return output.strip()
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def get_system_tools() -> List[BaseTool]:
    """Get all system command tools."""
    return [execute_command]
