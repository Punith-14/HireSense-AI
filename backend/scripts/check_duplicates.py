"""One-off maintenance script: check (and optionally clean) duplicate rows
before the new unique indexes are built.

The new schema declares unique indexes on:
  - Interview.session   (one interview per session)
  - Report.interview    (one report per interview)

MongoDB refuses to build a unique index if duplicates already exist. This
script finds them and, on request, removes the extras (keeping the newest) or
drops the interview-related collections entirely for a clean rebuild.

It talks to MongoDB directly with pymongo (no mongoengine), so it never triggers
the index build itself.

Usage (from the backend/ folder, using the project's Python):
    ..\\venv\\Scripts\\python.exe scripts\\check_duplicates.py            # report only (safe)
    ..\\venv\\Scripts\\python.exe scripts\\check_duplicates.py --fix      # delete older duplicates, keep newest
    ..\\venv\\Scripts\\python.exe scripts\\check_duplicates.py --drop     # drop sessions/interviews/reports collections
"""

import argparse
import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def resolve_settings():
    """Mirror config/db.py so we hit the same database as the app."""
    load_dotenv()
    db_name = os.getenv("MONGO_DB_NAME") or os.getenv("MONGODB_DB_NAME") or "hiresense_ai"
    uri = (
        os.getenv("MONGO_URI")
        or os.getenv("MONGODB_URI")
        or f"mongodb://localhost:27017/{db_name}"
    )
    timeout_ms = int(
        os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS")
        or os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS")
        or "3000"
    )
    return uri, db_name, timeout_ms


def find_duplicate_groups(collection, field):
    """Return groups of documents that share the same value for `field`."""
    pipeline = [
        {"$match": {field: {"$ne": None}}},
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    return list(collection.aggregate(pipeline))


def newest_first(collection, ids):
    """Order the given ids newest-first by created_at (fallback: _id)."""
    docs = list(collection.find({"_id": {"$in": ids}}, {"created_at": 1}))
    docs.sort(key=lambda d: (d.get("created_at") is not None, d.get("created_at"), d["_id"]), reverse=True)
    return [d["_id"] for d in docs]


def report_and_maybe_fix(db, label, coll_name, field, do_fix):
    collection = db[coll_name]
    groups = find_duplicate_groups(collection, field)

    if not groups:
        print(f"  [OK] {label}: no duplicates ({coll_name} by '{field}').")
        return 0

    total_extra = sum(g["count"] - 1 for g in groups)
    print(f"  [!!] {label}: {len(groups)} '{field}' value(s) have duplicates, {total_extra} extra doc(s).")

    removed = 0
    for group in groups:
        ordered = newest_first(collection, group["ids"])
        keep, extras = ordered[0], ordered[1:]
        print(f"       {field}={group['_id']}: keep {keep}, extras {extras}")
        if do_fix and extras:
            result = collection.delete_many({"_id": {"$in": extras}})
            removed += result.deleted_count

    if do_fix:
        print(f"       -> removed {removed} duplicate doc(s) from {coll_name}.")
    return total_extra


def main():
    parser = argparse.ArgumentParser(description="Check/clean duplicate interview & report rows.")
    parser.add_argument("--fix", action="store_true", help="Delete older duplicates, keeping the newest per group.")
    parser.add_argument("--drop", action="store_true", help="Drop sessions/interviews/reports collections entirely.")
    args = parser.parse_args()

    uri, db_name, timeout_ms = resolve_settings()
    print(f"Connecting to MongoDB db='{db_name}' ...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms, uuidRepresentation="standard")
        client.admin.command("ping")
    except PyMongoError as exc:
        print(f"ERROR: could not connect to MongoDB: {exc}")
        sys.exit(1)

    db = client[db_name]

    if args.drop:
        confirm = input("This DROPS the 'sessions', 'interviews', and 'reports' collections. Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            return
        for name in ("sessions", "interviews", "reports"):
            db[name].drop()
            print(f"  dropped collection '{name}'.")
        print("Done. The app will recreate the collections and unique indexes on next startup.")
        return

    print("\nScanning for duplicates:")
    extra = 0
    extra += report_and_maybe_fix(db, "Interviews per session", "interviews", "session", args.fix)
    extra += report_and_maybe_fix(db, "Reports per interview", "reports", "interview", args.fix)

    print()
    if extra == 0:
        print("All clear. The new unique indexes will build cleanly on next startup.")
    elif args.fix:
        print("Duplicates removed. Re-run without --fix to confirm everything is clean, then start the server.")
    else:
        print("Duplicates found. Re-run with --fix to remove the older copies (keeps the newest),")
        print("or with --drop to wipe the interview collections for a fresh start.")


if __name__ == "__main__":
    main()
