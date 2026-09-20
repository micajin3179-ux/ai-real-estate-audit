"""Lead + call persistence.

Production: PostgreSQL via DATABASE_URL (Render provides this automatically).
Local dev: SQLite fallback when DATABASE_URL is not set.
"""

import os
from datetime import datetime
from pathlib import Path

import aiosqlite
from databases import Database

DB_PATH = Path(__file__).parent / "leads.db"
DATABASE_URL = os.getenv("DATABASE_URL")

# Databases library expects postgresql://, but Render often gives postgres://.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_db: Database | None = None


async def _get_db():
    global _db
    if _db is None:
        if DATABASE_URL:
            _db = Database(DATABASE_URL)
            await _db.connect()
        else:
            _db = Database(f"sqlite+aiosqlite:///{DB_PATH}")
            await _db.connect()
    return _db


async def init_db():
    db = await _get_db()

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            agency TEXT,
            role TEXT,
            interest TEXT,
            source TEXT DEFAULT 'demo',
            status TEXT DEFAULT 'new',
            qualified INTEGER DEFAULT 0,
            notes TEXT,
            call_transcript TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        if DATABASE_URL else
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            agency TEXT,
            role TEXT,
            interest TEXT,
            source TEXT DEFAULT 'demo',
            status TEXT DEFAULT 'new',
            qualified INTEGER DEFAULT 0,
            notes TEXT,
            call_transcript TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS calls (
            id SERIAL PRIMARY KEY,
            lead_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            transcript TEXT,
            summary TEXT,
            outcome TEXT,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
        """
        if DATABASE_URL else
        """
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            transcript TEXT,
            summary TEXT,
            outcome TEXT,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
        """
    )


def _now():
    return datetime.utcnow().isoformat()


async def create_lead(name, phone, email=None, agency=None, role=None, interest=None, source='demo'):
    db = await _get_db()
    now = _now()
    if DATABASE_URL:
        query = """
            INSERT INTO leads (name, phone, email, agency, role, interest, source, status, created_at, updated_at)
            VALUES (:name, :phone, :email, :agency, :role, :interest, :source, 'new', :created_at, :updated_at)
            RETURNING id
        """
        row = await db.fetch_one(query, {
            "name": name, "phone": phone, "email": email, "agency": agency,
            "role": role, "interest": interest, "source": source,
            "created_at": now, "updated_at": now,
        })
        return await get_lead(row["id"])
    else:
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                INSERT INTO leads (name, phone, email, agency, role, interest, source, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
                """,
                (name, phone, email, agency, role, interest, source, now, now)
            )
            await conn.commit()
            return await get_lead(cursor.lastrowid)


async def get_lead(lead_id):
    db = await _get_db()
    row = await db.fetch_one("SELECT * FROM leads WHERE id = :id", {"id": lead_id})
    return dict(row) if row else None


async def get_leads(limit=100, offset=0):
    db = await _get_db()
    rows = await db.fetch_all(
        "SELECT * FROM leads ORDER BY created_at DESC LIMIT :limit OFFSET :offset",
        {"limit": limit, "offset": offset},
    )
    return [dict(row) for row in rows]


async def update_lead_status(lead_id, status, qualified=None, notes=None, call_transcript=None):
    db = await _get_db()
    now = _now()
    if DATABASE_URL:
        await db.execute(
            """
            UPDATE leads
            SET status = :status, updated_at = :updated_at,
                qualified = COALESCE(:qualified, qualified),
                notes = COALESCE(:notes, notes),
                call_transcript = COALESCE(:call_transcript, call_transcript)
            WHERE id = :id
            """,
            {
                "status": status, "updated_at": now, "id": lead_id,
                "qualified": 1 if qualified else None if qualified is None else 0,
                "notes": notes, "call_transcript": call_transcript,
            },
        )
    else:
        async with aiosqlite.connect(DB_PATH) as conn:
            params = [status, now]
            sets = ["status = ?", "updated_at = ?"]
            if qualified is not None:
                sets.append("qualified = ?")
                params.append(1 if qualified else 0)
            if notes is not None:
                sets.append("notes = ?")
                params.append(notes)
            if call_transcript is not None:
                sets.append("call_transcript = ?")
                params.append(call_transcript)
            params.append(lead_id)
            query = f"UPDATE leads SET {', '.join(sets)} WHERE id = ?"
            await conn.execute(query, params)
            await conn.commit()
    return await get_lead(lead_id)


async def create_call(lead_id, status='pending', transcript=None, summary=None, outcome=None):
    db = await _get_db()
    now = _now()
    if DATABASE_URL:
        query = """
            INSERT INTO calls (lead_id, status, transcript, summary, outcome, started_at)
            VALUES (:lead_id, :status, :transcript, :summary, :outcome, :started_at)
            RETURNING id
        """
        row = await db.fetch_one(query, {
            "lead_id": lead_id, "status": status, "transcript": transcript,
            "summary": summary, "outcome": outcome, "started_at": now,
        })
        return await get_call(row["id"])
    else:
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(
                """
                INSERT INTO calls (lead_id, status, transcript, summary, outcome, started_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (lead_id, status, transcript, summary, outcome, now)
            )
            await conn.commit()
            return await get_call(cursor.lastrowid)


async def get_call(call_id):
    db = await _get_db()
    row = await db.fetch_one("SELECT * FROM calls WHERE id = :id", {"id": call_id})
    return dict(row) if row else None


async def get_calls_for_lead(lead_id):
    db = await _get_db()
    rows = await db.fetch_all(
        "SELECT * FROM calls WHERE lead_id = :lead_id ORDER BY started_at DESC",
        {"lead_id": lead_id},
    )
    return [dict(row) for row in rows]


async def complete_call(call_id, transcript, summary, outcome):
    db = await _get_db()
    now = _now()
    await db.execute(
        """
        UPDATE calls
        SET status = 'completed', transcript = :transcript, summary = :summary,
            outcome = :outcome, completed_at = :completed_at
        WHERE id = :id
        """,
        {"transcript": transcript, "summary": summary, "outcome": outcome, "completed_at": now, "id": call_id},
    )
    return await get_call(call_id)
