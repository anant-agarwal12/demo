import re
from typing import Dict, Any
from database import Database

class NLPHandler:
    """Simple rule-based NLP command handler"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process natural language command and return structured response.
        """
        text = text.lower().strip()
        
        # Status command
        if any(keyword in text for keyword in ['status', 'report', 'what', 'how many']):
            return self._handle_status()
        
        # Stop/pause commands
        if any(keyword in text for keyword in ['stop', 'halt', 'pause']):
            return {
                'intent': 'stop',
                'text': 'Patrol stopped. Awaiting further instructions.',
                'action': 'stop_patrol'
            }
        
        # Start/resume commands
        if any(keyword in text for keyword in ['start', 'resume', 'begin', 'patrol']):
            return {
                'intent': 'start',
                'text': 'Patrol started. Monitoring for intruders.',
                'action': 'start_patrol'
            }
        
        # Follow command
        if 'follow' in text:
            return {
                'intent': 'follow',
                'text': 'Following mode activated. I will track the target.',
                'action': 'follow'
            }
        
        # Return home command
        if any(keyword in text for keyword in ['home', 'return', 'base']):
            return {
                'intent': 'return_home',
                'text': 'Returning to home position.',
                'action': 'return_home'
            }
        
        # Greet command
        if any(keyword in text for keyword in ['greet', 'hello', 'hi', 'wave']):
            return {
                'intent': 'greet',
                'text': 'Hello! I am DoggoBot, your security assistant.',
                'action': 'greet'
            }
        
        # Investigate command
        if any(keyword in text for keyword in ['investigate', 'check', 'inspect']):
            return {
                'intent': 'investigate',
                'text': 'Investigating the area. Stand by.',
                'action': 'investigate'
            }
        
        # Alarm command
        if any(keyword in text for keyword in ['alarm', 'alert', 'sound']):
            return {
                'intent': 'alarm',
                'text': 'Alarm activated!',
                'action': 'sound_alarm'
            }
        
        # Default response
        return {
            'intent': 'unknown',
            'text': 'I did not understand that command. Try: status, start, stop, investigate, or return home.',
            'action': None
        }
    
    def _handle_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            alerts = self.db.get_alerts(limit=100)
            total = len(alerts)
            unack = sum(1 for a in alerts if not a['acknowledged'])
            
            friendly = sum(1 for a in alerts if a['status'] == 'friendly')
            unknown = sum(1 for a in alerts if a['status'] == 'unknown')
            suspicious = sum(1 for a in alerts if a['status'] == 'suspicious')
            
            text = f"System status: {total} total alerts. "
            text += f"{unack} unacknowledged. "
            text += f"{friendly} friendly, {unknown} unknown, {suspicious} suspicious detections."
            
            return {
                'intent': 'status',
                'text': text,
                'action': None,
                'data': {
                    'total': total,
                    'unacknowledged': unack,
                    'friendly': friendly,
                    'unknown': unknown,
                    'suspicious': suspicious
                }
            }
        except Exception as e:
            return {
                'intent': 'status',
                'text': f'Error retrieving status: {str(e)}',
                'action': None
            }
