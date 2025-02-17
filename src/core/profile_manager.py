from typing import Dict, Optional
import json
import os
from ..utils.logger import get_logger


class Profile:
    def __init__(self, name: str, fingerprint: dict):
        self.name = name
        self.fingerprint = self._validate_fingerprint(fingerprint)
        self.cookies = {}
        self.proxy = None
        self.history = []

    def _validate_fingerprint(self, fingerprint: dict) -> dict:
        # Define default fingerprint structure
        default_fingerprint = {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'platform': 'Win32',
            'language': 'en-US',
            'screen_resolution': (1920, 1080),
            'color_depth': 24,
            'pixel_ratio': 1,
            'hardware_concurrency': 4,
            'memory': 8,
            'timezone': 'America/New_York',
            'webgl_vendor': 'Google Inc.',
            'webgl_renderer': 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0)',
            'canvas_noise': '',
            'touch_support': False
        }

        # Merge provided fingerprint with defaults
        validated = default_fingerprint.copy()
        if fingerprint:
            validated.update(fingerprint)

        return validated

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'fingerprint': self.fingerprint,
            'cookies': self.cookies,
            'proxy': self.proxy,
            'history': self.history
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Profile':
        profile = cls(data['name'], data.get('fingerprint', {}))
        profile.cookies = data.get('cookies', {})
        profile.proxy = data.get('proxy')
        profile.history = data.get('history', [])
        return profile


class ProfileManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.profiles: Dict[str, Profile] = {}
        self.load_profiles()

    def load_profiles(self):
        try:
            if not os.path.exists('profiles'):
                os.makedirs('profiles')
                return

            for filename in os.listdir('profiles'):
                if filename.endswith('.json'):
                    profile_name = filename[:-5]
                    try:
                        with open(f'profiles/{filename}', 'r') as f:
                            data = json.load(f)
                            self.profiles[profile_name] = Profile.from_dict(data)
                    except Exception as e:
                        self.logger.error(f"Error loading profile {filename}: {e}")

        except Exception as e:
            self.logger.error(f"Error loading profiles: {e}")

    def create_profile(self, name: str) -> bool:
        try:
            if name in self.profiles:
                return False

            from .fingerprint_manager import FingerprintManager
            fingerprint = FingerprintManager().generate_fingerprint()

            profile = Profile(name, fingerprint)
            self.profiles[name] = profile

            self.save_profile(profile)
            return True
        except Exception as e:
            self.logger.error(f"Error creating profile: {e}")
            return False

    def save_profile(self, profile: Profile):
        try:
            if not os.path.exists('profiles'):
                os.makedirs('profiles')

            with open(f'profiles/{profile.name}.json', 'w') as f:
                json.dump(profile.to_dict(), f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving profile: {e}")

    def get_profile(self, name: str) -> Optional[Profile]:
        return self.profiles.get(name)

    def get_all_profiles(self) -> Dict[str, Profile]:
        return self.profiles.copy()

    def cleanup(self):
        try:
            for profile in self.profiles.values():
                chrome_data_dir = f'profiles/chrome_data_{profile.name}'
                if os.path.exists(chrome_data_dir):
                    import shutil
                    shutil.rmtree(chrome_data_dir)
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")