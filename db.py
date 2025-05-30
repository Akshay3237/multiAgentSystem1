import sqlite3
import json
from datetime import datetime
from threading import Lock
from typing import Optional, List, Dict, Any

DB_PATH = "shared_memory.db"
_lock = Lock()

def init_db():
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL,
            thread_id TEXT
        )
        """)
        conn.commit()
        conn.close()

def add_entry(
    source: str,
    type_: str,
    data: Dict[str, Any],
    thread_id: Optional[str] = None,
    timestamp: Optional[str] = None
) -> int:
    """
    Insert a new entry into the memory table.
    Returns the inserted row id.
    """
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        ts = timestamp or datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO memory (source, type, timestamp, data, thread_id)
            VALUES (?, ?, ?, ?, ?)
        """, (source, type_, ts, json.dumps(data), thread_id))
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id

def get_entry_by_id(entry_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a single entry by its ID.
    """
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memory WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "source": row[1],
                "type": row[2],
                "timestamp": row[3],
                "data": json.loads(row[4]),
                "thread_id": row[5]
            }
        return None

def update_entry(
    entry_id: int,
    data: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None
) -> bool:
    """
    Update data and/or thread_id for a given entry.
    Returns True if updated, False if not found.
    """
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Build update query dynamically
        updates = []
        params = []

        if data is not None:
            updates.append("data = ?")
            params.append(json.dumps(data))
        if thread_id is not None:
            updates.append("thread_id = ?")
            params.append(thread_id)
        if not updates:
            return False  # nothing to update

        params.append(entry_id)
        query = f"UPDATE memory SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        updated = cursor.rowcount > 0
        conn.close()
        return updated

def delete_entry(entry_id: int) -> bool:
    """
    Delete an entry by ID.
    Returns True if deleted, False if not found.
    """
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory WHERE id = ?", (entry_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

def list_entries(
    source: Optional[str] = None,
    type_: Optional[str] = None,
    thread_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    List entries with optional filters.
    """
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = "SELECT * FROM memory"
        filters = []
        params = []
        if source:
            filters.append("source = ?")
            params.append(source)
        if type_:
            filters.append("type = ?")
            params.append(type_)
        if thread_id:
            filters.append("thread_id = ?")
            params.append(thread_id)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "source": row[1],
                "type": row[2],
                "timestamp": row[3],
                "data": json.loads(row[4]),
                "thread_id": row[5]
            }
            for row in rows
        ]

# Initialize DB when module loads
init_db()
