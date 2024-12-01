# db_models.py
import sqlite3
from datetime import datetime
import json

class ChatDatabase:
    def __init__(self, db_path="chat_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    model TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)

    def create_conversation(self, title: str, model: str) -> int:
        """创建新的对话"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO conversations (title, model) VALUES (?, ?)",
                (title, model)
            )
            return cursor.lastrowid

    def add_message(self, conversation_id: int, role: str, content: str):
        """添加消息到对话"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content)
            )

    def get_conversation(self, conversation_id: int):
        """获取特定对话的所有消息"""
        with sqlite3.connect(self.db_path) as conn:
            # 获取对话信息
            conv = conn.execute(
                "SELECT id, title, model, created_at FROM conversations WHERE id = ?",
                (conversation_id,)
            ).fetchone()
            
            if not conv:
                return None
            
            # 获取对话的所有消息
            messages = conn.execute(
                "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at",
                (conversation_id,)
            ).fetchall()
            
            return {
                "id": conv[0],
                "title": conv[1],
                "model": conv[2],
                "created_at": conv[3],
                "messages": [{"role": m[0], "content": m[1]} for m in messages]
            }

    def get_all_conversations(self):
        """获取所有对话的基本信息"""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT id, title, model, created_at FROM conversations ORDER BY created_at DESC"
            ).fetchall()

    def delete_conversation(self, conversation_id: int):
        """删除指定的对话及其消息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))

    def export_conversation(self, conversation_id: int, file_path: str):
        """导出对话到JSON文件"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)

    def import_conversation(self, file_path: str) -> int:
        """从JSON文件导入对话"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建新对话
        conv_id = self.create_conversation(data['title'], data['model'])
        
        # 添加所有消息
        for msg in data['messages']:
            self.add_message(conv_id, msg['role'], msg['content'])
        
        return conv_id