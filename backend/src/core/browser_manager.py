from typing import Dict, Optional
from .profile_manager import ProfileManager
from .chrome_launcher import ChromeLauncher
from ..utils.logger import get_logger

class BrowserManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.profile_manager = ProfileManager()
        self.chrome_launcher = ChromeLauncher()
        self.active_browsers: Dict[str, 'ChromeDriver'] = {}

    def create_profile(self, name: str) -> bool:
        try:
            return self.profile_manager.create_profile(name)
        except Exception as e:
            self.logger.error(f"Error creating profile: {e}")
            return False

    def launch_profile(self, profile_name: str) -> bool:
        print("launching profile", profile_name)
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            return False

        driver = self.chrome_launcher.launch(profile)
        if driver:
            self.active_browsers[profile_name] = driver
            return True
        return False

    def launch_and_get_browser(self, profile_name: str) -> Optional['ChromeDriver']:
        """
        Get the active browser instance for a profile
        :param profile_name: Name of the profile to get browser for
        :return: ChromeDriver instance if found, None otherwise
        """
        self.logger.debug(f"Getting browser for profile: {profile_name}")
        launch_profile = self.launch_profile(profile_name)
        if not launch_profile:
            self.logger.error(f"Failed to launch profile: {profile_name}")
            return None
        browser = self.active_browsers.get(profile_name)
        if browser is None:
            self.logger.warning(f"No active browser found for profile: {profile_name}")
        return browser

    def cleanup(self):
        try:
            for driver in self.active_browsers.values():
                try:
                    driver.quit()
                except:
                    pass
            self.active_browsers.clear()
            self.profile_manager.cleanup()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")