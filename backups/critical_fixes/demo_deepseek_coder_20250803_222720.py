import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
🚀 DeepSeek Coder Demo - Advanced Code Generation & Analysis
Made by @Lucariolucario55 on Telegram

This demo showcases all the new DeepSeek Coder capabilities:
- Code generation and completion
- Debugging and error fixing
- Self-healing code
- FIM (Fill-in-Middle) code completion
- Web search integration
- Web scraping with headless browsers
- Code analysis and optimization
- Logic and loop analysis
- Idea and code storage
- Learning from code examples
"""

import asyncio
import sys
from pathlib import Path
import colorama
from colorama import Fore, Style
import json

# Initialize colorama
colorama.init()

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from tools.deepseek_coder_tool import DeepSeekCoderTool

class DeepSeekCoderDemo:
    """Demo class for showcasing DeepSeek Coder features"""
    
    def __init__(self) -> Any:
        self.coder_tool = DeepSeekCoderTool()
        self.demo_examples = [
            # Code Generation Examples
            {
                "title": "🔧 Code Generation",
                "description": "Generate Python code for a web scraper",
                "operation": "code_generation",
                "params": {
                    "prompt": "Create a Python web scraper that extracts article titles from a news website",
                    "language": "python",
                    "requirements": ["Use requests and BeautifulSoup", "Handle errors gracefully", "Include rate limiting"]
                }
            },
            {
                "title": "🐛 Code Debugging",
                "description": "Debug a Python function with errors",
                "operation": "code_debugging",
                "params": {
                    "code": """
def calculate_fibonacci(n) -> Any:
    if n <= 0:
        return None
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Test the function
result = calculate_fibonacci(5)
logger.info(f"Fibonacci of 5 is: {result}")
""",
                    "language": "python",
                    "error_message": "RecursionError: maximum recursion depth exceeded"
                }
            },
            {
                "title": "🩹 Self-Healing Code",
                "description": "Self-heal code with potential issues",
                "operation": "self_healing",
                "params": {
                    "code": """
import os
def read_file(filename) -> Any:
    file = open(filename, 'r')
    content = file.read()
    return content

# Usage
data = read_file('test.txt')
logger.info(data)
""",
                    "language": "python"
                }
            },
            {
                "title": "🔗 FIM Code Completion",
                "description": "Fill-in-Middle code completion",
                "operation": "fim_completion",
                "params": {
                    "prefix": """
def process_data(data_list) -> Any:
    results = []
    for item in data_list:
""",
                    "suffix": """
    return results

# Test
data = [1, 2, 3, 4, 5]
result = process_data(data)
logger.info(result)
""",
                    "language": "python"
                }
            },
            {
                "title": "🔍 Web Search",
                "description": "Search for programming information",
                "operation": "web_search",
                "params": {
                    "query": "Python async await best practices",
                    "engine": "duckduckgo",
                    "max_results": 5
                }
            },
            {
                "title": "📄 Web Scraping",
                "description": "Scrape a simple webpage",
                "operation": "web_scraping",
                "params": {
                    "url": "https://httpbin.org/html",
                    "extract_text": True,
                    "extract_links": True
                }
            },
            {
                "title": "🔍 Code Analysis",
                "description": "Analyze code for issues and improvements",
                "operation": "code_analysis",
                "params": {
                    "code": """
def bubble_sort(arr) -> Any:
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
logger.info(sorted_numbers)
""",
                    "language": "python"
                }
            },
            {
                "title": "🧠 Logic Analysis",
                "description": "Analyze algorithm logic and complexity",
                "operation": "logic_analysis",
                "params": {
                    "code": """
def binary_search(arr, target) -> Any:
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Test
sorted_array = [1, 3, 5, 7, 9, 11, 13, 15]
result = binary_search(sorted_array, 7)
logger.info(f"Found at index: {result}")
""",
                    "language": "python"
                }
            },
            {
                "title": "💡 Store Idea",
                "description": "Store a programming idea",
                "operation": "store_idea",
                "params": {
                    "idea": "Create a machine learning pipeline for sentiment analysis using transformers",
                    "category": "machine_learning",
                    "tags": ["nlp", "transformers", "sentiment_analysis"],
                    "priority": "high"
                }
            },
            {
                "title": "💾 Store Code Example",
                "description": "Store a code example for learning",
                "operation": "store_code",
                "params": {
                    "code": """
