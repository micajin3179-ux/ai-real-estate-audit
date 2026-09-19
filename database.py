import aiosqlite
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "leads.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
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
        """)
        await db.execute("""
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
        """)
        await db.commit()


async def create_lead(name, phone, email=None, agency=None, role=None, interest=None, source='demo'):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            INSERT INTO leads (name, phone, email, agency, role, interest, source, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)
            """,
            (name, phone, email, agency, role, interest, source, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
        )
        await db.commit()
        lead_id = cursor.lastrowid
        return await get_lead(lead_id)


async def get_lead(lead_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_leads(limit=100, offset=0):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM leads ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def update_lead_status(lead_id, status, qualified=None, notes=None, call_transcript=None):
    async with aiosqlite.connect(DB_PATH) as db:
        params = [status, datetime.utcnow().isoformat()]
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
        await db.execute(query, params)
        await db.commit()
        return await get_lead(lead_id)


async def create_call(lead_id, status='pending', transcript=None, summary=None, outcome=None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            INSERT INTO calls (lead_id, status, transcript, summary, outcome, started_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (lead_id, status, transcript, summary, outcome, datetime.utcnow().isoformat())
        )
        await db.commit()
        call_id = cursor.lastrowid
        return await get_call(call_id)


async def get_call(call_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM calls WHERE id = ?", (call_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_calls_for_lead(lead_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM calls WHERE lead_id = ? ORDER BY started_at DESC",
            (lead_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def complete_call(call_id, transcript, summary, outcome):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE calls
            SET status = 'completed', transcript = ?, summary = ?, outcome = ?, completed_at = ?
            WHERE id = ?
            """,
            (transcript, summary, outcome, datetime.utcnow().isoformat(), call_id)
        )
        await db.commit()
        return await get_call(call_id)