import requests
import json
import time
import threading
import hashlib
import platform
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class BrowserFingerprintMonitor:
    def __init__(self, check_interval=5, api_url=None, user_id=1):
        """
        Initialize the browser fingerprint monitor.
        
        Args:
            check_interval (int): How often to check for fingerprint changes in seconds
            api_url (str): URL of the API to post fingerprint changes
            user_id (int): ID of the user being monitored
        """
        self.active = False
        self.check_interval = check_interval
        self.monitoring_thread = None
        self.lock = threading.Lock()
        self.initial_fingerprint = None
        self.current_fingerprint = None
        self.fingerprint_changes = []
        self.driver = None
        self.api_url = api_url  # Add this line
        self.user_id = user_id  # Add this line
        
    def start_monitoring(self):
        """Start monitoring browser fingerprint changes"""
        self.active = True
        
        # Initialize the WebDriver
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Create a new Chrome WebDriver instance
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Get initial fingerprint
            self.initial_fingerprint = self._generate_fingerprint()
            self.current_fingerprint = self.initial_fingerprint
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitoring_thread.start()
            
            print(f"Initial fingerprint: {self.initial_fingerprint['hash']}")
            return True
        except Exception as e:
            print(f"Error starting monitoring: {e}")
            if self.driver:
                self.driver.quit()
            return False
    
    def stop_monitoring(self):
        """Stop monitoring fingerprint changes"""
        self.active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        if self.driver:
            self.driver.quit()
        
        # Return the report when stopping
        return self.generate_report()
    
    def _monitor_loop(self):
        while self.active:
            try:
                # Generate new fingerprint
                new_fingerprint = self._generate_fingerprint()
                
                with self.lock:
                    # Check if fingerprint has changed
                    if new_fingerprint['hash'] != self.current_fingerprint['hash']:
                        # Create a JSON-serializable version of the event
                        change_event = {
                            'timestamp': datetime.now().isoformat(),  # Convert to ISO string
                            'previous_fingerprint': {
                                'hash': self.current_fingerprint['hash'],
                                'timestamp': self.current_fingerprint['timestamp'].isoformat()  # Convert to ISO string
                            },
                            'new_fingerprint': {
                                'hash': new_fingerprint['hash'],
                                'timestamp': new_fingerprint['timestamp'].isoformat()  # Convert to ISO string
                            },
                            'active_window': self._get_active_window()
                        }
                        
                        # Store the original event with datetime objects for internal use
                        internal_event = {
                            'timestamp': datetime.now(),
                            'previous_fingerprint': self.current_fingerprint,
                            'new_fingerprint': new_fingerprint,
                            'active_window': self._get_active_window()
                        }
                        
                        self.fingerprint_changes.append(internal_event)
                        self.current_fingerprint = new_fingerprint
                        
                        print(f"Fingerprint change detected at {change_event['timestamp']}")

                        # Send fingerprint change to API if URL is set
                        if self.api_url:
                            try:
                                # Include user_id in the data
                                api_payload = {
                                    'user_id': self.user_id,
                                    'timestamp': change_event['timestamp'],
                                    'previous_hash': change_event['previous_fingerprint']['hash'],
                                    'fingerprint_hash': change_event['new_fingerprint']['hash'],
                                    'active_window': change_event['active_window']
                                }
                                
                                response = requests.post(
                                    f"{self.api_url}/api/fingerprint_change",
                                    json=api_payload,
                                    headers={'Content-Type': 'application/json'}
                                )
                                if response.status_code == 201:
                                    print(f"Fingerprint change sent to API successfully")
                                else:
                                    print(f"Failed to send fingerprint change to API: {response.status_code}, {response.text}")
                            except Exception as e:
                                print(f"Error sending fingerprint change to API: {e}")
            
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
            
            time.sleep(self.check_interval)
        
    def _generate_fingerprint(self):
        """Generate browser fingerprint data"""
        fingerprint = {}
        
        try:
            # Navigate to a real page first to avoid data: URL issues
            self.driver.get("about:blank")
            
            # Execute JavaScript to collect browser fingerprint data
            fingerprint_data = self.driver.execute_script("""
            return {
                userAgent: navigator.userAgent,
                language: navigator.language,
                platform: navigator.platform,
                doNotTrack: navigator.doNotTrack,
                cookiesEnabled: navigator.cookieEnabled,
                screenWidth: screen.width,
                screenHeight: screen.height,
                colorDepth: screen.colorDepth,
                pixelRatio: window.devicePixelRatio || '',
                hardwareConcurrency: navigator.hardwareConcurrency || '',
                timezone: new Date().getTimezoneOffset(),
                timezoneString: Intl.DateTimeFormat().resolvedOptions().timeZone,
                // Remove problematic storage checks
                plugins: Array.from(navigator.plugins || []).map(p => p.name).join(','),
                canvas: (() => {
                    try {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        canvas.width = 200;
                        canvas.height = 50;
                        
                        ctx.textBaseline = 'top';
                        ctx.font = '14px Arial';
                        ctx.fillStyle = '#FF6600';
                        ctx.fillRect(0, 0, 100, 25);
                        ctx.fillStyle = '#0066FF';
                        ctx.fillText('Fingerprint 👍', 2, 15);
                        
                        return canvas.toDataURL().substr(0, 100);  // Just get the beginning of the string
                    } catch (e) {
                        return "Canvas not supported";
                    }
                })(),
                webGL: (() => {
                    try {
                        const canvas = document.createElement('canvas');
                        const gl = canvas.getContext('webgl');
                        
                        if (!gl) return "WebGL not supported";
                        
                        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                        if (debugInfo) {
                            return {
                                vendor: gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL),
                                renderer: gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
                            };
                        }
                        return "Debug info not available";
                    } catch (e) {
                        return "WebGL error";
                    }
                })()
            };
            """)
            
            # Create a hash of the fingerprint data
            fingerprint_json = json.dumps(fingerprint_data, sort_keys=True)
            hash_object = hashlib.sha256(fingerprint_json.encode())
            
            return {
                'data': fingerprint_data,
                'hash': hash_object.hexdigest(),
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error generating fingerprint: {e}")
            # Generate a simpler fingerprint on error
            simple_data = {
                'userAgent': self.driver.execute_script("return navigator.userAgent;"),
                'error': str(e)
            }
            fingerprint_json = json.dumps(simple_data, sort_keys=True)
            hash_object = hashlib.sha256(fingerprint_json.encode())
            
            return {
                'data': simple_data,
                'hash': hash_object.hexdigest(),
                'timestamp': datetime.now()
            }
    
    def _get_active_window(self):
        """Get the title of the currently active window/tab"""
        system = platform.system()
        
        if system == 'Windows':
            try:
                import win32gui
                window = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(window)
            except ImportError:
                return "Unknown (Windows)"
        elif system == 'Darwin':  # macOS
            try:
                cmd = """osascript -e 'tell application "System Events" to get name of application processes whose frontmost is true'"""
                output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                return output
            except Exception:
                return "Unknown (macOS)"
        elif system == 'Linux':
            try:
                cmd = "xdotool getactivewindow getwindowname"
                return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
            except Exception:
                return "Unknown (Linux)"
        else:
            return "Unknown OS"
    
    def get_change_count(self):
        """Get the number of fingerprint changes detected"""
        with self.lock:
            return len(self.fingerprint_changes)
    
    def get_changes(self):
        """Get all recorded fingerprint changes"""
        with self.lock:
            return self.fingerprint_changes.copy()
    
    def generate_report(self):
        """Generate a report of browser fingerprint changes"""
        with self.lock:
            change_count = self.get_change_count()
            report = {
                'timestamp': datetime.now().isoformat(),
                'initial_fingerprint': {
                    'hash': self.initial_fingerprint['hash'],
                    'timestamp': self.initial_fingerprint['timestamp'].isoformat() if self.initial_fingerprint else None
                },
                'current_fingerprint': {
                    'hash': self.current_fingerprint['hash'],
                    'timestamp': self.current_fingerprint['timestamp'].isoformat() if self.current_fingerprint else None
                },
                'fingerprint_change_count': change_count,
                'fingerprint_changes': [
                    {
                        'timestamp': change['timestamp'].isoformat(),
                        'previous_hash': change['previous_fingerprint']['hash'],
                        'new_hash': change['new_fingerprint']['hash'],
                        'active_window': change['active_window']
                    }
                    for change in self.fingerprint_changes
                ]
            }
        return report

    
    def save_report(self, filename=None):
        """Save the report to a JSON file"""
        if filename is None:
            filename = f"fingerprint_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to {filename}")
        return filename


# Example usage
if __name__ == "__main__":
    # Create instance
    monitor = BrowserFingerprintMonitor(check_interval=10)  # Check every 10 seconds
    
    # Start monitoring
    if monitor.start_monitoring():
        print("Monitoring started successfully!")
        print("Press Ctrl+C to stop monitoring...")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
        # Stop monitoring and get the report
        report = monitor.stop_monitoring()
        
        # Save report to JSON file
        output_file = monitor.save_report()
        print(f"Report saved to {output_file}")
        
        # Print summary
        print(f"Detected {report['fingerprint_change_count']} fingerprint changes")
    else:
        print("Failed to start monitoring")