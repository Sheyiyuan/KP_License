import sqlite3
import os
from typing import Optional, List, Tuple, Any

class DB:
    def __init__(self, db_path: str = "data/database/", file: str = "database.db"):
        self.db_path = db_path
        # 确保数据库目录存在
        os.makedirs(self.db_path, exist_ok=True)

        try:
            self.conn = sqlite3.connect(os.path.join(self.db_path, file))
            self.cursor = self.conn.cursor()
            self.init_db_option()
        except Exception as e:
            raise RuntimeError(f"数据库连接失败: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def init_db_option(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    lid TEXT PRIMARY KEY,
                    license_type TEXT NOT NULL,
                    info TEXT,
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"初始化数据库失败: {str(e)}")

    def add_record(self, lid: str, license_type: str, info: str, time: str) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO records (lid, license_type, info, time) VALUES (?,?,?,?)",
                (lid, license_type, info, time)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise RuntimeError(f"添加记录失败: {str(e)}")

    def get_record(self, lid: str) -> Optional[Tuple[Any, ...]]:
        try:
            self.cursor.execute("SELECT * FROM records WHERE lid=?", (lid,))
            return self.cursor.fetchone()
        except Exception as e:
            raise RuntimeError(f"查询记录失败: {str(e)}")

    def get_all_records(self) -> List[Tuple[Any, ...]]:
        try:
            self.cursor.execute("SELECT * FROM records")
            return self.cursor.fetchall()
        except Exception as e:
            raise RuntimeError(f"查询所有记录失败: {str(e)}")