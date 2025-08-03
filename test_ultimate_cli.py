#!/usr/bin/env python3
"""
Test script for Ultimate BASED GOD CODER CLI
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_ultimate_cli():
    """Test the Ultimate CLI"""
    try:
        # Import the CLI
        from ultimate_based_god_cli import UltimateBasedGodCLI
        print("✓ Successfully imported UltimateBasedGodCLI")
        
        # Initialize CLI
        cli = UltimateBasedGodCLI()
        print("✓ Successfully initialized CLI")
        
        # Test banner display
        cli.display_banner()
        print("✓ Banner displayed successfully")
        
        # Test menu display
        cli.display_menu()
        print("✓ Menu displayed successfully")
        
        # Test API connection
        print("\nTesting API connection...")
        try:
            response = await cli.chat_with_api("Hello, this is a test", use_reasoner=False)
            print(f"✓ API Response: {response[:100]}...")
        except Exception as e:
            print(f"✗ API Error: {e}")
        
        # Test available tools
        print(f"\n✓ Available tools: {len(cli.available_tools)}")
        for tool in cli.available_tools:
            print(f"  - {tool['function']['name']}")
        
        # Test scraper availability
        if cli.scraper:
            print("✓ SuperAgentScraper is available")
        else:
            print("✗ SuperAgentScraper not available")
        
        # Test Docker availability
        if cli.docker_client:
            print("✓ Docker client is available")
        else:
            print("✗ Docker client not available")
        
        print("\n✅ All basic tests passed!")
        
    except ImportError as e:
        print(f"✗ Import Error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements_enhanced.txt")
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔥 Testing Ultimate BASED GOD CODER CLI 🔥\n")
    asyncio.run(test_ultimate_cli())