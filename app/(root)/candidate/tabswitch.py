# Import additional libraries needed for tab switching detection
from pynput import keyboard, mouse
import time
import requests
import threading
from datetime import datetime
import platform
import subprocess

class TabSwitchingDetector:
    def __init__(self, proctor_system=None, api_url=None):
        self.proctor_system = proctor_system
        self.active = False
        self.last_active_window = None
        self.tab_switches = []
        self.tab = []  # Store tab switches
        self.full_screen_violations = []
        self.check_interval = 1.0  # Check interval in seconds
        self.monitoring_thread = None
        self.lock = threading.Lock()
        self.is_full_screen = False
        self.api_url = api_url  # Store the API URL
        
    def start_monitoring(self):
        """Start monitoring tab switches and full screen status"""
        self.active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        print("Tab switching and full screen monitoring started")
        
    def stop_monitoring(self):
        """Stop monitoring tab switches"""
        self.active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        print("Tab switching and full screen monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.active:
            current_window = self._get_active_window()
            is_current_full_screen = self._is_fullscreen()
            
            with self.lock:
                # Check for window/tab changes
                if self.last_active_window and current_window != self.last_active_window:
                    switch_event = {
                        'user_id': 1,  # Placeholder for user ID
                        'timestamp': datetime.now(),
                        'from_window': self.last_active_window,
                        'to_window': current_window
                    }
                    self.tab.append(switch_event)

                    if self.api_url:
                        try:
                            requests.post(
                                f"{self.api_url}/api/tab",
                                json={
                                    'user_id': 1,  # Include the user_id
                                    'from_window': self.last_active_window,
                                    'to_window': current_window

                                },
                                headers={'Content-Type': 'application/json'}
                            )
                            print(f"Tab switch sent to API: {self.last_active_window} → {current_window}")
                        except Exception as e:
                            print(f"Failed to send tab switch to API: {e}")
                    
                    # Notify the proctor system if available
                    if self.proctor_system:
                        pass
                        # self.proctor_system.set_focus_state(False)
                        
                    print(f"Tab/Window switch detected: {self.last_active_window} → {current_window}")
                
                # Check for full screen violations
                if not is_current_full_screen and self.is_full_screen != is_current_full_screen:
                    violation_event = {
                        'timestamp': datetime.now(),
                        'violation_type': 'exited_fullscreen',
                        'window': current_window
                    }
                    self.full_screen_violations.append(violation_event)
                    print(f"Full screen violation detected: User exited full screen mode")
                
                # Update current state
                self.last_active_window = current_window
                self.is_full_screen = is_current_full_screen
            
            time.sleep(self.check_interval)
    
    def _get_active_window(self):
        """Get the title of the currently active window/tab"""
        system = platform.system()
        
        if system == 'Windows':
            try:
                import win32gui
                window = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(window)
            except ImportError:
                try:
                    # Alternative method using ctypes
                    import ctypes
                    user32 = ctypes.windll.user32
                    h_wnd = user32.GetForegroundWindow()
                    length = user32.GetWindowTextLengthW(h_wnd)
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(h_wnd, buf, length + 1)
                    return buf.value
                except Exception:
                    return "Unknown (Windows)"
        elif system == 'Darwin':  # macOS
            try:
                cmd = """osascript -e 'tell application "System Events" to get name of application processes whose frontmost is true'"""
                output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                
                # Additional AppleScript to get the title of the frontmost window
                cmd_title = """osascript -e 'tell application "System Events" to get name of front window of (first application process whose frontmost is true)'"""
                try:
                    window_title = subprocess.check_output(cmd_title, shell=True).decode('utf-8').strip()
                    return f"{output} - {window_title}"
                except:
                    return output
            except Exception:
                return "Unknown (macOS)"
        elif system == 'Linux':
            try:
                # Attempt to get window title using xdotool
                cmd = "xdotool getactivewindow getwindowname"
                return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
            except Exception:
                try:
                    # Alternative method for some Linux desktops
                    cmd = "xprop -id $(xprop -root _NET_ACTIVE_WINDOW | cut -d ' ' -f 5) _NET_WM_NAME"
                    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                    return output.split('"')[1] if '"' in output else "Unknown window"
                except Exception:
                    return "Unknown (Linux)"
        else:
            return "Unknown OS"
    
    def _is_fullscreen(self):
        """Check if the current window is in full screen mode"""
        system = platform.system()
        
        if system == 'Windows':
            try:
                import win32gui
                import win32api
                
                # Get foreground window
                foreground_window = win32gui.GetForegroundWindow()
                
                # Get window and screen dimensions
                window_rect = win32gui.GetWindowRect(foreground_window)
                screen_width = win32api.GetSystemMetrics(0)
                screen_height = win32api.GetSystemMetrics(1)
                
                # Check if window covers the entire screen
                return (window_rect[0] <= 0 and 
                        window_rect[1] <= 0 and 
                        window_rect[2] >= screen_width and 
                        window_rect[3] >= screen_height)
            except ImportError:
                try:
                    # Alternative method using ctypes
                    import ctypes
                    user32 = ctypes.windll.user32
                    
                    h_wnd = user32.GetForegroundWindow()
                    rect = ctypes.wintypes.RECT()
                    user32.GetWindowRect(h_wnd, ctypes.byref(rect))
                    
                    screen_width = user32.GetSystemMetrics(0)
                    screen_height = user32.GetSystemMetrics(1)
                    
                    return (rect.left <= 0 and 
                            rect.top <= 0 and 
                            rect.right >= screen_width and 
                            rect.bottom >= screen_height)
                except Exception:
                    return False
        elif system == 'Darwin':  # macOS
            try:
            # Get frontmost app name first
                app_cmd = """osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true'"""
                app_name = subprocess.check_output(app_cmd, shell=True).decode('utf-8').strip()
                
                # Then use that name in the fullscreen check
                cmd = f"""osascript -e 'tell application "System Events" to tell process "{app_name}" to get value of attribute "AXFullScreen" of window 1'"""
                output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                return output.lower() == 'true'
            except Exception as e:
                print(f"Fullscreen check error: {e}")
                return False
        elif system == 'Linux':
            try:
                # Get active window ID
                window_id_cmd = "xdotool getactivewindow"
                window_id = subprocess.check_output(window_id_cmd, shell=True).decode('utf-8').strip()
                
                # Get window state
                state_cmd = f"xprop -id {window_id} _NET_WM_STATE"
                state_output = subprocess.check_output(state_cmd, shell=True).decode('utf-8').strip()
                
                # Check if full screen is in the state
                return "_NET_WM_STATE_FULLSCREEN" in state_output
            except Exception:
                return False
        else:
            return False
    
    def enforce_fullscreen(self):
        """Attempt to enforce full screen mode on the current window"""
        system = platform.system()
        
        if system == 'Windows':
            try:
                import win32gui
                import win32con
                
                # Get foreground window
                foreground_window = win32gui.GetForegroundWindow()
                
                # Set window to maximized state
                win32gui.ShowWindow(foreground_window, win32con.SW_MAXIMIZE)
                return True
            except Exception:
                return False
        elif system == 'Darwin':  # macOS
            try:
                cmd = """osascript -e 'tell application "System Events" to tell process (name of application processes whose frontmost is true) to set value of attribute "AXFullScreen" of window 1 to true'"""
                subprocess.check_output(cmd, shell=True)
                return True
            except Exception:
                return False
        elif system == 'Linux':
            try:
                # Get active window ID
                window_id_cmd = "xdotool getactivewindow"
                window_id = subprocess.check_output(window_id_cmd, shell=True).decode('utf-8').strip()
                
                # Set full screen
                fullscreen_cmd = f"xdotool windowstate --add FULLSCREEN {window_id}"
                subprocess.check_output(fullscreen_cmd, shell=True)
                return True
            except Exception:
                return False
        else:
            return False
    
    def get_tab_switch_count(self):
        """Get the number of tab/window switches detected"""
        with self.lock:
            return len(self.tab_switches)
    
    def get_fullscreen_violation_count(self):
        """Get the number of fullscreen violations detected"""
        with self.lock:
            return len(self.full_screen_violations)
    
    def get_events(self):
        """Get all recorded events"""
        with self.lock:
            return {
                'tab_switches': self.tab_switches.copy(),
                'fullscreen_violations': self.full_screen_violations.copy()
            }
    
    def generate_report(self):
        """Generate a report of tab switching and fullscreen activity"""
        switch_count = self.get_tab_switch_count()
        violation_count = self.get_fullscreen_violation_count()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'tab_switch_count': switch_count,
            'fullscreen_violation_count': violation_count,
            'events': self.get_events()
        }
        
        return report

