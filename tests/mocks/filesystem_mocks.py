"""
File System Mock Implementations

This module provides comprehensive mocks for file system operations including
file I/O, directory operations, and file metadata.
"""

import os
import tempfile
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, BinaryIO, TextIO
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import stat


class MockFile:
    """Mock implementation for file objects."""
    
    def __init__(self, path: str, mode: str = 'r', content: str = ""):
        self.path = path
        self.mode = mode
        self.content = content
        self.position = 0
        self.closed = False
        self._is_binary = 'b' in mode
    
    def read(self, size: int = -1) -> Union[str, bytes]:
        """Mock read operation."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        
        if size == -1:
            result = self.content[self.position:]
            self.position = len(self.content)
        else:
            result = self.content[self.position:self.position + size]
            self.position += len(result)
        
        return result.encode() if self._is_binary else result
    
    def write(self, data: Union[str, bytes]) -> int:
        """Mock write operation."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        
        if self._is_binary and isinstance(data, str):
            data = data.encode()
        elif not self._is_binary and isinstance(data, bytes):
            data = data.decode()
        
        # Insert data at current position
        self.content = self.content[:self.position] + data + self.content[self.position:]
        self.position += len(data)
        return len(data)
    
    def readline(self) -> Union[str, bytes]:
        """Mock readline operation."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        
        newline_pos = self.content.find('\n', self.position)
        if newline_pos == -1:
            result = self.content[self.position:]
            self.position = len(self.content)
        else:
            result = self.content[self.position:newline_pos + 1]
            self.position = newline_pos + 1
        
        return result.encode() if self._is_binary else result
    
    def readlines(self) -> List[Union[str, bytes]]:
        """Mock readlines operation."""
        lines = []
        while True:
            line = self.readline()
            if not line:
                break
            lines.append(line)
        return lines
    
    def writelines(self, lines: List[Union[str, bytes]]):
        """Mock writelines operation."""
        for line in lines:
            self.write(line)
    
    def seek(self, position: int, whence: int = 0):
        """Mock seek operation."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        
        if whence == 0:  # SEEK_SET
            self.position = position
        elif whence == 1:  # SEEK_CUR
            self.position += position
        elif whence == 2:  # SEEK_END
            self.position = len(self.content) + position
        
        return self.position
    
    def tell(self) -> int:
        """Mock tell operation."""
        if self.closed:
            raise ValueError("I/O operation on closed file")
        return self.position
    
    def flush(self):
        """Mock flush operation."""
        pass
    
    def close(self):
        """Mock close operation."""
        self.closed = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __iter__(self):
        """Mock iteration."""
        return iter(self.readlines())


