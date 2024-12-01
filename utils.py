# utils.py
import os
from datetime import datetime

def generate_conversation_title(first_message: str) -> str:
    """根据第一条消息生成对话标题"""
    # 取消息的前20个字符作为标题
    title = first_message[:20].strip()
    if len(first_message) > 20:
        title += "..."
    return title

def format_timestamp(timestamp: str) -> str:
    """格式化时间戳为易读格式"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def ensure_directory(directory: str):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_export_path(base_dir: str, conversation_id: int) -> str:
    """生成导出文件路径"""
    ensure_directory(base_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base_dir, f"conversation_{conversation_id}_{timestamp}.json")