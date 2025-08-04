"""
Web Scraper Tool - Enhanced BASED GOD CLI
Modular web scraping with Agent Zero reasoning patterns
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
import random

from .base_tool import BaseTool, ToolResponse, ToolStatus

class WebScraperTool(BaseTool):
    """
    Advanced web scraper with Agent Zero-inspired reasoning
    """
    
    def __init__(self) -> Any:
        super().__init__(
            name="Web Scraper",
            description="Intelligent web scraping with rate limiting, content analysis, and structured data extraction",
            capabilities=[
                "HTTP/HTTPS requests with session management",
                "HTML parsing and content extraction", 
                "Rate limiting and respectful scraping",
                "Content type detection and adaptation",
                "Link discovery and pagination handling",
                "Error handling and retry logic"
            ]
        )
        self.session = None
        self.rate_limit = 1.0
        
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute web scraping with enhanced reasoning"""
        
        url = kwargs.get("url")
        extraction_type = kwargs.get("extraction_type", "auto")
        rate_limit = kwargs.get("rate_limit", 1.0)
        max_retries = kwargs.get("max_retries", 3)
        
        if not url:
            return ToolResponse(
                success=False,
                message="URL parameter is required",
                status=ToolStatus.FAILED
            )
        
        try:
            # Initialize session if needed
            if not self.session:
                await self._init_session()
            
            # Apply rate limiting
            await asyncio.sleep(random.uniform(0.5, rate_limit))
            
            # Analyze target before scraping
            target_analysis = self._analyze_target(url)
            
            # Execute scraping with reasoning
            scraping_result = await self._scrape_with_reasoning(
                url, target_analysis, extraction_type, max_retries
            )
            
            return ToolResponse(
                success=True,
                message=f"Successfully scraped {url}",
                data={
                    "url": url,
                    "target_analysis": target_analysis,
                    "extracted_data": scraping_result["data"],
                    "items_found": len(scraping_result["data"]),
                    "scraping_strategy": scraping_result["strategy"]
                },
                metadata={
                    "response_code": scraping_result.get("response_code"),
                    "content_type": scraping_result.get("content_type"),
                    "page_size": scraping_result.get("page_size")
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Web scraping failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for web scraper"""
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target URL to scrape"
                },
                "extraction_type": {
                    "type": "string",
                    "enum": ["auto", "news", "ecommerce", "links", "text", "custom"],
                    "description": "Type of content to extract",
                    "default": "auto"
                },
                "rate_limit": {
                    "type": "number",
                    "description": "Rate limit in seconds between requests",
                    "default": 1.0,
                    "minimum": 0.1
                },
                "max_retries": {
                    "type": "integer",
                    "description": "Maximum number of retry attempts",
                    "default": 3,
                    "minimum": 0
                },
                "custom_selectors": {
                    "type": "object",
                    "description": "Custom CSS selectors for extraction"
                }
            },
            "required": ["url"]
        }
    
    async def _init_session(self) -> Any:
        """Initialize HTTP session with proper headers"""
        headers = {
            'User-Agent': 'BasedGod-Enhanced-Scraper/2.0 (Agent-Zero-Inspired; +https://github.com/based-god-cli)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
    
    def _analyze_target(self, url: str) -> Dict[str, Any]:
        """
        Agent Zero-inspired target analysis
        Determines the best scraping strategy
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        
        analysis = {
            "domain": domain,
            "path": path,
            "site_type": "unknown",
            "complexity": "medium",
            "strategy": "generic",
            "risk_level": "low"
        }
        
        # Domain-based analysis
        if any(keyword in domain for keyword in ['news', 'blog', 'article', 'press']):
            analysis.update({
                "site_type": "news",
                "strategy": "news_extraction",
                "complexity": "medium"
            })
        elif any(keyword in domain for keyword in ['shop', 'store', 'ecommerce', 'buy', 'sell']):
            analysis.update({
                "site_type": "ecommerce", 
                "strategy": "product_extraction",
                "complexity": "high",
                "risk_level": "medium"
            })
        elif any(keyword in domain for keyword in ['github', 'gitlab', 'bitbucket']):
            analysis.update({
                "site_type": "code_repository",
                "strategy": "repository_extraction",
                "complexity": "low"
            })
        elif any(keyword in domain for keyword in ['wiki']):
            analysis.update({
                "site_type": "wiki",
                "strategy": "wiki_extraction", 
                "complexity": "medium"
            })
        
        # Path-based refinement
        if '/api/' in path:
            analysis.update({
                "site_type": "api",
                "strategy": "api_extraction",
                "complexity": "low"
            })
        
        return analysis
    
    async def _scrape_with_reasoning(self, url: str, analysis: Dict, extraction_type: str, max_retries: int) -> Dict[str, Any]:
        """Execute scraping with Agent Zero reasoning patterns"""
        
        retries = 0
        while retries <= max_retries:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        content_type = response.headers.get('content-type', '')
                        
                        # Parse content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract data based on analysis and type
                        extracted_data = self._extract_data(
                            soup, analysis, extraction_type
                        )
                        
                        return {
                            "data": extracted_data,
                            "strategy": analysis["strategy"],
                            "response_code": response.status,
                            "content_type": content_type,
                            "page_size": len(content)
                        }
                    else:
                        retries += 1
                        if retries <= max_retries:
                            await asyncio.sleep(2 ** retries)  # Exponential backoff
                        else:
                            raise Exception(f"HTTP {response.status}: {response.reason}")
                        
            except Exception as e:
                retries += 1
                if retries > max_retries:
                    raise e
                await asyncio.sleep(2 ** retries)
    
    def _extract_data(self, soup: BeautifulSoup, analysis: Dict, extraction_type: str) -> List[Dict]:
        """Extract data based on site analysis and extraction type"""
        
        extracted = []
        strategy = analysis["strategy"]
        
        if extraction_type == "auto":
            extraction_type = self._determine_auto_extraction(strategy)
        
        if extraction_type == "news" or strategy == "news_extraction":
            extracted = self._extract_news_content(soup)
        elif extraction_type == "ecommerce" or strategy == "product_extraction":
            extracted = self._extract_product_content(soup)
        elif extraction_type == "links":
            extracted = self._extract_links(soup)
        elif extraction_type == "text":
            extracted = self._extract_text_content(soup)
        else:
            extracted = self._extract_generic_content(soup)
        
        return extracted
    
    def _determine_auto_extraction(self, strategy: str) -> str:
        """Automatically determine extraction type based on strategy"""
        strategy_mapping = {
            "news_extraction": "news",
            "product_extraction": "ecommerce", 
            "repository_extraction": "links",
            "wiki_extraction": "text",
            "api_extraction": "text"
        }
        return strategy_mapping.get(strategy, "text")
    
    def _extract_news_content(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract news articles and related content"""
        articles = []
        
        # Look for article containers
        article_selectors = [
            'article', 
            '[class*="article"]',
            '[class*="news"]',
            '[class*="post"]',
            '.entry-content',
            '.content'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)
            for element in elements[:10]:  # Limit results
                title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                content_elem = element.find(['p', 'div'])
                
                if title_elem:
                    article = {
                        "type": "article",
                        "title": title_elem.get_text(strip=True),
                        "content": content_elem.get_text(strip=True)[:300] + "..." if content_elem else "",
                        "link": self._find_link(element),
                        "timestamp": self._extract_timestamp(element)
                    }
                    articles.append(article)
            
            if articles:  # Found articles with this selector
                break
        
        return articles
    
    def _extract_product_content(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract product information"""
        products = []
        
        # Look for product containers
        product_selectors = [
            '[class*="product"]',
            '[class*="item"]', 
            '[class*="listing"]',
            '.product-card',
            '.item-card'
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            for element in elements[:15]:  # Limit results
                name_elem = element.find(['h1', 'h2', 'h3', 'h4'])
                price_elem = element.find(text=lambda x: x and any(currency in str(x) for currency in ['$', '€', '£', '¥', 'USD', 'EUR']))
                
                if name_elem:
                    product = {
                        "type": "product",
                        "name": name_elem.get_text(strip=True),
                        "price": price_elem.strip() if price_elem else "Price not found",
                        "link": self._find_link(element),
                        "image": self._find_image(element)
                    }
                    products.append(product)
            
            if products:  # Found products with this selector
                break
        
        return products
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all links from the page"""
        links = []
        
        for link in soup.find_all('a', href=True)[:20]:  # Limit to 20 links
            href = link['href']
            text = link.get_text(strip=True)
            
            if text and href:
                links.append({
                    "type": "link",
                    "text": text[:100],  # Truncate long text
                    "url": href,
                    "is_external": href.startswith(('http://', 'https://'))
                })
        
        return links
    
    def _extract_text_content(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract main text content"""
        content_areas = []
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Find main content areas
        main_selectors = ['main', 'article', '.content', '.main', '#content', '#main']
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                for i, p in enumerate(paragraphs[:10]):
                    text = p.get_text(strip=True)
                    if len(text) > 50:  # Only meaningful paragraphs
                        content_areas.append({
                            "type": "paragraph",
                            "content": text,
                            "position": i + 1,
                            "word_count": len(text.split())
                        })
                break
        
        # If no main content found, get all paragraphs
        if not content_areas:
            for i, p in enumerate(soup.find_all('p')[:10]):
                text = p.get_text(strip=True)
                if len(text) > 50:
                    content_areas.append({
                        "type": "paragraph",
                        "content": text,
                        "position": i + 1,
                        "word_count": len(text.split())
                    })
        
        return content_areas
    
    def _extract_generic_content(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract generic content when type is unknown"""
        content = []
        
        # Get title
        title = soup.find('title')
        if title:
            content.append({
                "type": "title",
                "content": title.get_text(strip=True)
            })
        
        # Get headings
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3'])[:5]):
            content.append({
                "type": "heading",
                "content": heading.get_text(strip=True),
                "level": heading.name,
                "position": i + 1
            })
        
        # Get some paragraphs
        for i, p in enumerate(soup.find_all('p')[:5]):
            text = p.get_text(strip=True)
            if len(text) > 30:
                content.append({
                    "type": "paragraph",
                    "content": text[:200] + "..." if len(text) > 200 else text,
                    "position": i + 1
                })
        
        return content
    
    def _find_link(self, element) -> Optional[str]:
        """Find a link within an element"""
        link = element.find('a', href=True)
        return link['href'] if link else None
    
    def _find_image(self, element) -> Optional[str]:
        """Find an image within an element"""
        img = element.find('img', src=True)
        return img['src'] if img else None
    
    def _extract_timestamp(self, element) -> Optional[str]:
        """Extract timestamp from an element"""
        # Look for time elements or date patterns
        time_elem = element.find('time')
        if time_elem:
            return time_elem.get('datetime') or time_elem.get_text(strip=True)
        
        # Look for date patterns in text
        import re
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
        text = element.get_text()
        match = re.search(date_pattern, text)
        return match.group() if match else None
    
    async def close(self) -> Any:
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None