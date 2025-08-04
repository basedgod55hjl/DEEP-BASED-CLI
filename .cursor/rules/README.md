# Cursor Rules for DeepSeek-Reasoner Brain System

This directory contains comprehensive Cursor Rules for the DeepSeek-Reasoner Brain System, a sophisticated AI agent platform built with Node.js.

## Available Rules

### 1. [nodejs-deepseek-brain-system.mdc](mdc:nodejs-deepseek-brain-system.mdc)
**Always Applied** - Complete development guide and architecture reference for the Node.js DeepSeek-Reasoner Brain System.

**Covers:**
- Core architecture and main entry points
- DeepSeek integration patterns
- Persona system (DEANNA default)
- Tool development guidelines
- Web scraping integration
- Memory management
- API endpoints and WebSocket events
- Integration guidelines for MCP, GitHub, IDE, testing, and build systems
- Development workflow and best practices
- Performance optimization and security considerations

### 2. [ide-development-integration.mdc](mdc:ide-development-integration.mdc)
**Applied to IDE-related files** - Comprehensive guide for IDE development and integration.

**Covers:**
- Desktop IDE (Electron-based) architecture
- Web IDE (Browser-based) components
- Codebox integration patterns
- GraphQL editor development
- DeepSeek integration in IDEs
- File system and terminal integration
- Debugging capabilities
- UI/UX guidelines and collaboration features
- Testing strategies and performance optimization
- Security considerations and deployment

### 3. [mcp-integration-tool-development.mdc](mdc:mcp-integration-tool-development.mdc)
**Applied to MCP and tool-related files** - Model Context Protocol integration and tool development.

**Covers:**
- MCP server implementation
- Tool implementation patterns (Web Scraper, Qwen Embedding, GitHub)
- Integration with DeepSeek-Reasoner Brain
- Resource management (File System, Database)
- Error handling and logging
- Testing and validation
- Performance optimization (caching, connection pooling)

### 4. [testing-cicd-integration.mdc](mdc:testing-cicd-integration.mdc)
**Applied to test and CI/CD files** - Comprehensive testing and CI/CD integration.

**Covers:**
- Testing strategy overview (Unit, Integration, E2E, Performance, Security)
- Jest configuration and setup
- Unit testing for core systems
- Integration testing for API endpoints and WebSocket
- End-to-End testing with Puppeteer
- Performance testing with autocannon
- demo-ci integration and configuration
- HRM (Human Resource Management) testing
- CI/CD pipeline with GitHub Actions
- Docker Compose for testing
- Test monitoring and alerting

### 5. [dataset-github-integration.mdc](mdc:dataset-github-integration.mdc)
**Applied to dataset and GitHub-related files** - Dataset integration and GitHub bot functionality.

**Covers:**
- Hugging Face dataset integration
- GitHub bot functionality
- Repository cloning and dataset creation
- Memory integration for datasets
- Tool registration in DeepSeek Brain

## Existing Rules

### 6. [enhanced-based-god-cli.mdc](mdc:enhanced-based-god-cli.mdc)
**Always Applied** - Development guide for the Enhanced BASED GOD CLI (Python component).

### 7. [tool-development.mdc](mdc:tool-development.mdc)
**Applied to tool files** - Tool development patterns and best practices.

### 8. [configuration-management.mdc](mdc:configuration-management.mdc)
**Applied to configuration files** - Configuration management system and settings.

### 9. [debugging-and-troubleshooting.mdc](mdc:debugging-and-troubleshooting.mdc)
**Applied to debugging scenarios** - Debugging and troubleshooting guide.

### 10. [deepseek-api-integration.mdc](mdc:deepseek-api-integration.mdc)
**Applied to API integration files** - DeepSeek API integration guidelines.

## Usage

### For Cursor Users
1. These rules are automatically applied based on file patterns
2. Rules with `alwaysApply: true` are active for all files
3. Rules with specific `globs` patterns apply to matching files
4. Use the rules to understand the codebase structure and development patterns

### For Development
1. **Node.js Development**: Follow patterns in `nodejs-deepseek-brain-system.mdc`
2. **IDE Development**: Use `ide-development-integration.mdc` for IDE-related work
3. **Tool Development**: Reference `mcp-integration-tool-development.mdc`
4. **Testing**: Use `testing-cicd-integration.mdc` for comprehensive testing
5. **Dataset Integration**: Follow `dataset-github-integration.mdc` for data work

## Key Features Covered

### DeepSeek Integration
- DeepSeek-Reasoner for chain-of-thought reasoning
- DeepSeek-Chat for dynamic conversation
- DeepSeek-Coder for code generation
- Streaming token feedback
- Tool calling capabilities

### Persona System
- DEANNA as default persona
- Dynamic persona switching
- Persona-specific memory and context
- Chain-of-thought reasoning storage

### Tool Ecosystem
- Web scraping with Puppeteer, Cheerio, Osmosis
- Qwen embedding generation
- GitHub repository management
- MCP server implementation
- Memory storage and retrieval

### Testing Framework
- Jest for unit and integration testing
- Puppeteer for E2E testing
- demo-ci for continuous integration
- HRM for human resource management testing
- Performance testing with autocannon

### IDE Development
- Desktop IDE with Electron
- Web IDE with React/Vue.js
- Codebox integration
- GraphQL editor
- Monaco Editor integration

### CI/CD Pipeline
- GitHub Actions workflows
- Docker containerization
- Automated testing
- Deployment to staging and production
- Monitoring and alerting

## Best Practices

1. **Code Quality**: Use ESLint, Prettier, and maintain high test coverage
2. **Security**: Implement proper authentication, authorization, and input validation
3. **Performance**: Use caching, compression, and optimize database queries
4. **Scalability**: Design for horizontal scaling and microservices architecture
5. **Documentation**: Maintain comprehensive documentation and comments

## Integration Guidelines

1. **MCP Integration**: Follow MCP protocol standards for tool integration
2. **GitHub Integration**: Use GitHub API for repository management and dataset creation
3. **IDE Integration**: Implement proper file system and terminal integration
4. **Testing Integration**: Use comprehensive testing strategies with proper mocking
5. **Memory Integration**: Store and retrieve data efficiently with proper indexing

## Development Workflow

1. **Environment Setup**: Use Docker for consistent development environment
2. **Development Commands**: Use npm scripts for common tasks
3. **Debugging**: Use Winston for logging and proper error handling
4. **Deployment**: Use Docker for containerized deployment
5. **Monitoring**: Implement health checks and performance monitoring

This comprehensive set of Cursor Rules provides a complete development guide for the DeepSeek-Reasoner Brain System, covering all aspects from architecture to deployment. 