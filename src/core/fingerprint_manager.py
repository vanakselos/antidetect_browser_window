import random
import uuid
import json
import os
from ..utils.logger import get_logger

class FingerprintManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.fingerprint_data = self.load_fingerprint_data()

    def load_fingerprint_data(self):
        """Load fingerprint data from file or use defaults"""
        try:
            # Try to load from file if it exists
            if os.path.exists('fingerprint_data.json'):
                with open('fingerprint_data.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load fingerprint data file: {e}")

        # Return default data if file doesn't exist or loading fails
        return {
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
            ],
            'languages': [
                'en-US',
                'en-GB',
                'es-ES',
                'fr-FR',
                'de-DE',
                'it-IT',
                'pt-BR',
                'ja-JP',
                'ko-KR',
                'zh-CN'
            ],
            'platforms': [
                'Win32',
                'MacIntel',
                'Linux x86_64'
            ],
            'vendors': [
                'Google Inc.',
                'Apple Computer, Inc.',
                'Intel Inc.',
                'NVIDIA Corporation'
            ],
            'renderers': [
                'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0)',
                'ANGLE (NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0)',
                'ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0)',
                'Metal',
                'Intel Iris OpenGL Engine'
            ],
            'screen_resolutions': [
                (1920, 1080),
                (1366, 768),
                (1440, 900),
                (1536, 864),
                (2560, 1440),
                (3840, 2160)
            ],
            'color_depths': [24, 32],
            'pixel_ratios': [1, 1.25, 1.5, 2],
            'timezones': [
                'America/New_York',
                'America/Los_Angeles',
                'America/Chicago',
                'Europe/London',
                'Europe/Paris',
                'Europe/Berlin',
                'Asia/Tokyo',
                'Asia/Shanghai',
                'Australia/Sydney'
            ]
        }

    def generate_fingerprint(self):
        """Generate a realistic browser fingerprint"""
        try:
            screen_resolution = random.choice(self.fingerprint_data['screen_resolutions'])
            return {
                'user_agent': random.choice(self.fingerprint_data['user_agents']),
                'language': random.choice(self.fingerprint_data['languages']),
                'platform': random.choice(self.fingerprint_data['platforms']),
                'vendor': random.choice(self.fingerprint_data['vendors']),
                'renderer': random.choice(self.fingerprint_data['renderers']),
                'canvas_noise': str(uuid.uuid4()),
                'webgl_vendor': random.choice(self.fingerprint_data['vendors']),
                'webgl_renderer': random.choice(self.fingerprint_data['renderers']),
                'hardware_concurrency': random.choice([2, 4, 6, 8, 12, 16]),
                'memory': random.choice([4, 8, 16, 32]),
                'screen_resolution': screen_resolution,
                'color_depth': random.choice(self.fingerprint_data['color_depths']),
                'pixel_ratio': random.choice(self.fingerprint_data['pixel_ratios']),
                'timezone': random.choice(self.fingerprint_data['timezones']),
                'touch_support': random.choice([True, False])
            }
        except Exception as e:
            self.logger.error(f"Error generating fingerprint: {e}")
            # Return a default fingerprint if generation fails
            return self.get_default_fingerprint()

    def get_default_fingerprint(self):
        """Return a default fingerprint if generation fails"""
        return {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'language': 'en-US',
            'platform': 'Win32',
            'vendor': 'Google Inc.',
            'renderer': 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0)',
            'canvas_noise': str(uuid.uuid4()),
            'webgl_vendor': 'Google Inc.',
            'webgl_renderer': 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0)',
            'hardware_concurrency': 4,
            'memory': 8,
            'screen_resolution': (1920, 1080),
            'color_depth': 24,
            'pixel_ratio': 1,
            'timezone': 'America/New_York',
            'touch_support': False
        }

    def save_fingerprint_data(self):
        """Save current fingerprint data to file"""
        try:
            with open('fingerprint_data.json', 'w') as f:
                json.dump(self.fingerprint_data, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving fingerprint data: {e}")

    def add_user_agent(self, user_agent: str):
        """Add a new user agent to the list"""
        if user_agent not in self.fingerprint_data['user_agents']:
            self.fingerprint_data['user_agents'].append(user_agent)
            self.save_fingerprint_data()

    def add_platform(self, platform: str):
        """Add a new platform to the list"""
        if platform not in self.fingerprint_data['platforms']:
            self.fingerprint_data['platforms'].append(platform)
            self.save_fingerprint_data()

    def add_renderer(self, renderer: str):
        """Add a new renderer to the list"""
        if renderer not in self.fingerprint_data['renderers']:
            self.fingerprint_data['renderers'].append(renderer)
            self.save_fingerprint_data()

    def add_resolution(self, width: int, height: int):
        """Add a new screen resolution"""
        resolution = (width, height)
        if resolution not in self.fingerprint_data['screen_resolutions']:
            self.fingerprint_data['screen_resolutions'].append(resolution)
            self.save_fingerprint_data()

    def add_timezone(self, timezone: str):
        """Add a new timezone"""
        if timezone not in self.fingerprint_data['timezones']:
            self.fingerprint_data['timezones'].append(timezone)
            self.save_fingerprint_data()