from fastapi import APIRouter
from datetime import datetime
import os
from .logging_utils import get_logger
from .settings import settings

router = APIRouter()
logger = get_logger()


@router.get("/")
async def health_check():
    """
    Health check endpoint with system information
    Returns basic system health and metrics
    """
    logger.info("Health check requested")

    try:
        # Check if config directory exists
        config_dir_exists = os.path.exists(settings.CONFIG_STORAGE_PATH)

        # Count configuration files
        configs_count = 0
        if config_dir_exists:
            for root, dirs, files in os.walk(settings.CONFIG_STORAGE_PATH):
                configs_count += len([f for f in files if f.endswith(('.yaml', '.yml', '.json'))])

        # Get disk usage (in MB)
        disk_usage = 0
        if config_dir_exists:
            total_size = 0
            for root, dirs, files in os.walk(settings.CONFIG_STORAGE_PATH):
                for file in files:
                    total_size += os.path.getsize(os.path.join(root, file))
            disk_usage = round(total_size / (1024 * 1024), 2)  # Convert to MB

        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.ENVIRONMENT,
            "version": settings.API_VERSION,
            "metrics": {
                "total_configs": configs_count,
                "disk_usage_mb": disk_usage,
                "config_directory_exists": config_dir_exists
            }
        }

        logger.info(f"Health check completed: {configs_count} configs, {disk_usage}MB disk usage")
        return health_data

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
