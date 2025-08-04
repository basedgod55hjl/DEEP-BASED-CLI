#!/usr/bin/env python3
"""
Git RAG Tool - Repository Analysis and Learning
Provides Git repository analysis, commit history, and RAG capabilities
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import git
from git import Repo
import hashlib

from .base_tool import BaseTool, ToolResponse

logger = logging.getLogger(__name__)

@dataclass
class GitCommit:
    """Git commit information"""
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int

@dataclass
class GitFileHistory:
    """File history information"""
    file_path: str
    commits: List[GitCommit]
    total_changes: int
    last_modified: str
    contributors: List[str]

@dataclass
class RepositoryAnalysis:
    """Repository analysis results"""
    repo_path: str
    is_git_repo: bool
    current_branch: str
    total_commits: int
    contributors: List[str]
    recent_commits: List[GitCommit]
    file_history: Dict[str, GitFileHistory]
    commit_frequency: Dict[str, int]

class GitRAGTool(BaseTool):
    """Git Repository Analysis and RAG Tool"""
    
    def __init__(self):
        super().__init__()
        self.repo_path = Path(".").resolve()
        self.repo = None
        self.analysis = None
        
    def _check_git_available(self) -> bool:
        """Check if Git is available on the system"""
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Git not available: {e}")
            return False
    
    def _initialize_repo(self) -> bool:
        """Initialize Git repository object"""
        try:
            if not self._check_git_available():
                return False
                
            if not (self.repo_path / '.git').exists():
                logger.warning(f"No Git repository found at {self.repo_path}")
                return False
                
            self.repo = Repo(self.repo_path)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Git repository: {e}")
            return False
    
    async def execute(self, operation: str, **kwargs) -> ToolResponse:
        """Execute Git RAG operations"""
        try:
            if operation == "analyze_repository":
                return await self._analyze_repository()
            elif operation == "get_file_history":
                file_path = kwargs.get('file_path')
                if not file_path:
                    return ToolResponse(False, "file_path parameter required")
                return await self._get_file_history(file_path)
            elif operation == "get_recent_changes":
                days = kwargs.get('days', 7)
                return await self._get_recent_changes(days)
            elif operation == "search_commits":
                query = kwargs.get('query')
                if not query:
                    return ToolResponse(False, "query parameter required")
                return await self._search_commits(query)
            elif operation == "get_commit_analysis":
                commit_hash = kwargs.get('commit_hash')
                if not commit_hash:
                    return ToolResponse(False, "commit_hash parameter required")
                return await self._get_commit_analysis(commit_hash)
            elif operation == "create_rag_index":
                return await self._create_rag_index()
            elif operation == "get_contributor_stats":
                return await self._get_contributor_stats()
            else:
                return ToolResponse(False, f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"Git RAG operation failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _analyze_repository(self) -> ToolResponse:
        """Analyze the entire repository"""
        try:
            if not self._initialize_repo():
                return ToolResponse(False, "Failed to initialize Git repository")
            
            # Basic repository info
            current_branch = self.repo.active_branch.name
            total_commits = len(list(self.repo.iter_commits()))
            
            # Recent commits
            recent_commits = []
            for commit in self.repo.iter_commits(max_count=20):
                recent_commits.append(GitCommit(
                    hash=commit.hexsha,
                    short_hash=commit.hexsha[:8],
                    author=commit.author.name,
                    email=commit.author.email,
                    date=commit.committed_datetime.isoformat(),
                    message=commit.message.strip(),
                    files_changed=list(commit.stats.files.keys()),
                    insertions=sum(stats.get('insertions', 0) for stats in commit.stats.files.values()),
                    deletions=sum(stats.get('deletions', 0) for stats in commit.stats.files.values())
                ))
            
            # Contributors analysis
            contributors = set()
            commit_frequency = {}
            for commit in self.repo.iter_commits():
                author = commit.author.name
                contributors.add(author)
                commit_frequency[author] = commit_frequency.get(author, 0) + 1
            
            # File history analysis
            file_history = {}
            for file_path in self.repo.git.ls_files().split('\n'):
                if file_path and Path(file_path).exists():
                    try:
                        file_commits = []
                        file_contributors = set()
                        total_changes = 0
                        last_modified = ""
                        
                        for commit in self.repo.iter_commits(paths=file_path, max_count=20):
                            file_commits.append(GitCommit(
                                hash=commit.hexsha,
                                short_hash=commit.hexsha[:8],
                                author=commit.author.name,
                                email=commit.author.email,
                                date=commit.committed_datetime.isoformat(),
                                message=commit.message.strip(),
                                files_changed=[file_path],
                                insertions=commit.stats.files.get(file_path, {}).get('insertions', 0),
                                deletions=commit.stats.files.get(file_path, {}).get('deletions', 0)
                            ))
                            file_contributors.add(commit.author.name)
                            total_changes += 1
                            if not last_modified:
                                last_modified = commit.committed_datetime.isoformat()
                        
                        file_history[file_path] = GitFileHistory(
                            file_path=file_path,
                            commits=file_commits,
                            total_changes=total_changes,
                            last_modified=last_modified,
                            contributors=list(file_contributors)
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get history for {file_path}: {e}")
            
            self.analysis = RepositoryAnalysis(
                repo_path=str(self.repo_path),
                is_git_repo=True,
                current_branch=current_branch,
                total_commits=total_commits,
                contributors=list(contributors),
                recent_commits=recent_commits,
                file_history=file_history,
                commit_frequency=commit_frequency
            )
            
            return ToolResponse(True, "Repository analyzed successfully", {
                'analysis': {
                    'repo_path': self.analysis.repo_path,
                    'current_branch': self.analysis.current_branch,
                    'total_commits': self.analysis.total_commits,
                    'contributors': self.analysis.contributors,
                    'recent_commits_count': len(self.analysis.recent_commits),
                    'files_with_history': len(self.analysis.file_history)
                }
            })
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            return ToolResponse(False, str(e))
    
    async def _get_file_history(self, file_path: str) -> ToolResponse:
        """Get Git history for a specific file"""
        try:
            if not self.repo:
                if not self._initialize_repo():
                    return ToolResponse(False, "Failed to initialize Git repository")
            
            if not Path(file_path).exists():
                return ToolResponse(False, f"File not found: {file_path}")
            
            file_commits = []
            for commit in self.repo.iter_commits(paths=file_path, max_count=20):
                file_commits.append({
                    'hash': commit.hexsha[:8],
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'insertions': commit.stats.files.get(file_path, {}).get('insertions', 0),
                    'deletions': commit.stats.files.get(file_path, {}).get('deletions', 0)
                })
            
            return ToolResponse(True, f"File history retrieved for {file_path}", {
                'file_path': file_path,
                'commits': file_commits,
                'total_commits': len(file_commits)
            })
            
        except Exception as e:
            logger.error(f"Failed to get file history for {file_path}: {e}")
            return ToolResponse(False, str(e))
    
    async def _get_recent_changes(self, days: int = 7) -> ToolResponse:
        """Get recent changes in the repository"""
        try:
            if not self.repo:
                if not self._initialize_repo():
                    return ToolResponse(False, "Failed to initialize Git repository")
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            recent_changes = []
            for commit in self.repo.iter_commits():
                if commit.committed_datetime < cutoff_date:
                    break
                    
                for file_path, stats in commit.stats.files.items():
                    recent_changes.append({
                        'file': file_path,
                        'commit': commit.hexsha[:8],
                        'date': commit.committed_datetime.isoformat(),
                        'author': commit.author.name,
                        'message': commit.message.strip(),
                        'insertions': stats.get('insertions', 0),
                        'deletions': stats.get('deletions', 0)
                    })
            
            return ToolResponse(True, f"Recent changes retrieved (last {days} days)", {
                'changes': recent_changes,
                'total_changes': len(recent_changes),
                'days': days
            })
            
        except Exception as e:
            logger.error(f"Failed to get recent changes: {e}")
            return ToolResponse(False, str(e))
    
    async def _search_commits(self, query: str) -> ToolResponse:
        """Search commits by message content"""
        try:
            if not self.repo:
                if not self._initialize_repo():
                    return ToolResponse(False, "Failed to initialize Git repository")
            
            matching_commits = []
            for commit in self.repo.iter_commits():
                if query.lower() in commit.message.lower():
                    matching_commits.append({
                        'hash': commit.hexsha[:8],
                        'date': commit.committed_datetime.isoformat(),
                        'message': commit.message.strip(),
                        'author': commit.author.name,
                        'files_changed': list(commit.stats.files.keys())
                    })
                
                if len(matching_commits) >= 20:  # Limit results
                    break
            
            return ToolResponse(True, f"Found {len(matching_commits)} commits matching '{query}'", {
                'query': query,
                'commits': matching_commits,
                'total_found': len(matching_commits)
            })
            
        except Exception as e:
            logger.error(f"Failed to search commits: {e}")
            return ToolResponse(False, str(e))
    
    async def _get_commit_analysis(self, commit_hash: str) -> ToolResponse:
        """Get detailed analysis of a specific commit"""
        try:
            if not self.repo:
                if not self._initialize_repo():
                    return ToolResponse(False, "Failed to initialize Git repository")
            
            commit = self.repo.commit(commit_hash)
            
            analysis = {
                'hash': commit.hexsha,
                'short_hash': commit.hexsha[:8],
                'author': commit.author.name,
                'email': commit.author.email,
                'date': commit.committed_datetime.isoformat(),
                'message': commit.message,
                'files_changed': list(commit.stats.files.keys()),
                'stats': commit.stats.total,
                'insertions': sum(stats.get('insertions', 0) for stats in commit.stats.files.values()),
                'deletions': sum(stats.get('deletions', 0) for stats in commit.stats.files.values())
            }
            
            return ToolResponse(True, f"Commit analysis completed for {commit_hash[:8]}", analysis)
            
        except Exception as e:
            logger.error(f"Failed to analyze commit {commit_hash}: {e}")
            return ToolResponse(False, str(e))
    
    async def _create_rag_index(self) -> ToolResponse:
        """Create RAG index from repository analysis"""
        try:
            if not self.analysis:
                # Analyze repository first
                analysis_result = await self._analyze_repository()
                if not analysis_result.success:
                    return analysis_result
            
            # Create RAG data structure
            rag_data = {
                'repository_info': {
                    'path': self.analysis.repo_path,
                    'branch': self.analysis.current_branch,
                    'total_commits': self.analysis.total_commits,
                    'contributors': self.analysis.contributors
                },
                'recent_commits': [
                    {
                        'hash': commit.short_hash,
                        'author': commit.author,
                        'date': commit.date,
                        'message': commit.message,
                        'files_changed': commit.files_changed
                    }
                    for commit in self.analysis.recent_commits
                ],
                'file_history': {
                    file_path: {
                        'total_changes': history.total_changes,
                        'last_modified': history.last_modified,
                        'contributors': history.contributors,
                        'recent_commits': [
                            {
                                'hash': commit.short_hash,
                                'date': commit.date,
                                'message': commit.message,
                                'author': commit.author
                            }
                            for commit in history.commits[:5]  # Last 5 commits
                        ]
                    }
                    for file_path, history in self.analysis.file_history.items()
                },
                'contributor_stats': self.analysis.commit_frequency,
                'created_at': datetime.now().isoformat()
            }
            
            # Save RAG index
            os.makedirs("data", exist_ok=True)
            rag_file = f"data/git_rag_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(rag_file, 'w', encoding='utf-8') as f:
                json.dump(rag_data, f, indent=2, ensure_ascii=False)
            
            return ToolResponse(True, f"RAG index created successfully: {rag_file}", {
                'rag_file': rag_file,
                'total_files': len(self.analysis.file_history),
                'total_commits': self.analysis.total_commits,
                'contributors': len(self.analysis.contributors)
            })
            
        except Exception as e:
            logger.error(f"Failed to create RAG index: {e}")
            return ToolResponse(False, str(e))
    
    async def _get_contributor_stats(self) -> ToolResponse:
        """Get contributor statistics"""
        try:
            if not self.analysis:
                # Analyze repository first
                analysis_result = await self._analyze_repository()
                if not analysis_result.success:
                    return analysis_result
            
            # Sort contributors by commit count
            sorted_contributors = sorted(
                self.analysis.commit_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            stats = {
                'total_contributors': len(self.analysis.contributors),
                'top_contributors': sorted_contributors[:10],
                'commit_distribution': {
                    'total_commits': self.analysis.total_commits,
                    'average_commits_per_contributor': self.analysis.total_commits / len(self.analysis.contributors) if self.analysis.contributors else 0
                }
            }
            
            return ToolResponse(True, "Contributor statistics retrieved", stats)
            
        except Exception as e:
            logger.error(f"Failed to get contributor stats: {e}")
            return ToolResponse(False, str(e)) 