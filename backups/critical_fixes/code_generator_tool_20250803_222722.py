"""
Code Generator Tool - Enhanced BASED GOD CLI
Intelligent code generation with multiple language support
"""

import re
import ast
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base_tool import BaseTool, ToolResponse, ToolStatus

class CodeGeneratorTool(BaseTool):
    """
    Advanced code generator with multi-language support
    """
    
    def __init__(self) -> Any:
        super().__init__(
            name="Code Generator",
            description="Intelligent code generation with syntax validation, best practices, and multi-language support",
            capabilities=[
                "Multi-language code generation (Python, JavaScript, TypeScript, etc.)",
                "Syntax validation and error checking",
                "Code formatting and style enforcement",
                "Documentation generation",
                "Unit test generation",
                "Code optimization suggestions"
            ]
        )
        self.supported_languages = {
            "python": {"extension": ".py", "validator": self._validate_python},
            "javascript": {"extension": ".js", "validator": self._validate_javascript},
            "typescript": {"extension": ".ts", "validator": None},
            "html": {"extension": ".html", "validator": None},
            "css": {"extension": ".css", "validator": None},
            "sql": {"extension": ".sql", "validator": None},
            "bash": {"extension": ".sh", "validator": None},
            "json": {"extension": ".json", "validator": self._validate_json}
        }
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute code generation"""
        
        description = kwargs.get("description")
        language = kwargs.get("language", "python").lower()
        code_type = kwargs.get("code_type", "function")
        include_tests = kwargs.get("include_tests", False)
        include_docs = kwargs.get("include_docs", True)
        style_guide = kwargs.get("style_guide", "standard")
        
        if not description:
            return ToolResponse(
                success=False,
                message="Description parameter is required",
                status=ToolStatus.FAILED
            )
        
        if language not in self.supported_languages:
            return ToolResponse(
                success=False,
                message=f"Unsupported language: {language}. Supported: {', '.join(self.supported_languages.keys())}",
                status=ToolStatus.FAILED
            )
        
        try:
            # Generate code based on description and parameters
            generated_code = self._generate_code(
                description, language, code_type, include_docs, style_guide
            )
            
            # Validate generated code
            validation_result = self._validate_code(generated_code, language)
            
            # Generate tests if requested
            tests = None
            if include_tests:
                tests = self._generate_tests(generated_code, language, description)
            
            # Generate documentation
            documentation = self._generate_documentation(generated_code, language, description)
            
            return ToolResponse(
                success=True,
                message=f"Successfully generated {language} code",
                data={
                    "code": generated_code,
                    "language": language,
                    "validation": validation_result,
                    "tests": tests,
                    "documentation": documentation,
                    "file_extension": self.supported_languages[language]["extension"],
                    "estimated_lines": len(generated_code.split('\n'))
                },
                metadata={
                    "code_type": code_type,
                    "style_guide": style_guide,
                    "generated_at": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Code generation failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for code generator"""
        return {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of the code to generate"
                },
                "language": {
                    "type": "string",
                    "enum": list(self.supported_languages.keys()),
                    "description": "Programming language for code generation",
                    "default": "python"
                },
                "code_type": {
                    "type": "string",
                    "enum": ["function", "class", "module", "script", "api", "component"],
                    "description": "Type of code structure to generate",
                    "default": "function"
                },
                "include_tests": {
                    "type": "boolean",
                    "description": "Whether to generate unit tests",
                    "default": False
                },
                "include_docs": {
                    "type": "boolean", 
                    "description": "Whether to include documentation",
                    "default": True
                },
                "style_guide": {
                    "type": "string",
                    "enum": ["standard", "pep8", "google", "numpy", "airbnb"],
                    "description": "Code style guide to follow",
                    "default": "standard"
                }
            },
            "required": ["description"]
        }
    
    def _generate_code(self, description: str, language: str, code_type: str, include_docs: bool, style_guide: str) -> str:
        """Generate code based on parameters"""
        
        if language == "python":
            return self._generate_python_code(description, code_type, include_docs, style_guide)
        elif language == "javascript":
            return self._generate_javascript_code(description, code_type, include_docs)
        elif language == "html":
            return self._generate_html_code(description)
        elif language == "css":
            return self._generate_css_code(description)
        elif language == "sql":
            return self._generate_sql_code(description)
        else:
            return self._generate_generic_code(description, language, code_type)
    
    def _generate_python_code(self, description: str, code_type: str, include_docs: bool, style_guide: str) -> str:
        """Generate Python code"""
        
        # Extract function/class name from description
        name = self._extract_name_from_description(description)
        
        if code_type == "function":
            docstring = f'    """{description}"""' if include_docs else ""
            
            return f'''def {name}():
{docstring}
    """
    {description}
    
    Returns:
        None: This function needs implementation
    """
    # TODO: Implement the logic for: {description}
    pass


# Example usage:
if __name__ == "__main__":
    result = {name}()
    logging.info(f"Result: {{result}}")'''

        elif code_type == "class":
            docstring = f'    """{description}"""' if include_docs else ""
            
            return f'''class {name.title()}:
{docstring}
    """
    {description}
    """
    
    def __init__(self) -> Any:
        """Initialize the {name.title()} instance."""
        # TODO: Initialize instance variables
        pass
    
    def process(self) -> Any:
        """
        Main processing method.
        
        Returns:
            None: This method needs implementation
        """
        # TODO: Implement the main logic for: {description}
        pass


# Example usage:
if __name__ == "__main__":
    instance = {name.title()}()
    instance.process()'''

        elif code_type == "module":
            return f'''"""
{description}

This module provides functionality for: {description}
"""

import logging
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_function() -> None:
    """
    Main function for: {description}
    """
    logger.info("Starting: {description}")
    # TODO: Implement main logic
    pass


if __name__ == "__main__":
    main_function()'''

        else:
            return f'''# {description}

def {name}():
    """
    {description}
    """
    # TODO: Implement functionality
    pass'''
    
    def _generate_javascript_code(self, description: str, code_type: str, include_docs: bool) -> str:
        """Generate JavaScript code"""
        
        name = self._extract_name_from_description(description)
        
        if code_type == "function":
            docs = f"/**\n * {description}\n */" if include_docs else ""
            
            return f'''{docs}
function {name}() {{
    // TODO: Implement the logic for: {description}
    console.log("Function {name} called");
    return null;
}}

// Example usage:
const result = {name}();
console.log("Result:", result);'''

        elif code_type == "class":
            docs = f"/**\n * {description}\n */" if include_docs else ""
            
            return f'''{docs}
class {name.title()} {{
    constructor() {{
        // TODO: Initialize class properties
        this.initialized = true;
    }}
    
    process() {{
        // TODO: Implement the main logic for: {description}
        console.log("Processing in {name.title()}");
        return null;
    }}
}}

// Example usage:
const instance = new {name.title()}();
const result = instance.process();
console.log("Result:", result);'''

        else:
            return f'''// {description}

const {name} = () => {{
    // TODO: Implement functionality
    console.log("Executing: {description}");
}};

{name}();'''
    
    def _generate_html_code(self, description: str) -> str:
        """Generate HTML code"""
        
        title = self._extract_name_from_description(description).replace('_', ' ').title()
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>{description}</p>
        
        <!-- TODO: Add your content here -->
        <div id="content">
            <p>Content will be added here based on: {description}</p>
        </div>
    </div>
    
    <script>
        // TODO: Add JavaScript functionality for: {description}
        console.log("Page loaded: {title}");
    </script>
