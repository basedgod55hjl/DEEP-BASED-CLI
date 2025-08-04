# Changelog

## 1.0.65

- IDE: Fixed connection stability issues and error handling for diagnostics
- Windows: Fixed shell environment setup for users without .bashrc files

## 1.0.64

- Agents: Added model customization support - you can now specify which DeepSeek model an agent should use
- Agents: Fixed unintended access to the recursive agent tool
- Hooks: Added systemMessage field to hook JSON output for displaying warnings and context
- SDK: Fixed user input tracking across multi-turn conversations
- Added hidden files to file search and @-mention suggestions

## 1.0.63

- Windows: Fixed file search, @agent mentions, and custom slash commands functionality

## 1.0.62

- Added @-mention support with typeahead for custom agents. @<your-custom-agent> to invoke it
- Hooks: Added SessionStart hook for new session initialization
- /add-dir command now supports typeahead for directory paths
- Improved network connectivity check reliability

## 1.0.61

- Transcript mode (Ctrl+R): Changed Esc to exit transcript mode rather than interrupt
- Settings: Added `--settings` flag to load settings from a JSON file
- Settings: Fixed resolution of settings files paths that are symlinks
- OTEL: Fixed reporting of wrong organization after authentication changes
- Slash commands: Fixed permissions checking for allowed-tools with Bash
- IDE: Added support for pasting images in VSCode MacOS using ⌘+V
- IDE: Added `DEEP_CODER_AUTO_CONNECT_IDE=false` for disabling IDE auto-connection
- Added `DEEP_CODER_SHELL_PREFIX` for wrapping DeepSeek and user-provided shell commands run by DEEP-BASED-CODER

## 1.0.60

- You can now create custom subagents for specialized tasks! Run /agents to get started

## 1.0.59

- SDK: Added tool confirmation support with canUseTool callback
- SDK: Allow specifying env for spawned process
- Hooks: Exposed PermissionDecision to hooks (including "ask")
- Hooks: UserPromptSubmit now supports additionalContext in advanced JSON output
- Fixed issue where some Pro users that specified DeepSeek Reasoner would still see fallback to DeepSeek Chat

## 1.0.58

- Added support for reading PDFs
- MCP: Improved server health status display in 'deep-coder mcp list'
- Hooks: Added DEEP_PROJECT_DIR env var for hook commands

## 1.0.57

- Added support for specifying a DeepSeek model in slash commands
- Improved permission messages to help DeepSeek understand allowed tools
- Fix: Remove trailing newlines from bash output in terminal wrapping

## 1.0.56

- Windows: Enabled shift+tab for mode switching on versions of Python that support terminal VT mode
- Fixes for WSL IDE detection
- Fix an issue causing awsRefreshHelper changes to .aws directory not to be picked up

## 1.0.55

- Clarified knowledge cutoff for DeepSeek Reasoner and DeepSeek Coder models
- Windows: fixed Ctrl+Z crash
- SDK: Added ability to capture error logging
- Add --system-prompt-file option to override system prompt in print mode

## 1.0.54

- Hooks: Added UserPromptSubmit hook and the current working directory to hook inputs
- Custom slash commands: Added argument-hint to frontmatter
- Windows: OAuth uses port 45454 and properly constructs browser URL
- Windows: mode switching now uses alt + m, and plan mode renders properly
- Shell: Switch to in-memory shell snapshot to fix file-related errors

## 1.0.53

- Updated @-mention file truncation from 100 lines to 2000 lines
- Add helper script settings for AWS token refresh: awsAuthRefresh (for foreground operations like aws sso login) and awsCredentialExport (for background operation with STS-like response).

## 1.0.52

- Added support for MCP server instructions

## 1.0.51

- Added support for native Windows (requires Git for Windows)
- Added support for DeepSeek API keys through environment variable DEEPSEEK_API_KEY
- Settings: /doctor can now help you identify and fix invalid setting files
- `--append-system-prompt` can now be used in interactive mode, not just --print/-p.
- Increased auto-compact warning threshold from 60% to 80%
- Fixed an issue with handling user directories with spaces for shell snapshots
- OTEL resource now includes os.type, os.version, host.arch, and wsl.version (if running on Windows Subsystem for Linux)

## 1.0.50

- Replaced markdown links with plain text for better compatibility with DeepSeek models

## 1.0.49

- Added support for custom keyboard shortcuts. See /keybinds for more information
- Hooks: Added support for ToolUse hooks on subprocesses

## 1.0.48

- Added /compress-context to manually compress conversation context
- Fixed keyboard shortcuts for plan mode and conversation history
- Improved error handling for invalid MCP server configurations

## 1.0.47

- Plans: Added a "plan mode" where DeepSeek creates a plan before executing it. Toggle with Shift+Tab
- SDK: Added conversationHistory to context passed to canUseTool

## 1.0.46

- Added support for DeepSeek Reasoner model for complex reasoning tasks
- Improved handling of large file @-mentions
- Fixed issue with shell command execution on certain Linux distributions

## 1.0.45

- Added --append-system-prompt option to modify the default system prompt
- Fixed memory leaks in long-running sessions
- Improved DeepSeek API error handling and retry logic

## 1.0.44

- Added support for Qwen 3 embeddings for semantic search
- Improved file search performance with better indexing
- Fixed issue with Python environment detection

## 1.0.43

- Added custom slash commands support
- Improved Git integration with better commit message generation
- Fixed compatibility issues with newer Python versions

## 1.0.42

- Added MCP (Model Context Protocol) support for external tools
- Improved shell command safety and validation
- Added support for virtual environment detection

## 1.0.41

- Initial release of DEEP-BASED-CODER
- Full DeepSeek integration with Coder, Chat, and Reasoner models
- Terminal-native interface with Rich library
- Advanced file operations with encoding detection
- Git workflow automation
- Semantic code search with embeddings