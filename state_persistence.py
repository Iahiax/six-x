import sqlite3
import os
from datetime import datetime

class SystemStateManager:
    """إدارة قاعدة البيانات المحلية وحفظ حالة الصفقات والسجلات محلياً"""
    def __init__(self, db_path: str = "system_state.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الصفقات المفتوحة والمغلقة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_trades (
                deal_id TEXT PRIMARY KEY,
                epic TEXT,
                direction TEXT,
                size REAL,
                entry_price REAL,
                status TEXT,
                timestamp TEXT
            )
        ''')

        # جدول سجل الحوادث
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                timestamp TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def log_trade(self, deal_id: str, epic: str, direction: str, size: float, entry_price: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO active_trades (deal_id, epic, direction, size, entry_price, status, timestamp)
            VALUES (?, ?, ?, ?, ?, 'OPEN', ?)
        ''', (deal_id, epic, direction, size, entry_price, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

    def get_open_trades(self) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT deal_id, epic, direction, size, entry_price FROM active_trades WHERE status = 'OPEN'")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def close_trade(self, deal_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE active_trades SET status = 'CLOSED' WHERE deal_id = ?", (deal_id,))
        conn.commit()
        conn.close()

    def add_log(self, level: str, message: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO system_logs (level, message, timestamp) VALUES (?, ?, ?)",
                       (level, message, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
