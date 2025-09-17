#!/usr/bin/env python3
"""
Project Setu - FastAPI Application Runner
Main entry point for the FastAPI backend server.
"""

import asyncio
import logging
import sys
from pathlib import Path
import uvicorn

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for FastAPI server"""
    logger.info("🚀 Starting Project Setu FastAPI Backend Server")
    
    try:
        # Run FastAPI with uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            reload_dirs=[str(project_root)]
        )
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
