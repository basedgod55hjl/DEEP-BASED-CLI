"""
SuperAgentScraper - Advanced Multi-Modal Web Scraper with DeepSeek AI
Production-ready scraper with media processing, vector memory, and intelligent analysis
"""

import os
import re
import json
import time
import mimetypes
import hashlib
import importlib.util
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Union
import requests
import pdfplumber
import pytesseract
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import moviepy.editor as mp
import speech_recognition as sr
import base64
from datetime import datetime
import subprocess
import platform
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
import tempfile
import shutil

# Initialize console for rich output
console = Console()

class SuperAgentScraper:
    def __init__(self, api_key=None, storage_path="scraped_media", max_workers=5):
        # Hardcoded DeepSeek API key
        self.api_key = api_key or "sk-90e0dd863b8c4e0d879a02851a0ee194"
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize DeepSeek clients
        self.openai_client = OpenAI(
            api_key=self.api_key, 
            base_url="https://api.deepseek.com"
        )
        self.beta_client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/beta"
        )
        
        # Initialize vector database
        self.qdrant_client = QdrantClient(":memory:")
        self.create_vector_db()
        
        # State management
        self.conversation_history = []
        self.scrape_memory = {}
        self.driver_pool = []
        self.max_workers = max_workers
        
        # Watchdog systems
        self.watchdogs = {
            "block_detection": self.detect_blocks,
            "anomaly_monitor": self.monitor_anomalies,
            "rate_limiter": self.rate_limit_check,
            "fingerprint_rotation": self.rotate_fingerprint
        }
        
        # Initialize driver pool
        self.init_driver_pool(3)
        
        # Load dynamic tool handlers
        self.tool_handlers = self.load_tool_handlers()
        
        # Session tracking
        self.session_stats = {
            "total_scrapes": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "media_processed": 0,
            "blocks_detected": 0
        }

    def load_tool_handlers(self) -> Dict[str, Any]:
        """Dynamically load all handlers from ./tools directory."""
        handlers = {
            "image": self.process_image,
            "img": self.process_image,
            "pdf": self.process_pdf,
            "video": self.process_video,
            "audio": self.process_audio,
            "document": self.process_document,
            "text": self.process_text,
            "code": self.process_code
        }
        
        # Create tools directory if it doesn't exist
        os.makedirs('./tools', exist_ok=True)
        
        # Load custom handlers
        for fname in glob.glob('./tools/*.py'):
            try:
                spec = importlib.util.spec_from_file_location("mod", fname)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, 'TYPE') and hasattr(mod, 'process'):
                    handlers[mod.TYPE] = mod.process
                    console.print(f"[green]Loaded handler: {mod.TYPE} from {fname}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to load handler from {fname}: {e}[/red]")
        
        return handlers

    def create_vector_db(self):
        """Initialize vector database collections"""
        collections = [
            ("media_memory", 1536),  # For general embeddings
            ("scrape_patterns", 1536),  # For URL patterns
            ("conversation_memory", 1536)  # For conversation context
        ]
        
        for collection_name, vector_size in collections:
            try:
                self.qdrant_client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
            except:
                pass

    def init_driver_pool(self, size):
        """Initialize pool of Selenium drivers with stealth settings"""
        for i in range(size):
            options = Options()
            
            # Stealth mode settings
            options.add_argument("--headless=new")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            ]
            options.add_argument(f'user-agent={user_agents[i % len(user_agents)]}')
            
            try:
                driver = webdriver.Chrome(options=options)
                
                # Inject anti-detection JavaScript
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
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
                        Object.defineProperty(navigator, 'permissions', {
                            get: () => ({
                                query: () => Promise.resolve({ state: 'granted' })
                            })
                        });
                    '''
                })
                
                self.driver_pool.append(driver)
            except Exception as e:
                console.print(f"[red]Failed to create driver {i}: {e}[/red]")

    def get_driver(self):
        """Get an available driver from the pool"""
        if not self.driver_pool:
            self.init_driver_pool(1)
        return self.driver_pool.pop()

    def release_driver(self, driver):
        """Return driver to the pool"""
        self.driver_pool.append(driver)

    def detect_blocks(self, html):
        """Detect common blocking patterns"""
        block_signals = [
            "access denied", "cloudflare", "captcha", "bot detected", 
            "security check", "rate limit", "forbidden", "blocked",
            "verification required", "unusual traffic"
        ]
        detected = any(signal in html.lower() for signal in block_signals)
        if detected:
            self.session_stats["blocks_detected"] += 1
        return detected

    def monitor_anomalies(self, response):
        """Monitor for anomalous responses"""
        anomalies = []
        
        if hasattr(response, 'status_code'):
            if response.status_code == 403:
                anomalies.append("FORBIDDEN")
            elif response.status_code == 429:
                anomalies.append("RATE_LIMITED")
            elif response.status_code >= 500:
                anomalies.append("SERVER_ERROR")
                
        if hasattr(response, 'elapsed') and response.elapsed.total_seconds() > 10:
            anomalies.append("SLOW_RESPONSE")
            
        return anomalies if anomalies else None

    def rate_limit_check(self):
        """Check if we're hitting rate limits"""
        # Simple rate limiting based on recent requests
        current_time = time.time()
        window_size = 60  # 1 minute window
        
        # Clean old entries
        self.scrape_memory = {
            k: v for k, v in self.scrape_memory.items() 
            if current_time - v < window_size
        }
        
        requests_per_minute = len(self.scrape_memory)
        if requests_per_minute > 30:  # Max 30 requests per minute
            return True
        return False

    def rotate_fingerprint(self, driver):
        """Rotate browser fingerprint"""
        # Change viewport size
        viewports = [(1920, 1080), (1366, 768), (1440, 900), (1536, 864)]
        width, height = viewports[hash(str(time.time())) % len(viewports)]
        driver.set_window_size(width, height)
        
        # Inject new fingerprint
        driver.execute_script("""
            Object.defineProperty(screen, 'width', { get: () => %d });
            Object.defineProperty(screen, 'height', { get: () => %d });
        """ % (width, height))

    def deepseek_reason(self, prompt: str) -> Dict[str, str]:
        """Use DeepSeek reasoner for complex analysis"""
        try:
            response = self.openai_client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            message = response.choices[0].message
            return {
                "reasoning": getattr(message, 'reasoning_content', ''),
                "answer": message.content
            }
        except Exception as e:
            console.print(f"[red]Reasoner error: {e}[/red]")
            return {"reasoning": "", "answer": str(e)}

    def deepseek_chat(self, messages: List[Dict[str, str]]) -> str:
        """Use DeepSeek chat for conversations"""
        try:
            response = self.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"[red]Chat error: {e}[/red]")
            return str(e)

    def deepseek_fim(self, prefix: str, suffix: str = "") -> str:
        """Use DeepSeek FIM completion"""
        try:
            response = self.beta_client.completions.create(
                model="deepseek-chat",
                prompt=prefix,
                suffix=suffix,
                max_tokens=500
            )
            return response.choices[0].text
        except Exception as e:
            console.print(f"[red]FIM error: {e}[/red]")
            return str(e)

    def deepseek_prefix_complete(self, messages: List[Dict[str, str]], prefix: str) -> str:
        """Use DeepSeek prefix completion"""
        try:
            # Add prefix to last assistant message
            messages.append({"role": "assistant", "content": prefix, "prefix": True})
            
            response = self.beta_client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"[red]Prefix completion error: {e}[/red]")
            return str(e)

    def embed_content(self, content: str) -> List[float]:
        """Generate embeddings for content"""
        try:
            response = self.openai_client.embeddings.create(
                input=content[:8000],  # Limit content length
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            console.print(f"[red]Embedding error: {e}[/red]")
            return [0.0] * 1536  # Return zero vector

    def store_memory(self, content: str, metadata: Dict[str, Any], collection: str = "media_memory") -> str:
        """Store content in vector database"""
        try:
            vector = self.embed_content(content)
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            
            self.qdrant_client.upsert(
                collection_name=collection,
                points=[
                    PointStruct(
                        id=content_hash,
                        vector=vector,
                        payload={
                            "content": content[:5000],  # Limit stored content
                            "metadata": metadata,
                            "timestamp": int(time.time())
                        }
                    )
                ]
            )
            return content_hash
        except Exception as e:
            console.print(f"[red]Memory storage error: {e}[/red]")
            return ""

    def query_memory(self, query: str, top_k: int = 3, collection: str = "media_memory") -> List[Dict[str, Any]]:
        """Query vector memory"""
        try:
            query_vector = self.embed_content(query)
            results = self.qdrant_client.search(
                collection_name=collection,
                query_vector=query_vector,
                limit=top_k
            )
            return [{"score": r.score, "payload": r.payload} for r in results]
        except Exception as e:
            console.print(f"[red]Memory query error: {e}[/red]")
            return []

    def extract_all_media(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract all media links from HTML"""
        media_links = []
        
        # Images
        for img in soup.find_all(['img', 'picture']):
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                media_links.append({
                    'url': urljoin(base_url, src),
                    'type': 'image',
                    'alt': img.get('alt', ''),
                    'element': str(img)[:200]
                })
        
        # Videos
        for video in soup.find_all(['video', 'source']):
            src = video.get('src')
            if src:
                media_links.append({
                    'url': urljoin(base_url, src),
                    'type': 'video',
                    'element': str(video)[:200]
                })
        
        # Audio
        for audio in soup.find_all('audio'):
            src = audio.get('src')
            if src:
                media_links.append({
                    'url': urljoin(base_url, src),
                    'type': 'audio',
                    'element': str(audio)[:200]
                })
        
        # Documents
        for link in soup.find_all('a', href=True):
            href = link['href']
            ext = os.path.splitext(href)[1].lower()
            if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv']:
                media_links.append({
                    'url': urljoin(base_url, href),
                    'type': 'document',
                    'text': link.get_text(strip=True),
                    'element': str(link)[:200]
                })
        
        # Scripts and data
        for script in soup.find_all('script'):
            if script.get('src'):
                media_links.append({
                    'url': urljoin(base_url, script['src']),
                    'type': 'script',
                    'element': str(script)[:200]
                })
        
        return media_links

    def download_media(self, url: str, media_type: str) -> Optional[str]:
        """Download media file with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            ext = mimetypes.guess_extension(content_type)
            if not ext:
                ext = os.path.splitext(urlparse(url).path)[1] or f".{media_type}"
            
            # Generate unique filename
            filename = f"{hashlib.md5(url.encode()).hexdigest()}{ext}"
            filepath = os.path.join(self.storage_path, filename)
            
            # Download file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.session_stats["media_processed"] += 1
            return filepath
            
        except Exception as e:
            console.print(f"[red]Download failed for {url}: {str(e)}[/red]")
            return None

    def process_image(self, filepath: str) -> Dict[str, Any]:
        """Process image with OCR and AI vision"""
        try:
            result = {}
            
            # OCR extraction
            try:
                text = pytesseract.image_to_string(Image.open(filepath))
                result['ocr_text'] = text.strip()
            except Exception as e:
                result['ocr_error'] = str(e)
            
            # AI vision analysis (if available)
            try:
                with open(filepath, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                
                # Use DeepSeek chat with image description
                prompt = """Analyze this image and provide:
                1. Detailed description
                2. Any text visible
                3. Key objects or elements
                4. Overall context or purpose"""
                
                description = self.deepseek_chat([
                    {"role": "user", "content": prompt}
                ])
                
                result['ai_description'] = description
            except Exception as e:
                result['vision_error'] = str(e)
            
            # Image metadata
            try:
                img = Image.open(filepath)
                result['metadata'] = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'info': img.info
                }
            except:
                pass
            
            return result
            
        except Exception as e:
            return {"error": str(e), "filepath": filepath}

    def process_pdf(self, filepath: str) -> Dict[str, Any]:
        """Extract text and metadata from PDF"""
        try:
            text = ""
            metadata = {}
            tables = []
            
            with pdfplumber.open(filepath) as pdf:
                # Extract metadata
                if pdf.metadata:
                    metadata = {k: str(v) for k, v in pdf.metadata.items()}
                
                # Extract text from each page
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {i+1} ---\n{page_text}"
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            
            # Analyze with AI
            if text:
                analysis_prompt = f"Analyze this PDF content and provide key insights:\n{text[:3000]}"
                analysis = self.deepseek_reason(analysis_prompt)
                
                return {
                    "text": text,
                    "metadata": metadata,
                    "tables": tables,
                    "page_count": len(pdf.pages),
                    "ai_analysis": analysis
                }
            else:
                return {"error": "No text extracted from PDF", "metadata": metadata}
                
        except Exception as e:
            return {"error": str(e), "filepath": filepath}

    def process_video(self, filepath: str) -> Dict[str, Any]:
        """Extract audio and frames from video"""
        try:
            result = {}
            
            # Extract audio for transcription
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                audio_path = tmp_audio.name
                
            video = mp.VideoFileClip(filepath)
            
            # Get video metadata
            result['metadata'] = {
                'duration': video.duration,
                'fps': video.fps,
                'size': video.size
            }
            
            # Extract audio
            if video.audio:
                video.audio.write_audiofile(audio_path, logger=None)
                audio_result = self.process_audio(audio_path)
                result['audio'] = audio_result
                os.unlink(audio_path)
            
            # Extract key frames
            frame_times = [0, video.duration/4, video.duration/2, 3*video.duration/4]
            frames = []
            
            for t in frame_times:
                if t < video.duration:
                    frame = video.get_frame(t)
                    frame_img = Image.fromarray(frame)
                    
                    # Save frame temporarily
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_frame:
                        frame_img.save(tmp_frame.name)
                        frame_analysis = self.process_image(tmp_frame.name)
                        frames.append({
                            'time': t,
                            'analysis': frame_analysis
                        })
                        os.unlink(tmp_frame.name)
            
            result['frames'] = frames
            video.close()
            
            return result
            
        except Exception as e:
            return {"error": str(e), "filepath": filepath}

    def process_audio(self, filepath: str) -> Dict[str, Any]:
        """Transcribe audio to text"""
        try:
            r = sr.Recognizer()
            
            with sr.AudioFile(filepath) as source:
                # Adjust for ambient noise
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.record(source)
                
                # Try multiple recognition engines
                transcript = None
                
                # Try Google Speech Recognition
                try:
                    transcript = r.recognize_google(audio)
                except:
                    pass
                
                # If Google fails, try other engines
                if not transcript:
                    try:
                        # Could try other engines here
                        transcript = "Transcription failed"
                    except:
                        pass
                
                # Analyze transcript with AI
                if transcript and transcript != "Transcription failed":
                    analysis = self.deepseek_chat([
                        {"role": "user", "content": f"Summarize this transcript: {transcript[:1000]}"}
                    ])
                    
                    return {
                        "transcript": transcript,
                        "summary": analysis,
                        "duration": len(audio.frame_data) / audio.sample_rate
                    }
                else:
                    return {"error": "Failed to transcribe audio"}
                    
        except Exception as e:
            return {"error": str(e), "filepath": filepath}

    def process_document(self, filepath: str) -> Dict[str, Any]:
        """Process various document types"""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.txt':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return {"text": content, "type": "text"}
                
            elif ext == '.csv':
                import pandas as pd
                df = pd.read_csv(filepath)
                return {
                    "type": "csv",
                    "shape": df.shape,
                    "columns": list(df.columns),
                    "preview": df.head(10).to_dict(),
                    "summary": df.describe().to_dict()
                }
                
            elif ext in ['.doc', '.docx']:
                # Would need python-docx for proper handling
                return {"type": "word", "note": "Word processing not fully implemented"}
                
            else:
                # Try to read as text
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(5000)  # Read first 5KB
                return {"text": content, "type": "unknown"}
                
        except Exception as e:
            return {"error": str(e), "filepath": filepath}

    def process_text(self, content: str) -> Dict[str, Any]:
        """Process text content with NLP"""
        try:
            # Basic text analysis
            result = {
                "length": len(content),
                "word_count": len(content.split()),
                "line_count": len(content.splitlines())
            }
            
            # AI analysis
            if len(content) > 100:
                analysis = self.deepseek_reason(
                    f"Analyze this text and extract key information:\n{content[:2000]}"
                )
                result['ai_analysis'] = analysis
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    def process_code(self, content: str) -> Dict[str, Any]:
        """Analyze code content"""
        try:
            # Detect language
            language = "unknown"
            if "def " in content or "import " in content:
                language = "python"
            elif "function " in content or "const " in content:
                language = "javascript"
            elif "#include" in content:
                language = "c/c++"
            
            # Code analysis
            analysis = self.deepseek_chat([
                {"role": "user", "content": f"Analyze this {language} code:\n```\n{content[:1500]}\n```"}
            ])
            
            return {
                "language": language,
                "analysis": analysis,
                "line_count": len(content.splitlines())
            }
            
        except Exception as e:
            return {"error": str(e)}

    def adaptive_scrape(self, url: str) -> Dict[str, Any]:
        """Main scraping function with adaptive strategies"""
        driver = None
        try:
            self.session_stats["total_scrapes"] += 1
            console.print(f"[bold green]🚀 Scraping: {url}[/bold green]")
            
            # Check rate limiting
            if self.rate_limit_check():
                time.sleep(2)  # Brief pause
            
            # Record scrape attempt
            self.scrape_memory[url] = time.time()
            
            driver = self.get_driver()
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Random delay to appear human
            time.sleep(1 + hash(url) % 3)
            
            # Rotate fingerprint periodically
            if self.session_stats["total_scrapes"] % 10 == 0:
                self.rotate_fingerprint(driver)
            
            # Get page source
            html = driver.page_source
            
            # Check for blocks
            if self.detect_blocks(html):
                console.print(f"[yellow]⚠️  Block detected on {url}[/yellow]")
                # Try to bypass or wait
                time.sleep(5)
                html = driver.page_source
            
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract main content
            main_content = soup.get_text(separator=' ', strip=True)
            
            # Extract structured data
            structured_data = self.extract_structured_data(soup)
            
            # Extract all media
            media_links = self.extract_all_media(soup, url)
            console.print(f"[blue]Found {len(media_links)} media items[/blue]")
            
            # Process media files
            media_results = []
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("Processing media...", total=len(media_links))
                
                for media in media_links:
                    progress.update(task, advance=1, description=f"Processing {media['type']}")
                    
                    filepath = self.download_media(media['url'], media['type'])
                    if filepath:
                        # Get appropriate handler
                        handler = self.tool_handlers.get(
                            media['type'],
                            self.tool_handlers.get('document')
                        )
                        
                        # Process media
                        result = handler(filepath)
                        result.update({
                            "source_url": media['url'],
                            "local_path": filepath,
                            "media_type": media['type'],
                            "context": media.get('alt') or media.get('text', '')
                        })
                        
                        media_results.append(result)
                        
                        # Store in memory if text content
                        if 'text' in result or 'transcript' in result:
                            content = result.get('text') or result.get('transcript', '')
                            self.store_memory(content, {
                                "url": url,
                                "media_url": media['url'],
                                "media_type": media['type'],
                                "filepath": filepath
                            })
            
            # AI analysis of page structure
            page_analysis = self.analyze_page_intelligence(html, url)
            
            self.session_stats["successful_scrapes"] += 1
            
            return {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "html": html[:10000] + "..." if len(html) > 10000 else html,
                "text_content": main_content[:5000],
                "structured_data": structured_data,
                "media": media_results,
                "media_count": len(media_results),
                "ai_analysis": page_analysis,
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "page_size": len(html),
                    "media_processed": len(media_results),
                    "text_length": len(main_content)
                }
            }
            
        except Exception as e:
            console.print(f"[red]Scrape error on {url}: {str(e)}[/red]")
            self.session_stats["failed_scrapes"] += 1
            return {
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            if driver:
                self.release_driver(driver)

    def extract_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract structured data from HTML"""
        structured = {}
        
        # Meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content
        structured['meta'] = meta_tags
        
        # JSON-LD data
        json_ld = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                json_ld.append(data)
            except:
                pass
        structured['json_ld'] = json_ld
        
        # Open Graph data
        og_data = {}
        for meta in soup.find_all('meta', property=re.compile('^og:')):
            og_data[meta.get('property')] = meta.get('content')
        structured['open_graph'] = og_data
        
        # Forms
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method'),
                'inputs': [
                    {
                        'name': inp.get('name'),
                        'type': inp.get('type'),
                        'value': inp.get('value')
                    }
                    for inp in form.find_all('input')
                ]
            }
            forms.append(form_data)
        structured['forms'] = forms
        
        return structured

    def analyze_page_intelligence(self, html: str, url: str) -> Dict[str, Any]:
        """Use AI to analyze page structure and content"""
        try:
            # Prepare analysis prompt
            prompt = f"""Analyze this webpage and identify:
            1. Main purpose and content type
            2. Key information extraction opportunities
            3. Dynamic content indicators
            4. Potential API endpoints
            5. Security measures or anti-bot systems
            
            URL: {url}
            HTML Preview (first 3000 chars):
            {html[:3000]}
            
            Provide structured analysis with actionable insights."""
            
            # Get AI analysis
            analysis = self.deepseek_reason(prompt)
            
            # Check for specific patterns
            patterns = {
                "has_api": bool(re.search(r'/api/|/v\d+/|\.json', html)),
                "has_ajax": 'XMLHttpRequest' in html or 'fetch(' in html,
                "has_websocket": 'WebSocket' in html,
                "has_react": 'react' in html.lower() or '_app.js' in html,
                "has_vue": 'vue' in html.lower() or 'v-' in html,
                "has_angular": 'ng-' in html or 'angular' in html.lower()
            }
            
            return {
                "ai_analysis": analysis,
                "patterns": patterns,
                "technologies": [k for k, v in patterns.items() if v]
            }
            
        except Exception as e:
            return {"error": str(e)}

    def rag_enhanced_analysis(self, query: str, scraped_data: Dict[str, Any]) -> str:
        """Perform RAG-enhanced analysis of scraped content"""
        try:
            # Build context from scraped data
            context_parts = [
                f"URL: {scraped_data.get('url', 'Unknown')}",
                f"Title: {scraped_data.get('title', 'No title')}",
                f"Text Content: {scraped_data.get('text_content', '')[:2000]}"
            ]
            
            # Add media content
            for media in scraped_data.get('media', []):
                if 'text' in media:
                    context_parts.append(f"\nDocument Text: {media['text'][:500]}")
                elif 'ocr_text' in media:
                    context_parts.append(f"\nImage OCR: {media['ocr_text'][:500]}")
                elif 'transcript' in media:
                    context_parts.append(f"\nAudio/Video Transcript: {media['transcript'][:500]}")
                elif 'ai_description' in media:
                    context_parts.append(f"\nImage Description: {media['ai_description'][:300]}")
            
            # Query similar content from memory
            memory_results = self.query_memory(query, top_k=3)
            for mem in memory_results:
                if mem['score'] > 0.7:  # High relevance
                    context_parts.append(f"\nRelated Memory: {mem['payload']['content'][:300]}")
            
            # Add conversation history
            if self.conversation_history:
                recent_history = self.conversation_history[-3:]
                context_parts.append(f"\nRecent Conversation: {json.dumps(recent_history)}")
            
            # Build full context
            full_context = "\n".join(context_parts)
            
            # Create analysis prompt
            prompt = f"""You are an advanced intelligence analyst. Perform deep analysis of scraped web content including all media files.

User Query: {query}

Context and Scraped Data:
{full_context}

Instructions:
1. Cross-reference all media content (images, PDFs, videos, audio) with text content
2. Identify hidden connections and patterns across different media types
3. Extract actionable intelligence combining visual, textual, and audio information
4. Highlight any suspicious or notable findings
5. Provide specific answers to the user's query
6. Suggest follow-up actions or additional scraping targets

Generate a comprehensive intelligence report."""

            # Get AI analysis
            response = self.deepseek_reason(prompt)
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
            
            self.conversation_history.append({
                "role": "assistant",
                "content": response['answer'],
                "reasoning": response['reasoning'],
                "timestamp": datetime.now().isoformat()
            })
            
            # Store analysis in memory
            self.store_memory(
                response['answer'],
                {
                    "query": query,
                    "url": scraped_data.get('url'),
                    "type": "analysis"
                },
                collection="conversation_memory"
            )
            
            return response['answer']
            
        except Exception as e:
            return f"Analysis error: {str(e)}"

    def generate_scraping_strategy(self, urls: List[str]) -> Dict[str, Any]:
        """Use AI to generate optimal scraping strategy"""
        prompt = f"""Generate an optimal web scraping strategy for these URLs:
        {json.dumps(urls, indent=2)}
        
        Consider:
        1. Likely anti-bot measures
        2. Content types to expect
        3. Optimal scraping order
        4. Required tools/handlers
        5. Potential rate limiting needs
        
        Return a structured strategy."""
        
        strategy = self.deepseek_reason(prompt)
        return json.loads(strategy['answer']) if strategy else {}

    def streaming_scrape(self, urls: List[str], analysis_query: Optional[str] = None) -> Dict[str, Any]:
        """Scrape multiple URLs concurrently with streaming results"""
        results = {}
        errors = []
        
        # Generate scraping strategy
        strategy = self.generate_scraping_strategy(urls)
        
        console.print(f"[bold cyan]Starting concurrent scraping of {len(urls)} URLs[/bold cyan]")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scraping tasks
            future_to_url = {
                executor.submit(self.adaptive_scrape, url): url 
                for url in urls
            }
            
            # Process results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                
                try:
                    scraped_data = future.result()
                    
                    if "error" not in scraped_data:
                        # Perform analysis if requested
                        if analysis_query:
                            analysis = self.rag_enhanced_analysis(analysis_query, scraped_data)
                            scraped_data['analysis'] = analysis
                        
                        results[url] = scraped_data
                        console.print(f"[green]✓ Completed: {url}[/green]")
                    else:
                        errors.append(scraped_data)
                        console.print(f"[red]✗ Failed: {url}[/red]")
                        
                except Exception as e:
                    errors.append({"url": url, "error": str(e)})
                    console.print(f"[red]✗ Exception on {url}: {e}[/red]")
        
        # Summary
        summary = {
            "total_urls": len(urls),
            "successful": len(results),
            "failed": len(errors),
            "stats": self.session_stats,
            "strategy_used": strategy
        }
        
        return {
            "results": results,
            "errors": errors,
            "summary": summary
        }

    def export_results(self, data: Dict[str, Any], format: str = "json", output_path: str = "output") -> str:
        """Export results in various formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filename = f"{output_path}_{timestamp}.json"
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                
        elif format == "html":
            filename = f"{output_path}_{timestamp}.html"
            html = self.generate_html_report(data)
            with open(filename, "w", encoding='utf-8') as f:
                f.write(html)
                
        elif format == "markdown":
            filename = f"{output_path}_{timestamp}.md"
            md = self.generate_markdown_report(data)
            with open(filename, "w", encoding='utf-8') as f:
                f.write(md)
        
        console.print(f"[green]✓ Exported to {filename}[/green]")
        return filename

    def generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report with styling"""
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Web Scraping Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; margin: -20px -20px 20px -20px; }
        .url-result { border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }
        .success { border-left: 5px solid #27ae60; }
        .error { border-left: 5px solid #e74c3c; }
        .media-item { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 3px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-box { background: #3498db; color: white; padding: 15px; border-radius: 5px; text-align: center; }
        .code { background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 3px; overflow-x: auto; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
        .analysis { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 3px solid #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Web Scraping Intelligence Report</h1>
            <p>Generated: {timestamp}</p>
        </div>
"""
        
        # Add summary stats
        if 'summary' in data:
            summary = data['summary']
            html += """
        <div class="stats">
            <div class="stat-box">
                <h3>{total_urls}</h3>
                <p>Total URLs</p>
            </div>
            <div class="stat-box">
                <h3>{successful}</h3>
                <p>Successful</p>
            </div>
            <div class="stat-box">
                <h3>{failed}</h3>
                <p>Failed</p>
            </div>
            <div class="stat-box">
                <h3>{media_processed}</h3>
                <p>Media Processed</p>
            </div>
        </div>
""".format(**summary, media_processed=summary.get('stats', {}).get('media_processed', 0))
        
        # Add results
        if 'results' in data:
            html += "<h2>Scraping Results</h2>"
            
            for url, result in data['results'].items():
                status_class = "success" if "error" not in result else "error"
                html += f"""
        <div class="url-result {status_class}">
            <h3>{url}</h3>
            <p><strong>Title:</strong> {result.get('title', 'No title')}</p>
            <p><strong>Timestamp:</strong> {result.get('timestamp', 'Unknown')}</p>
"""
                
                # Add AI analysis
                if 'analysis' in result:
                    html += f"""
            <div class="analysis">
                <h4>AI Analysis</h4>
                <pre>{result['analysis']}</pre>
            </div>
"""
                
                # Add media results
                if 'media' in result and result['media']:
                    html += f"<h4>Media Files ({len(result['media'])})</h4>"
                    
                    for media in result['media']:
                        html += f"""
            <div class="media-item">
                <strong>Type:</strong> {media.get('media_type', 'Unknown')}<br>
                <strong>URL:</strong> <a href="{media.get('source_url', '#')}">{media.get('source_url', 'Unknown')}</a><br>
"""
                        
                        if 'text' in media:
                            html += f"<strong>Extracted Text:</strong> {media['text'][:200]}...<br>"
                        elif 'ocr_text' in media:
                            html += f"<strong>OCR Text:</strong> {media['ocr_text'][:200]}...<br>"
                        elif 'transcript' in media:
                            html += f"<strong>Transcript:</strong> {media['transcript'][:200]}...<br>"
                        
                        html += "</div>"
                
                html += "</div>"
        
        # Add errors
        if 'errors' in data and data['errors']:
            html += "<h2>Errors</h2>"
            for error in data['errors']:
                html += f"""
        <div class="url-result error">
            <h3>{error.get('url', 'Unknown URL')}</h3>
            <p><strong>Error:</strong> {error.get('error', 'Unknown error')}</p>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return html

    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        md = f"""# Web Scraping Intelligence Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary

"""
        
        if 'summary' in data:
            summary = data['summary']
            md += f"""- **Total URLs**: {summary.get('total_urls', 0)}
- **Successful**: {summary.get('successful', 0)}
- **Failed**: {summary.get('failed', 0)}
- **Media Processed**: {summary.get('stats', {}).get('media_processed', 0)}

"""
        
        if 'results' in data:
            md += "## Results\n\n"
            
            for url, result in data['results'].items():
                md += f"### {url}\n\n"
                md += f"- **Title**: {result.get('title', 'No title')}\n"
                md += f"- **Timestamp**: {result.get('timestamp', 'Unknown')}\n"
                md += f"- **Media Count**: {result.get('media_count', 0)}\n\n"
                
                if 'analysis' in result:
                    md += "#### AI Analysis\n\n"
                    md += f"```\n{result['analysis']}\n```\n\n"
                
                if 'media' in result and result['media']:
                    md += f"#### Media Files\n\n"
                    
                    for media in result['media']:
                        md += f"- **{media.get('media_type', 'Unknown')}**: {media.get('source_url', 'Unknown')}\n"
                        
                        if 'text' in media:
                            md += f"  - Text: {media['text'][:100]}...\n"
                        elif 'ocr_text' in media:
                            md += f"  - OCR: {media['ocr_text'][:100]}...\n"
        
        return md

    def cli_command(self, cmd: str, **kwargs) -> Any:
        """Execute CLI commands"""
        if cmd == "scrape":
            urls = kwargs.get("urls", [])
            analysis_query = kwargs.get("analysis_query")
            return self.streaming_scrape(urls, analysis_query)
            
        elif cmd == "memory":
            query = kwargs.get("query", "")
            results = self.query_memory(query)
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        elif cmd == "export":
            data = kwargs.get("data", {})
            format = kwargs.get("format", "json")
            output = kwargs.get("output", "output")
            return self.export_results(data, format, output)
            
        elif cmd == "stats":
            return self.session_stats
            
        elif cmd == "analyze":
            # Analyze existing scraped data
            data = kwargs.get("data", {})
            query = kwargs.get("query", "")
            return self.rag_enhanced_analysis(query, data)
            
        elif cmd == "fim":
            # FIM completion
            prefix = kwargs.get("prefix", "")
            suffix = kwargs.get("suffix", "")
            return self.deepseek_fim(prefix, suffix)
            
        else:
            return {"error": f"Unknown command: {cmd}"}

    def close(self):
        """Clean up resources"""
        console.print("[yellow]Cleaning up resources...[/yellow]")
        
        # Close all drivers
        for driver in self.driver_pool:
            try:
                driver.quit()
            except:
                pass
        
        # Clean up temporary files
        for file in glob.glob(os.path.join(self.storage_path, "*.tmp")):
            try:
                os.remove(file)
            except:
                pass
        
        console.print("[green]✅ All resources cleaned up[/green]")
        
        # Print final stats
        table = Table(title="Session Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in self.session_stats.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        
        console.print(table)


# CLI Interface
def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SuperAgentScraper - Advanced AI-Powered Web Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python super_agent_scraper.py scrape --urls https://example.com https://example.org --analysis_query "Extract technical specifications"
  python super_agent_scraper.py memory --query "security protocols"
  python super_agent_scraper.py export --format html --output report
  python super_agent_scraper.py stats
        """
    )
    
    parser.add_argument(
        "command",
        choices=["scrape", "memory", "export", "stats", "analyze", "fim"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--urls",
        nargs="*",
        help="URLs to scrape (for scrape command)"
    )
    
    parser.add_argument(
        "--analysis_query",
        help="Analysis query for scraped data"
    )
    
    parser.add_argument(
        "--query",
        help="Search query (for memory command)"
    )
    
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "html", "markdown"],
        help="Export format"
    )
    
    parser.add_argument(
        "--output",
        default="output",
        help="Output file prefix"
    )
    
    parser.add_argument(
        "--data_file",
        help="JSON file with data to analyze/export"
    )
    
    parser.add_argument(
        "--prefix",
        help="Prefix for FIM completion"
    )
    
    parser.add_argument(
        "--suffix",
        help="Suffix for FIM completion"
    )
    
    parser.add_argument(
        "--api_key",
        help="DeepSeek API key (optional, uses hardcoded if not provided)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent workers"
    )
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = SuperAgentScraper(
        api_key=args.api_key,
        storage_path="scraped_content",
        max_workers=args.workers
    )
    
    try:
        # Load data from file if provided
        data = {}
        if args.data_file:
            with open(args.data_file, 'r') as f:
                data = json.load(f)
        
        # Execute command
        if args.command == "scrape":
            if not args.urls:
                console.print("[red]Error: --urls required for scrape command[/red]")
                return
                
            result = scraper.cli_command(
                "scrape",
                urls=args.urls,
                analysis_query=args.analysis_query
            )
            
            # Auto-export results
            scraper.cli_command(
                "export",
                data=result,
                format=args.format,
                output=args.output
            )
            
        elif args.command == "memory":
            result = scraper.cli_command(
                "memory",
                query=args.query or ""
            )
            console.print(json.dumps(result, indent=2))
            
        elif args.command == "export":
            result = scraper.cli_command(
                "export",
                data=data,
                format=args.format,
                output=args.output
            )
            console.print(result)
            
        elif args.command == "stats":
            stats = scraper.cli_command("stats")
            table = Table(title="Session Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in stats.items():
                table.add_row(key.replace("_", " ").title(), str(value))
            
            console.print(table)
            
        elif args.command == "analyze":
            if not data:
                console.print("[red]Error: --data_file required for analyze command[/red]")
                return
                
            result = scraper.cli_command(
                "analyze",
                data=data,
                query=args.query or "Provide comprehensive analysis"
            )
            console.print(result)
            
        elif args.command == "fim":
            result = scraper.cli_command(
                "fim",
                prefix=args.prefix or "",
                suffix=args.suffix or ""
            )
            console.print(result)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()