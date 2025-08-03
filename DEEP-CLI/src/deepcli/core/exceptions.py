"""
Custom exceptions for DeepCLI
"""


class DeepCLIError(Exception):
    """Base exception for DeepCLI"""
    pass


class ConfigError(DeepCLIError):
    """Configuration related errors"""
    pass


class APIError(DeepCLIError):
    """API related errors"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    pass


class AuthenticationError(APIError):
    """Authentication failed error"""
    pass


class ValidationError(DeepCLIError):
    """Input validation error"""
    pass


class MemoryError(DeepCLIError):
    """Memory system error"""
    pass


class CommandError(DeepCLIError):
    """Command execution error"""
    pass


class MCPError(DeepCLIError):
    """MCP server error"""
    pass