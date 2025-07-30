#!/usr/bin/env python3
"""
Coffee Shop Runner
Simple script to start the coffee shop system
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coffee_shop_server import main

if __name__ == "__main__":
    print("☕ Starting Coffee Shop System...")
    print("Press Ctrl+C to stop the shop")
    print("-" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Coffee Shop closed. Thank you!")
    except Exception as e:
        print(f"Error: {e}")
