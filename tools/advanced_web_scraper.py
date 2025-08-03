"""
Advanced Web Scraper Tool with DeepSeek Integration
A sophisticated, production-ready web scraping system with AI-powered intelligence
"""

import asyncio
import aiohttp
import json
import hashlib
import random
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from queue import Queue, PriorityQueue
from enum import Enum

# Third-party imports
from bs4 import BeautifulSoup
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Selenium imports for advanced scraping
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium_stealth import stealth
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

console = Console()


class ScrapeMode(Enum):
    """Scraping modes for different scenarios"""
    STATIC = "static"  # Simple HTTP requests
    BROWSER = "browser"  # Full browser rendering
    API = "api"  # Direct API access
    HYBRID = "hybrid"  # Mix of methods


class AgentStatus(Enum):
    """Agent lifecycle states"""
    IDLE = "idle"
    ACTIVE = "active"
    BLOCKED = "blocked"
    FAILED = "failed"
    ROTATING = "rotating"


@dataclass
class ScrapeTask:
    """Represents a scraping task"""
    url: str
    mode: ScrapeMode
    depth: int = 1
    priority: int = 5
    patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    callback: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        return self.priority < other.priority


@dataclass
class ScrapedData:
    """Container for scraped data with metadata"""
    url: str
    content: str
    raw_html: str
    timestamp: datetime
    agent_id: str
    mode: ScrapeMode
    metadata: Dict[str, Any]
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    media: List[Dict[str, str]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class DeepSeekIntelligence:
    """DeepSeek API integration for intelligent scraping"""
    
    def __init__(self, api_key: str, use_reasoner: bool = True):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.beta_client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/beta"
        )
        self.use_reasoner = use_reasoner
        self.context_cache = {}
        self.conversation_history = []
        
    async def analyze_page_structure(self, html: str) -> Dict[str, Any]:
        """Use DeepSeek to understand page structure"""
        prompt = f"""Analyze this HTML and identify:
        1. Main content areas
        2. Navigation patterns
        3. Data extraction opportunities
        4. Dynamic content indicators
        5. Anti-bot measures
        
        HTML: {html[:3000]}...
        
        Return as JSON with extraction strategies."""
        
        response = await self._async_chat(prompt, json_mode=True)
        return json.loads(response)
    
    async def generate_extraction_code(self, structure: Dict[str, Any]) -> str:
        """Generate custom extraction code using DeepSeek"""
        messages = [
            {"role": "user", "content": f"Generate Python extraction code for: {json.dumps(structure)}"},
            {"role": "assistant", "content": "```python\n", "prefix": True}
        ]
        
        response = await self._async_chat_beta(messages, stop=["```"])
        return response
    
    async def detect_antibot_patterns(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze for anti-bot measures"""
        if self.use_reasoner:
            prompt = f"""Analyze these response patterns for anti-bot measures:
            - Status: {response_data.get('status')}
            - Headers: {response_data.get('headers')}
            - Content preview: {response_data.get('content', '')[:500]}
            
            Identify: Cloudflare, reCAPTCHA, rate limits, fingerprinting, honeypots."""
            
            response = await self._async_reasoner(prompt)
            return {
                'reasoning': response.get('reasoning_content', ''),
                'detection': json.loads(response.get('content', '{}'))
            }
        else:
            return await self._standard_antibot_detection(response_data)
    
    async def _async_chat(self, prompt: str, json_mode: bool = False) -> str:
        """Async wrapper for DeepSeek chat"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_chat,
            prompt,
            json_mode
        )
    
    def _sync_chat(self, prompt: str, json_mode: bool = False) -> str:
        """Synchronous DeepSeek chat call"""
        messages = [{"role": "user", "content": prompt}]
        
        kwargs = {"model": "deepseek-chat", "messages": messages}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def _async_chat_beta(self, messages: List[Dict], **kwargs) -> str:
        """Async wrapper for DeepSeek beta features"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.beta_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                **kwargs
            ).choices[0].message.content
        )
    
    async def _async_reasoner(self, prompt: str) -> Dict[str, str]:
        """Async wrapper for DeepSeek reasoner"""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[{"role": "user", "content": prompt}]
            )
        )
        
        message = response.choices[0].message
        return {
            'reasoning_content': getattr(message, 'reasoning_content', ''),
            'content': message.content
        }


class StealthAgent:
    """Individual scraping agent with stealth capabilities"""
    
    def __init__(self, agent_id: str, proxy: Optional[str] = None):
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.proxy = proxy
        self.session = None
        self.driver = None
        self.user_agents = self._load_user_agents()
        self.fingerprint = self._generate_fingerprint()
        self.request_count = 0
        self.blocked_count = 0
        self.success_count = 0
        
    def _load_user_agents(self) -> List[str]:
        """Load realistic user agent strings"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def _generate_fingerprint(self) -> Dict[str, Any]:
        """Generate browser fingerprint for stealth"""
        return {
            'user_agent': random.choice(self.user_agents),
            'accept_language': 'en-US,en;q=0.9',
            'accept_encoding': 'gzip, deflate, br',
            'viewport': {'width': 1920, 'height': 1080},
            'timezone': 'America/New_York',
            'webgl_vendor': 'Intel Inc.',
            'canvas_hash': hashlib.md5(str(random.random()).encode()).hexdigest()
        }
    
    async def setup_session(self):
        """Setup aiohttp session with stealth headers"""
        headers = {
            'User-Agent': self.fingerprint['user_agent'],
            'Accept-Language': self.fingerprint['accept_language'],
            'Accept-Encoding': self.fingerprint['accept_encoding'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        connector = aiohttp.TCPConnector(
            limit=100,
            ttl_dns_cache=300,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30)
        
        self.session = aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
        
        if self.proxy:
            self.session._default_proxy = self.proxy
    
    def setup_browser(self):
        """Setup Selenium browser with maximum stealth"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not installed")
            
        options = Options()
        
        # Stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent={self.fingerprint["user_agent"]}')
        
        # Performance options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-logging')
        
        # Headless with stealth
        options.add_argument('--headless=new')
        
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
        
        self.driver = webdriver.Chrome(options=options)
        
        # Apply stealth techniques
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        
        # Inject anti-detection scripts
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {},
                };
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
            '''
        })
    
    async def scrape_static(self, task: ScrapeTask) -> ScrapedData:
        """Static scraping with aiohttp"""
        if not self.session:
            await self.setup_session()
            
        self.status = AgentStatus.ACTIVE
        start_time = time.time()
        
        try:
            # Add random delay
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            async with self.session.get(task.url) as response:
                html = await response.text()
                
                # Check for blocks
                if response.status == 403 or 'cloudflare' in html.lower():
                    self.blocked_count += 1
                    self.status = AgentStatus.BLOCKED
                    raise Exception("Blocked by anti-bot measures")
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract data
                data = ScrapedData(
                    url=task.url,
                    content=soup.get_text(strip=True),
                    raw_html=html,
                    timestamp=datetime.now(),
                    agent_id=self.agent_id,
                    mode=ScrapeMode.STATIC,
                    metadata={
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'response_time': time.time() - start_time
                    }
                )
                
                # Extract links
                data.links = [
                    urljoin(task.url, link.get('href'))
                    for link in soup.find_all('a', href=True)
                ]
                
                # Extract media
                data.media = [
                    {'type': 'image', 'url': urljoin(task.url, img.get('src'))}
                    for img in soup.find_all('img', src=True)
                ]
                
                self.success_count += 1
                self.status = AgentStatus.IDLE
                return data
                
        except Exception as e:
            self.status = AgentStatus.FAILED
            return ScrapedData(
                url=task.url,
                content='',
                raw_html='',
                timestamp=datetime.now(),
                agent_id=self.agent_id,
                mode=ScrapeMode.STATIC,
                metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def scrape_browser(self, task: ScrapeTask) -> ScrapedData:
        """Browser-based scraping with Selenium"""
        if not self.driver:
            self.setup_browser()
            
        self.status = AgentStatus.ACTIVE
        
        try:
            # Navigate with random delay
            await asyncio.sleep(random.uniform(1, 3))
            self.driver.get(task.url)
            
            # Wait for dynamic content
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Random scrolling to appear human
            for _ in range(random.randint(2, 5)):
                scroll_height = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Get page source
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Execute custom JavaScript if needed
            if 'js_commands' in task.metadata:
                for js in task.metadata['js_commands']:
                    self.driver.execute_script(js)
            
            data = ScrapedData(
                url=task.url,
                content=soup.get_text(strip=True),
                raw_html=html,
                timestamp=datetime.now(),
                agent_id=self.agent_id,
                mode=ScrapeMode.BROWSER,
                metadata={
                    'title': self.driver.title,
                    'cookies': self.driver.get_cookies(),
                    'window_size': self.driver.get_window_size()
                }
            )
            
            # Screenshot capability
            if task.metadata.get('screenshot'):
                screenshot = self.driver.get_screenshot_as_base64()
                data.metadata['screenshot'] = screenshot
            
            self.success_count += 1
            self.status = AgentStatus.IDLE
            return data
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            return ScrapedData(
                url=task.url,
                content='',
                raw_html='',
                timestamp=datetime.now(),
                agent_id=self.agent_id,
                mode=ScrapeMode.BROWSER,
                metadata={'error': str(e)},
                errors=[str(e)]
            )
    
    async def rotate_identity(self):
        """Rotate agent identity to avoid detection"""
        self.status = AgentStatus.ROTATING
        
        # Close existing connections
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()
            
        # Generate new fingerprint
        self.fingerprint = self._generate_fingerprint()
        
        # Reset counters
        self.request_count = 0
        self.blocked_count = 0
        
        # Re-setup connections
        await self.setup_session()
        if SELENIUM_AVAILABLE:
            self.setup_browser()
            
        self.status = AgentStatus.IDLE


class AgentPool:
    """Manages a pool of scraping agents"""
    
    def __init__(self, size: int = 5, proxies: Optional[List[str]] = None):
        self.size = size
        self.proxies = proxies or []
        self.agents = []
        self.task_queue = PriorityQueue()
        self.result_queue = Queue()
        self.watchdog_active = True
        self._setup_agents()
        
    def _setup_agents(self):
        """Initialize agent pool"""
        for i in range(self.size):
            proxy = self.proxies[i % len(self.proxies)] if self.proxies else None
            agent = StealthAgent(f"agent_{i}", proxy)
            self.agents.append(agent)
    
    async def submit_task(self, task: ScrapeTask):
        """Submit a scraping task to the pool"""
        await self.task_queue.put(task)
    
    async def get_result(self) -> Optional[ScrapedData]:
        """Get a scraping result"""
        try:
            return await asyncio.wait_for(
                self.result_queue.get(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            return None
    
    async def agent_worker(self, agent: StealthAgent):
        """Worker coroutine for each agent"""
        while self.watchdog_active:
            try:
                # Get task with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                # Check agent health
                if agent.blocked_count > 3:
                    await agent.rotate_identity()
                
                # Execute scraping based on mode
                if task.mode == ScrapeMode.STATIC:
                    result = await agent.scrape_static(task)
                elif task.mode == ScrapeMode.BROWSER:
                    result = await agent.scrape_browser(task)
                else:
                    result = await agent.scrape_static(task)  # Default
                
                # Handle retries
                if result.errors and task.retry_count < task.max_retries:
                    task.retry_count += 1
                    await self.task_queue.put(task)
                else:
                    await self.result_queue.put(result)
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                console.print(f"[red]Agent {agent.agent_id} error: {e}[/red]")
    
    async def watchdog(self):
        """Monitor agent health and performance"""
        while self.watchdog_active:
            await asyncio.sleep(10)  # Check every 10 seconds
            
            for agent in self.agents:
                # Check for stuck agents
                if agent.status == AgentStatus.ACTIVE:
                    # Implement timeout logic
                    pass
                    
                # Auto-rotate blocked agents
                if agent.status == AgentStatus.BLOCKED:
                    await agent.rotate_identity()
                    
                # Log statistics
                if agent.request_count > 0:
                    success_rate = agent.success_count / agent.request_count
                    if success_rate < 0.5:
                        console.print(f"[yellow]Agent {agent.agent_id} low success rate: {success_rate:.2%}[/yellow]")
    
    async def start(self):
        """Start the agent pool"""
        # Setup agents
        for agent in self.agents:
            await agent.setup_session()
        
        # Start workers
        workers = [
            asyncio.create_task(self.agent_worker(agent))
            for agent in self.agents
        ]
        
        # Start watchdog
        watchdog_task = asyncio.create_task(self.watchdog())
        
        # Wait for all tasks
        await asyncio.gather(*workers, watchdog_task)
    
    async def shutdown(self):
        """Gracefully shutdown the pool"""
        self.watchdog_active = False
        
        # Close all agents
        for agent in self.agents:
            if agent.session:
                await agent.session.close()
            if agent.driver:
                agent.driver.quit()


class AdvancedWebScraper:
    """Main orchestrator for advanced web scraping operations"""
    
    def __init__(self, deepseek_api_key: str, pool_size: int = 5):
        self.deepseek = DeepSeekIntelligence(deepseek_api_key)
        self.agent_pool = AgentPool(pool_size)
        self.vector_store = self._setup_vector_store()
        self.context_cache = {}
        self.session_data = {}
        
    def _setup_vector_store(self):
        """Setup ChromaDB for memory and pattern storage"""
        client = chromadb.Client()
        return client.create_collection(
            name="scrape_patterns",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def intelligent_scrape(self, url: str, depth: int = 1) -> Dict[str, Any]:
        """Perform intelligent scraping with AI analysis"""
        console.print(f"[green]Starting intelligent scrape of {url}[/green]")
        
        # First pass: analyze with static scraping
        initial_task = ScrapeTask(
            url=url,
            mode=ScrapeMode.STATIC,
            depth=depth,
            priority=1
        )
        
        await self.agent_pool.submit_task(initial_task)
        initial_result = await self.agent_pool.get_result()
        
        if not initial_result or initial_result.errors:
            console.print("[red]Initial scrape failed[/red]")
            return {}
        
        # AI analysis of page structure
        structure = await self.deepseek.analyze_page_structure(initial_result.raw_html)
        
        # Detect anti-bot measures
        antibot_analysis = await self.deepseek.detect_antibot_patterns({
            'status': initial_result.metadata.get('status_code'),
            'headers': initial_result.metadata.get('headers'),
            'content': initial_result.content[:1000]
        })
        
        # Generate extraction strategy
        if antibot_analysis.get('detection', {}).get('requires_browser'):
            # Switch to browser mode
            browser_task = ScrapeTask(
                url=url,
                mode=ScrapeMode.BROWSER,
                depth=depth,
                priority=1,
                metadata={'structure': structure}
            )
            await self.agent_pool.submit_task(browser_task)
            result = await self.agent_pool.get_result()
        else:
            result = initial_result
        
        # Generate custom extraction code
        extraction_code = await self.deepseek.generate_extraction_code(structure)
        
        # Execute extraction (safely)
        try:
            namespace = {'soup': BeautifulSoup(result.raw_html, 'html.parser')}
            exec(extraction_code, namespace)
            extracted = namespace.get('extract', lambda x: {})(namespace['soup'])
            result.extracted_data = extracted
        except Exception as e:
            console.print(f"[red]Extraction error: {e}[/red]")
        
        # Store patterns for future use
        self._store_pattern(url, structure, extraction_code)
        
        # Recursive scraping if depth > 1
        if depth > 1 and result.links:
            sub_tasks = [
                ScrapeTask(
                    url=link,
                    mode=ScrapeMode.STATIC,
                    depth=depth - 1,
                    priority=5
                )
                for link in result.links[:10]  # Limit to 10 links
            ]
            
            for task in sub_tasks:
                await self.agent_pool.submit_task(task)
        
        return {
            'url': url,
            'data': result.extracted_data,
            'content': result.content,
            'links': result.links,
            'media': result.media,
            'ai_analysis': {
                'structure': structure,
                'antibot': antibot_analysis,
                'extraction_code': extraction_code
            }
        }
    
    def _store_pattern(self, url: str, structure: Dict, code: str):
        """Store scraping patterns for reuse"""
        pattern_id = hashlib.md5(url.encode()).hexdigest()
        
        self.vector_store.add(
            ids=[pattern_id],
            documents=[json.dumps(structure)],
            metadatas=[{
                'url': url,
                'code': code,
                'timestamp': datetime.now().isoformat()
            }]
        )
    
    async def scrape_with_pattern_matching(self, url: str) -> Dict[str, Any]:
        """Use stored patterns for efficient scraping"""
        # Search for similar patterns
        domain = urlparse(url).netloc
        results = self.vector_store.query(
            query_texts=[domain],
            n_results=5
        )
        
        if results['metadatas'][0]:
            # Use existing pattern
            pattern = results['metadatas'][0][0]
            console.print(f"[blue]Using cached pattern for {domain}[/blue]")
            
            # Apply pattern
            task = ScrapeTask(
                url=url,
                mode=ScrapeMode.STATIC,
                priority=3,
                metadata={'pattern': pattern}
            )
            
            await self.agent_pool.submit_task(task)
            result = await self.agent_pool.get_result()
            
            if result and not result.errors:
                # Execute stored extraction code
                try:
                    namespace = {'soup': BeautifulSoup(result.raw_html, 'html.parser')}
                    exec(pattern['code'], namespace)
                    extracted = namespace.get('extract', lambda x: {})(namespace['soup'])
                    result.extracted_data = extracted
                except:
                    pass
                    
                return {
                    'url': url,
                    'data': result.extracted_data,
                    'content': result.content,
                    'pattern_used': True
                }
        
        # Fall back to intelligent scraping
        return await self.intelligent_scrape(url)
    
    async def media_extraction(self, url: str) -> Dict[str, List[str]]:
        """Extract and analyze media from a page"""
        task = ScrapeTask(
            url=url,
            mode=ScrapeMode.BROWSER,  # Browser for dynamic media
            priority=2,
            metadata={'screenshot': True}
        )
        
        await self.agent_pool.submit_task(task)
        result = await self.agent_pool.get_result()
        
        if not result:
            return {'images': [], 'videos': [], 'audio': []}
        
        # Extract media URLs
        soup = BeautifulSoup(result.raw_html, 'html.parser')
        
        media = {
            'images': [
                urljoin(url, img.get('src', ''))
                for img in soup.find_all(['img', 'picture'])
                if img.get('src')
            ],
            'videos': [
                urljoin(url, vid.get('src', ''))
                for vid in soup.find_all(['video', 'source'])
                if vid.get('src')
            ],
            'audio': [
                urljoin(url, aud.get('src', ''))
                for aud in soup.find_all('audio')
                if aud.get('src')
            ]
        }
        
        # AI analysis of media context
        if media['images']:
            prompt = f"Analyze these image URLs and their context: {media['images'][:5]}"
            analysis = await self.deepseek._async_chat(prompt)
            media['ai_analysis'] = analysis
        
        return media
    
    async def social_media_scrape(self, profile_url: str) -> Dict[str, Any]:
        """Specialized scraping for social media profiles"""
        # Use browser mode for JavaScript-heavy sites
        task = ScrapeTask(
            url=profile_url,
            mode=ScrapeMode.BROWSER,
            priority=1,
            metadata={
                'js_commands': [
                    # Scroll to load more content
                    'window.scrollTo(0, document.body.scrollHeight);',
                    # Wait for lazy loading
                    'await new Promise(r => setTimeout(r, 2000));'
                ]
            }
        )
        
        await self.agent_pool.submit_task(task)
        result = await self.agent_pool.get_result()
        
        if not result:
            return {}
        
        # Extract social media specific data
        soup = BeautifulSoup(result.raw_html, 'html.parser')
        
        # Use AI to identify profile elements
        profile_analysis = await self.deepseek.analyze_page_structure(result.raw_html)
        
        return {
            'url': profile_url,
            'profile_data': profile_analysis,
            'media': result.media,
            'extracted_text': result.content
        }
    
    async def api_endpoint_discovery(self, base_url: str) -> List[Dict[str, Any]]:
        """Discover and document API endpoints"""
        # Scrape the main page
        task = ScrapeTask(url=base_url, mode=ScrapeMode.BROWSER, priority=1)
        await self.agent_pool.submit_task(task)
        result = await self.agent_pool.get_result()
        
        if not result:
            return []
        
        # Analyze network requests using browser logs
        if result.mode == ScrapeMode.BROWSER:
            # This would require browser network interception
            # Placeholder for API discovery logic
            pass
        
        # Use AI to identify API patterns
        api_patterns = await self.deepseek._async_chat(
            f"Identify potential API endpoints in this HTML:\n{result.raw_html[:3000]}",
            json_mode=True
        )
        
        return json.loads(api_patterns).get('endpoints', [])
    
    async def run_campaign(self, targets: List[str], strategy: str = "intelligent"):
        """Run a scraping campaign across multiple targets"""
        console.print(f"[bold green]Starting scraping campaign with {len(targets)} targets[/bold green]")
        
        # Start agent pool
        pool_task = asyncio.create_task(self.agent_pool.start())
        
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task_id = progress.add_task("Scraping...", total=len(targets))
            
            for target in targets:
                try:
                    if strategy == "intelligent":
                        result = await self.intelligent_scrape(target)
                    elif strategy == "pattern":
                        result = await self.scrape_with_pattern_matching(target)
                    elif strategy == "media":
                        result = await self.media_extraction(target)
                    else:
                        result = await self.intelligent_scrape(target)
                        
                    results.append(result)
                    progress.update(task_id, advance=1, description=f"Scraped {target}")
                    
                except Exception as e:
                    console.print(f"[red]Error scraping {target}: {e}[/red]")
                    results.append({'url': target, 'error': str(e)})
        
        # Shutdown pool
        await self.agent_pool.shutdown()
        pool_task.cancel()
        
        return results
    
    def export_results(self, results: List[Dict], format: str = "json") -> str:
        """Export scraping results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"scrape_results_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
                
        elif format == "csv":
            filename = f"scrape_results_{timestamp}.csv"
            # Flatten nested data for CSV
            flattened = []
            for r in results:
                flat = {'url': r.get('url', '')}
                if isinstance(r.get('data'), dict):
                    flat.update(r['data'])
                flattened.append(flat)
            
            df = pd.DataFrame(flattened)
            df.to_csv(filename, index=False)
            
        elif format == "html":
            filename = f"scrape_report_{timestamp}.html"
            # Generate HTML report
            html_content = self._generate_html_report(results)
            with open(filename, 'w') as f:
                f.write(html_content)
        
        console.print(f"[green]Results exported to {filename}[/green]")
        return filename
    
    def _generate_html_report(self, results: List[Dict]) -> str:
        """Generate an HTML report of scraping results"""
        html = """
        <html>
        <head>
            <title>Scraping Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .result { border: 1px solid #ddd; padding: 10px; margin: 10px 0; }
                .url { font-weight: bold; color: #0066cc; }
                .data { background-color: #f5f5f5; padding: 10px; margin: 10px 0; }
                .error { color: red; }
                pre { white-space: pre-wrap; }
            </style>
        </head>
        <body>
            <h1>Web Scraping Report</h1>
            <p>Generated: {timestamp}</p>
            <p>Total URLs: {total}</p>
            <hr>
        """.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total=len(results)
        )
        
        for result in results:
            html += f"""
            <div class="result">
                <div class="url">{result.get('url', 'Unknown')}</div>
            """
            
            if 'error' in result:
                html += f'<div class="error">Error: {result["error"]}</div>'
            else:
                if result.get('data'):
                    html += '<div class="data"><pre>{}</pre></div>'.format(
                        json.dumps(result['data'], indent=2)
                    )
                if result.get('ai_analysis'):
                    html += '<div class="data"><h4>AI Analysis</h4><pre>{}</pre></div>'.format(
                        json.dumps(result['ai_analysis'], indent=2)
                    )
            
            html += "</div>"
        
        html += "</body></html>"
        return html


# Utility functions
from urllib.parse import urljoin, urlparse


async def main():
    """Example usage of the advanced scraper"""
    # Initialize scraper
    scraper = AdvancedWebScraper(
        deepseek_api_key="your_api_key_here",
        pool_size=5
    )
    
    # Example 1: Intelligent scraping
    result = await scraper.intelligent_scrape("https://example.com", depth=2)
    console.print(result)
    
    # Example 2: Media extraction
    media = await scraper.media_extraction("https://example.com")
    console.print(f"Found {len(media['images'])} images")
    
    # Example 3: Campaign mode
    targets = [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com"
    ]
    
    campaign_results = await scraper.run_campaign(targets, strategy="intelligent")
    
    # Export results
    scraper.export_results(campaign_results, format="html")


if __name__ == "__main__":
    asyncio.run(main())