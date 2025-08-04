#!/usr/bin/env python3
"""
🔧 JSON Mode Support - Anthropic Cookbook Inspired
Made by @Lucariolucario55 on Telegram

Enhanced JSON mode support with validation and error handling
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union, TypeVar, Generic
from dataclasses import dataclass, asdict
from enum import Enum
import re
from datetime import datetime
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T')

class JSONModeType(Enum):
    """JSON mode types"""
    STRICT = "strict"
    FLEXIBLE = "flexible"
    SCHEMA_VALIDATED = "schema_validated"

@dataclass
class JSONSchema:
    """JSON schema definition"""
    schema: Dict[str, Any]
    description: str
    examples: List[Dict[str, Any]]
    required_fields: List[str]
    optional_fields: List[str]

class JSONModeManager:
    """Enhanced JSON mode manager with validation and error handling"""
    
    def __init__(self, mode: JSONModeType = JSONModeType.STRICT):
        self.mode = mode
        self.schemas: Dict[str, JSONSchema] = {}
        self.validation_cache: Dict[str, bool] = {}
        
    def register_schema(self, name: str, schema: JSONSchema) -> None:
        """Register a JSON schema"""
        # Validate the schema itself
        try:
            jsonschema.Draft7Validator.check_schema(schema.schema)
        except ValidationError as e:
            raise ValueError(f"Invalid JSON schema for {name}: {e}")
        
        # Validate examples against schema
        for i, example in enumerate(schema.examples):
            try:
                validate(instance=example, schema=schema.schema)
            except ValidationError as e:
                raise ValueError(f"Example {i} for schema {name} is invalid: {e}")
        
        self.schemas[name] = schema
        logger.info(f"Registered JSON schema: {name}")
    
    def validate_json(self, data: Any, schema_name: str) -> bool:
        """Validate JSON data against a schema"""
        if schema_name not in self.schemas:
            raise ValueError(f"Schema {schema_name} not found")
        
        schema = self.schemas[schema_name]
        
        try:
            validate(instance=data, schema=schema.schema)
            return True
        except ValidationError as e:
            logger.error(f"JSON validation failed for {schema_name}: {e}")
            return False
    
    def extract_json_from_text(self, text: str, schema_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extract JSON from text with validation"""
        # Find JSON blocks in text
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON code blocks
            r'```\s*(\{.*?\})\s*```',      # Generic code blocks
            r'(\{.*?\})',                  # Inline JSON objects
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    # Clean up the JSON string
                    json_str = match.strip()
                    # Remove any trailing commas
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    
                    parsed_json = json.loads(json_str)
                    
                    # Validate against schema if provided
                    if schema_name and not self.validate_json(parsed_json, schema_name):
                        continue
                    
                    return parsed_json
                    
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON: {e}")
                    continue
        
        return None
    
    def format_json_response(self, data: Dict[str, Any], schema_name: str) -> str:
        """Format JSON response with proper structure"""
        if schema_name not in self.schemas:
            raise ValueError(f"Schema {schema_name} not found")
        
        schema = self.schemas[schema_name]
        
        # Validate data against schema
        if not self.validate_json(data, schema_name):
            raise ValueError("Data does not match schema")
        
        # Format with proper indentation
        formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
        
        return f"```json\n{formatted_json}\n```"
    
    def create_json_prompt(self, schema_name: str, task_description: str) -> str:
        """Create a prompt that enforces JSON output"""
        if schema_name not in self.schemas:
            raise ValueError(f"Schema {schema_name} not found")
        
        schema = self.schemas[schema_name]
        
        prompt = f"""
Please respond with valid JSON that matches the following schema:

**Task**: {task_description}

**Required JSON Schema**:
```json
{json.dumps(schema.schema, indent=2)}
```

**Required Fields**: {', '.join(schema.required_fields)}
**Optional Fields**: {', '.join(schema.optional_fields) if schema.optional_fields else 'None'}

**Examples**:
"""
        
        for i, example in enumerate(schema.examples, 1):
            prompt += f"\nExample {i}:\n```json\n{json.dumps(example, indent=2)}\n```\n"
        
        prompt += """
**Important**: 
- Respond ONLY with valid JSON that matches the schema
- Do not include any explanatory text outside the JSON
- Ensure all required fields are present
- Use proper JSON syntax with double quotes for strings
"""
        
        return prompt.strip()

