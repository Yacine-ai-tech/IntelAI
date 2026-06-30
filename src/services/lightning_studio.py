"""Lightning AI Studio service for programmatic wake-up and management.

This service provides programmatic control over Lightning AI Studios using the lightning-sdk.
It allows the IntelAI backend to wake up the Lightning Studio when needed for inference
operations, reducing dependency on manual UI intervention.

Usage:
    from src.services.lightning_studio import wake_studio, get_studio_status
    
    # Wake up the studio
    status = wake_studio()
    
    # Check current status
    status = get_studio_status()
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Load configuration from environment
LIGHTNING_USER_ID = os.environ.get('LIGHTNING_USER_ID')
LIGHTNING_API_KEY = os.environ.get('LIGHTNING_API_KEY')
LIGHTNING_STUDIO_NAME = os.environ.get('LIGHTNING_STUDIO_NAME', 'upwork')
LIGHTNING_TEAMSPACE = os.environ.get('LIGHTNING_TEAMSPACE', 'default')


def get_studio_status() -> Dict[str, Any]:
    """Get the current status of the Lightning Studio.
    
    Returns:
        Dict with studio status information including:
        - status: Current studio status (Running, Stopped, etc.)
        - machine: Current machine type
        - configured: Whether credentials are configured
        - error: Error message if any
    """
    try:
        if not LIGHTNING_USER_ID or not LIGHTNING_API_KEY:
            return {
                'status': 'unconfigured',
                'machine': None,
                'configured': False,
                'error': 'LIGHTNING_USER_ID and LIGHTNING_API_KEY must be set'
            }
        
        from lightning_sdk import Studio
        
        studio = Studio(LIGHTNING_STUDIO_NAME, LIGHTNING_TEAMSPACE, user=LIGHTNING_USER_ID)
        
        return {
            'status': str(studio.status),
            'machine': str(studio.machine),
            'configured': True,
            'error': None
        }
    except ImportError:
        return {
            'status': 'sdk_not_installed',
            'machine': None,
            'configured': False,
            'error': 'lightning-sdk not installed. Install with: pip install lightning-sdk'
        }
    except Exception as e:
        logger.error(f"Error getting studio status: {e}")
        return {
            'status': 'error',
            'machine': None,
            'configured': True,
            'error': str(e)
        }


def wake_studio(machine: Optional[str] = None) -> Dict[str, Any]:
    """Wake up the Lightning Studio programmatically.
    
    Args:
        machine: Optional machine type to start with (e.g., 'CPU-4', 'L4', 'T4')
                If not specified, uses the studio's default machine.
    
    Returns:
        Dict with operation result including:
        - success: Whether the operation succeeded
        - status: Current studio status after operation
        - machine: Current machine type
        - error: Error message if any
    """
    try:
        if not LIGHTNING_USER_ID or not LIGHTNING_API_KEY:
            return {
                'success': False,
                'status': 'unconfigured',
                'machine': None,
                'error': 'LIGHTNING_USER_ID and LIGHTNING_API_KEY must be set'
            }
        
        from lightning_sdk import Studio, Machine
        
        studio = Studio(LIGHTNING_STUDIO_NAME, LIGHTNING_TEAMSPACE, user=LIGHTNING_USER_ID)
        
        # Check if already running
        if str(studio.status) == 'Running':
            logger.info(f"Studio {LIGHTNING_STUDIO_NAME} is already running")
            return {
                'success': True,
                'status': str(studio.status),
                'machine': str(studio.machine),
                'error': None,
                'message': 'Studio already running'
            }
        
        # Start the studio
        logger.info(f"Waking up studio {LIGHTNING_STUDIO_NAME}...")
        
        if machine:
            # Start with specific machine
            studio.start(getattr(Machine, machine.upper(), Machine.CPU_4))
        else:
            # Start with default machine
            studio.start()
        
        logger.info(f"Studio {LIGHTNING_STUDIO_NAME} started successfully")
        
        return {
            'success': True,
            'status': str(studio.status),
            'machine': str(studio.machine),
            'error': None,
            'message': 'Studio started successfully'
        }
        
    except ImportError:
        return {
            'success': False,
            'status': 'sdk_not_installed',
            'machine': None,
            'error': 'lightning-sdk not installed. Install with: pip install lightning-sdk'
        }
    except Exception as e:
        logger.error(f"Error waking up studio: {e}")
        return {
            'success': False,
            'status': 'error',
            'machine': None,
            'error': str(e)
        }


def stop_studio() -> Dict[str, Any]:
    """Stop the Lightning Studio to save compute resources.
    
    Returns:
        Dict with operation result including:
        - success: Whether the operation succeeded
        - status: Current studio status after operation
        - error: Error message if any
    """
    try:
        if not LIGHTNING_USER_ID or not LIGHTNING_API_KEY:
            return {
                'success': False,
                'status': 'unconfigured',
                'error': 'LIGHTNING_USER_ID and LIGHTNING_API_KEY must be set'
            }
        
        from lightning_sdk import Studio
        
        studio = Studio(LIGHTNING_STUDIO_NAME, LIGHTNING_TEAMSPACE, user=LIGHTNING_USER_ID)
        
        # Stop the studio
        logger.info(f"Stopping studio {LIGHTNING_STUDIO_NAME}...")
        studio.stop()
        
        logger.info(f"Studio {LIGHTNING_STUDIO_NAME} stopped successfully")
        
        return {
            'success': True,
            'status': str(studio.status),
            'error': None,
            'message': 'Studio stopped successfully'
        }
        
    except ImportError:
        return {
            'success': False,
            'status': 'sdk_not_installed',
            'error': 'lightning-sdk not installed. Install with: pip install lightning-sdk'
        }
    except Exception as e:
        logger.error(f"Error stopping studio: {e}")
        return {
            'success': False,
            'status': 'error',
            'error': str(e)
        }
