"""
File Processor Tool - Enhanced BASED GOD CLI
Intelligent file processing with multiple format support
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_tool import BaseTool, ToolResponse, ToolStatus

class FileProcessorTool(BaseTool):
    """
    Advanced file processing tool
    """
    
    def __init__(self) -> Any:
        super().__init__(
            name="File Processor",
            description="Intelligent file processing including reading, writing, analysis, and batch operations",
            capabilities=[
                "File reading and writing with encoding detection",
                "File metadata extraction and analysis",
                "Batch file operations",
                "File format conversion",
                "Directory tree analysis",
                "File integrity checking (checksums)"
            ]
        )
        self.supported_operations = ["read", "write", "analyze", "checksum", "list_directory", "batch_process"]
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute file processing operation"""
        
        operation = kwargs.get("operation", "read").lower()
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")
        encoding = kwargs.get("encoding", "utf-8")
        create_backup = kwargs.get("create_backup", False)
        
        if operation not in self.supported_operations:
            return ToolResponse(
                success=False,
                message=f"Unsupported operation: {operation}. Supported: {', '.join(self.supported_operations)}",
                status=ToolStatus.FAILED
            )
        
        try:
            if operation == "read":
                return await self._read_file(file_path, encoding)
            elif operation == "write":
                return await self._write_file(file_path, content, encoding, create_backup)
            elif operation == "analyze":
                return await self._analyze_file(file_path)
            elif operation == "checksum":
                return await self._calculate_checksum(file_path)
            elif operation == "list_directory":
                return await self._list_directory(file_path)
            elif operation == "batch_process":
                return await self._batch_process(kwargs)
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"File operation failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for file processor"""
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": self.supported_operations,
                    "description": "File operation to perform",
                    "default": "read"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file or directory"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write operation)"
                },
                "encoding": {
                    "type": "string",
                    "description": "File encoding",
                    "default": "utf-8"
                },
                "create_backup": {
                    "type": "boolean",
                    "description": "Create backup before writing",
                    "default": False
                },
                "pattern": {
                    "type": "string",
                    "description": "File pattern for batch operations"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Recursive directory operations",
                    "default": False
                }
            },
            "required": ["file_path"]
        }
    
    async def _read_file(self, file_path: str, encoding: str) -> ToolResponse:
        """Read file content"""
        
        if not file_path or not os.path.exists(file_path):
            return ToolResponse(
                success=False,
                message=f"File not found: {file_path}",
                status=ToolStatus.FAILED
            )
        
        # Detect encoding if auto
        if encoding == "auto":
            encoding = self._detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            file_stats = os.stat(file_path)
            
            return ToolResponse(
                success=True,
                message=f"Successfully read file: {file_path}",
                data={
                    "content": content,
                    "file_path": file_path,
                    "encoding": encoding,
                    "size_bytes": file_stats.st_size,
                    "line_count": len(content.splitlines()),
                    "character_count": len(content)
                },
                metadata={
                    "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    "mime_type": mimetypes.guess_type(file_path)[0]
                }
            )
            
        except UnicodeDecodeError as e:
            return ToolResponse(
                success=False,
                message=f"Encoding error: {str(e)}. Try different encoding.",
                status=ToolStatus.FAILED
            )
    
    async def _write_file(self, file_path: str, content: str, encoding: str, create_backup: bool) -> ToolResponse:
        """Write content to file"""
        
        if not file_path:
            return ToolResponse(
                success=False,
                message="File path is required for write operation",
                status=ToolStatus.FAILED
            )
        
        if content is None:
            return ToolResponse(
                success=False,
                message="Content is required for write operation",
                status=ToolStatus.FAILED
            )
        
        # Create backup if requested and file exists
        backup_path = None
        if create_backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{int(datetime.now().timestamp())}"
            try:
                import shutil
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                return ToolResponse(
                    success=False,
                    message=f"Failed to create backup: {str(e)}",
                    status=ToolStatus.FAILED
                )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            file_stats = os.stat(file_path)
            
            return ToolResponse(
                success=True,
                message=f"Successfully wrote file: {file_path}",
                data={
                    "file_path": file_path,
                    "encoding": encoding,
                    "size_bytes": file_stats.st_size,
                    "line_count": len(content.splitlines()),
                    "character_count": len(content),
                    "backup_created": backup_path is not None,
                    "backup_path": backup_path
                },
                metadata={
                    "created_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to write file: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _analyze_file(self, file_path: str) -> ToolResponse:
        """Analyze file properties and content"""
        
        if not file_path or not os.path.exists(file_path):
            return ToolResponse(
                success=False,
                message=f"File not found: {file_path}",
                status=ToolStatus.FAILED
            )
        
        file_stats = os.stat(file_path)
        path_obj = Path(file_path)
        
        # Basic file information
        analysis = {
            "basic_info": {
                "name": path_obj.name,
                "extension": path_obj.suffix,
                "size_bytes": file_stats.st_size,
                "size_human": self._format_file_size(file_stats.st_size),
                "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(file_stats.st_atime).isoformat()
            },
            "permissions": {
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "executable": os.access(file_path, os.X_OK)
            },
            "type_info": {
                "mime_type": mimetypes.guess_type(file_path)[0],
                "is_text": self._is_text_file(file_path),
                "is_binary": not self._is_text_file(file_path)
            }
        }
        
        # Content analysis for text files
        if analysis["type_info"]["is_text"] and file_stats.st_size < 10 * 1024 * 1024:  # < 10MB
            try:
                encoding = self._detect_encoding(file_path)
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                lines = content.splitlines()
                
                analysis["content_analysis"] = {
                    "encoding": encoding,
                    "line_count": len(lines),
                    "character_count": len(content),
                    "word_count": len(content.split()),
                    "empty_lines": sum(1 for line in lines if not line.strip()),
                    "max_line_length": max(len(line) for line in lines) if lines else 0,
                    "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
                }
                
                # Language detection for code files
                if path_obj.suffix in ['.py', '.js', '.ts', '.html', '.css', '.sql', '.sh']:
                    analysis["code_analysis"] = self._analyze_code_file(content, path_obj.suffix)
                
            except Exception as e:
                analysis["content_analysis"] = {"error": f"Could not analyze content: {str(e)}"}
        
        return ToolResponse(
            success=True,
            message=f"Successfully analyzed file: {file_path}",
            data=analysis,
            metadata={
                "analyzed_at": datetime.now().isoformat()
            }
        )
    
    async def _calculate_checksum(self, file_path: str) -> ToolResponse:
        """Calculate file checksums"""
        
        if not file_path or not os.path.exists(file_path):
            return ToolResponse(
                success=False,
                message=f"File not found: {file_path}",
                status=ToolStatus.FAILED
            )
        
        checksums = {}
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Calculate multiple hash types
            checksums["md5"] = hashlib.md5(content).hexdigest()
            checksums["sha1"] = hashlib.sha1(content).hexdigest()
            checksums["sha256"] = hashlib.sha256(content).hexdigest()
            
            file_stats = os.stat(file_path)
            
            return ToolResponse(
                success=True,
                message=f"Successfully calculated checksums for: {file_path}",
                data={
                    "file_path": file_path,
                    "file_size": file_stats.st_size,
                    "checksums": checksums
                },
                metadata={
                    "calculated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to calculate checksum: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _list_directory(self, dir_path: str) -> ToolResponse:
        """List directory contents with analysis"""
        
        if not dir_path or not os.path.exists(dir_path):
            return ToolResponse(
                success=False,
                message=f"Directory not found: {dir_path}",
                status=ToolStatus.FAILED
            )
        
        if not os.path.isdir(dir_path):
            return ToolResponse(
                success=False,
                message=f"Path is not a directory: {dir_path}",
                status=ToolStatus.FAILED
            )
        
        items = []
        summary = {
            "total_items": 0,
            "files": 0,
            "directories": 0,
            "total_size": 0,
            "file_types": {}
        }
        
        try:
            for item_name in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item_name)
                item_stats = os.stat(item_path)
                
                is_dir = os.path.isdir(item_path)
                
                item_info = {
                    "name": item_name,
                    "path": item_path,
                    "type": "directory" if is_dir else "file",
                    "size": 0 if is_dir else item_stats.st_size,
                    "size_human": "N/A" if is_dir else self._format_file_size(item_stats.st_size),
                    "modified": datetime.fromtimestamp(item_stats.st_mtime).isoformat(),
                    "permissions": {
                        "readable": os.access(item_path, os.R_OK),
                        "writable": os.access(item_path, os.W_OK),
                        "executable": os.access(item_path, os.X_OK)
                    }
                }
                
                if not is_dir:
                    # Add file-specific info
                    extension = Path(item_name).suffix.lower()
                    item_info["extension"] = extension
                    item_info["mime_type"] = mimetypes.guess_type(item_path)[0]
                    
                    # Update summary
                    summary["files"] += 1
                    summary["total_size"] += item_stats.st_size
                    summary["file_types"][extension] = summary["file_types"].get(extension, 0) + 1
                else:
                    summary["directories"] += 1
                
                items.append(item_info)
                summary["total_items"] += 1
            
            # Sort items: directories first, then files
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return ToolResponse(
                success=True,
                message=f"Successfully listed directory: {dir_path}",
                data={
                    "directory": dir_path,
                    "items": items,
                    "summary": summary
                },
                metadata={
                    "listed_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Failed to list directory: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    async def _batch_process(self, kwargs: Dict[str, Any]) -> ToolResponse:
        """Process multiple files in batch"""
        
        # This is a placeholder for batch processing functionality
        return ToolResponse(
            success=True,
            message="Batch processing functionality - to be implemented",
            data={"note": "Batch processing feature coming soon"}
        )
    
    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        
        try:
            import chardet
            
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
            
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') or 'utf-8'
        
        except ImportError:
            # Fallback if chardet not available
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1000)
                return 'utf-8'
            except UnicodeDecodeError:
                return 'latin-1'
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file"""
        
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
            
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return False
            
            # Check if most bytes are printable
            printable_ratio = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13]) / len(chunk)
            return printable_ratio > 0.7
        
        except Exception:
            return False
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _analyze_code_file(self, content: str, extension: str) -> Dict[str, Any]:
        """Analyze code file content"""
        
        lines = content.splitlines()
        analysis = {
            "language": {
                ".py": "Python",
                ".js": "JavaScript", 
                ".ts": "TypeScript",
                ".html": "HTML",
                ".css": "CSS",
                ".sql": "SQL",
                ".sh": "Shell"
            }.get(extension, "Unknown"),
            "total_lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": 0,
            "code_lines": 0
        }
        
        # Language-specific comment detection
        comment_patterns = {
            ".py": ["#"],
            ".js": ["//", "/*"],
            ".ts": ["//", "/*"],
            ".html": ["<!--"],
            ".css": ["/*"],
            ".sql": ["--", "/*"],
            ".sh": ["#"]
        }
        
        patterns = comment_patterns.get(extension, [])
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            is_comment = any(stripped.startswith(pattern) for pattern in patterns)
            if is_comment:
                analysis["comment_lines"] += 1
            else:
                analysis["code_lines"] += 1
        
        # Calculate ratios
        total_non_blank = analysis["comment_lines"] + analysis["code_lines"]
        if total_non_blank > 0:
            analysis["comment_ratio"] = analysis["comment_lines"] / total_non_blank
            analysis["code_ratio"] = analysis["code_lines"] / total_non_blank
        
        return analysis