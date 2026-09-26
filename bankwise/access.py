"""Server-key access gate and an atomic per-instance daily question budget."""
from contextlib import closing
from datetime import datetime, timezone
import hmac
import sqlite3
from .data import ROOT

def authorize_server_key(expected, supplied):
    if not expected or not supplied or not hmac.compare_digest(expected.encode(), supplied.encode()):
        raise ValueError('请输入正确的模型访问口令；未配置口令时服务器密钥保持禁用。')

def reserve_question(path=None, limit=30, day=None):
    """Reserve before calling API, including failed requests; resets if disk is replaced."""
    path = path or ROOT / 'data' / 'usage.db'
    day = day or datetime.now(timezone.utc).date().isoformat()
    with closing(sqlite3.connect(path, timeout=5)) as conn, conn:
        conn.execute('CREATE TABLE IF NOT EXISTS usage(day TEXT PRIMARY KEY, questions INTEGER NOT NULL)')
        conn.execute('BEGIN IMMEDIATE')
        current = conn.execute('SELECT questions FROM usage WHERE day=?', (day,)).fetchone()
        used = current[0] if current else 0
        if used >= limit:
            raise ValueError('本站今日模型提问额度已用完，请明天再试。')
        conn.execute('INSERT INTO usage VALUES (?,1) ON CONFLICT(day) DO UPDATE SET questions=questions+1', (day,))
        return used+1