class MockPath:
    """Mock implementation for Path objects."""
    
    def __init__(self, path: str):
        self._path = str(path)
        self._parts = Path(path).parts
        self._name = Path(path).name
        self._stem = Path(path).stem
        self._suffix = Path(path).suffix
        self._parent = Path(path).parent
        self._exists = False
        self._is_file = False
        self._is_dir = False
        self._size = 0
        self._stat = None
    
    def __str__(self):
        return self._path
    
    def __repr__(self):
        return f"MockPath('{self._path}')"
    
    def __truediv__(self, other):
        return MockPath(str(self) + "/" + str(other))
    
    def exists(self) -> bool:
        """Mock exists check."""
        return self._exists
    
    def is_file(self) -> bool:
        """Mock is_file check."""
        return self._is_file
    
    def is_dir(self) -> bool:
        """Mock is_dir check."""
        return self._is_dir
    
    def is_symlink(self) -> bool:
        """Mock is_symlink check."""
        return False
    
    def is_absolute(self) -> bool:
        """Mock is_absolute check."""
        return os.path.isabs(self._path)
    
    def resolve(self):
        """Mock resolve operation."""
        return MockPath(os.path.abspath(self._path))
    
    def absolute(self):
        """Mock absolute operation."""
        return MockPath(os.path.abspath(self._path))
    
    def stat(self):
        """Mock stat operation."""
        if self._stat is None:
            self._stat = MockStat(
                st_size=self._size,
                st_mtime=datetime.now().timestamp(),
                st_ctime=datetime.now().timestamp(),
                st_atime=datetime.now().timestamp()
            )
        return self._stat
    
    def lstat(self):
        """Mock lstat operation."""
        return self.stat()
    
    def chmod(self, mode: int):
        """Mock chmod operation."""
        pass
    
    def unlink(self, missing_ok: bool = False):
        """Mock unlink operation."""
        if not self._exists and not missing_ok:
            raise FileNotFoundError(f"No such file: '{self._path}'")
        self._exists = False
        self._is_file = False
    
    def rmdir(self):
        """Mock rmdir operation."""
        if not self._is_dir:
            raise NotADirectoryError(f"Not a directory: '{self._path}'")
        self._exists = False
        self._is_dir = False
    
    def mkdir(self, mode: int = 0o777, parents: bool = False, exist_ok: bool = False):
        """Mock mkdir operation."""
        if self._exists and not exist_ok:
            raise FileExistsError(f"Directory exists: '{self._path}'")
        self._exists = True
        self._is_dir = True
    
    def touch(self, mode: int = 0o666, exist_ok: bool = True):
        """Mock touch operation."""
        if self._exists and not exist_ok:
            raise FileExistsError(f"File exists: '{self._path}'")
        self._exists = True
        self._is_file = True
    
    def open(self, mode: str = 'r', buffering: int = -1, encoding: str = None, 
             errors: str = None, newline: str = None):
        """Mock open operation."""
        return MockFile(self._path, mode)
    
    def read_text(self, encoding: str = None, errors: str = None) -> str:
        """Mock read_text operation."""
        if not self._exists:
            raise FileNotFoundError(f"No such file: '{self._path}'")
        return "mock file content"
    
    def write_text(self, data: str, encoding: str = None, errors: str = None) -> int:
        """Mock write_text operation."""
        self._exists = True
        self._is_file = True
        self._size = len(data)
        return len(data)
    
    def read_bytes(self) -> bytes:
        """Mock read_bytes operation."""
        if not self._exists:
            raise FileNotFoundError(f"No such file: '{self._path}'")
        return b"mock file content"
    
    def write_bytes(self, data: bytes) -> int:
        """Mock write_bytes operation."""
        self._exists = True
        self._is_file = True
        self._size = len(data)
        return len(data)
    
    def iterdir(self):
        """Mock iterdir operation."""
        if not self._is_dir:
            raise NotADirectoryError(f"Not a directory: '{self._path}'")
        return []
    
    def glob(self, pattern: str):
        """Mock glob operation."""
        return []
    
    def rglob(self, pattern: str):
        """Mock rglob operation."""
        return []
    
    def rename(self, target):
        """Mock rename operation."""
        self._path = str(target)
    
    def replace(self, target):
        """Mock replace operation."""
        self._path = str(target)
    
    def symlink_to(self, target, target_is_directory: bool = False):
        """Mock symlink_to operation."""
        pass
    
    def with_name(self, name: str):
        """Mock with_name operation."""
        return MockPath(str(self.parent / name))
    
    def with_suffix(self, suffix: str):
        """Mock with_suffix operation."""
        return MockPath(str(self.parent / (self.stem + suffix)))
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def stem(self) -> str:
        return self._stem
    
    @property
    def suffix(self) -> str:
        return self._suffix
    
    @property
    def parent(self):
        return MockPath(str(self._parent))
    
    @property
    def parts(self):
        return self._parts


class MockStat:
    """Mock implementation for stat results."""
    
    def __init__(self, st_size: int = 0, st_mtime: float = None, 
                 st_ctime: float = None, st_atime: float = None):
        self.st_size = st_size
        self.st_mtime = st_mtime or datetime.now().timestamp()
        self.st_ctime = st_ctime or datetime.now().timestamp()
        self.st_atime = st_atime or datetime.now().timestamp()
        self.st_mode = stat.S_IFREG | 0o644
        self.st_ino = 12345
        self.st_dev = 1
        self.st_nlink = 1
        self.st_uid = 1000
        self.st_gid = 1000
        self.st_blksize = 4096
        self.st_blocks = 1