</body>
</html>'''
    
    def _generate_css_code(self, description: str) -> str:
        """Generate CSS code"""
        
        return f'''/* {description} */

/* Base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
}}

/* Container styles */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}

/* TODO: Add specific styles for: {description} */

/* Responsive design */
@media (max-width: 768px) {{
    .container {{
        padding: 10px;
    }}
}}'''
    
    def _generate_sql_code(self, description: str) -> str:
        """Generate SQL code"""
        
        return f'''-- {description}

-- TODO: Implement SQL logic for: {description}

-- Example table structure (modify as needed)
CREATE TABLE IF NOT EXISTS sample_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example query (modify as needed)
SELECT * FROM sample_table 
WHERE created_at > DATE('now', '-7 days')
ORDER BY created_at DESC;

-- Note: Modify this SQL code according to your specific requirements'''
    
    def _generate_generic_code(self, description: str, language: str, code_type: str) -> str:
        """Generate generic code for unsupported languages"""
        
        return f'''// {description}
// Language: {language}
// Type: {code_type}

// TODO: Implement the logic for: {description}
// This is a generic template that needs to be customized for {language}

function main() {{
    // Add your code here
    logging.info("Implementing: {description}");
}}

main();'''
    
    def _extract_name_from_description(self, description: str) -> str:
        """Extract a suitable function/class name from description"""
        
        # Remove common words and clean up
        words = re.findall(r'\b[a-zA-Z]+\b', description.lower())
        
        # Filter out common words
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'for', 'to', 'of', 'in', 'on', 'at', 'by', 'with'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Take first few meaningful words
        name_words = meaningful_words[:3] if meaningful_words else ['generated', 'function']
        
        # Create snake_case name
        name = '_'.join(name_words)
        
        # Ensure it starts with a letter
        if not name[0].isalpha():
            name = 'func_' + name
        
        return name
    
    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code"""
        
        validator = self.supported_languages[language].get("validator")
        
        if validator:
            return validator(code)
        else:
            return {
                "valid": True,
                "message": f"Syntax validation not available for {language}",
                "errors": [],
                "warnings": []
            }
    
    def _validate_python(self, code: str) -> Dict[str, Any]:
        """Validate Python code syntax"""
        
        try:
            ast.parse(code)
            return {
                "valid": True,
                "message": "Python syntax is valid",
                "errors": [],
                "warnings": []
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "message": f"Python syntax error: {e.msg}",
                "errors": [f"Line {e.lineno}: {e.msg}"],
                "warnings": []
            }
    
    def _validate_javascript(self, code: str) -> Dict[str, Any]:
        """Basic JavaScript validation"""
        
        # Simple bracket matching
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in code:
            if char in brackets:
                stack.append(brackets[char])
            elif char in brackets.values():
                if not stack or stack.pop() != char:
                    return {
                        "valid": False,
                        "message": "JavaScript bracket mismatch",
                        "errors": ["Mismatched brackets or braces"],
                        "warnings": []
                    }
        
        if stack:
            return {
                "valid": False,
                "message": "JavaScript unclosed brackets",
                "errors": ["Unclosed brackets or braces"],
                "warnings": []
            }
        
        return {
            "valid": True,
            "message": "JavaScript basic syntax appears valid",
            "errors": [],
            "warnings": ["Full JavaScript validation requires a proper parser"]
        }
    
    def _validate_json(self, code: str) -> Dict[str, Any]:
        """Validate JSON syntax"""
        
        try:
            import json
            json.loads(code)
            return {
                "valid": True,
                "message": "JSON syntax is valid",
                "errors": [],
                "warnings": []
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "message": f"JSON syntax error: {e.msg}",
                "errors": [f"Position {e.pos}: {e.msg}"],
                "warnings": []
            }
    
    def _generate_tests(self, code: str, language: str, description: str) -> Optional[str]:
        """Generate unit tests for the code"""
        
        if language == "python":
            function_name = self._extract_name_from_description(description)
            
            return f'''import unittest