import asyncio
import aiohttp

async def fetch_url(session, url) -> Any:
    async with session.get(url) as response:
        return await response.text()

async def fetch_multiple_urls(urls) -> Any:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# Usage
urls = ['https://httpbin.org/delay/1', 'https://httpbin.org/delay/2']
results = asyncio.run(fetch_multiple_urls(urls))
logger.info(f"Fetched {len(results)} pages")
""",
                    "language": "python",
                    "description": "Async web scraping with aiohttp",
                    "tags": ["async", "aiohttp", "web_scraping"]
                }
            },
            {
                "title": "🎓 Learn from Code",
                "description": "Extract learning insights from code",
                "operation": "learn_from_code",
                "params": {
                    "code": """
from typing import List, Optional
from dataclasses import dataclass
import logging

@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True

class UserService:
    def __init__(self) -> Any:
        self.users: List[User] = []
        self.logger = logging.getLogger(__name__)
    
    def add_user(self, user: User) -> bool:
        try:
            if self._validate_user(user):
                self.users.append(user)
                self.logger.info(f"User {user.name} added successfully")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error adding user: {e}")
            return False
    
    def _validate_user(self, user: User) -> bool:
        return user.id > 0 and user.name and '@' in user.email
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return next((user for user in self.users if user.id == user_id), None)
""",
                    "language": "python"
                }
            },
            {
                "title": "▶️ Run Code",
                "description": "Execute Python code",
                "operation": "run_code",
                "params": {
                    "code": """
import math

def calculate_circle_area(radius) -> Any:
    return math.pi * radius ** 2

def calculate_circle_circumference(radius) -> Any:
    return 2 * math.pi * radius

# Test calculations
radius = 5
area = calculate_circle_area(radius)
circumference = calculate_circle_circumference(radius)

logger.info(f"Circle with radius {radius}:")
logger.info(f"Area: {area:.2f}")
logger.info(f"Circumference: {circumference:.2f}")
""",
                    "language": "python"
                }
            }
        ]
    
    def print_demo_banner(self) -> Any:
        """Print demo banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🚀 DeepSeek Coder Demo - Advanced Code Generation & Analysis               ║
