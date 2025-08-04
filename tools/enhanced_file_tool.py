"""
Enhanced File Tool - Inspired by Google Gemini CLI
Integrates advanced file operations into existing DEEP-CLI architecture
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import fnmatch
import re
import chardet
from datetime import datetime

from .base_tool import BaseTool, ToolResponse
from .enhanced_base_tool import EnhancedBaseTool, ToolResult, ToolLocation, ToolSchema, Icon, ToolErrorType

logger = logging.getLogger(__name__)

class EnhancedFileTool(EnhancedBaseTool):
    """
    Enhanced file operations tool inspired by Gemini CLI
    Combines multiple file operations with smart validation and streaming
    """
    
    @property
    def name(self) -> str:
        return "enhanced_file_tool"
    
    @property
    def display_name(self) -> str:
        return "Enhanced File Operations"
    
    @property
    def description(self) -> str:
        return "Advanced file operations including read, write, edit, search, and analysis with smart validation"
    
    @property
    def icon(self) -> Icon:
        return Icon.FILE
    
    @property
    def schema(self) -> ToolSchema:
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "edit", "search", "analyze", "list", "glob"],
                        "description": "File operation to perform"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory path"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (for write/edit operations)"
                    },
                    "pattern": {
                        "type": "string", 
                        "description": "Search pattern or glob pattern"
                    },
                    "encoding": {
                        "type": "string",
                        "default": "utf-8",
                        "description": "File encoding"
                    },
                    "max_size": {
                        "type": "integer",
                        "default": 1048576,
                        "description": "Maximum file size to process (bytes)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "default": False,
                        "description": "Recursive operation for directories"
                    }
                },
                "required": ["operation", "path"]
            },
            required=["operation", "path"]
        )
    
    @property
    def can_update_output(self) -> bool:
        return True
    
    def tool_locations(self, params: Dict[str, Any]) -> List[ToolLocation]:
        """Determine what file system locations will be affected"""
        operation = params.get("operation")
        path = params.get("path", "")
        
        locations = []
        
        if operation in ["write", "edit"]:
            locations.append(ToolLocation(
                path=path,
                operation="write",
                description=f"Will modify file: {path}"
            ))
        elif operation == "read":
            locations.append(ToolLocation(
                path=path,
                operation="read",
                description=f"Will read file: {path}"
            ))
        elif operation in ["list", "glob", "search"]:
            locations.append(ToolLocation(
                path=path,
                operation="read",
                description=f"Will scan directory: {path}"
            ))
            
        return locations
    
    async def execute(
        self,
        params: Dict[str, Any],
        signal: Optional[asyncio.Event] = None,
        update_output: Optional[callable] = None
    ) -> ToolResult:
        """Execute file operation with enhanced features"""
        operation = params["operation"]
        path = params["path"]
        
        try:
            if operation == "read":
                return await self._read_file(params, update_output)
            elif operation == "write":
                return await self._write_file(params, update_output)
            elif operation == "edit":
                return await self._edit_file(params, update_output)
            elif operation == "search":
                return await self._search_files(params, update_output)
            elif operation == "analyze":
                return await self._analyze_file(params, update_output)
            elif operation == "list":
                return await self._list_directory(params, update_output)
            elif operation == "glob":
                return await self._glob_search(params, update_output)
            else:
                return ToolResult(
                    success=False,
                    error_message=f"Unknown operation: {operation}",
                    error_type=ToolErrorType.VALIDATION_ERROR
                )
                
        except Exception as e:
            logger.error(f"File operation {operation} failed: {str(e)}")
            return ToolResult(
                success=False,
                error_message=str(e),
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _read_file(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Read file with smart encoding detection and size limits"""
        path = params["path"]
        max_size = params.get("max_size", 1048576)
        encoding = params.get("encoding", "utf-8")
        
        file_path = Path(path)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error_message=f"File not found: {path}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
        
        if file_path.stat().st_size > max_size:
            return ToolResult(
                success=False,
                error_message=f"File too large: {file_path.stat().st_size} bytes (max: {max_size})",
                error_type=ToolErrorType.RESOURCE_ERROR
            )
        
        # Detect encoding if not specified
        if encoding == "auto":
            with open(file_path, 'rb') as f:
                raw_data = f.read(1024)
                detected = chardet.detect(raw_data)
                encoding = detected.get('encoding', 'utf-8')
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            if update_output:
                update_output(f"📄 Read {len(content)} characters from {path}")
            
            return ToolResult(
                success=True,
                content=content,
                metadata={
                    "file_size": file_path.stat().st_size,
                    "encoding": encoding,
                    "line_count": content.count('\n') + 1,
                    "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                },
                locations_affected=[ToolLocation(path, "read", f"Read {len(content)} characters")]
            )
            
        except UnicodeDecodeError as e:
            return ToolResult(
                success=False,
                error_message=f"Encoding error: {str(e)}. Try with different encoding.",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _write_file(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Write file with backup and validation"""
        path = params["path"]
        content = params.get("content", "")
        encoding = params.get("encoding", "utf-8")
        
        file_path = Path(path)
        
        # Create backup if file exists
        backup_path = None
        if file_path.exists():
            backup_path = f"{path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_path.rename(backup_path)
            if update_output:
                update_output(f"💾 Created backup: {backup_path}")
        
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            if update_output:
                update_output(f"✅ Wrote {len(content)} characters to {path}")
            
            return ToolResult(
                success=True,
                content=f"Successfully wrote {len(content)} characters to {path}",
                metadata={
                    "bytes_written": len(content.encode(encoding)),
                    "backup_created": backup_path,
                    "encoding": encoding
                },
                locations_affected=[ToolLocation(path, "write", f"Wrote {len(content)} characters")]
            )
            
        except Exception as e:
            # Restore backup if write failed
            if backup_path and Path(backup_path).exists():
                Path(backup_path).rename(file_path)
                if update_output:
                    update_output(f"🔄 Restored backup due to error")
            
            return ToolResult(
                success=False,
                error_message=f"Write failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _search_files(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Search for pattern in files with context"""
        path = params["path"]
        pattern = params.get("pattern", "")
        recursive = params.get("recursive", False)
        
        if not pattern:
            return ToolResult(
                success=False,
                error_message="Search pattern is required",
                error_type=ToolErrorType.VALIDATION_ERROR
            )
        
        search_path = Path(path)
        results = []
        total_files = 0
        
        try:
            # Compile regex pattern
            regex = re.compile(pattern, re.IGNORECASE)
            
            # Determine search scope
            if search_path.is_file():
                files_to_search = [search_path]
            else:
                glob_pattern = "**/*" if recursive else "*"
                files_to_search = [f for f in search_path.glob(glob_pattern) if f.is_file()]
            
            for file_path in files_to_search:
                total_files += 1
                
                if update_output and total_files % 10 == 0:
                    update_output(f"🔍 Searched {total_files} files...")
                
                try:
                    # Detect encoding
                    with open(file_path, 'rb') as f:
                        raw_data = f.read(1024)
                        detected = chardet.detect(raw_data)
                        encoding = detected.get('encoding', 'utf-8')
                    
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        if regex.search(line):
                            results.append({
                                "file": str(file_path),
                                "line": line_num,
                                "content": line.strip(),
                                "match": regex.search(line).group()
                            })
                            
                except Exception as e:
                    logger.warning(f"Could not search {file_path}: {e}")
                    continue
            
            result_text = f"Found {len(results)} matches in {total_files} files:\n\n"
            for result in results[:50]:  # Limit to first 50 results
                result_text += f"📄 **{result['file']}:{result['line']}**\n"
                result_text += f"   `{result['content']}`\n\n"
            
            if len(results) > 50:
                result_text += f"... and {len(results) - 50} more matches"
            
            if update_output:
                update_output(f"✅ Search complete: {len(results)} matches found")
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata={
                    "total_matches": len(results),
                    "files_searched": total_files,
                    "pattern": pattern,
                    "recursive": recursive
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Search failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _analyze_file(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Analyze file properties and content"""
        path = params["path"]
        file_path = Path(path)
        
        if not file_path.exists():
            return ToolResult(
                success=False,
                error_message=f"File not found: {path}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
        
        try:
            stat = file_path.stat()
            
            # Basic file info
            analysis = {
                "path": str(file_path.absolute()),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:],
                "is_binary": False,
                "encoding": "unknown",
                "line_count": 0,
                "word_count": 0,
                "char_count": 0
            }
            
            if update_output:
                update_output(f"🔍 Analyzing {path}...")
            
            # Content analysis for text files
            if file_path.is_file() and stat.st_size < 10485760:  # 10MB limit
                try:
                    # Detect if binary
                    with open(file_path, 'rb') as f:
                        chunk = f.read(1024)
                        if b'\x00' in chunk:
                            analysis["is_binary"] = True
                        else:
                            # Detect encoding
                            detected = chardet.detect(chunk)
                            analysis["encoding"] = detected.get('encoding', 'utf-8')
                    
                    # Text analysis
                    if not analysis["is_binary"]:
                        with open(file_path, 'r', encoding=analysis["encoding"], errors='ignore') as f:
                            content = f.read()
                            analysis["line_count"] = content.count('\n') + 1
                            analysis["word_count"] = len(content.split())
                            analysis["char_count"] = len(content)
                            
                            # File type detection
                            extension = file_path.suffix.lower()
                            if extension in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs']:
                                analysis["file_type"] = "code"
                            elif extension in ['.md', '.txt', '.rst']:
                                analysis["file_type"] = "text"
                            elif extension in ['.json', '.yaml', '.yml', '.xml']:
                                analysis["file_type"] = "data"
                            else:
                                analysis["file_type"] = "unknown"
                                
                except Exception as e:
                    logger.warning(f"Content analysis failed: {e}")
            
            # Format results
            result_text = f"""
# File Analysis: {path}

## Basic Information
- **Size**: {analysis['size']:,} bytes
- **Type**: {'Binary' if analysis['is_binary'] else 'Text'} file
- **Encoding**: {analysis['encoding']}
- **Permissions**: {analysis['permissions']}

## Timestamps
- **Created**: {analysis['created']}
- **Modified**: {analysis['modified']}

## Content Analysis
- **Lines**: {analysis['line_count']:,}
- **Words**: {analysis['word_count']:,}
- **Characters**: {analysis['char_count']:,}
- **File Type**: {analysis.get('file_type', 'unknown')}
"""
            
            if update_output:
                update_output("✅ Analysis complete")
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata=analysis,
                locations_affected=[ToolLocation(path, "read", "File analysis")]
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Analysis failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _list_directory(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """List directory contents with detailed information"""
        path = params["path"]
        recursive = params.get("recursive", False)
        
        dir_path = Path(path)
        
        if not dir_path.exists():
            return ToolResult(
                success=False,
                error_message=f"Directory not found: {path}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
        
        if not dir_path.is_dir():
            return ToolResult(
                success=False,
                error_message=f"Path is not a directory: {path}",
                error_type=ToolErrorType.VALIDATION_ERROR
            )
        
        try:
            entries = []
            total_size = 0
            
            pattern = "**/*" if recursive else "*"
            for item in dir_path.glob(pattern):
                try:
                    stat = item.stat()
                    entry = {
                        "name": item.name,
                        "path": str(item.relative_to(dir_path)),
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else 0,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "permissions": oct(stat.st_mode)[-3:]
                    }
                    entries.append(entry)
                    total_size += entry["size"]
                    
                    if update_output and len(entries) % 50 == 0:
                        update_output(f"📁 Listed {len(entries)} items...")
                        
                except Exception as e:
                    logger.warning(f"Could not stat {item}: {e}")
                    continue
            
            # Sort entries
            entries.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            # Format output
            result_text = f"# Directory Listing: {path}\n\n"
            result_text += f"**Total items**: {len(entries)}\n"
            result_text += f"**Total size**: {total_size:,} bytes\n\n"
            
            for entry in entries[:100]:  # Limit to first 100 entries
                icon = "📁" if entry["type"] == "directory" else "📄"
                size_str = f"{entry['size']:,}B" if entry["type"] == "file" else "-"
                result_text += f"{icon} **{entry['name']}** ({size_str}) - {entry['modified']}\n"
            
            if len(entries) > 100:
                result_text += f"\n... and {len(entries) - 100} more items"
            
            if update_output:
                update_output(f"✅ Listed {len(entries)} items")
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata={
                    "total_items": len(entries),
                    "total_size": total_size,
                    "recursive": recursive
                },
                locations_affected=[ToolLocation(path, "read", f"Listed {len(entries)} items")]
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Directory listing failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
    
    async def _glob_search(self, params: Dict[str, Any], update_output: Optional[callable]) -> ToolResult:
        """Search files using glob patterns"""
        path = params["path"]
        pattern = params.get("pattern", "*")
        
        search_path = Path(path)
        
        if not search_path.exists():
            return ToolResult(
                success=False,
                error_message=f"Path not found: {path}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )
        
        try:
            matches = list(search_path.glob(pattern))
            
            if update_output:
                update_output(f"🔍 Found {len(matches)} matches for pattern: {pattern}")
            
            result_text = f"# Glob Search Results\n\n"
            result_text += f"**Pattern**: `{pattern}`\n"
            result_text += f"**Base Path**: {path}\n"
            result_text += f"**Matches**: {len(matches)}\n\n"
            
            for match in matches[:50]:  # Limit to first 50 matches
                relative_path = match.relative_to(search_path) if match.is_relative_to(search_path) else match
                icon = "📁" if match.is_dir() else "📄"
                result_text += f"{icon} `{relative_path}`\n"
            
            if len(matches) > 50:
                result_text += f"\n... and {len(matches) - 50} more matches"
            
            return ToolResult(
                success=True,
                content=result_text,
                metadata={
                    "pattern": pattern,
                    "matches": len(matches),
                    "base_path": str(search_path)
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Glob search failed: {str(e)}",
                error_type=ToolErrorType.EXECUTION_ERROR
            )

# Legacy compatibility with existing DEEP-CLI structure
class EnhancedFileProcessor(BaseTool):
    """Legacy wrapper for enhanced file tool"""
    
    def __init__(self):
        super().__init__()
        self.enhanced_tool = EnhancedFileTool()
    
    def get_schema(self) -> Dict[str, Any]:
        return self.enhanced_tool.schema.parameters
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute with legacy ToolResponse format"""
        try:
            result = await self.enhanced_tool.execute_with_validation(
                kwargs, 
                require_confirmation=False
            )
            
            return ToolResponse(
                success=result.success,
                data={"content": result.content, "metadata": result.metadata},
                message=result.error_message if not result.success else "File operation completed successfully"
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Enhanced file operation failed: {str(e)}"
            )