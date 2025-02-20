import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional, Dict, Any
from ..utils.logger import get_logger
import os
import re
import subprocess
import platform


class ChromeLauncher:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.chrome_version = self.get_chrome_version()

    def get_chrome_version(self) -> int:
        try:
            system = platform.system()
            if system == "Windows":
                import winreg
                # Check both HKLM and HKCU
                paths = [
                    r"SOFTWARE\Google\Chrome\BLBeacon",
                    r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"
                ]
                for path in paths:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                        version, _ = winreg.QueryValueEx(key, "version")
                        winreg.CloseKey(key)
                        major_version = int(version.split('.')[0])
                        self.logger.info(f"Detected Chrome version: {version}")
                        return major_version
                    except WindowsError:
                        continue

            elif system == "Linux":
                process = subprocess.Popen(
                    ['google-chrome', '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, _ = process.communicate()
                version = re.search(r'(\d+)\.', output.decode()).group(1)
                return int(version)

            elif system == "Darwin":  # macOS
                process = subprocess.Popen(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, _ = process.communicate()
                version = re.search(r'(\d+)\.', output.decode()).group(1)
                return int(version)

        except Exception as e:
            self.logger.error(f"Error detecting Chrome version: {e}")
            # Default to latest stable version
            return 132

    def launch(self, profile: 'Profile') -> Optional[uc.Chrome]:
        options = self.create_chrome_options(profile)
        driver = self.create_driver(options)
        # self.apply_stealth_settings(driver, profile)
        return driver


    def create_chrome_options(self, profile: 'Profile') -> uc.ChromeOptions:
        options = uc.ChromeOptions()

        # Essential arguments
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={profile.fingerprint["user_agent"]}')

        # Window configuration
        window_size = profile.fingerprint['screen_resolution']
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')

        # Language and timezone
        options.add_argument(f'--lang={profile.fingerprint["language"]}')
        options.add_argument(f'--timezone={profile.fingerprint["timezone"]}')

        # User data directory
        user_data_dir = os.path.abspath(
            f'profiles/chrome_data_{profile.name}'
        )
        options.add_argument(f'--user-data-dir={user_data_dir}')

        # Proxy settings
        if profile.proxy:
            options.add_argument(f'--proxy-server={profile.proxy}')

        # Add preferences
        prefs = self.get_chrome_preferences(profile)
        options.add_experimental_option('prefs', prefs)

        return options

    def get_chrome_preferences(self, profile: 'Profile') -> Dict[str, Any]:
        return {
            'profile.default_content_setting_values': {
                'notifications': 2,
                'geolocation': 2,
                'media_stream': 2,
            },
            'webrtc': {
                'ip_handling_policy': 'default_public_interface_only',
                'multiple_routes_enabled': False,
                'nonproxied_udp_enabled': True
            },
            'profile.managed_default_content_settings': {
                'images': 1,
                'javascript': 1,
                'cookies': 1
            },
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }

    def get_chromium_version(self):
        chromium_path = "./chromium/chrome.exe"
        result = subprocess.check_output([chromium_path, "--version"], stderr=subprocess.STDOUT)
        print(f"chromium version: {result.decode()}")
        version = result.decode().strip().split()[-1]  # Get the version number
        print(f"chromium version: {version}")
        major_version = int(version.split('.')[0])  # Get major version number
        return major_version


    def create_driver(self, options: uc.ChromeOptions) -> Optional[uc.Chrome]:
        # Point to local Chromium
        print("== create_driver", options)
        # options.binary_location = "./chromium/chrome.exe"
        # Get Chromium version
        # version = self.get_chromium_version()
        # print("== version", version)
        #Keep essential features while minimizing tracking
        # options.add_argument('--disable-background-networking')
        # options.add_argument('--disable-default-apps')
        # options.add_argument('--disable-sync')
        # # options.add_argument('--disable-translate-new-ux')
        # options.add_argument('--disable-web-security')
        # options.add_argument('--no-default-browser-check')
        # options.add_argument('--no-first-run')
        # options.add_argument('--no-service-autorun')
        # options.add_argument('--password-store=basic')
        #
        # # Keep translation but disable other Google services
        # options.add_argument('--enable-translate')
        # options.add_argument('--disable-cloud-import')
        # options.add_argument('--disable-gaia-services')

        driver = uc.Chrome(
            options=options,
            # version_main=version,
            use_subprocess=True
        )
        return driver


    def apply_stealth_settings(self, driver: uc.Chrome, profile: 'Profile'):
        # 1. Basic WebDriver stealth
        self.add_cdp_stealth(driver)

        # 2. Inject fingerprint scripts
        self.inject_fingerprint_scripts(driver, profile)

        # 3. Set custom headers
        self.set_custom_headers(driver)

        # 4. Apply advanced stealth settings
        self.apply_advanced_stealth(driver)


    def add_cdp_stealth(self, driver: uc.Chrome):
        """Add basic CDP stealth scripts"""
        # Remove webdriver flag
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })

        # Add Chrome runtime
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                window.chrome = {
                    runtime: {
                        connect: () => {},
                        sendMessage: () => {},
                        onMessage: {
                            addListener: () => {},
                            removeListener: () => {}
                        },
                        getPlatformInfo: () => {},
                        getManifest: () => ({
                            version: '1.0.0'
                        })
                    },
                    app: {
                        isInstalled: false,
                        getDetails: () => {},
                        getIsInstalled: () => false
                    },
                    csi: () => {},
                    loadTimes: () => {}
                };
            """
        })


    def inject_fingerprint_scripts(self, driver: uc.Chrome, profile: 'Profile'):
        """Inject fingerprint spoofing scripts"""
        # Hardware specifications script
        hardware_script = f"""
            // Override hardware-related properties
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {profile.fingerprint['hardware_concurrency']}
            }});
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {profile.fingerprint['memory']}
            }});
            Object.defineProperty(navigator, 'platform', {{
                get: () => '{profile.fingerprint["platform"]}'
            }});
        """

        # Screen properties script
        screen_script = f"""
            // Override screen properties
            Object.defineProperty(window, 'devicePixelRatio', {{
                get: () => {profile.fingerprint['pixel_ratio']}
            }});
            Object.defineProperty(screen, 'width', {{
                get: () => {profile.fingerprint['screen_resolution'][0]}
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => {profile.fingerprint['screen_resolution'][1]}
            }});
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {profile.fingerprint['color_depth']}
            }});
        """

        # WebGL spoofing script
        webgl_script = f"""
            // Override WebGL properties
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                // Spoof vendor and renderer
                if (parameter === 37445) {{ // UNMASKED_VENDOR_WEBGL
                    return '{profile.fingerprint["webgl_vendor"]}';
                }}
                if (parameter === 37446) {{ // UNMASKED_RENDERER_WEBGL
                    return '{profile.fingerprint["webgl_renderer"]}';
                }}
                return getParameter.apply(this, arguments);
            }};
        """

        # Canvas fingerprint randomization
        canvas_script = """
            // Add noise to canvas fingerprint
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const dataURL = originalToDataURL.apply(this, arguments);
                if (type === 'image/png' && this.width > 0 && this.height > 0) {
                    const canvas = document.createElement('canvas');
                    canvas.width = this.width;
                    canvas.height = this.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(this, 0, 0);

                    // Add subtle noise
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const pixels = imageData.data;
                    for (let i = 0; i < pixels.length; i += 4) {
                        pixels[i] += Math.floor(Math.random() * 2);     // Red
                        pixels[i + 1] += Math.floor(Math.random() * 2); // Green
                        pixels[i + 2] += Math.floor(Math.random() * 2); // Blue
                    }
                    ctx.putImageData(imageData, 0, 0);
                    return canvas.toDataURL(type);
                }
                return dataURL;
            };
        """

        # Audio fingerprint randomization
        audio_script = """
            // Add noise to audio fingerprint
            const originalCreateOscillator = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {
                const oscillator = originalCreateOscillator.apply(this, arguments);
                oscillator.frequency.value += Math.random() * 0.1;
                return oscillator;
            };
        """

        # Plugins and mime-types spoofing
        plugins_script = """
            // Spoof plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    const plugins = [
                        {
                            name: 'Chrome PDF Plugin',
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer',
                            length: 1,
                            item: () => null
                        },
                        {
                            name: 'Chrome PDF Viewer',
                            description: 'Chrome PDF Viewer',
                            filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
                            length: 1,
                            item: () => null
                        }
                    ];
                    plugins.refresh = () => {};
                    plugins.item = (index) => plugins[index];
                    plugins.namedItem = (name) => plugins.find(p => p.name === name);
                    return plugins;
                }
            });
        """

        # Inject all scripts
        scripts = [
            hardware_script,
            screen_script,
            webgl_script,
            canvas_script,
            audio_script,
            plugins_script
        ]

        for script in scripts:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": script
            })

    def apply_advanced_stealth(self, driver: uc.Chrome):
        """Apply advanced stealth techniques"""
        # Permission management
        permissions_script = """
            // Override permission behavior
            const originalQuery = window.Notification.requestPermission;
            window.Notification.requestPermission = function() {
                return new Promise(function(resolve, reject) {
                    resolve('denied');
                });
            };

            // Override geolocation
            navigator.geolocation.getCurrentPosition = function(success, error) {
                error({ code: 1, message: 'Permission denied.' });
            };
        """

        # Performance timing randomization
        performance_script = """
            // Randomize performance timing
            const originalGetEntries = Performance.prototype.getEntries;
            Performance.prototype.getEntries = function() {
                const entries = originalGetEntries.apply(this, arguments);
                return entries.map(entry => {
                    entry.duration += Math.random() * 10;
                    entry.startTime += Math.random() * 10;
                    return entry;
                });
            };
        """

        # WebRTC handling
        webrtc_script = """
            // Override WebRTC behavior
            const originalRTCPeerConnection = window.RTCPeerConnection;
            window.RTCPeerConnection = function(...args) {
                const pc = new originalRTCPeerConnection(...args);
                pc.createDataChannel = function() { return {}; };
                return pc;
            };
        """

        # Inject advanced scripts
        advanced_scripts = [
            permissions_script,
            performance_script,
            webrtc_script
        ]

        for script in advanced_scripts:
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": script
            })


    def set_custom_headers(self, driver: uc.Chrome):
        """Set custom headers to appear more natural"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': headers})