║                                                                              ║
║  Features:                                                                   ║
║  ✅ Code Generation and Completion                                           ║
║  ✅ Debugging and Error Fixing                                               ║
║  ✅ Self-Healing Code                                                        ║
║  ✅ FIM (Fill-in-Middle) Code Completion                                     ║
║  ✅ Web Search Integration                                                   ║
║  ✅ Web Scraping with Headless Browsers                                      ║
║  ✅ Code Analysis and Optimization                                           ║
║  ✅ Logic and Loop Analysis                                                   ║
║  ✅ Idea and Code Storage                                                     ║
║  ✅ Learning from Code Examples                                               ║
║                                                                              ║
║  Made by @Lucariolucario55 on Telegram                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        logger.info(banner)
    
    async def run_demo(self) -> Any:
        """Run the DeepSeek Coder demo"""
        self.print_demo_banner()
        
        logger.info(f"{Fore.GREEN}🎯 Initializing DeepSeek Coder Tool...{Style.RESET_ALL}")
        await self.coder_tool.initialize()
        
        logger.info(f"{Fore.GREEN}✅ DeepSeek Coder Tool initialized successfully!{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}🚀 Starting demo...{Style.RESET_ALL}\n")
        
        # Run demo examples
        for i, example in enumerate(self.demo_examples, 1):
            logger.info(f"{Fore.CYAN}📋 Demo {i}/{len(self.demo_examples)}: {example['title']}{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}📝 {example['description']}{Style.RESET_ALL}")
            
            try:
                # Execute the operation
                result = await self.coder_tool.execute(
                    operation=example['operation'],
                    **example['params']
                )
                
                # Display results
                logger.info(f"{Fore.GREEN}✅ Operation completed successfully!{Style.RESET_ALL}")
                
                if result.success:
                    # Format output based on operation type
                    if example['operation'] == 'code_generation':
                        logger.info(f"{Fore.WHITE}Generated Code:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}{result.data.get('code', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'code_debugging':
                        logger.info(f"{Fore.WHITE}Fixed Code:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}{result.data.get('fixed_code', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'self_healing':
                        logger.info(f"{Fore.WHITE}Self-Healed Code:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}{result.data.get('healed_code', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'fim_completion':
                        logger.info(f"{Fore.WHITE}FIM Completion:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}{result.data.get('completion', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'web_search':
                        results = result.data.get('results', [])
                        logger.info(f"{Fore.WHITE}Search Results:{Style.RESET_ALL}")
                        for j, res in enumerate(results[:3], 1):
                            logger.info(f"{Fore.WHITE}  {j}. {res.title}{Style.RESET_ALL}")
                            logger.info(f"{Fore.WHITE}     {res.url}{Style.RESET_ALL}")
                            logger.info(f"{Fore.WHITE}     {res.snippet[:100]}...{Style.RESET_ALL}\n")
                    
                    elif example['operation'] == 'web_scraping':
                        data = result.data.get('scraped_data', {})
                        logger.info(f"{Fore.WHITE}Scraped Data:{Style.RESET_ALL}")
                        if 'text' in data:
                            logger.info(f"{Fore.WHITE}Text: {data['text'][:200]}...{Style.RESET_ALL}")
                        if 'links' in data:
                            logger.info(f"{Fore.WHITE}Links found: {len(data['links'])}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'code_analysis':
                        analysis = result.data.get('analysis', {})
                        logger.info(f"{Fore.WHITE}Code Analysis:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}Language: {analysis.language}{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}Complexity: {analysis.complexity}{Style.RESET_ALL}")
                        if analysis.issues:
                            logger.info(f"{Fore.WHITE}Issues: {', '.join(analysis.issues)}{Style.RESET_ALL}")
                        if analysis.suggestions:
                            logger.info(f"{Fore.WHITE}Suggestions: {', '.join(analysis.suggestions)}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'logic_analysis':
                        logger.info(f"{Fore.WHITE}Logic Analysis:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}{result.data.get('analysis', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'store_idea':
                        logger.info(f"{Fore.WHITE}Idea stored with ID: {result.data.get('idea_id', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'store_code':
                        logger.info(f"{Fore.WHITE}Code stored with ID: {result.data.get('example_id', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'learn_from_code':
                        logger.info(f"{Fore.WHITE}Learning Insights:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}{result.data.get('insights', '')}{Style.RESET_ALL}")
                    
                    elif example['operation'] == 'run_code':
                        logger.info(f"{Fore.WHITE}Code Execution Result:{Style.RESET_ALL}")
                        logger.info(f"{Fore.WHITE}STDOUT: {result.data.get('stdout', '')}{Style.RESET_ALL}")
                        if result.data.get('stderr'):
                            logger.info(f"{Fore.WHITE}STDERR: {result.data.get('stderr', '')}{Style.RESET_ALL}")
                    
                    else:
                        logger.info(f"{Fore.WHITE}Result: {json.dumps(result.data, indent=2)}{Style.RESET_ALL}")
                
                else:
                    logger.info(f"{Fore.RED}❌ Operation failed: {result.message}{Style.RESET_ALL}")
                
            except Exception as e:
                logger.info(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
            
            logger.info(f"{Fore.BLUE}{'='*80}{Style.RESET_ALL}\n")
            
            # Small delay between demos
            await asyncio.sleep(2)
        
        logger.info(f"{Fore.GREEN}🎉 DeepSeek Coder Demo completed successfully!{Style.RESET_ALL}")
        logger.info(f"{Fore.YELLOW}💡 Try using these features in the main CLI: python based_coder_cli.py{Style.RESET_ALL}")
        
        # Show tool capabilities
        schema = self.coder_tool.get_schema()
        logger.info(f"\n{Fore.CYAN}🔧 DeepSeek Coder Capabilities:{Style.RESET_ALL}")
        logger.info(f"{Fore.WHITE}Supported Languages: {', '.join(schema['supported_languages'][:10])}...{Style.RESET_ALL}")
        logger.info(f"{Fore.WHITE}Search Engines: {', '.join(schema['search_engines'])}{Style.RESET_ALL}")
        logger.info(f"{Fore.WHITE}Operations: {', '.join(schema['operations'])}{Style.RESET_ALL}")

async def main() -> None:
    """Main demo function"""
    demo = DeepSeekCoderDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main()) 