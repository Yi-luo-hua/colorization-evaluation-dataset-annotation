"""
Append Tier 1 (4,964 samples: train/lcad remaining) directly into current running recovery5000 runtime.
Ensures zero disruption to active workers, atomic transaction, and online backup.
"""
import sqlite3
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
import sys

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT / 'scripts'))
from pipeline_store import Store

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    target_run = PROJECT / 'runtime/recovery5000_20261016_01'
    source_run = PROJECT / 'runtime/tier1_train_lcad_remaining_20261017_01'

    target_db_path = target_run / 'state.sqlite3'
    source_db_path = source_run / 'state.sqlite3'

    if not target_db_path.exists():
        print(f"Error: Target db not found at {target_db_path}")
        return 1
    if not source_db_path.exists():
        print(f"Error: Source db not found at {source_db_path}")
        return 1

    print(f"=== Step 1: Performing online safe backup of {target_db_path.name} ===")
    backup_path = target_run / f"state.sqlite3.bak_pre_tier1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with sqlite3.connect(target_db_path) as src_conn, sqlite3.connect(backup_path) as dst_conn:
        src_conn.backup(dst_conn)
    print(f"Backup created successfully: {backup_path.name} ({backup_path.stat().st_size} bytes)")

    print("=== Step 2: Reading 4,964 samples from Tier 1 ===")
    with sqlite3.connect(source_db_path) as src_conn:
        src_conn.row_factory = sqlite3.Row
        cur = src_conn.cursor()
        cur.execute("SELECT key, state, role, group_id, ready_at, body FROM samples")
        tier1_rows = [dict(r) for r in cur.fetchall()]
    print(f"Read {len(tier1_rows)} samples from source tier1.")

    # Verify no collision with existing keys in target
    with sqlite3.connect(target_db_path) as tgt_conn:
        existing_keys = set(r[0] for r in tgt_conn.execute("SELECT key FROM samples"))

    collision = [r for r in tier1_rows if r['key'] in existing_keys]
    if collision:
        print(f"CRITICAL ERROR: Found {len(collision)} colliding keys! Aborting.")
        return 1
    print("Collision check passed: 0 collisions with target database.")

    print("=== Step 3: Atomic injection into target state.sqlite3 via Store ===")
    target_store = Store(target_run)
    current_time = now_iso()

    insert_records = []
    for r in tier1_rows:
        body = json.loads(r['body'])
        # Ensure ready_at is fresh so claiming picks them up smoothly
        if r['state'] == 'secondary_chroma_ready':
            body['ready_at'] = current_time
            ready_at = current_time
        else:
            ready_at = r['ready_at']
        insert_records.append((
            r['key'],
            r['state'],
            r['role'],
            r['group_id'],
            ready_at,
            json.dumps(body, ensure_ascii=False)
        ))

    with target_store.tx() as db:
        db.executemany(
            "INSERT INTO samples(key, state, role, group_id, ready_at, body) VALUES (?, ?, ?, ?, ?, ?)",
            insert_records
        )

        # Update meta scope and state_updated_at
        scope_row = db.execute("SELECT value FROM meta WHERE key='scope'").fetchone()
        scope = json.loads(scope_row[0]) if scope_row else {}
        scope['target'] = len(existing_keys) + len(tier1_rows)
        scope['tier1_appended'] = {
            'count': len(tier1_rows),
            'appended_at': current_time,
            'source_tier': 'tier1_train_lcad_remaining_4964'
        }

        target_store.put_meta(db, 'scope', scope)
        target_store.put_meta(db, 'state_updated_at', current_time)

    print(f"=== Step 4: Verification of target database ===")
    with sqlite3.connect(target_db_path) as conn:
        counts = dict(conn.execute("SELECT state, count(*) FROM samples GROUP BY state").fetchall())
        total = conn.execute("SELECT count(*) FROM samples").fetchone()[0]

    print(f"Total samples in target database: {total}")
    for state, cnt in sorted(counts.items()):
        print(f"  - {state}: {cnt}")

    print("Append complete! Workers can now seamlessly claim the remaining train/lcad tasks.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