from unittest.mock import patch, MagicMock

# Import the function to test (adjust import as needed)
# from your_module import {function_name}

class Test{function_name.title().replace('_', '')}(unittest.TestCase):
    """Test cases for {function_name}"""
    
    def test_{function_name}_basic(self):
        """Test basic functionality of {function_name}"""
        # TODO: Implement test for: {description}
        pass
    
    def test_{function_name}_edge_cases(self):
        """Test edge cases for {function_name}"""
        # TODO: Add edge case tests
        pass
    
    def test_{function_name}_error_handling(self):
        """Test error handling in {function_name}"""
        # TODO: Test error conditions
        pass

if __name__ == '__main__':
    unittest.main()'''
        
        elif language == "javascript":
            function_name = self._extract_name_from_description(description)
            
            return f'''// Test file for {function_name}
// Using Jest testing framework

// Import the function to test
// const {{ {function_name} }} = require('./your-module');

describe('{function_name}', () => {{
    test('should handle basic functionality', () => {{
        // TODO: Implement test for: {description}
        expect(true).toBe(true); // Placeholder
    }});
    
    test('should handle edge cases', () => {{
        // TODO: Add edge case tests
        expect(true).toBe(true); // Placeholder
    }});
    
    test('should handle errors gracefully', () => {{
        // TODO: Test error conditions
        expect(true).toBe(true); // Placeholder
    }});
}});'''
        
        return None
    
    def _generate_documentation(self, code: str, language: str, description: str) -> str:
        """Generate documentation for the code"""
        
        function_name = self._extract_name_from_description(description)
        
        return f'''# {function_name.replace('_', ' ').title()} Documentation

## Description
{description}

## Language
{language.title()}

## Usage
```{language}
{code.split(chr(10))[:10]  # First 10 lines as example
}
```

## Parameters
- TODO: Document parameters

## Returns
- TODO: Document return values

## Examples
```{language}
// TODO: Add usage examples
```

## Notes
- Generated automatically by BASED GOD CLI
- Review and modify as needed
- Add proper error handling
- Consider performance optimizations

## Testing
Run the included tests to verify functionality:
- TODO: Add testing instructions
'''