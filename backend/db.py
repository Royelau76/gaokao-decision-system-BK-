"""
共享数据库工具模块 - 统一数据库路径和连接管理
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'data')


def get_db_path():
    """统一的数据库文件路径"""
    os.makedirs(DB_DIR, exist_ok=True)
    return os.path.join(DB_DIR, 'gaokao.db')


def get_connection():
    """获取数据库连接（带 row_factory 设置）"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn
