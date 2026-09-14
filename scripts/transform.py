"""
Phase 3 - Data Transformation (Milestone 3)
Reads raw Reddit posts from data/raw/ (Arctic Shift JSONL archives + PRAW JSON
exports), cleans them, parses intent from titles, and writes a clean dataset to
data/processed/.
"""

import os
import re
import csv
import json
from datetime import datetime, timedelta, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "..", "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "..", "data", "processed")
REFERENCE_DIR = os.path.join(BASE_DIR, "..", "data", "reference")
GAZETTEER_CSV = os.path.join(REFERENCE_DIR, "metro_manila_gazetteer.csv")
CLEAN_CSV = os.path.join(PROCESSED_DATA_DIR, "posts_clean.csv")
CLEANING_LOG = os.path.join(PROCESSED_DATA_DIR, "cleaning_log.md")

MANILA = timezone(timedelta(hours=8))

# subreddit -> posting category
CATEGORY_MAP = {
    "phr4r_2": "all",
    "phr4friends": "platonic",
    "phr4dating": "romantic",
    "dirtyphpr4r": "sexual",
}

AGE_RE = re.compile(r"(?<!\d)(\d{2})(?!\d)")
TAG_RE = re.compile(r"\[?\s*([A-Za-z]{1,3})\s*4\s*([A-Za-z]{1,3})\s*\]?", re.IGNORECASE)

OUTPUT_COLUMNS = [
    "post_id", "title", "selftext", "author", "subreddit", "category",
    "created_utc", "created_datetime_manila", "date_manila", "hour_manila",
    "day_of_week", "year", "month", "score", "num_comments",
    "seeker_age", "seeker_gender", "target_gender", "intent_tag", "city",
]


