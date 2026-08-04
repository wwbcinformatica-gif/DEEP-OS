import logging
import queue
import sqlite3
import threading
from pathlib import Path
from types import TracebackType

_log = logging.getLogger("wbc.db")

_db_path: Path | None = None
_pool: queue.Queue | None = None
_pool_lock = threading.Lock()
POOL_SIZE = 5


class PooledConnection:
    """Wraps sqlite3.Connection e devolve ao pool no close()."""

    def __init__(self, conn: sqlite3.Connection, pool: queue.Queue):
        self._conn = conn
        self._pool = pool
        self._closed = False

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        if not self._closed:
            self._closed = True
            self._conn.rollback()
            self._pool.put(self._conn)

    def __enter__(self) -> "PooledConnection":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        self.close()


def set_db_path(path: Path):
    global _db_path, _pool
    _db_path = path
    _init_pool()


def _init_pool():
    global _pool
    if _db_path is None:
        return
    with _pool_lock:
        if _pool is not None:
            return
        _pool = queue.Queue(maxsize=POOL_SIZE)
        for _ in range(POOL_SIZE):
            conn = sqlite3.connect(str(_db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA foreign_keys=ON")
            _pool.put(conn)
    _log.info("Pool SQLite inicializado com %d conexões", POOL_SIZE)


def get_conn() -> PooledConnection:
    if _pool is None:
        raise RuntimeError("Pool não inicializado. Chame set_db_path() primeiro.")
    conn = _pool.get()
    return PooledConnection(conn, _pool)


def init_db():
    conn = get_conn()
    with conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            approved BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS task_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT UNIQUE NOT NULL,
            messages TEXT NOT NULL,
            tool_logs TEXT NOT NULL,
            system_prompt TEXT NOT NULL,
            step INTEGER DEFAULT 0,
            max_steps INTEGER DEFAULT 100,
            context TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS brain_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            importance REAL DEFAULT 0.5,
            access_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
    _log.info("Banco de dados inicializado em %s", _db_path)