class MockFileSystem:
    """Mock implementation for file system operations."""
    
    def __init__(self):
        self._files = {}
        self._directories = set()
        self._current_dir = "/"
        self._temp_dir = None
    
    def setup_temp_directory(self):
        """Set up temporary directory for testing."""
        self._temp_dir = tempfile.mkdtemp()
        self._current_dir = self._temp_dir
        return self._temp_dir
    
    def cleanup_temp_directory(self):
        """Clean up temporary directory."""
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir)
            self._temp_dir = None
    
    def add_file(self, path: str, content: str = "", size: int = None):
        """Add a mock file."""
        self._files[path] = {
            "content": content,
            "size": size or len(content),
            "created_at": datetime.now(),
            "modified_at": datetime.now()
        }
    
    def add_directory(self, path: str):
        """Add a mock directory."""
        self._directories.add(path)
    
    def remove_file(self, path: str):
        """Remove a mock file."""
        if path in self._files:
            del self._files[path]
    
    def remove_directory(self, path: str):
        """Remove a mock directory."""
        self._directories.discard(path)
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return path in self._files or path in self._directories
    
    def is_file(self, path: str) -> bool:
        """Check if path is a file."""
        return path in self._files
    
    def is_dir(self, path: str) -> bool:
        """Check if path is a directory."""
        return path in self._directories
    
    def get_size(self, path: str) -> int:
        """Get file size."""
        if path in self._files:
            return self._files[path]["size"]
        return 0
    
    def get_content(self, path: str) -> str:
        """Get file content."""
        if path in self._files:
            return self._files[path]["content"]
        return ""
    
    def set_content(self, path: str, content: str):
        """Set file content."""
        self._files[path] = {
            "content": content,
            "size": len(content),
            "created_at": datetime.now(),
            "modified_at": datetime.now()
        }
    
    def list_directory(self, path: str) -> List[str]:
        """List directory contents."""
        if path not in self._directories:
            return []
        
        contents = []
        for file_path in self._files:
            if file_path.startswith(path + "/") and "/" not in file_path[len(path) + 1:]:
                contents.append(file_path.split("/")[-1])
        
        for dir_path in self._directories:
            if dir_path.startswith(path + "/") and "/" not in dir_path[len(path) + 1:]:
                contents.append(dir_path.split("/")[-1])
        
        return contents
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get file system statistics."""
        return {
            "total_files": len(self._files),
            "total_directories": len(self._directories),
            "total_size": sum(file_info["size"] for file_info in self._files.values()),
            "files": list(self._files.keys()),
            "directories": list(self._directories)
        }


class FileSystemMockManager:
    """Manager for file system mocks."""
    
    def __init__(self):
        self.filesystem = MockFileSystem()
        self._patches = []
    
    def start_mocking(self):
        """Start file system mocking."""
        # Mock os.path functions
        self._patches.append(patch('os.path.exists', side_effect=self.filesystem.exists))
        self._patches.append(patch('os.path.isfile', side_effect=self.filesystem.is_file))
        self._patches.append(patch('os.path.isdir', side_effect=self.filesystem.is_dir))
        self._patches.append(patch('os.path.getsize', side_effect=self.filesystem.get_size))
        
        # Mock os functions
        self._patches.append(patch('os.listdir', side_effect=self.filesystem.list_directory))
        self._patches.append(patch('os.makedirs', side_effect=self._mock_makedirs))
        self._patches.append(patch('os.remove', side_effect=self._mock_remove))
        self._patches.append(patch('os.rmdir', side_effect=self._mock_rmdir))
        
        # Mock open function
        self._patches.append(patch('builtins.open', side_effect=self._mock_open))
        
        # Mock Path class
        self._patches.append(patch('pathlib.Path', side_effect=self._mock_path))
        
        # Start all patches
        for patch_obj in self._patches:
            patch_obj.start()
    
    def stop_mocking(self):
        """Stop file system mocking."""
        for patch_obj in self._patches:
            patch_obj.stop()
        self._patches.clear()
    
    def _mock_makedirs(self, path, mode=0o777, exist_ok=False):
        """Mock makedirs function."""
        self.filesystem.add_directory(path)
    
    def _mock_remove(self, path):
        """Mock remove function."""
        self.filesystem.remove_file(path)
    
    def _mock_rmdir(self, path):
        """Mock rmdir function."""
        self.filesystem.remove_directory(path)
    
    def _mock_open(self, path, mode='r', *args, **kwargs):
        """Mock open function."""
        if 'w' in mode or 'a' in mode:
            # Writing mode
            return MockFile(path, mode)
        else:
            # Reading mode
            content = self.filesystem.get_content(path)
            return MockFile(path, mode, content)
    
    def _mock_path(self, path):
        """Mock Path class."""
        return MockPath(path)
    
    def reset_filesystem(self):
        """Reset file system state."""
        self.filesystem._files.clear()
        self.filesystem._directories.clear()
    
    def get_filesystem_statistics(self):
        """Get file system statistics."""
        return self.filesystem.get_statistics()


# Global file system mock manager instance
fs_mock_manager = FileSystemMockManager()


def get_filesystem_mock():
    """Get file system mock."""
    return fs_mock_manager.filesystem


def start_filesystem_mocking():
    """Start file system mocking."""
    fs_mock_manager.start_mocking()


def stop_filesystem_mocking():
    """Stop file system mocking."""
    fs_mock_manager.stop_mocking()


def reset_filesystem_mock():
    """Reset file system mock."""
    fs_mock_manager.reset_filesystem()


def get_filesystem_statistics():
    """Get file system statistics."""
    return fs_mock_manager.get_filesystem_statistics()


# Context manager for easy mocking
class MockFileSystemContext:
    """Context manager for file system mocking."""
    
    def __init__(self):
        self.fs_mock = fs_mock_manager
    
    def __enter__(self):
        """Enter context."""
        self.fs_mock.start_mocking()
        return self.fs_mock.filesystem
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        self.fs_mock.stop_mocking()


def mock_filesystem():
    """Get file system mock context manager."""
    return MockFileSystemContext()

