import sqlite3
from pathlib import Path
from datetime import datetime

class ClipboardStorage:
    def __init__(self):
        self.db_path = "clipboard.db"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clipboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip_address TEXT,
                hostname TEXT,
                content TEXT
            )
        """)
        self.conn.commit()

    def insert_data(self, content, ip_address, hostname):
        timestamp = datetime.now().isoformat()
        self.cursor.execute(
            "INSERT INTO clipboard (timestamp, ip_address, hostname, content) VALUES (?, ?, ?, ?)",
            (timestamp, ip_address, hostname, content)
        )
        self.conn.commit()

    def get_entries(self):
        self.cursor.execute("SELECT * FROM clipboard ORDER BY timestamp DESC")
        entries = self.cursor.fetchall()
        return [{
            "id": entry[0],
            "timestamp": entry[1],
            "caller": {
                "ip": entry[2],
                "hostname": entry[3]
            },
            "content": entry[4]
        } for entry in entries]
