import subprocess
import os
from typing import List, Dict, Union, Optional # Optional hinzugefügt
from crewai.tools import tool

# --- Die Logik-Klasse für die Befehlsausführung ---
class CommandExecutionLogic:
    def _sanitize_output(self, output: str) -> str:
        """
        A very basic and initial attempt to sanitize output.
        This needs to be significantly improved for production to prevent leaking sensitive info.
        For now, it's a placeholder.
        """
        # TODO: Implement robust output scrubbing (e.g., for API keys, passwords, specific paths)
        return output

    def execute_command(self, command_list: List[str], working_directory: Optional[str] = None) -> Dict[str, Union[str, int, None]]: # working_directory als Optional markiert
        """
        Executes a system command securely using subprocess.

        Args:
            command_list (List[str]): The command and its arguments as a list of strings.
            working_directory (str, optional): The directory in which to execute the command.
                                               Defaults to the current working directory.

        Returns:
            Dict[str, Union[str, int, None]]: A dictionary containing:
                'stdout': The standard output of the command (string, sanitized).
                'stderr': The standard error of the command (string, sanitized).
                'returncode': The exit code of the command (int).
                'error': An error message if the command execution itself failed (string, or None).
        """
        result = {
            "stdout": None,
            "stderr": None,
            "returncode": None,
            "error": None
        }
        
        if not isinstance(command_list, list) or not all(isinstance(item, str) for item in command_list):
            result["error"] = "TOOL_ERROR: Command must be provided as a list of strings."
            return result
        
        if not command_list:
            result["error"] = "TOOL_ERROR: Command list cannot be empty."
            return result

        effective_cwd = working_directory if working_directory else os.getcwd()
        print(f"--- Debug (execute_command): Executing command: {' '.join(command_list)} in directory: {effective_cwd} ---")

        try:
            process = subprocess.run(
                command_list,
                capture_output=True,
                text=True,
                cwd=working_directory, 
                shell=False, 
                check=False 
            )
            result["stdout"] = self._sanitize_output(process.stdout.strip())
            result["stderr"] = self._sanitize_output(process.stderr.strip())
            result["returncode"] = process.returncode

            if process.returncode != 0:
                print(f"--- Debug (execute_command): Command exited with code {process.returncode}. Stderr: {process.stderr.strip()} ---")
            else:
                print(f"--- Debug (execute_command): Command executed successfully. Stdout: {process.stdout.strip()} ---")

        except FileNotFoundError:
            error_msg = f"TOOL_ERROR: Command not found: '{command_list[0]}'. Ensure it's in PATH or provide full path."
            print(f"--- Debug (execute_command): {error_msg} ---")
            result["error"] = error_msg
            result["returncode"] = -1 
        except Exception as e:
            error_msg = f"TOOL_ERROR: An unexpected error occurred while trying to execute the command: {e}"
            print(f"--- Debug (execute_command): {error_msg} ---")
            result["error"] = error_msg
            result["returncode"] = -2 
        
        return result

_command_execution_logic = CommandExecutionLogic()

@tool("Secure Command Executor Tool")
def secure_command_executor_tool(command: str, arguments: Optional[List[str]] = None, working_directory: Optional[str] = None) -> Dict[str, Union[str, int, None]]:
    """
    Executes a system command securely. 
    The command and its arguments should be provided carefully.
    This tool should be used for tasks like running scripts, build processes, or linters.
    It returns a dictionary with 'stdout', 'stderr', 'returncode', and 'error' (if any).

    Args:
        command (str): The main command to execute (e.g., "node", "python", "npm", "git").
        arguments (Optional[List[str]]): A list of arguments for the command. Defaults to an empty list.
        working_directory (Optional[str]): The directory in which to execute the command. 
                                           If None, uses the current working directory of the agent system.
                                           It's highly recommended to specify an absolute path within the project's
                                           application_code directory.
    """
    print(f"--- Debug (Tool Call): 'Secure Command Executor Tool' called with command: '{command}', args: {arguments}, cwd: {working_directory} ---")
    
    if not command:
        return {"stdout": "", "stderr": "TOOL_ERROR: 'command' argument cannot be empty.", "returncode": -1, "error": "TOOL_ERROR: 'command' argument cannot be empty."}

    command_list = [command]
    if arguments:
        if not isinstance(arguments, list) or not all(isinstance(arg, str) for arg in arguments):
            return {"stdout": "", "stderr": "TOOL_ERROR: 'arguments' must be a list of strings.", "returncode": -1, "error": "TOOL_ERROR: 'arguments' must be a list of strings."}
        command_list.extend(arguments)
    
    if working_directory:
        if ".." in working_directory : # Simple check, can be improved
             print(f"--- Debug (Tool Call): Warning - working_directory '{working_directory}' contains '..'. Ensure it's a safe, absolute path within the project sandbox. ---")
        if not os.path.isabs(working_directory) and not os.path.exists(working_directory): # Check if relative path exists from CWD
            print(f"--- Debug (Tool Call): Warning - relative working_directory '{working_directory}' does not exist from CWD. This might lead to errors. Using CWD instead if it's not found later by subprocess.")
            # subprocess.run will use CWD if cwd=None or if the path is invalid in some OS,
            # but it's better to be explicit or ensure the path is valid.
            # For now, we pass it as is and let subprocess handle it, but logging a warning.

    execution_result = _command_execution_logic.execute_command(command_list, working_directory)
    print(f"--- Debug (Tool Call): Execution result: {execution_result} ---")
    return execution_result