def load_gazetteer():
    # alias (lowercase) -> canonical city name, from the PSGC publication
    gazetteer = {}
    with open(os.path.join(REFERENCE_DIR, "metro_manila_gazetteer.csv"), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gazetteer[row["alias"].strip().lower()] = row["city"].strip()
    return gazetteer


def build_city_matcher(gazetteer):
    # longest aliases first so "quezon city" wins over "qc"
    aliases = sorted(gazetteer, key=len, reverse=True)
    pattern = re.compile(r"(?<![a-z0-9])(" + "|".join(re.escape(a) for a in aliases) + r")(?![a-z0-9])")
    return pattern


def extract_city(text, matcher, gazetteer):
    m = matcher.search(text.lower())
    return gazetteer[m.group(1)] if m else ""


def iter_raw_files():
    for name in sorted(os.listdir(RAW_DATA_DIR)):
        path = os.path.join(RAW_DATA_DIR, name)
        if name.endswith(".jsonl"):
            yield path, "jsonl"
        elif name.endswith(".json"):
            yield path, "json"


def load_records():
    records = []
    stats = {"files": 0, "lines": 0, "json_errors": 0}
    for path, kind in iter_raw_files():
        stats["files"] += 1
        if kind == "jsonl":
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    stats["lines"] += 1
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        stats["json_errors"] += 1
        else:
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    stats["json_errors"] += 1
                    continue
                if isinstance(data, list):
                    stats["lines"] += len(data)
                    records.extend(data)
    return records, stats


def parse_intent(title):
    age = None
    tag = None
    seeker_gender = None
    target_gender = None
    m = TAG_RE.search(title)
    if m:
        seeker_gender = m.group(1).upper()
        target_gender = m.group(2).upper()
        tag = "{}4{}".format(seeker_gender, target_gender)
    am = AGE_RE.search(title)
    if am:
        age = int(am.group(1))
    return age, seeker_gender, target_gender, tag


def normalize(rec, city_matcher, gazetteer):
    post_id = rec.get("id")
    title = rec.get("title")
    created = rec.get("created_utc")
    if not post_id or not title or created is None:
        return None
    try:
        created = int(created)
    except (TypeError, ValueError):
        return None
    dt = datetime.fromtimestamp(created, tz=MANILA)
    subreddit = (rec.get("subreddit") or "").strip()
    category = CATEGORY_MAP.get(subreddit.lower(), "unknown")
    age, seeker_gender, target_gender, tag = parse_intent(title)
    selftext = (rec.get("selftext") or "").strip()
    return {
        "post_id": post_id,
        "title": title.strip(),
        "selftext": selftext,
        "author": rec.get("author"),
        "subreddit": subreddit,
        "category": category,
        "created_utc": created,
        "created_datetime_manila": dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date_manila": dt.strftime("%Y-%m-%d"),
        "hour_manila": dt.hour,
        "day_of_week": dt.strftime("%A"),
        "year": dt.year,
        "month": dt.month,
        "score": rec.get("score"),
        "num_comments": rec.get("num_comments"),
        "seeker_age": age,
        "seeker_gender": seeker_gender,
        "target_gender": target_gender,
        "intent_tag": tag,
        "city": extract_city(title + " " + selftext, city_matcher, gazetteer),
    }


def drop_reason(rec):
    if rec.get("stickied") is True:
        return "mod_or_removed"
    if rec.get("removed_by_category"):
        return "mod_or_removed"
    return None


def clean(raw_records, city_matcher, gazetteer):
    stats = {
        "input": len(raw_records),
        "missing_required": 0,
        "mod_or_removed": 0,
        "deleted_author": 0,
        "empty_body": 0,
        "duplicate_id": 0,
        "no_intent_tag": 0,
        "no_city": 0,
    }
    seen = set()
    rows = []
    for rec in raw_records:
        reason = drop_reason(rec)
        if reason:
            stats[reason] += 1
            continue
        row = normalize(rec, city_matcher, gazetteer)
        if row is None:
            stats["missing_required"] += 1
            continue
        author = (row["author"] or "").lower()
        if author in ("[deleted]", "[removed]", ""):
            stats["deleted_author"] += 1
            continue
        if not row["selftext"]:
            stats["empty_body"] += 1
            continue
        if row["post_id"] in seen:
            stats["duplicate_id"] += 1
            continue
        seen.add(row["post_id"])
        if not row["intent_tag"]:
            stats["no_intent_tag"] += 1
        if not row["city"]:
            stats["no_city"] += 1
        rows.append(row)
    rows.sort(key=lambda r: (r["created_utc"], r["post_id"]))
    return rows, stats


def write_csv(rows):
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    with open(CLEAN_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def validate(rows, gazetteer):
    checks = []
    checks.append(("non_empty_output", len(rows) > 0))
    ids = [r["post_id"] for r in rows]
    checks.append(("unique_post_ids", len(ids) == len(set(ids))))
    checks.append(("all_have_title", all(r["title"] for r in rows)))
    checks.append(("all_have_created_utc", all(r["created_utc"] is not None for r in rows)))
    checks.append(("all_have_subreddit", all(r["subreddit"] for r in rows)))
    checks.append(("all_have_category", all(r["category"] != "unknown" for r in rows)))
    years = [r["year"] for r in rows]
    checks.append(("date_range_2023_2026", min(years) >= 2023 and max(years) <= 2026))
    cities = {c for c in (r["city"] for r in rows) if c}
    checks.append(("city_values_from_gazetteer", all(c in gazetteer.values() for c in cities)))
    return checks


def write_log(load_stats, clean_stats, checks, rows):
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    with open(CLEANING_LOG, "w", encoding="utf-8") as f:
        f.write("# Cleaning Log\n\n")
        f.write("Generated by scripts/transform.py. Same input always produces the same output.\n\n")
        f.write("## Source files read\n\n")
        f.write("- Files read: {}\n".format(load_stats["files"]))
        f.write("- Raw records parsed: {}\n".format(load_stats["lines"]))
        f.write("- JSON parse errors: {}\n\n".format(load_stats["json_errors"]))
        f.write("## Cleaning decisions (in order)\n\n")
        f.write("1. Drop stickied/pinned moderator posts and removed posts. Reason: not user connection-seeking content.\n")
        f.write("2. Drop records missing id, title, or created_utc. Reason: cannot place post in time or identify it.\n")
        f.write("3. Drop posts with deleted/removed author. Reason: author info is not usable.\n")
        f.write("4. Drop posts with empty body. Reason: body carries the location/intent signal we need.\n")
        f.write("5. Deduplicate by post_id. Reason: Arctic Shift archives and PRAW exports overlap.\n")
        f.write("6. Parse seeker_age and intent_tag (X4Y) from title with regex. Missing tags are kept but flagged.\n")
        f.write("7. Convert created_utc to Asia/Manila (UTC+8) and derive date/hour/day_of_week.\n")
        f.write("8. Map subreddit to category (all/platonic/romantic/sexual).\n")
        f.write("9. Gazetteer-based geoparsing: match city aliases from data/reference/metro_manila_gazetteer.csv\n")
        f.write("   (canonical names from the PSGC 2Q 2026 publication) against title + selftext with\n")
        f.write("   word-boundary regex. Blank when no city is matched.\n\n")
        f.write("## Row counts\n\n")
        f.write("| Step | Dropped | Remaining |\n|---|---|---|\n")
        remaining = clean_stats["input"]
        f.write("| Input raw records | - | {} |\n".format(remaining))
        for key, label in [
            ("mod_or_removed", "mod/removed posts"),
            ("missing_required", "missing id/title/date"),
            ("deleted_author", "deleted author"),
            ("empty_body", "empty body"),
            ("duplicate_id", "duplicate post_id"),
        ]:
            remaining -= clean_stats[key]
            f.write("| {} | {} | {} |\n".format(label, clean_stats[key], remaining))
        f.write("\nFinal clean rows: {}\n".format(len(rows)))
        f.write("Rows without a parsed intent_tag: {}\n".format(clean_stats["no_intent_tag"]))
        f.write("Rows with a matched city: {} ({:.1f}%)\n\n".format(
            len(rows) - clean_stats["no_city"],
            100.0 * (len(rows) - clean_stats["no_city"]) / len(rows) if rows else 0.0))
        f.write("## Validation checks\n\n")
        f.write("| Check | Result |\n|---|---|\n")
        for name, ok in checks:
            f.write("| {} | {} |\n".format(name, "PASS" if ok else "FAIL"))


def main():
    gazetteer = load_gazetteer()
    city_matcher = build_city_matcher(gazetteer)
    raw, load_stats = load_records()
    rows, clean_stats = clean(raw, city_matcher, gazetteer)
    write_csv(rows)
    checks = validate(rows, gazetteer)
    write_log(load_stats, clean_stats, checks, rows)

    print("Loaded {} raw records from {} files".format(load_stats["lines"], load_stats["files"]))
    print("Clean rows: {}".format(len(rows)))
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print("  {}: {}".format("PASS" if ok else "FAIL", name))
    print("Wrote {}".format(os.path.relpath(CLEAN_CSV, BASE_DIR)))
    print("Wrote {}".format(os.path.relpath(CLEANING_LOG, BASE_DIR)))
    if failed:
        raise SystemExit("Validation failed: {}".format(", ".join(failed)))


if __name__ == "__main__":
    main()
