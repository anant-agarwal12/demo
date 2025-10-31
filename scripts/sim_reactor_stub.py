#!/usr/bin/env python3
"""
Example simulation reactor that subscribes to DoggoBot alerts and reacts accordingly.

This script demonstrates how to:
1. Connect to the backend SSE stream
2. Listen for real-time alert events
3. React to different alert types (e.g., trigger Gazebo actions)

Usage:
    python sim_reactor_stub.py [--api-url http://localhost:8000]
"""

import requests
import json
import argparse
import time
from datetime import datetime

class SimReactor:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.alert_count = 0
        self.last_action = None
    
    def connect_sse(self):
        """Connect to SSE stream and process events"""
        print(f"?? Connecting to SSE stream: {self.api_url}/stream")
        
        try:
            response = requests.get(
                f"{self.api_url}/stream",
                stream=True,
                timeout=None,
                headers={'Accept': 'text/event-stream'}
            )
            
            if response.status_code != 200:
                print(f"? Failed to connect: {response.status_code}")
                return
            
            print("? Connected to SSE stream\n")
            
            # Process SSE events
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    # SSE format: "data: {json}"
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove "data: " prefix
                        try:
                            event = json.loads(data_str)
                            self.handle_event(event)
                        except json.JSONDecodeError:
                            print(f"??  Invalid JSON: {data_str}")
        
        except KeyboardInterrupt:
            print("\n??  Stopped by user")
        except Exception as e:
            print(f"? SSE Error: {e}")
    
    def handle_event(self, event):
        """Handle incoming SSE events"""
        event_type = event.get('type')
        
        if event_type == 'connected':
            print(f"? Connection established at {datetime.fromtimestamp(event.get('timestamp', 0))}")
        
        elif event_type == 'heartbeat':
            # Heartbeat - no action needed
            pass
        
        elif event_type == 'alert':
            self.handle_alert(event.get('alert', {}))
        
        elif event_type == 'nlp':
            self.handle_nlp(event)
        
        elif event_type == 'ack':
            alert_id = event.get('alert_id')
            print(f"? Alert acknowledged: {alert_id}")
        
        else:
            print(f"??  Unknown event type: {event_type}")
    
    def handle_alert(self, alert):
        """Handle detection alert and trigger appropriate action"""
        self.alert_count += 1
        
        alert_id = alert.get('id', 'unknown')
        status = alert.get('status', 'unknown')
        identity = alert.get('identity', 'Unknown')
        distance = alert.get('distance', 0)
        angle = alert.get('angle', 0)
        
        print(f"\n?? ALERT #{self.alert_count}: {status.upper()}")
        print(f"   ID: {alert_id}")
        print(f"   Identity: {identity}")
        print(f"   Distance: {distance:.2f}m")
        print(f"   Angle: {angle:.2f} rad ({angle * 180 / 3.14159:.1f}?)")
        
        # Determine action based on status
        if status == 'friendly':
            self.react_friendly(alert)
        elif status == 'unknown':
            self.react_unknown(alert)
        elif status == 'suspicious':
            self.react_suspicious(alert)
    
    def react_friendly(self, alert):
        """React to friendly detection"""
        identity = alert.get('identity', 'Friend')
        action = f"Wave and greet {identity}"
        print(f"   ?? Action: {action}")
        self.last_action = action
        
        # TODO: Send ROS2 command to Gazebo
        # Example: publish to /doggo/action topic
        # self.publish_ros_action('greet', target=identity)
    
    def react_unknown(self, alert):
        """React to unknown detection"""
        distance = alert.get('distance', 0)
        angle = alert.get('angle', 0)
        
        if distance < 3.0:
            action = "Approach slowly and investigate"
        else:
            action = f"Rotate {angle * 180 / 3.14159:.1f}? and observe"
        
        print(f"   ?? Action: {action}")
        self.last_action = action
        
        # TODO: Send ROS2 command to Gazebo
        # Example: publish navigation goal
        # self.publish_ros_navigation(angle, distance)
    
    def react_suspicious(self, alert):
        """React to suspicious detection"""
        action = "Sound alarm and alert operator"
        print(f"   ?? Action: {action}")
        self.last_action = action
        
        # TODO: Send ROS2 command to Gazebo
        # Example: trigger alarm animation
        # self.publish_ros_action('alarm')
    
    def handle_nlp(self, event):
        """Handle NLP command response"""
        text = event.get('text', '')
        intent = event.get('intent', 'unknown')
        action = event.get('action')
        
        print(f"\n?? NLP Response: {text}")
        if action:
            print(f"   ?? Executing action: {action}")
            self.execute_nlp_action(action, event)
    
    def execute_nlp_action(self, action, data):
        """Execute NLP-triggered action"""
        # Map NLP actions to robot behaviors
        action_map = {
            'stop_patrol': 'Stop all movement',
            'start_patrol': 'Begin patrol route',
            'return_home': 'Navigate to home position',
            'follow': 'Enter follow mode',
            'investigate': 'Approach and scan area',
            'sound_alarm': 'Activate alarm',
            'greet': 'Play greeting animation'
        }
        
        behavior = action_map.get(action, f"Unknown action: {action}")
        print(f"   ?? Behavior: {behavior}")
        
        # TODO: Implement actual ROS2 commands
        # self.publish_ros_action(action, **data)
    
    def poll_alerts(self, interval=5):
        """Alternative: Poll alerts endpoint instead of SSE"""
        print(f"?? Polling alerts every {interval} seconds")
        print("   (SSE streaming is recommended for real-time response)\n")
        
        try:
            while True:
                try:
                    response = requests.get(
                        f"{self.api_url}/alerts",
                        params={'limit': 5, 'acknowledged': False},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        alerts = data.get('alerts', [])
                        
                        if alerts:
                            print(f"\n?? Found {len(alerts)} unacknowledged alerts")
                            for alert in alerts:
                                self.handle_alert(alert)
                    
                except requests.RequestException as e:
                    print(f"??  Poll error: {e}")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n??  Stopped by user")
    
    def get_status(self):
        """Get backend health and metrics"""
        try:
            health = requests.get(f"{self.api_url}/health", timeout=5).json()
            metrics = requests.get(f"{self.api_url}/metrics", timeout=5).json()
            
            print("\n?? Backend Status:")
            print(f"   Health: {health.get('status')}")
            print(f"   Total Alerts: {metrics.get('total_alerts')}")
            print(f"   Unacknowledged: {metrics.get('unacknowledged_alerts')}")
            print(f"   SSE Clients: {metrics.get('sse_clients')}")
            print()
        except Exception as e:
            print(f"? Could not get status: {e}")

def main():
    parser = argparse.ArgumentParser(description="DoggoBot Simulation Reactor")
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='Backend API URL (default: http://localhost:8000)')
    parser.add_argument('--mode', choices=['sse', 'poll'], default='sse',
                       help='Connection mode: sse (streaming) or poll (default: sse)')
    parser.add_argument('--poll-interval', type=int, default=5,
                       help='Polling interval in seconds (default: 5)')
    
    args = parser.parse_args()
    
    reactor = SimReactor(api_url=args.api_url)
    
    # Show initial status
    reactor.get_status()
    
    # Start listening
    if args.mode == 'sse':
        reactor.connect_sse()
    else:
        reactor.poll_alerts(interval=args.poll_interval)

if __name__ == "__main__":
    main()
