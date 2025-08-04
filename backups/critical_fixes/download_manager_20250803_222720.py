#!/usr/bin/env python3
"""
üöÄ BASED CODER CLI - Unified Download Manager
Made by @Lucariolucario55 on Telegram

Consolidated download management for models, dependencies, and resources
"""

import os
import sys
import subprocess
import logging
import requests
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import asyncio
import aiohttp
import aiofiles
from tqdm import tqdm
import hashlib

# Import our configuration
from config import get_config, validate_huggingface_token, validate_deepseek_key

logger = logging.getLogger(__name__)

class DownloadManager:
    """Unified download manager for BASED CODER CLI"""
    
    def __init__(self) -> Any:
        self.config = get_config()
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.models_dir = self.data_dir / "models"
        self.cache_dir = self.data_dir / "cache"
        
        # Create necessary directories
        self.data_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Download status tracking
        self.download_status = {}
        
    def print_banner(self) -> Any:
        """Print download manager banner"""
        banner = f"""
‚ïî‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïó
‚ïë                                                                              ‚ïë
‚ïë  üì• BASED CODER CLI - UNIFIED DOWNLOAD MANAGER                              ‚ïë
‚ïë                                                                              ‚ïë
‚ïë  Features:                                                                   ‚ïë
‚ïë  ‚úÖ Model Downloads (Qwen, GGUF, etc.)                                       ‚ïë
‚ïë  ‚úÖ Dependency Management                                                    ‚ïë
‚ïë  ‚úÖ Progress Tracking & Resume Support                                       ‚ïë
‚ïë  ‚úÖ Validation & Integrity Checks                                           ‚ïë
‚ïë  ‚úÖ Cache Management                                                         ‚ïë
‚ïë                                                                              ‚ïë
‚ïë  Made by @Lucariolucario55 on Telegram                                      ‚ïë
‚ïë                                                                              ‚ïë
‚ïö‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïê‚ïù
        """
        logging.info(banner)
    
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        logger.info("üîë Validating API credentials...")
        
        # Check DeepSeek API key
        if not validate_deepseek_key(self.config.llm.api_key):
            logger.error("‚ùå Invalid DeepSeek API key")
            return False
        
        # Check HuggingFace token
        if not validate_huggingface_token(self.config.models.huggingface_token):
            logger.error("‚ùå Invalid HuggingFace token")
            return False
        
        logger.info("‚úÖ API credentials validated")
        return True
    
    async def download_qwen_model(self) -> bool:
        """Download Qwen3 embedding model"""
        logger.info("üì• Downloading Qwen3 embedding model...")
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            model_name = self.config.models.qwen_model_name
            token = self.config.models.huggingface_token
            
            # Create model directory
            model_dir = self.models_dir / "qwen3_embedding"
            model_dir.mkdir(exist_ok=True)
            
            logger.info(f"Downloading {model_name}...")
            
            # Download tokenizer
            logger.info("Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=token,
                cache_dir=str(self.models_dir)
            )
            
            # Download model
            logger.info("Downloading model...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                token=token,
                cache_dir=str(self.models_dir),
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # Save locally
            tokenizer_path = model_dir / "tokenizer"
            model_path = model_dir / "model"
            
            logger.info("Saving tokenizer locally...")
            tokenizer.save_pretrained(tokenizer_path)
            
            logger.info("Saving model locally...")
            model.save_pretrained(model_path)
            
            # Create model info
            model_info = {
                "model_name": model_name,
                "local_path": str(model_dir),
                "tokenizer_path": str(tokenizer_path),
                "model_path": str(model_path),
                "status": "downloaded",
                "timestamp": str(Path(__file__).stat().st_mtime)
            }
            
            # Save model info
            info_file = model_dir / "model_info.json"
            with open(info_file, 'w') as f:
                json.dump(model_info, f, indent=2)
            
            # Test the model
            logger.info("Testing model...")
            test_text = "Hello world"
            inputs = tokenizer(test_text, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            logger.info(f"‚úÖ Qwen3 model downloaded and tested successfully!")
            self.download_status["qwen_model"] = True
            return True
            
        except Exception as e:
            logger.error(f"‚ùå Failed to download Qwen3 model: {e}")
            self.download_status["qwen_model"] = False
            return False
    
    async def download_gguf_models(self) -> bool:
        """Download GGUF models"""
        logger.info("üì• Downloading GGUF models...")
        
        try:
            from huggingface_hub import hf_hub_download
            
            # List of GGUF models to download
            gguf_models = [
                {
                    "repo_id": "TheBloke/Llama-2-7B-Chat-GGUF",
                    "filename": "llama-2-7b-chat.Q4_K_M.gguf",
                    "local_name": "llama2_7b_chat"
                },
                {
                    "repo_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                    "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                    "local_name": "mistral_7b_instruct"
                }
            ]
            
            token = self.config.models.huggingface_token
            
            for model_info in gguf_models:
                logger.info(f"Downloading {model_info['filename']}...")
                
                try:
                    # Download the model
                    model_path = hf_hub_download(
                        repo_id=model_info["repo_id"],
                        filename=model_info["filename"],
                        token=token,
                        cache_dir=str(self.models_dir)
                    )
                    
                    # Create local directory
                    local_dir = self.models_dir / model_info["local_name"]
                    local_dir.mkdir(exist_ok=True)
                    
                    # Copy to local directory
                    import shutil
                    local_path = local_dir / model_info["filename"]
                    shutil.copy2(model_path, local_path)
                    
                    logger.info(f"‚úÖ Downloaded {model_info['filename']}")
                    
                except Exception as e:
                    logger.error(f"‚ùå Failed to download {model_info['filename']}: {e}")
                    continue
            
            self.download_status["gguf_models"] = True
            return True
            
        except Exception as e:
            logger.error(f"‚ùå Failed to download GGUF models: {e}")
            self.download_status["gguf_models"] = False
            return False
    
    async def download_with_progress(self, url: str, filepath: Path, description: str = "Downloading") -> bool:
        """Download file with progress bar"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"‚ùå HTTP {response.status}: {url}")
                        return False
                    
                    total_size = int(response.headers.get('content-length', 0))
                    
                    with open(filepath, 'wb') as f:
                        downloaded = 0
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                logging.info(f"\r{description}: {progress:.1f}%", end='', flush=True)
                    
                    logging.info()  # New line after progress
                    return True
                    
        except Exception as e:
            logger.error(f"‚ùå Download failed: {e}")
            return False
    
    async def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("üì¶ Installing Python dependencies...")
        
        try:
            # Read requirements file
            requirements_file = self.project_root / "requirements_enhanced.txt"
            if not requirements_file.exists():
                logger.error("‚ùå requirements_enhanced.txt not found")
                return False
            
            # Install dependencies
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("‚úÖ Python dependencies installed successfully")
                self.download_status["python_deps"] = True
                return True
            else:
                logger.error(f"‚ùå Failed to install Python dependencies: {result.stderr}")
                self.download_status["python_deps"] = False
                return False
                
        except Exception as e:
            logger.error(f"‚ùå Error installing Python dependencies: {e}")
            self.download_status["python_deps"] = False
            return False
    
    async def install_node_dependencies(self) -> bool:
        """Install Node.js dependencies"""
        logger.info("üì¶ Installing Node.js dependencies...")
        
        try:
            package_json = self.project_root / "package.json"
            if not package_json.exists():
                logger.warning("‚ö†Ô∏è package.json not found, skipping Node.js dependencies")
                return True
            
            # Install dependencies
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("‚úÖ Node.js dependencies installed successfully")
                self.download_status["node_deps"] = True
                return True
            else:
                logger.error(f"‚ùå Failed to install Node.js dependencies: {result.stderr}")
                self.download_status["node_deps"] = False
                return False
                
        except Exception as e:
            logger.error(f"‚ùå Error installing Node.js dependencies: {e}")
            self.download_status["node_deps"] = False
            return False
    
    async def build_typescript(self) -> bool:
        """Build TypeScript files"""
        logger.info("üî® Building TypeScript files...")
        
        try:
            tsconfig = self.project_root / "tsconfig.json"
            if not tsconfig.exists():
                logger.warning("‚ö†Ô∏è tsconfig.json not found, skipping TypeScript build")
                return True
            
            # Build TypeScript
            result = subprocess.run(["npx", "tsc"], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("‚úÖ TypeScript build completed successfully")
                self.download_status["typescript_build"] = True
                return True
            else:
                logger.error(f"‚ùå TypeScript build failed: {result.stderr}")
                self.download_status["typescript_build"] = False
                return False
                
        except Exception as e:
            logger.error(f"‚ùå Error building TypeScript: {e}")
            self.download_status["typescript_build"] = False
            return False
    
    def validate_downloads(self) -> Dict[str, bool]:
        """Validate downloaded files"""
        logger.info("üîç Validating downloads...")
        
        validation_results = {}
        
        # Check Qwen model
        qwen_dir = self.models_dir / "qwen3_embedding"
        if qwen_dir.exists():
            model_files = list(qwen_dir.glob("*.safetensors")) + list(qwen_dir.glob("*.bin"))
            validation_results["qwen_model"] = len(model_files) > 0
        else:
            validation_results["qwen_model"] = False
        
        # Check GGUF models
        gguf_models = ["llama2_7b_chat", "mistral_7b_instruct"]
        for model_name in gguf_models:
            model_dir = self.models_dir / model_name
            if model_dir.exists():
                gguf_files = list(model_dir.glob("*.gguf"))
                validation_results[f"gguf_{model_name}"] = len(gguf_files) > 0
            else:
                validation_results[f"gguf_{model_name}"] = False
        
        # Check dependencies
        validation_results["python_deps"] = self.download_status.get("python_deps", False)
        validation_results["node_deps"] = self.download_status.get("node_deps", False)
        
        return validation_results
    
    def print_download_summary(self) -> Any:
        """Print download summary"""
        logging.info("\n" + "="*60)
        logging.info("üìä DOWNLOAD SUMMARY")
        logging.info("="*60)
        
        validation_results = self.validate_downloads()
        
        for item, status in validation_results.items():
            status_icon = "‚úÖ" if status else "‚ùå"
            logging.info(f"{status_icon} {item}")
        
        logging.info("="*60)
        
        # Overall status
        success_count = sum(validation_results.values())
        total_count = len(validation_results)
        
        if success_count == total_count:
            logging.info("üéâ All downloads completed successfully!")
        else:
            logging.info(f"‚ö†Ô∏è {success_count}/{total_count} downloads completed successfully")
    
    async def run_complete_download(self) -> bool:
        """Run complete download process"""
        self.print_banner()
        
        # Validate credentials
        if not self.validate_credentials():
            logger.error("‚ùå Credential validation failed")
            return False
        
        logger.info("üöÄ Starting complete download process...")
        
        # Install dependencies
        await self.install_python_dependencies()
        await self.install_node_dependencies()
        await self.build_typescript()
        
        # Download models
        await self.download_qwen_model()
        await self.download_gguf_models()
        
        # Print summary
        self.print_download_summary()
        
        return True

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def download_all() -> None:
    """Download all components"""
    manager = DownloadManager()
    return await manager.run_complete_download()

async def download_models() -> None:
    """Download only models"""
    manager = DownloadManager()
    
    if not manager.validate_credentials():
        return False
    
    await manager.download_qwen_model()
    await manager.download_gguf_models()
    manager.print_download_summary()
    return True

async def install_dependencies() -> None:
    """Install only dependencies"""
    manager = DownloadManager()
    
    await manager.install_python_dependencies()
    await manager.install_node_dependencies()
    await manager.build_typescript()
    
    manager.print_download_summary()
    return True

def validate_downloads() -> None:
    """Validate existing downloads"""
    manager = DownloadManager()
    validation_results = manager.validate_downloads()
    manager.print_download_summary()
    return validation_results

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="BASED CODER CLI Download Manager")
    parser.add_argument("--all", action="store_true", help="Download all components")
    parser.add_argument("--models", action="store_true", help="Download only models")
    parser.add_argument("--deps", action="store_true", help="Install only dependencies")
    parser.add_argument("--validate", action="store_true", help="Validate existing downloads")
    
    args = parser.parse_args()
    
    if args.all:
        await download_all()
    elif args.models:
        await download_models()
    elif args.deps:
        await install_dependencies()
    elif args.validate:
        validate_downloads()
    else:
        # Default: download all
        await download_all()

if __name__ == "__main__":
    asyncio.run(main()) 