from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import yaml
import shutil
from datetime import datetime
from .settings import settings
from .logging_utils import get_logger

router = APIRouter()
logger = get_logger()

security = HTTPBearer()


async def verify_token(service: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Basic token validation"""
    if settings.SERVICE_TOKENS.get(service) == credentials.credentials:
        logger.info(f"Token matched for {service} token")
        return

    for admin, token in settings.ADMIN_TOKENS.items():
        if credentials.credentials == token:
            logger.info(f"Token matched for {admin} admin token")
            return

    logger.error("The provided token does not match admin or service tokens")
    raise HTTPException(
        status_code=403,
        detail="Permission is denied"
    )


async def create_backup(service: str, environment: str) -> str:
    """
    Creates a backup of a configuration file and returns the backup path
    """
    source_path = f"ingsoft/configs/{service}/{environment}.yaml"
    if not os.path.exists(source_path):
        return None

    backup_dir = f"ingsoft/backups/{service}"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/{environment}_{timestamp}.yaml"

    shutil.copy2(source_path, backup_path)
    return backup_path


@router.get("/backups/{service}")
async def list_backups(
        service: str,
        token: str = Depends(verify_token)
):
    backup_path = f"ingsoft/backups/{service}"
    if not os.path.exists(backup_path):
        return {
            "service": service,
            "backups": []
        }

    backups = []
    for file in os.listdir(backup_path):
        if file.endswith('.yaml'):
            backup_info = {
                "filename": file,
                "timestamp": file.split('_')[-1].replace('.yaml', ''),
                "environment": file.split('_')[0],
                "path": f"{backup_path}/{file}"
            }
            backups.append(backup_info)

    return {
        "service": service,
        "backups": sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    }


@router.get("/backups/{service}/{backup_file}")
async def get_backup(
        service: str,
        backup_file: str,
        token: str = Depends(verify_token)
):
    backup_path = f"ingsoft/backups/{service}/{backup_file}"

    if not os.path.exists(backup_path):
        raise HTTPException(
            status_code=404,
            detail=f"Backup not found: {backup_file}"
        )

    try:
        with open(backup_path, 'r') as f:
            config = yaml.safe_load(f)
            return {
                "service": service,
                "backup_file": backup_file,
                "config": config
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading backup: {str(e)}"
        )


@router.get("/")
async def list_all_configs():
    """
    List all available configurations
    Returns a summary of all services and environments
    """
    logger.info("Listing all configurations")

    try:
        config_path = settings.CONFIG_STORAGE_PATH
        if not os.path.exists(config_path):
            return {"services": [], "total": 0}

        services = {}
        for item in os.listdir(config_path):
            service_path = os.path.join(config_path, item)
            if os.path.isdir(service_path):
                environments = []
                for file in os.listdir(service_path):
                    if file.endswith(('.yaml', '.yml', '.json')):
                        env_name = file.split('.')[0]
                        environments.append(env_name)
                services[item] = environments

        total_configs = sum(len(envs) for envs in services.values())

        result = {
            "services": services,
            "total": total_configs,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Listed {total_configs} configurations for {len(services)} services")
        return result

    except Exception as e:
        logger.error(f"Error listing configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing configurations: {str(e)}")


@router.get("/{service}")
async def list_service_configs(service: str):
    """
    List all environments for a specific service
    """
    logger.info(f"Listing configurations for service: {service}")

    try:
        service_path = os.path.join(settings.CONFIG_STORAGE_PATH, service)
        if not os.path.exists(service_path):
            return {"service": service, "environments": [], "total": 0}

        environments = []
        for file in os.listdir(service_path):
            if file.endswith(('.yaml', '.yml', '.json')):
                env_name = file.split('.')[0]
                file_path = os.path.join(service_path, file)
                file_size = os.path.getsize(file_path)
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))

                environments.append({
                    "name": env_name,
                    "file": file,
                    "size_bytes": file_size,
                    "modified": file_modified.isoformat()
                })

        result = {
            "service": service,
            "environments": environments,
            "total": len(environments),
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Found {len(environments)} environments for service {service}")
        return result

    except Exception as e:
        logger.error(f"Error listing service configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing service configurations: {str(e)}")


@router.post("/{service}/{environment}")
async def create_config(
        service: str,
        environment: str,
        config: dict = Body(...),
        token: str = Depends(verify_token)
):
    backup_path = await create_backup(service, environment)

    service_path = f"ingsoft/configs/{service}"
    os.makedirs(service_path, exist_ok=True)

    config_path = f"{service_path}/{environment}.yaml"

    try:
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f)

        return {
            "status": "success",
            "message": "Configuration created/updated successfully",
            "service": service,
            "environment": environment,
            "backup_created": backup_path is not None,
            "backup_path": backup_path,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving configuration: {str(e)}"
        )


@router.get("/{service}/{environment}")
async def get_config(
        service: str,
        environment: str,
        token: str = Depends(verify_token)
):
    config_path = f"ingsoft/configs/{service}/{environment}.yaml"

    if not os.path.exists(config_path):
        raise HTTPException(
            status_code=404,
            detail=f"Configuration not found for {service} in {environment}"
        )

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return {
                "service": service,
                "environment": environment,
                "config": config
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading configuration: {str(e)}"
        )


@router.delete("/{service}/{environment}")
async def delete_config(
        service: str,
        environment: str,
        token: str = Depends(verify_token)
):
    config_path = f"ingsoft/configs/{service}/{environment}.yaml"

    if not os.path.exists(config_path):
        raise HTTPException(
            status_code=404,
            detail=f"Configuration not found for {service} in {environment}"
        )

    try:
        backup_path = await create_backup(service, environment)

        os.remove(config_path)

        service_dir = f"ingsoft/configs/{service}"
        if os.path.exists(service_dir) and not os.listdir(service_dir):
            os.rmdir(service_dir)

        return {
            "status": "success",
            "message": "Configuration deleted successfully",
            "service": service,
            "environment": environment,
            "backup_path": backup_path,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting configuration: {str(e)}"
        )


