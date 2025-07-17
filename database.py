### database.py
### SQLiteデータベースを操作して、セッションデータを永続化します。

import sqlite3
from datetime import datetime

# データベースファイル名
DB_FILE = "transcription_library.db"

def get_db_connection():
    """データベース接続を取得します。"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # カラム名でアクセスできるようにする
    return conn

def init_db():
    """
    データベースとテーブルを初期化します。
    テーブルがまだ存在しない場合にのみ作成されます。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        topic TEXT,
        transcription TEXT,
        summary TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("データベースが初期化されました。")

def add_session(topic, transcription, summary):
    """
    新しいセッション（文字起こしと要約のセット）をデータベースに追加します。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO sessions (timestamp, topic, transcription, summary) VALUES (?, ?, ?, ?)",
        (timestamp, topic, transcription, summary)
    )
    conn.commit()
    conn.close()
    print(f"セッション「{topic}」が保存されました。")

def get_all_sessions():
    """
    保存されているすべてのセッションのID、タイムスタンプ、トピックを取得します。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, topic FROM sessions ORDER BY timestamp DESC")
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_session_by_id(session_id):
    """
    指定されたIDのセッション詳細（文字起こしと要約）を取得します。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    conn.close()
    return session

def delete_session_by_id(session_id):
    """
    指定されたIDのセッションを削除します。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    print(f"セッションID:{session_id} が削除されました。")

# ★★★ 新機能: ライブラリ横断検索 ★★★
def search_sessions(keyword):
    """
    指定されたキーワードをタイムスタンプ、トピック、文字起こし、要約から検索します。
    パフォーマンスのため、LIKE検索を使用します。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    search_term = f'%{keyword}%'
    cursor.execute("""
        SELECT id, timestamp, topic FROM sessions
        WHERE topic LIKE ? OR transcription LIKE ? OR summary LIKE ? OR timestamp LIKE ?
        ORDER BY timestamp DESC
    """, (search_term, search_term, search_term, search_term))
    sessions = cursor.fetchall()
    conn.close()
    return sessions
