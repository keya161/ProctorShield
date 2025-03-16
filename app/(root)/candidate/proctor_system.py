import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from pynput import keyboard, mouse
import time
from datetime import datetime
import threading
import json
import matplotlib.pyplot as plt
import io
import base64

class ProctorSystem:
    def __init__(self):
        # Keystroke data storage
        self.key_press_times = {}
        self.key_release_times = {}
        self.keystroke_data = []
        
        # Mouse data storage
        self.mouse_positions = []
        self.mouse_clicks = []
        self.last_mouse_time = time.time()

        # Copy-paste tracking
        self.copy_paste_events = []
        self.copy_paste_detected = False
        
        # self.last_activity_time = time.time()
        
        # Models
        self.keystroke_model = None
        self.mouse_model = None
        
        # Baseline data
        self.baseline_keystroke_data = None
        self.baseline_mouse_data = None

        
        # User profile
        self.user_profile = {
            'avg_hold_time': 0,
            'std_hold_time': 0,
            'avg_flight_time': 0,
            'std_flight_time': 0,
            'typing_speed': 0,
            'common_digraphs': {},
            'mouse_movement_speed': 0,
            'typical_pause_duration': 0
        }
        
        # Sensitivity level (1-10, where 10 is most sensitive)
        self.sensitivity = 5
        
        # Threading locks
        self.data_lock = threading.Lock()
        
    def set_sensitivity(self, level):
        """Set the sensitivity level (1-10)"""
        if 1 <= level <= 10:
            self.sensitivity = level
            print(f"Sensitivity set to {level}/10")
        else:
            print("Sensitivity must be between 1 and 10")
    
    def start_collection(self):
        """Start collecting keystroke and mouse data"""
        # Set up keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release)
        
        # Set up mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click)
        
        # Start listeners
        self.keyboard_listener.start()
        self.mouse_listener.start()
        
    def stop_collection(self):
        """Stop collecting data"""
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
    
    def _on_key_press(self, key):
        """Record when a key is pressed"""
        try:
            current_time = time.time()
            key_char = key.char if hasattr(key, 'char') else str(key)
            self.key_press_times[key_char] = current_time
            self.last_activity_time = current_time
        except AttributeError:
            pass
    
    def _on_key_release(self, key):
        """Record when a key is released and calculate metrics"""
        try:
            current_time = time.time()
            key_char = key.char if hasattr(key, 'char') else str(key)
            
            if key_char in self.key_press_times:
                press_time = self.key_press_times[key_char]
                hold_time = current_time - press_time
                
                with self.data_lock:
                    # Find the previous key release if it exists
                    flight_time = None
                    previous_key = None
                    if self.keystroke_data:
                        last_release = self.keystroke_data[-1]['timestamp']
                        flight_time = press_time - last_release
                        previous_key = self.keystroke_data[-1]['key']
                    
                    # Store the keystroke data
                    self.keystroke_data.append({
                        'key': key_char,
                        'hold_time': hold_time,
                        'flight_time': flight_time,
                        'previous_key': previous_key,
                        'timestamp': current_time,
                    })
                    
                    # Record digraph if we have a previous key
                    if previous_key:
                        digraph = previous_key + key_char
                        if 'digraphs' not in self.__dict__:
                            self.digraphs = {}
                        
                        if digraph not in self.digraphs:
                            self.digraphs[digraph] = []
                            
                        self.digraphs[digraph].append({
                            'flight_time': flight_time,
                            'timestamp': current_time
                        })
        except AttributeError:
            pass
    
    def _on_mouse_move(self, x, y):
        """Record mouse movement"""
        current_time = time.time()
        time_since_last = current_time - self.last_mouse_time
        self.last_mouse_time = current_time
        self.last_activity_time = current_time
        
        with self.data_lock:
            # Calculate velocity if we have previous positions
            velocity_x, velocity_y = 0, 0
            if self.mouse_positions:
                prev_x = self.mouse_positions[-1]['x']
                prev_y = self.mouse_positions[-1]['y']
                
                if time_since_last > 0:
                    velocity_x = (x - prev_x) / time_since_last
                    velocity_y = (y - prev_y) / time_since_last
            
            self.mouse_positions.append({
                'x': x,
                'y': y,
                'timestamp': current_time,
                'time_since_last': time_since_last,
                'velocity_x': velocity_x,
                'velocity_y': velocity_y,
                'velocity_magnitude': np.sqrt(velocity_x**2 + velocity_y**2),
            })
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Record mouse clicks"""
        current_time = time.time()
        self.last_activity_time = current_time
        
        with self.data_lock:
            self.mouse_clicks.append({
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'timestamp': current_time,
            })

    def register_copy_paste_event(self, event_type="paste"):
        """Register a copy or paste event from the website"""
        current_time = time.time()
        self.copy_paste_events.append({
            'type': event_type,  # 'copy' or 'paste'
            'timestamp': current_time
        })
        self.copy_paste_detected = True
        print(f"{event_type.capitalize()} event detected at {datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}")
        return {"status": "recorded", "event_type": event_type}
        
    def start_baseline_collection(self):
        """Start collecting baseline data when a button is pressed"""
        print("Starting baseline data collection...")
        print("Please type naturally to establish your typing pattern.")
        
        # Reset any existing baseline data
        self.baseline_keystroke_data = None
        self.baseline_mouse_data = None
        if hasattr(self, 'baseline_digraphs'):
            delattr(self, 'baseline_digraphs')
        
        # Start data collection
        self.start_collection()
        return {"status": "success", "message": "Baseline collection started"}

    def stop_baseline_collection(self):
        """Stop baseline collection and process the data"""
        self.stop_collection()
        
        with self.data_lock:
            if not self.keystroke_data:
                return {"status": "error", "message": "No keystroke data collected. Try again."}
                
            self.baseline_keystroke_data = self.keystroke_data.copy()
            self.baseline_mouse_data = {
                'positions': self.mouse_positions.copy(),
                'clicks': self.mouse_clicks.copy()
            }
            self.baseline_digraphs = self.digraphs.copy() if hasattr(self, 'digraphs') else {}
            
            # Reset data for the actual test
            self.keystroke_data = []
            self.mouse_positions = []
            self.mouse_clicks = []
            if hasattr(self, 'digraphs'):
                self.digraphs = {}
        
        print("Baseline collection complete!")
        self._build_user_profile()
        self._train_models()
        
        return {
            "status": "success", 
            "message": "Baseline collection completed successfully",
            "data_points": len(self.baseline_keystroke_data)
        }        

        
    def _build_user_profile(self):
        """Build a profile of the user's typing and mouse behavior"""
        if not self.baseline_keystroke_data:
            return
            
        # Process keystroke data
        df = pd.DataFrame(self.baseline_keystroke_data)
        df['flight_time'] = df['flight_time'].fillna(0)
        
        # Calculate key typing metrics
        self.user_profile['avg_hold_time'] = df['hold_time'].mean()
        self.user_profile['std_hold_time'] = df['hold_time'].std()
        self.user_profile['avg_flight_time'] = df['flight_time'][df['flight_time'] > 0].mean()
        self.user_profile['std_flight_time'] = df['flight_time'][df['flight_time'] > 0].std()
        
        # Calculate typing speed (characters per minute)
        if len(df) > 1:
            total_time = df['timestamp'].max() - df['timestamp'].min()
            if total_time > 0:
                self.user_profile['typing_speed'] = len(df) / total_time * 60
        
        # Analyze common digraphs
        if hasattr(self, 'baseline_digraphs'):
            for digraph, occurrences in self.baseline_digraphs.items():
                if len(occurrences) >= 3:  # Only consider digraphs with multiple occurrences
                    flight_times = [o['flight_time'] for o in occurrences]
                    self.user_profile['common_digraphs'][digraph] = {
                        'mean': np.mean(flight_times),
                        'std': np.std(flight_times),
                        'count': len(flight_times)
                    }
        
        # Analyze mouse movement
        if self.baseline_mouse_data['positions']:
            mouse_df = pd.DataFrame(self.baseline_mouse_data['positions'])
            if 'velocity_magnitude' in mouse_df:
                self.user_profile['mouse_movement_speed'] = mouse_df['velocity_magnitude'].mean()
        
        # Analyze typical pauses
        pause_threshold = self.user_profile['avg_flight_time'] * 2
        pauses = df['flight_time'][df['flight_time'] > pause_threshold]
        if not pauses.empty:
            self.user_profile['typical_pause_duration'] = pauses.mean()
        
        print("User profile created successfully")
        
    def _train_models(self):
        """Train anomaly detection models on baseline data"""
        # Process keystroke data
        if self.baseline_keystroke_data:
            df = pd.DataFrame(self.baseline_keystroke_data)
            # Fill NaN values for the first entry which won't have flight_time
            df['flight_time'] = df['flight_time'].fillna(0)
            
            # Extract features
            features = df[['hold_time', 'flight_time']].values
            
            # Adjust contamination based on sensitivity (lower value = more sensitive)
            contamination = 0.1 * (11 - self.sensitivity) / 10
            
            # Train isolation forest model
            self.keystroke_model = IsolationForest(contamination=contamination, random_state=42)
            self.keystroke_model.fit(features)
            
            # Train a KMeans model to cluster typing behaviors
            n_clusters = min(3, len(features) // 10) if len(features) > 30 else 1
            if n_clusters > 0:
                self.keystroke_cluster = KMeans(n_clusters=n_clusters, random_state=42)
                self.keystroke_cluster.fit(features)
            
        # Process mouse data if needed
        if self.baseline_mouse_data['positions']:
            positions_df = pd.DataFrame(self.baseline_mouse_data['positions'])
            
            if 'velocity_magnitude' in positions_df and len(positions_df) > 10:
                # Calculate velocity and acceleration
                positions_df['velocity'] = positions_df['velocity_magnitude']
                
                # Extract features
                mouse_features = positions_df[['time_since_last', 'velocity']].values
                
                # Adjust contamination based on sensitivity
                contamination = 0.1 * (11 - self.sensitivity) / 10
                
                # Train model
                self.mouse_model = IsolationForest(contamination=contamination, random_state=42)
                self.mouse_model.fit(mouse_features)
    
    def start_test(self):
        """Start the actual test"""
        if not self.baseline_keystroke_data:
            print("Error: Baseline data not collected. Run collect_baseline() first.")
            return
        
        print("Starting test monitoring...")
        self.start_collection()
    
    def end_test(self):
        """End the test and analyze the results"""
        self.stop_collection()
        return self.analyze_test_data()
    
    def analyze_test_data(self):
        """Analyze collected test data for anomalies with detailed explanations"""
        with self.data_lock:
            test_keystroke_df = pd.DataFrame(self.keystroke_data)
            
            if test_keystroke_df.empty:
                return {
                    "result": "insufficient_data",
                    "message": "Not enough keystroke data collected during the test",
                    "details": []
                }
            
            # Fill NaN values
            test_keystroke_df['flight_time'] = test_keystroke_df['flight_time'].fillna(0)
            
            # Extract features
            test_features = test_keystroke_df[['hold_time', 'flight_time']].values
            # Initialize result details
            anomaly_details = []
            anomaly_scores = {}
            overall_suspicion_level = 0
            copy_paste_count = len(self.copy_paste_events)
            anomaly_scores['copy_paste_events'] = copy_paste_count      

            # Adjust thresholds based on sensitivity level
            sensitivity_factor = self.sensitivity / 5  # Normalize to 1.0 for default sensitivity

            if copy_paste_count > 0:
                copy_paste_timestamps = [event['timestamp'] for event in self.copy_paste_events]
                
                anomaly_details.append({
                    "type": "copy_paste",
                    "subtype": "clipboard_usage",
                    "description": f"User used copy/paste {copy_paste_count} times during the test",
                    "severity": min(copy_paste_count * 3, 10),  # Each copy-paste has high severity
                    "timestamps": copy_paste_timestamps
                })
                
                # Add to overall suspicion level - copy-paste is highly suspicious
                overall_suspicion_level += min(copy_paste_count * 2, 6)
            # Analyze keystrokes
            if self.keystroke_model and len(test_keystroke_df) > 5:
                # Get anomaly scores (-1 for anomalies, 1 for normal)
                raw_scores = self.keystroke_model.decision_function(test_features)
                predictions = self.keystroke_model.predict(test_features)
                
                # Calculate anomaly percentage
                anomaly_percent = (predictions == -1).mean() * 100
                anomaly_scores['keystroke_anomaly_percent'] = float(anomaly_percent)
                
                # Adjust suspicion threshold based on sensitivity
                keystroke_threshold = 15 * (1 / sensitivity_factor)
                
                if anomaly_percent > keystroke_threshold:
                    # Find the anomalous keystrokes
                    anomalous_indices = np.where(predictions == -1)[0]
                    
                    # Group consecutive anomalous keystrokes
                    keystroke_anomaly_groups = self._group_consecutive_indices(anomalous_indices)
                    
                    for group in keystroke_anomaly_groups[:3]:  # Limit to top 3 groups
                        group_df = test_keystroke_df.iloc[group]
                        anomaly_type = self._classify_keystroke_anomaly(group_df)
                        
                        anomaly_details.append({
                            "type": "keystroke_anomaly",
                            "subtype": anomaly_type["type"],
                            "description": anomaly_type["description"],
                            "severity": anomaly_type["severity"],
                            "timestamp_start": group_df['timestamp'].min(),
                            "timestamp_end": group_df['timestamp'].max(),
                            "affected_keys": group_df['key'].tolist()
                        })
                    
                    # Add to overall suspicion level
                    overall_suspicion_level += min(anomaly_percent / keystroke_threshold, 3) * 2
            
            # Analyze typing consistency
            if len(test_keystroke_df) > 10:
                baseline_consistency = self.user_profile['std_hold_time']
                test_consistency = test_keystroke_df['hold_time'].std()
                
                consistency_ratio = test_consistency / baseline_consistency if baseline_consistency > 0 else 1
                anomaly_scores['typing_consistency_ratio'] = float(consistency_ratio)
                
                consistency_threshold = 1.5 * (1 / sensitivity_factor)
                if consistency_ratio > consistency_threshold:
                    anomaly_details.append({
                        "type": "typing_consistency",
                        "subtype": "inconsistent_rhythm",
                        "description": f"Typing rhythm is {consistency_ratio:.1f}x more variable than baseline",
                        "severity": min(int(consistency_ratio * 2), 10),
                        "baseline_consistency": float(baseline_consistency),
                        "test_consistency": float(test_consistency)
                    })
                    
                    overall_suspicion_level += min(consistency_ratio / consistency_threshold, 3)
            
            # Analyze typing speed
            if len(test_keystroke_df) > 10:
                baseline_speed = self.user_profile['typing_speed']
                
                total_test_time = test_keystroke_df['timestamp'].max() - test_keystroke_df['timestamp'].min()
                test_speed = len(test_keystroke_df) / total_test_time * 60 if total_test_time > 0 else 0
                
                speed_ratio = baseline_speed / test_speed if test_speed > 0 else 1
                anomaly_scores['typing_speed_ratio'] = float(speed_ratio)
                
                speed_threshold = 1.4 * (1 / sensitivity_factor)
                if speed_ratio > speed_threshold or speed_ratio < 1/speed_threshold:
                    description = f"Typing speed is "
                    if speed_ratio > 1:
                        description += f"{speed_ratio:.1f}x slower than baseline"
                    else:
                        description += f"{1/speed_ratio:.1f}x faster than baseline"
                    
                    anomaly_details.append({
                        "type": "typing_speed",
                        "subtype": "abnormal_speed",
                        "description": description,
                        "severity": min(int(abs(speed_ratio - 1) * 5), 10),
                        "baseline_speed": float(baseline_speed),
                        "test_speed": float(test_speed)
                    })
                    
                    overall_suspicion_level += min(abs(speed_ratio - 1) * 3, 3)
            
            # Detect unusual pauses
            if len(test_keystroke_df) > 5:
                flight_times = test_keystroke_df['flight_time'].dropna()
                baseline_flight_mean = self.user_profile['avg_flight_time']
                baseline_flight_std = self.user_profile['std_flight_time']
                
                pause_threshold = baseline_flight_mean + 3 * baseline_flight_std
                unusual_pauses = flight_times[flight_times > pause_threshold]
                
                # Adjust pause threshold based on sensitivity
                pause_sensitivity = 3 * (1 / sensitivity_factor)
                unusual_pauses_count = len(unusual_pauses)
                anomaly_scores['unusual_pauses'] = unusual_pauses_count
                
                if unusual_pauses_count > pause_sensitivity:
                    # Find timestamps of unusual pauses
                    pause_timestamps = []
                    for idx in unusual_pauses.index:
                        if idx < len(test_keystroke_df):
                            pause_timestamps.append(test_keystroke_df.iloc[idx]['timestamp'])
                    
                    anomaly_details.append({
                        "type": "typing_pauses",
                        "subtype": "frequent_pauses",
                        "description": f"Detected {unusual_pauses_count} unusually long pauses during typing",
                        "severity": min(unusual_pauses_count, 10),
                        "timestamps": pause_timestamps[:5]  # Limit to first 5 instances
                    })
                    
                    overall_suspicion_level += min(unusual_pauses_count / pause_sensitivity, 3)
            
            
            # Analyze digraph patterns if we have enough data
            if hasattr(self, 'digraphs') and self.user_profile['common_digraphs']:
                digraph_anomalies = []
                
                for digraph, baseline_stats in self.user_profile['common_digraphs'].items():
                    if digraph in self.digraphs and len(self.digraphs[digraph]) >= 2:
                        test_flight_times = [d['flight_time'] for d in self.digraphs[digraph]]
                        test_mean = np.mean(test_flight_times)
                        
                        # Calculate z-score of test mean compared to baseline
                        if baseline_stats['std'] > 0:
                            z_score = abs(test_mean - baseline_stats['mean']) / baseline_stats['std']
                            
                            # Adjust threshold based on sensitivity
                            digraph_threshold = 2.5 * (1 / sensitivity_factor)
                            
                            if z_score > digraph_threshold:
                                digraph_anomalies.append({
                                    "digraph": digraph,
                                    "z_score": float(z_score),
                                    "baseline_mean": float(baseline_stats['mean']),
                                    "test_mean": float(test_mean)
                                })
                
                if digraph_anomalies:
                    # Sort by z-score in descending order
                    digraph_anomalies.sort(key=lambda x: x['z_score'], reverse=True)
                    top_anomalies = digraph_anomalies[:3]  # Limit to top 3
                    
                    anomaly_details.append({
                        "type": "digraph_patterns",
                        "subtype": "inconsistent_patterns",
                        "description": f"Detected {len(digraph_anomalies)} common letter combinations typed with abnormal timing",
                        "severity": min(int(top_anomalies[0]['z_score']), 10),
                        "details": top_anomalies
                    })
                    
                    overall_suspicion_level += min(top_anomalies[0]['z_score'] / digraph_threshold, 3)
            
            # Mouse behavior analysis
            mouse_positions_df = pd.DataFrame(self.mouse_positions)
            if not mouse_positions_df.empty and 'velocity_magnitude' in mouse_positions_df and self.mouse_model:
                mouse_features = mouse_positions_df[['time_since_last', 'velocity_magnitude']].values
                mouse_predictions = self.mouse_model.predict(mouse_features)
                mouse_anomalies = (mouse_predictions == -1).mean() * 100
                anomaly_scores['mouse_anomaly_percent'] = float(mouse_anomalies)
                
                mouse_threshold = 20 * (1 / sensitivity_factor)
                if mouse_anomalies > mouse_threshold:
                    # Find the anomalous mouse movements
                    mouse_anomalous_indices = np.where(mouse_predictions == -1)[0]
                    
                    # Group consecutive anomalous movements
                    mouse_anomaly_groups = self._group_consecutive_indices(mouse_anomalous_indices)
                    
                    for group in mouse_anomaly_groups[:2]:  # Limit to top 2 groups
                        group_df = mouse_positions_df.iloc[group]
                        mouse_anomaly_type = self._classify_mouse_anomaly(group_df)
                        
                        anomaly_details.append({
                            "type": "mouse_anomaly",
                            "subtype": mouse_anomaly_type["type"],
                            "description": mouse_anomaly_type["description"],
                            "severity": mouse_anomaly_type["severity"],
                            "timestamp_start": group_df['timestamp'].min(),
                            "timestamp_end": group_df['timestamp'].max()
                        })
                    
                    overall_suspicion_level += min(mouse_anomalies / mouse_threshold, 3)
            
            # Calculate overall suspicion level (0-10 scale)
            normalized_suspicion = min(overall_suspicion_level, 10)
            
            # Generate a conclusion based on suspicion level
            conclusion = self._generate_conclusion(normalized_suspicion, anomaly_details)
            
            # Generate suspicion category
            suspicion_category = "normal"
            if normalized_suspicion >= 7:
                suspicion_category = "high_suspicion"
            elif normalized_suspicion >= 4:
                suspicion_category = "moderate_suspicion"
            elif normalized_suspicion >= 2:
                suspicion_category = "low_suspicion"
            
            return {
                "result": suspicion_category,
                "suspicion_level": float(normalized_suspicion),
                "conclusion": conclusion,
                "anomaly_details": anomaly_details,
                "metrics": anomaly_scores,
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_conclusion(self, suspicion_level, anomalies):
        """Generate a human-readable conclusion from the analysis"""
        if suspicion_level < 2:
            return "Behavior appears normal and consistent with baseline patterns."
        
        conclusion = []
        
        # Categorize anomalies by type
        anomaly_types = {}
        for anomaly in anomalies:
            type_key = anomaly["type"]
            if type_key not in anomaly_types:
                anomaly_types[type_key] = []
            anomaly_types[type_key].append(anomaly)
        
        # Generate conclusion for each type
        if "keystroke_anomaly" in anomaly_types:
            conclusion.append("Typing patterns show significant deviations from baseline.")
        
        if "typing_consistency" in anomaly_types:
            conclusion.append("Typing rhythm is unusually inconsistent.")
        
        if "typing_speed" in anomaly_types:
            conclusion.append("Typing speed differs notably from baseline patterns.")
        
        if "typing_pauses" in anomaly_types:
            conclusion.append("Unusual pauses detected during typing that may indicate consultation of external resources.")
                
        if "digraph_patterns" in anomaly_types:
            conclusion.append("Common letter combinations typed with timing significantly different from baseline.")
        
        if "mouse_anomaly" in anomaly_types:
            conclusion.append("Mouse movement patterns show abnormal behaviors.")
        if "copy_paste" in anomaly_types:
            conclusion.append("Copy and paste operations detected, which may indicate unauthorized content transfer.")
        
        # Overall assessment
        if suspicion_level >= 7:
            conclusion.append("Overall behavior is highly inconsistent with baseline and suggests potential impersonation or cheating.")
        elif suspicion_level >= 4:
            conclusion.append("Several behavioral inconsistencies detected that warrant further investigation.")
        else:
            conclusion.append("Minor behavioral inconsistencies detected, but may be due to normal variations.")
        
        return " ".join(conclusion)
    
    def _group_consecutive_indices(self, indices):
        """Group consecutive indices into separate lists"""
        if len(indices) == 0:
            return []
            
        groups = []
        current_group = [indices[0]]
        
        for i in range(1, len(indices)):
            if indices[i] == indices[i-1] + 1:
                current_group.append(indices[i])
            else:
                groups.append(current_group)
                current_group = [indices[i]]
        
        groups.append(current_group)
        return groups
    
    def _classify_keystroke_anomaly(self, anomaly_df):
        """Classify the type of keystroke anomaly"""
        # Calculate metrics
        hold_times = anomaly_df['hold_time']
        flight_times = anomaly_df['flight_time'].dropna()
        
        avg_hold_time = hold_times.mean()
        avg_flight_time = flight_times.mean() if not flight_times.empty else 0
        
        baseline_hold = self.user_profile['avg_hold_time']
        baseline_flight = self.user_profile['avg_flight_time']
        
        # Compare with baseline
        hold_ratio = avg_hold_time / baseline_hold if baseline_hold > 0 else 1
        flight_ratio = avg_flight_time / baseline_flight if baseline_flight > 0 else 1
        
        # Determine severity (1-10)
        severity = min(int(max(abs(hold_ratio - 1), abs(flight_ratio - 1)) * 5), 10)
        
        # Classify type
        if hold_ratio > 1.5:
            return {
                "type": "long_key_holds",
                "description": f"Keys held down {hold_ratio:.1f}x longer than baseline",
                "severity": severity
            }
        elif hold_ratio < 0.6:
            return {
                "type": "short_key_holds",
                "description": f"Keys released {1/hold_ratio:.1f}x faster than baseline",
                "severity": severity
            }
        elif flight_ratio > 1.5:
            return {
                "type": "slow_transitions",
                "description": f"Transitions between keys {flight_ratio:.1f}x slower than baseline",
                "severity": severity
            }
        elif flight_ratio < 0.6:
            return {
                "type": "fast_transitions",
                "description": f"Transitions between keys {1/flight_ratio:.1f}x faster than baseline",
                "severity": severity
            }
        else:
            return {
                "type": "rhythm_disruption",
                "description": "Significant change in typing rhythm",
                "severity": severity
            }
    
    def _classify_mouse_anomaly(self, anomaly_df):
        """Classify the type of mouse movement anomaly"""
        # Calculate metrics
        velocities = anomaly_df['velocity_magnitude']
        avg_velocity = velocities.mean()
        
        baseline_velocity = self.user_profile['mouse_movement_speed']
        
        # Compare with baseline
        velocity_ratio = avg_velocity / baseline_velocity if baseline_velocity > 0 else 1
        
        # Check for straight line movements
        has_straight_lines = False
        if len(anomaly_df) > 5:
            x_values = anomaly_df['x'].values
            y_values = anomaly_df['y'].values
            
            if len(x_values) > 5:
                # Check if points roughly fall on a line
                x_corr = np.corrcoef(np.arange(len(x_values)), x_values)[0, 1]
                y_corr = np.corrcoef(np.arange(len(y_values)), y_values)[0, 1]
                
                has_straight_lines = abs(x_corr) > 0.95 or abs(y_corr) > 0.95
        
        # Determine severity (1-10)
        if has_straight_lines:
            severity = 8
        else:
            severity = min(int(abs(velocity_ratio - 1) * 5), 10)
        
        # Classify type
        if has_straight_lines:
            return {
                "type": "unnatural_trajectory",
                "description": "Mouse movements follow unnaturally straight lines",
                "severity": severity
            }
        elif velocity_ratio > 1.5:
            return {
                "type": "fast_movement",
                "description": f"Mouse movements {velocity_ratio:.1f}x faster than baseline",
                "severity": severity
            }
        elif velocity_ratio < 0.6:
            return {
                "type": "slow_movement",
                "description": f"Mouse movements {1/velocity_ratio:.1f}x slower than baseline",
                "severity": severity
            }
        else:
            return {
                "type": "irregular_movement",
                "description": "Mouse movement pattern significantly different from baseline",
                "severity": severity
            }
    
    def detect_inactivity(self, threshold_seconds=30):
        """Check if the user has been inactive for longer than the threshold"""
        current_time = time.time()
        inactive_time = current_time - self.last_activity_time
        
        return inactive_time > threshold_seconds
    
    def save_results(self, results, filename=None):
        """Save the analysis results to a JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proctor_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
            
        print(f"Results saved to {filename}")
        return filename
    
    def visualize_results(self, results):
        """Generate visualizations of the analysis results"""
        if not results or 'anomaly_details' not in results:
            return None
            
        # Create a figure with multiple subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Suspicion level gauge
        suspicion_level = results.get('suspicion_level', 0)
        axs[0, 0].pie([suspicion_level, 10-suspicion_level], 
                     labels=['', ''], 
                     colors=['red', 'lightgray'],
                     startangle=90,
                     counterclock=False)
        axs[0, 0].add_artist(plt.Circle((0, 0), 0.6, color='white'))
        axs[0, 0].text(0, 0, f"{suspicion_level:.1f}/10", 
                      horizontalalignment='center',
                      verticalalignment='center', 
                      fontsize=20)
        axs[0, 0].set_title('Overall Suspicion Level')
        
        # Plot 2: Anomaly types
        anomaly_counts = {}
        for anomaly in results['anomaly_details']:
            anomaly_type = anomaly['type']
            if anomaly_type not in anomaly_counts:
                anomaly_counts[anomaly_type] = 0
            anomaly_counts[anomaly_type] += 1
        
        if anomaly_counts:
            labels = list(anomaly_counts.keys())
            values = list(anomaly_counts.values())
            axs[0, 1].bar(labels, values, color='skyblue')
            axs[0, 1].set_title('Anomaly Types Detected')
            axs[0, 1].set_xticklabels(labels, rotation=45, ha='right')
            
        # Plot 3: Anomaly severity
        severities = [a['severity'] for a in results['anomaly_details'] if 'severity' in a]
        if severities:
            axs[1, 0].hist(severities, bins=range(1, 12), color='orange', edgecolor='black')
            axs[1, 0].set_title('Anomaly Severity Distribution')
            axs[1, 0].set_xlabel('Severity (1-10)')
            axs[1, 0].set_ylabel('Count')
            axs[1, 0].set_xticks(range(1, 11))
            
        # Plot 4: Metrics
        if 'metrics' in results:
            metrics = results['metrics']
            metric_names = list(metrics.keys())
            metric_values = list(metrics.values())
            
            y_pos = range(len(metric_names))
            axs[1, 1].barh(y_pos, metric_values, color='lightgreen')
            axs[1, 1].set_yticks(y_pos)
            axs[1, 1].set_yticklabels(metric_names)
            axs[1, 1].set_title('Anomaly Metrics')
            axs[1, 1].invert_yaxis()  # labels read top-to-bottom
        
        plt.tight_layout()
        
        # Convert plot to base64 for embedding in reports
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_str
    
    def generate_report(self, results):
        """Generate a detailed HTML report of the analysis results"""
        if not results:
            return "No results to report."
            
        # Generate visualizations
        viz_img = self.visualize_results(results)
        
        # Start building HTML
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Proctor Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .summary { background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .summary.high { background-color: #ffebee; }
                .summary.moderate { background-color: #fff8e1; }
                .summary.low { background-color: #e8f5e9; }
                .anomaly { margin-bottom: 15px; padding: 15px; border-left: 4px solid #2196F3; background-color: #f5f5f5; }
                .severity { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; }
                .severity.high { background-color: #f44336; color: white; }
                .severity.medium { background-color: #ff9800; color: white; }
                .severity.low { background-color: #4caf50; color: white; }
                .viz-container { text-align: center; margin: 30px 0; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Proctor Analysis Report</h1>
                    <p>Generated on: """ + results.get('timestamp', datetime.now().isoformat()) + """</p>
                </div>
        """
        
        # Add summary section
        suspicion_level = results.get('suspicion_level', 0)
        suspicion_class = "high" if suspicion_level >= 7 else "moderate" if suspicion_level >= 4 else "low"
        
        html += f"""
                <div class="summary {suspicion_class}">
                    <h2>Analysis Summary</h2>
                    <p><strong>Suspicion Level:</strong> {suspicion_level:.1f}/10</p>
                    <p><strong>Result:</strong> {results.get('result', 'Unknown').replace('_', ' ').title()}</p>
                    <p><strong>Conclusion:</strong> {results.get('conclusion', 'No conclusion available.')}</p>
                </div>
        """
        
        # Add visualization if available
        if viz_img:
            html += f"""
                <div class="viz-container">
                    <h2>Visualization</h2>
                    <img src="data:image/png;base64,{viz_img}" alt="Analysis Visualization" style="max-width: 100%;">
                </div>
            """
        
        # Add anomaly details
        if 'anomaly_details' in results and results['anomaly_details']:
            html += """
                <h2>Detected Anomalies</h2>
            """
            
            for anomaly in results['anomaly_details']:
                severity = anomaly.get('severity', 0)
                severity_class = "high" if severity >= 7 else "medium" if severity >= 4 else "low"
                
                html += f"""
                <div class="anomaly">
                    <h3>{anomaly.get('type', '').replace('_', ' ').title()}: {anomaly.get('subtype', '').replace('_', ' ').title()}</h3>
                    <p>{anomaly.get('description', 'No description available.')}</p>
                    <p><span class="severity {severity_class}">Severity: {severity}/10</span></p>
                """
                
                # Add timestamps if available
                if 'timestamp_start' in anomaly and 'timestamp_end' in anomaly:
                    start = datetime.fromtimestamp(anomaly['timestamp_start']).strftime('%H:%M:%S')
                    end = datetime.fromtimestamp(anomaly['timestamp_end']).strftime('%H:%M:%S')
                    html += f"<p>Time Range: {start} to {end}</p>"
                
                # Add affected keys if available
                if 'affected_keys' in anomaly:
                    html += f"<p>Affected Keys: {', '.join(anomaly['affected_keys'])}</p>"
                
                html += "</div>"
        
        # Add metrics table
        if 'metrics' in results and results['metrics']:
            html += """
                <h2>Analysis Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
            """
            
            for metric, value in results['metrics'].items():
                html += f"""
                    <tr>
                        <td>{metric.replace('_', ' ').title()}</td>
                        <td>{value}</td>
                    </tr>
                """
            
            html += "</table>"
        
        # Close HTML tags
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def save_report(self, results, filename=None):
        """Generate and save an HTML report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proctor_report_{timestamp}.html"
        
        html_report = self.generate_report(results)
        
        with open(filename, 'w') as f:
            f.write(html_report)
            
        print(f"Report saved to {filename}")
        return filename
    def get_baseline_status(self):
        """Return if baseline has been collected"""
        has_baseline = hasattr(self, 'baseline_keystroke_data') and self.baseline_keystroke_data is not None
        return {
            "baseline_collected": has_baseline,
            "keystroke_count": len(self.baseline_keystroke_data) if has_baseline else 0
        }

    def get_current_metrics(self):
        """Return current metrics that could be displayed during testing"""
        with self.data_lock:
            return {
                "keystroke_count": len(self.keystroke_data),
                "mouse_movement_count": len(self.mouse_positions),
                "mouse_click_count": len(self.mouse_clicks),
                "focus_changes": len(self.focus_events),
                "copy_paste_events": len(self.copy_paste_events)
            }

# Example usage:
if __name__ == "__main__":
    # Create instance
    proctor = ProctorSystem()
    
    # Set sensitivity (1-10, higher = more sensitive to anomalies)
    proctor.set_sensitivity(5)
    
    # Collect baseline data until Enter is pressed
    print("First, we'll collect baseline data for your normal typing patterns.")
    print("Please type naturally and press Enter when you want to finish baseline collection.")
    proctor.start_baseline_collection()
    
    try:
        input("Press Enter to stop baseline collection...")
    except KeyboardInterrupt:
        print("\nBaseline collection interrupted!")
    
    baseline_result = proctor.stop_baseline_collection()
    print(f"Baseline collection complete! Collected {baseline_result['data_points']} data points.")
    
    # Start the actual test
    print("\nNow starting the actual test.")
    print("Please continue with the test or assessment as normal.")
    proctor.start_test()
    
    # In a real application, you would let the test run for its duration
    # For demonstration, we'll just wait for a short time
    try:
        input("\nPress Enter when you want to end the test...")
    except KeyboardInterrupt:
        print("\nTest interrupted!")
    
    # End test and analyze results
    print("\nAnalyzing results...")
    results = proctor.end_test()
    
    # Save results
    results_file = proctor.save_results(results)
    print(f"Results saved to {results_file}")
    
    # Generate and save report
    report_file = proctor.save_report(results)
    print(f"HTML report saved to {report_file}")
    
    # Print summary to console
    print("\nTest Analysis Summary:")
    print(f"Suspicion Level: {results['suspicion_level']:.1f}/10")
    print(f"Result: {results['result'].replace('_', ' ').title()}")
    print(f"Conclusion: {results['conclusion']}")