# Integration with ProctorSystem
def integrate_with_proctor_system(proctor_system):
    """Integrate the TabSwitchingDetector with an existing ProctorSystem"""
    # Create the detector and link it to the proctor system
    detector = TabSwitchingDetector(proctor_system)
    
    # Extend the ProctorSystem's start_test method
    original_start_test = proctor_system.start_test
    
    def extended_start_test():
        """Extended start_test that also starts tab switching detection"""
        original_start_test()
        detector.start_monitoring()
        detector.enforce_fullscreen()
        
    proctor_system.start_test = extended_start_test
    
    # Extend the ProctorSystem's end_test method
    original_end_test = proctor_system.end_test
    
    def extended_end_test():
        """Extended end_test that also stops tab switching detection"""
        detector.stop_monitoring()
        results = original_end_test()
        
        # Get tab switching report
        tab_report = detector.generate_report()
        
        # Add tab switching data to the results
        if 'metrics' not in results:
            results['metrics'] = {}
        
        results['metrics']['tab_switches'] = tab_report['tab_switch_count']
        results['metrics']['fullscreen_violations'] = tab_report['fullscreen_violation_count']
        
        # Add anomaly details if switches were detected
        if tab_report['tab_switch_count'] > 0:
            switch_anomaly = {
                "type": "window_switching",
                "subtype": "tab_changes",
                "count": tab_report['tab_switch_count'],
                "switches": [
                    {
                        "time": switch['timestamp'].isoformat(),
                        "from": switch['from_window'],
                        "to": switch['to_window']
                    } for switch in tab_report['events']['tab_switches']
                ]
            }
            
            if 'anomalies' not in results:
                results['anomalies'] = []
            
            results['anomalies'].append(switch_anomaly)
        
        # Add fullscreen violation details if detected
        if tab_report['fullscreen_violation_count'] > 0:
            fullscreen_anomaly = {
                "type": "fullscreen_violation",
                "subtype": "exited_fullscreen",
                "count": tab_report['fullscreen_violation_count'],
                "violations": [
                    {
                        "time": violation['timestamp'].isoformat(),
                        "window": violation['window']
                    } for violation in tab_report['events']['fullscreen_violations']
                ]
            }
            
            if 'anomalies' not in results:
                results['anomalies'] = []
            
            results['anomalies'].append(fullscreen_anomaly)
        
        return results
    
    proctor_system.end_test = extended_end_test
    
    return detector

# Example usage
if __name__ == "__main__":
    # Standalone example
    detector = TabSwitchingDetector(api_url="http://localhost:8000")
    detector.start_monitoring()
    
    print("Monitoring active. Press Ctrl+C to stop and see report.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_monitoring()
        report = detector.generate_report()
        
        print("\nTab Switching Report:")
        print(f"Total tab/window switches: {report['tab_switch_count']}")
        print(f"Fullscreen violations: {report['fullscreen_violation_count']}")
        
        if report['tab_switch_count'] > 0:
            print("\nTab Switch Events:")
            for switch in report['events']['tab_switches']:
                print(f"- {switch['timestamp']}: {switch['from_window']} → {switch['to_window']}")
        
        if report['fullscreen_violation_count'] > 0:
            print("\nFullscreen Violation Events:")
            for violation in report['events']['fullscreen_violations']:
                print(f"- {violation['timestamp']}: {violation['violation_type']} in {violation['window']}")

