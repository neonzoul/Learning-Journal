#!/usr/bin/env python3
"""
Configuration validation script for deployment checks.

This script validates the application configuration without starting the full application.
Useful for deployment pipelines and health checks.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings
from app.core.logging_config import setup_logging, get_logger


def validate_environment() -> bool:
    """
    Validate environment configuration.
    
    Returns:
        True if validation passes, False otherwise
    """
    # Setup basic logging
    setup_logging(log_level="INFO", enable_json_logging=False)
    logger = get_logger(__name__)
    
    logger.info("Starting configuration validation...")
    
    try:
        # Test settings loading
        logger.info(f"Project: {settings.PROJECT_NAME}")
        logger.info(f"API Version: {settings.API_V1_STR}")
        logger.info(f"Debug Mode: {settings.DEBUG}")
        logger.info(f"SSL Verification: {settings.VERIFY_SSL}")
        
        # Validate startup requirements
        settings.validate_startup_requirements()
        logger.info("✓ Configuration validation passed")
        
        # Test Redis connection
        logger.info("Testing Redis connection...")
        from app.infrastructure.queue import create_queue_service
        try:
            queue_service = create_queue_service()
            queue_info = queue_service.get_queue_info()
            logger.info(f"✓ Redis connection successful: {queue_info}")
            queue_service.close()
        except Exception as e:
            logger.error(f"✗ Redis connection failed: {e}")
            return False
        
        # Test database initialization
        logger.info("Testing database initialization...")
        try:
            from app.infrastructure.database import init_database
            init_database()
            logger.info("✓ Database initialization successful")
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            return False
        
        # Validate N8N webhook URL accessibility (optional check)
        if settings.N8N_WEBHOOK_URL:
            logger.info("Testing N8N webhook URL accessibility...")
            try:
                import httpx
                with httpx.Client(
                    timeout=10.0,
                    verify=settings.VERIFY_SSL
                ) as client:
                    # Just test if the URL is reachable (don't send actual data)
                    response = client.get(
                        settings.N8N_WEBHOOK_URL.replace('/webhook/', '/ping'),
                        headers={"User-Agent": f"{settings.PROJECT_NAME}/config-validator"}
                    )
                    logger.info(f"✓ N8N endpoint reachable (status: {response.status_code})")
            except Exception as e:
                logger.warning(f"⚠ N8N endpoint check failed (this may be normal): {e}")
        
        logger.info("🎉 All configuration checks passed!")
        return True
        
    except Exception as e:
        logger.error(f"✗ Configuration validation failed: {e}")
        return False


def main():
    """Main entry point for configuration validation."""
    print("=" * 60)
    print("Accounting Automation Backend - Configuration Validator")
    print("=" * 60)
    
    success = validate_environment()
    
    if success:
        print("\n✅ Configuration validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Configuration validation failed!")
        print("\nPlease check the following:")
        print("1. All required environment variables are set")
        print("2. Redis server is running and accessible")
        print("3. Database directory is writable")
        print("4. N8N webhook URL is correctly configured")
        print("5. SSL certificates are valid (if using HTTPS)")
        sys.exit(1)


if __name__ == "__main__":
    main()