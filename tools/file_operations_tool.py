import os
import shutil
from pathlib import Path
from crewai.tools import tool

class FileOperationsLogic:
    """
    Contains the core logic for file system operations.
    Not intended to be a CrewAI Tool directly, but a helper class.
    """
    def write_file(self, file_path: str, content: str, overwrite: bool = False) -> str:
        try:
            path = Path(file_path)
            if path.exists() and not overwrite:
                return f"Error: File '{file_path}' already exists and 'overwrite' is set to False."
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"File '{file_path}' written successfully."
        except Exception as e:
            return f"Error writing file '{file_path}': {e}"

    def read_file(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' not found."
            if not path.is_file():
                return f"Error: '{file_path}' is not a file."
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file '{file_path}': {e}"

    def create_directory(self, directory_path: str, make_parents: bool = True, exist_ok: bool = True) -> str:
        try:
            path = Path(directory_path)
            path.mkdir(parents=make_parents, exist_ok=exist_ok)
            return f"Directory '{directory_path}' created successfully."
        except Exception as e:
            return f"Error creating directory '{directory_path}': {e}"

    def list_directory_contents(self, directory_path: str, recursive: bool = False) -> str:
        try:
            path = Path(directory_path)
            if not path.exists():
                return f"Error: Directory '{directory_path}' not found."
            if not path.is_dir():
                return f"Error: '{directory_path}' is not a directory."
            contents = []
            if recursive:
                for item in path.rglob('*'): 
                    contents.append(str(item.relative_to(path)))
            else:
                for item in path.iterdir():
                    contents.append(item.name)
            
            if not contents:
                return f"Directory '{directory_path}' is empty."
            header = f"Contents of '{directory_path}' (recursive: {recursive}):"
            return f"{header}\n--------------------\n" + "\n".join(contents)
        except Exception as e:
            return f"Error listing directory contents of '{directory_path}': {e}"

    def delete_file(self, file_path: str) -> str:
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' not found."
            if not path.is_file():
                return f"Error: '{file_path}' is not a file but a directory or something else."
            path.unlink() 
            return f"File '{file_path}' deleted successfully."
        except Exception as e:
            return f"Error deleting file '{file_path}': {e}"

    def delete_directory(self, directory_path: str, recursive: bool = False) -> str:
        try:
            path = Path(directory_path)
            if not path.exists():
                return f"Error: Directory '{directory_path}' not found."
            if not path.is_dir():
                return f"Error: '{directory_path}' is not a directory."
            
            if recursive:
                shutil.rmtree(path) 
                return f"Directory '{directory_path}' and its contents deleted recursively successfully."
            else:
                if any(path.iterdir()): 
                    return f"Error: Directory '{directory_path}' is not empty. Set 'recursive=True' to delete."
                path.rmdir() 
                return f"Empty directory '{directory_path}' deleted successfully."
        except Exception as e:
            return f"Error deleting directory '{directory_path}': {e}"

    def move_path(self, source_path: str, destination_path: str) -> str:
        try:
            src = Path(source_path)
            dst = Path(destination_path)

            if not src.exists():
                return f"Error: Source path '{source_path}' not found."

            if not dst.parent.exists():
                 dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src), str(dst))
            return f"Path '{source_path}' moved/renamed to '{destination_path}' successfully."
        except Exception as e:
            return f"Error moving/renaming from '{source_path}' to '{destination_path}': {e}"

    def copy_path(self, source_path: str, destination_path: str) -> str:
        try:
            src = Path(source_path)
            dst = Path(destination_path)

            if not src.exists():
                return f"Error: Source path '{source_path}' not found."

            if not dst.parent.exists():
                 dst.parent.mkdir(parents=True, exist_ok=True)

            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True) # Added dirs_exist_ok=True for robustness
                return f"Directory '{source_path}' copied to '{destination_path}' successfully."
            elif src.is_file():
                shutil.copy2(src, dst) 
                return f"File '{source_path}' copied to '{destination_path}' successfully."
            else:
                return f"Error: Source path '{source_path}' is neither a file nor a directory."
        except Exception as e:
            return f"Error copying from '{source_path}' to '{destination_path}': {e}"

_file_ops_logic = FileOperationsLogic()

@tool("Write File Tool")
def write_file_tool(file_path: str, content: str, overwrite: bool = False) -> str:
    """
    Writes the given content to the specified file.
    Creates the file and parent directories if they do not exist.
    
    Args:
        file_path (str): The full path to the file to be written.
        content (str): The content to write into the file.
        overwrite (bool): Whether to overwrite the file if it already exists. Defaults to False.
    """
    return _file_ops_logic.write_file(file_path, content, overwrite)

@tool("Read File Tool")
def read_file_tool(file_path: str) -> str:
    """
    Reads the content of the specified file and returns it as a string.

    Args:
        file_path (str): The full path to the file to be read.
    """
    return _file_ops_logic.read_file(file_path)

@tool("Create Directory Tool")
def create_directory_tool(directory_path: str, make_parents: bool = True, exist_ok: bool = True) -> str:
    """
    Creates the specified directory.

    Args:
        directory_path (str): The full path to the directory to be created.
        make_parents (bool): If True, create parent directories as needed. Defaults to True.
        exist_ok (bool): If True, do not raise an error if the directory already exists. Defaults to True.
    """
    return _file_ops_logic.create_directory(directory_path, make_parents, exist_ok)

@tool("List Directory Contents Tool")
def list_directory_contents_tool(directory_path: str, recursive: bool = False) -> str:
    """
    Lists the contents (files and subdirectories) of the specified directory.

    Args:
        directory_path (str): The full path to the directory.
        recursive (bool): Whether to list contents of all subdirectories recursively. Defaults to False.
    """
    return _file_ops_logic.list_directory_contents(directory_path, recursive)

@tool("Delete File Tool")
def delete_file_tool(file_path: str) -> str:
    """
    Deletes the specified file.

    Args:
        file_path (str): The full path to the file to be deleted.
    """
    return _file_ops_logic.delete_file(file_path)

@tool("Delete Directory Tool")
def delete_directory_tool(directory_path: str, recursive: bool = False) -> str:
    """
    Deletes the specified directory. 
    If 'recursive' is True, the directory and all its contents will be deleted.
    If 'recursive' is False (default), only an empty directory will be deleted.

    Args:
        directory_path (str): The full path to the directory to be deleted.
        recursive (bool): Whether to delete the directory recursively (including contents). Defaults to False.
    """
    return _file_ops_logic.delete_directory(directory_path, recursive)

@tool("Move/Rename Path Tool")
def move_path_tool(source_path: str, destination_path: str) -> str:
    """
    Moves or renames a file or directory.
    If 'destination_path' is an existing directory, 'source_path' is moved into it.
    If 'destination_path' does not exist, 'source_path' is renamed/moved to 'destination_path'.

    Args:
        source_path (str): The source path of the file or directory.
        destination_path (str): The destination path or new name.
    """
    return _file_ops_logic.move_path(source_path, destination_path)

@tool("Copy Path Tool")
def copy_path_tool(source_path: str, destination_path: str) -> str:
    """
    Copies a file or a directory (recursively).
    If 'destination_path' is an existing directory, 'source_path' is copied into it.
    If 'destination_path' is a file and 'source_path' is a file, it will be overwritten (use with caution!).
    If 'destination_path' is a new path, 'source_path' is copied to it.

    Args:
        source_path (str): The source path of the file or directory.
        destination_path (str): The destination path.
    """
    return _file_ops_logic.copy_path(source_path, destination_path)
