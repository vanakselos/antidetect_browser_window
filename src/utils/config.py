import json
import os
from typing import Dict, Any
from .logger import get_logger

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        self.logger = get_logger(__name__)
        self.config_path = 'config.json'
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self.get_default_config()

    def save_config(self):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "browser": {
                "default_user_data_dir": "profiles",
                "chrome_version": "latest",
                "launch_timeout": 30
            },
            "proxy": {
                "enabled": False,
                "type": "http",
                "host": "",
                "port": "",
                "username": "",
                "password": ""
            },
            "profiles": {
                "max_concurrent": 5,
                "auto_save": True
            },
            "ui": {
                "theme": "light",
                "language": "en",
                "window_size": {
                    "width": 1000,
                    "height": 600
                }
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any):
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                config = config.setdefault(k, {})
            config[keys[-1]] = value
            self.save_config()
        except Exception as e:
            self.logger.error(f"Error setting config value: {e}")