# Predefined JSON Schemas
class CommonSchemas:
    """Common JSON schemas for different use cases"""
    
    @staticmethod
    def get_code_analysis_schema() -> JSONSchema:
        """Schema for code analysis results"""
        return JSONSchema(
            schema={
                "type": "object",
                "properties": {
                    "analysis_type": {"type": "string", "enum": ["security", "performance", "style", "complexity"]},
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                                "message": {"type": "string"},
                                "line_number": {"type": "integer"},
                                "suggestion": {"type": "string"}
                            },
                            "required": ["severity", "message"]
                        }
                    },
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "summary": {"type": "string"}
                },
                "required": ["analysis_type", "issues", "score", "summary"]
            },
            description="Code analysis results with issues and scoring",
            examples=[
                {
                    "analysis_type": "security",
                    "issues": [
                        {
                            "severity": "high",
                            "message": "Potential SQL injection vulnerability",
                            "line_number": 15,
                            "suggestion": "Use parameterized queries"
                        }
                    ],
                    "score": 75.5,
                    "summary": "Code has moderate security issues that should be addressed"
                }
            ],
            required_fields=["analysis_type", "issues", "score", "summary"],
            optional_fields=[]
        )
    
    @staticmethod
    def get_search_results_schema() -> JSONSchema:
        """Schema for search results"""
        return JSONSchema(
            schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "snippet": {"type": "string"},
                                "relevance_score": {"type": "number"}
                            },
                            "required": ["title", "url", "snippet"]
                        }
                    },
                    "total_results": {"type": "integer"},
                    "search_time": {"type": "number"}
                },
                "required": ["query", "results", "total_results"]
            },
            description="Search results with relevance scoring",
            examples=[
                {
                    "query": "Python async programming",
                    "results": [
                        {
                            "title": "AsyncIO in Python",
                            "url": "https://example.com/asyncio",
                            "snippet": "Learn about async programming in Python",
                            "relevance_score": 0.95
                        }
                    ],
                    "total_results": 1,
                    "search_time": 0.5
                }
            ],
            required_fields=["query", "results", "total_results"],
            optional_fields=["search_time"]
        )
    
    @staticmethod
    def get_code_generation_schema() -> JSONSchema:
        """Schema for code generation results"""
        return JSONSchema(
            schema={
                "type": "object",
                "properties": {
                    "language": {"type": "string"},
                    "code": {"type": "string"},
                    "explanation": {"type": "string"},
                    "complexity": {"type": "string", "enum": ["simple", "moderate", "complex"]},
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "test_cases": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "string"},
                                "expected_output": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["input", "expected_output"]
                        }
                    }
                },
                "required": ["language", "code", "explanation"]
            },
            description="Generated code with metadata and test cases",
            examples=[
                {
                    "language": "python",
                    "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                    "explanation": "Recursive implementation of Fibonacci sequence",
                    "complexity": "moderate",
                    "dependencies": [],
                    "test_cases": [
                        {
                            "input": "5",
                            "expected_output": "5",
                            "description": "Basic Fibonacci test"
                        }
                    ]
                }
            ],
            required_fields=["language", "code", "explanation"],
            optional_fields=["complexity", "dependencies", "test_cases"]
        )

# Enhanced LLM Integration
class JSONModeLLMIntegration:
    """Enhanced LLM integration with JSON mode support"""
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.json_manager = JSONModeManager()
        self._register_common_schemas()
    
    def _register_common_schemas(self):
        """Register common schemas"""
        schemas = [
            ("code_analysis", CommonSchemas.get_code_analysis_schema()),
            ("search_results", CommonSchemas.get_search_results_schema()),
            ("code_generation", CommonSchemas.get_code_generation_schema())
        ]
        
        for name, schema in schemas:
            self.json_manager.register_schema(name, schema)
    
    async def generate_json_response(self, prompt: str, schema_name: str, 
                                   max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Generate JSON response with validation and retries"""
        
        json_prompt = self.json_manager.create_json_prompt(schema_name, prompt)
        
        for attempt in range(max_retries):
            try:
                # Generate response from LLM
                response = await self.llm_client.generate_response(json_prompt)
                
                # Extract JSON from response
                json_data = self.json_manager.extract_json_from_text(response, schema_name)
                
                if json_data:
                    return json_data
                
                logger.warning(f"Attempt {attempt + 1}: Failed to extract valid JSON")
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
        
        logger.error(f"Failed to generate valid JSON after {max_retries} attempts")
        return None
    
    async def analyze_code_with_json(self, code: str, analysis_type: str = "security") -> Optional[Dict[str, Any]]:
        """Analyze code and return results in JSON format"""
        prompt = f"Analyze the following code for {analysis_type} issues:\n\n```\n{code}\n```"
        return await self.generate_json_response(prompt, "code_analysis")
    
    async def search_with_json(self, query: str) -> Optional[Dict[str, Any]]:
        """Perform search and return results in JSON format"""
        prompt = f"Search for: {query}"
        return await self.generate_json_response(prompt, "search_results")
    
    async def generate_code_with_json(self, description: str, language: str = "python") -> Optional[Dict[str, Any]]:
        """Generate code and return in JSON format"""
        prompt = f"Generate {language} code for: {description}"
        return await self.generate_json_response(prompt, "code_generation")

# Utility functions
def validate_json_structure(data: Any, expected_structure: Dict[str, Any]) -> bool:
    """Validate JSON structure without strict schema"""
    if not isinstance(data, dict):
        return False
    
    for key, expected_type in expected_structure.items():
        if key not in data:
            return False
        
        if not isinstance(data[key], expected_type):
            return False
    
    return True

def sanitize_json_string(json_str: str) -> str:
    """Sanitize JSON string for parsing"""
    # Remove common issues
    json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)  # Remove control characters
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
    json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)  # Remove comments
    
    return json_str.strip()

# Example usage
async def test_json_mode():
    """Test JSON mode functionality"""
    manager = JSONModeManager()
    
    # Register a schema
    schema = CommonSchemas.get_code_analysis_schema()
    manager.register_schema("test_schema", schema)
    
    # Test JSON extraction
    test_text = """
    Here's the analysis result:
    ```json
    {
        "analysis_type": "security",
        "issues": [
            {
                "severity": "high",
                "message": "SQL injection vulnerability",
                "line_number": 15,
                "suggestion": "Use parameterized queries"
            }
        ],
        "score": 75.5,
        "summary": "Code has security issues"
    }
    ```
    """
    
    extracted = manager.extract_json_from_text(test_text, "test_schema")
    print(f"Extracted JSON: {extracted}")
    
    # Test validation
    is_valid = manager.validate_json(extracted, "test_schema")
    print(f"Is valid: {is_valid}")

if __name__ == "__main__":
    asyncio.run(test_json_mode()) 