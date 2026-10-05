import sqlite3
import torch
from datetime import datetime, timedelta

class SystemMaintenanceEngine:
    """تفريغ الـ VRAM وتنظيف قاعدة البيانات ومسارات Tor"""
    def __init__(self, db_path: str = "system_state.db"):
        self.db_path = db_path

    def clear_gpu_cache(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("[Maintenance]: تم تنظيف ذاكرة الـ GPU VRAM بنجاح.")

    def purge_old_logs(self, days_to_keep: int = 7):
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_to_keep)).isoformat()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM system_logs WHERE timestamp < ?", (cutoff_date,))
            cursor.execute("VACUUM")
            conn.commit()
            conn.close()
            print(f"[Maintenance]: تم حذف السجلات الأقدم من {days_to_keep} أيام.")
        except Exception as e:
            print(f"[Maintenance Error]: {e}")

    def run_full_maintenance_cycle(self):
        self.clear_gpu_cache()
        self.purge_old_logs()

if __name__ == "__main__":
    engine = SystemMaintenanceEngine()
    engine.run_full_maintenance_cycle()
