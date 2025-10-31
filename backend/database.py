import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

class Database:
    def __init__(self, db_path: str = "storage/doggobot.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                timestamp REAL NOT NULL,
                status TEXT NOT NULL,
                identity TEXT,
                confidence REAL,
                angle REAL,
                distance REAL,
                snapshot_path TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                meta TEXT
            )
        """)
        
        # Create whitelist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                sample_images TEXT,
                enc_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL
            )
        """)
        
        # Create index for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged)")
        
        conn.commit()
        conn.close()
    
    def insert_alert(self, alert_data: Dict[str, Any]) -> str:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        alert_id = alert_data.get('id', f"alert_{int(datetime.now().timestamp() * 1000)}")
        
        cursor.execute("""
            INSERT INTO alerts (id, timestamp, status, identity, confidence, angle, distance, snapshot_path, acknowledged, meta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_id,
            alert_data.get('timestamp', datetime.now().timestamp()),
            alert_data.get('status', 'unknown'),
            alert_data.get('identity'),
            alert_data.get('confidence'),
            alert_data.get('angle'),
            alert_data.get('distance'),
            alert_data.get('snapshot_path'),
            False,
            json.dumps(alert_data.get('meta', {}))
        ))
        
        conn.commit()
        conn.close()
        return alert_id
    
    def get_alerts(self, limit: int = 20, offset: int = 0, status: Optional[str] = None, acknowledged: Optional[bool] = None) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM alerts WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if acknowledged is not None:
            query += " AND acknowledged = ?"
            params.append(1 if acknowledged else 0)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            alert = dict(row)
            if alert['meta']:
                alert['meta'] = json.loads(alert['meta'])
            alerts.append(alert)
        
        return alerts
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            alert = dict(row)
            if alert['meta']:
                alert['meta'] = json.loads(alert['meta'])
            return alert
        return None
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    def add_whitelist_person(self, name: str, sample_images: List[str]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO whitelist (name, sample_images, enc_count, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, json.dumps(sample_images), len(sample_images), datetime.now().timestamp()))
        
        conn.commit()
        person_id = cursor.lastrowid
        conn.close()
        
        return person_id
    
    def get_whitelist(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM whitelist ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        whitelist = []
        for row in rows:
            person = dict(row)
            if person['sample_images']:
                person['sample_images'] = json.loads(person['sample_images'])
            whitelist.append(person)
        
        return whitelist
    
    def delete_old_alerts(self, before_timestamp: float) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (before_timestamp,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        
        return deleted
