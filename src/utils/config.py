"""
Configuration management for CivilAI Twin
Handles application settings, API keys, and user preferences
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from loguru import logger


class ConfigManager:
    """Manages application configuration and settings"""
    
    def __init__(self):
        # Determine base directory based on execution mode
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller bundle - use EXE directory
            self.app_dir = Path(sys.executable).parent
        else:
            # Running as script
            self.app_dir = Path(__file__).parent.parent.parent
        
        self.config_dir = self.app_dir / "config"
        self.config_file = self.config_dir / "default_config.yaml"
        self.user_config_file = self.config_dir / "user_config.yaml"
        self.api_key_file = self.config_dir / "api_keys.encrypted"
        
        # Ensure config directory exists
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create config directory: {e}")
            # Use a temporary config directory if we can't write to app directory
            import tempfile
            self.config_dir = Path(tempfile.gettempdir()) / "CivilAI_Twin_Config"
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.config_file = self.config_dir / "default_config.yaml"
            self.user_config_file = self.config_dir / "user_config.yaml"
            self.api_key_file = self.config_dir / "api_keys.encrypted"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize encryption key
        self.encryption_key = self._get_or_create_encryption_key()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from files"""
        # Load default config
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = self._create_default_config()
        
        # Merge with user config if exists
        if self.user_config_file.exists():
            with open(self.user_config_file, 'r') as f:
                user_config = yaml.safe_load(f) or {}
                config.update(user_config)
        
        return config
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            'application': {
                'name': 'CivilAI Twin',
                'version': '1.0.0',
                'theme': 'light',
                'language': 'en'
            },
            'ai': {
                'mode': 'built-in',  # 'built-in' or 'api'
                'provider': 'openai',  # 'openai' or 'anthropic'
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 2000
            },
            'analysis': {
                'structural': {
                    'safety_factor': 1.5,
                    'code_standard': 'ACI'
                },
                'geotechnical': {
                    'soil_classification': 'USCS',
                    'settlement_limit_mm': 25
                },
                'materials': {
                    'concrete_grade': 'M25',
                    'steel_grade': 'Fe500'
                }
            },
            'visualization': {
                'render_quality': 'high',
                'show_grid': True,
                'show_axes': True,
                'background_color': '#f0f0f0'
            },
            'reporting': {
                'include_calculations': True,
                'include_graphs': True,
                'include_3d_views': True,
                'logo_path': ''
            }
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for API keys"""
        key_file = self.config_dir / ".key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Hide the key file on Windows
            if os.name == 'nt':
                os.system(f'attrib +h "{key_file}"')
        
        return key
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('ai.provider')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation
        Example: config.set('ai.provider', 'openai')
        """
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self._save_user_config()
    
    def _save_user_config(self):
        """Save user configuration to file"""
        with open(self.user_config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def set_api_key(self, provider: str, api_key: str):
        """Securely store API key"""
        cipher = Fernet(self.encryption_key)
        encrypted_key = cipher.encrypt(api_key.encode())
        
        # Load existing keys
        api_keys = {}
        if self.api_key_file.exists():
            with open(self.api_key_file, 'rb') as f:
                try:
                    encrypted_data = f.read()
                    decrypted_data = cipher.decrypt(encrypted_data)
                    api_keys = yaml.safe_load(decrypted_data) or {}
                except:
                    pass
        
        # Add new key
        api_keys[provider] = encrypted_key.decode()
        
        # Save encrypted keys
        encrypted_data = cipher.encrypt(yaml.dump(api_keys).encode())
        with open(self.api_key_file, 'wb') as f:
            f.write(encrypted_data)
        
        logger.info(f"API key for {provider} stored securely")
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Retrieve API key"""
        if not self.api_key_file.exists():
            return None
        
        try:
            cipher = Fernet(self.encryption_key)
            
            with open(self.api_key_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = cipher.decrypt(encrypted_data)
                api_keys = yaml.safe_load(decrypted_data) or {}
            
            if provider in api_keys:
                encrypted_key = api_keys[provider].encode()
                return cipher.decrypt(encrypted_key).decode()
        
        except Exception as e:
            logger.error(f"Error retrieving API key for {provider}: {e}")
        
        return None
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key is configured"""
        return self.get_api_key(provider) is not None
    
    def remove_api_key(self, provider: str):
        """Remove API key"""
        if not self.api_key_file.exists():
            return
        
        try:
            cipher = Fernet(self.encryption_key)
            
            with open(self.api_key_file, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = cipher.decrypt(encrypted_data)
                api_keys = yaml.safe_load(decrypted_data) or {}
            
            if provider in api_keys:
                del api_keys[provider]
                
                # Save updated keys
                encrypted_data = cipher.encrypt(yaml.dump(api_keys).encode())
                with open(self.api_key_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.info(f"API key for {provider} removed")
        
        except Exception as e:
            logger.error(f"Error removing API key for {provider}: {e}")
