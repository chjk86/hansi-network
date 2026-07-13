"""hanja_backfill_A/B.csv를 authors.csv에 병합해 ja/ho 필드를
'한글(한자)' 형식으로 통일한다 (한글만 있던 66개 행 보정)."""
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
MAP_DIR = BASE / "data" / "mapping"
AUTHORS_PATH = MAP_DIR / "authors.csv"
OUT_PATH = MAP_DIR / "authors.csv"  # in place


def load_backfill():
    backfill = {}
    for fname in ("hanja_backfill_A.csv", "hanja_backfill_B.csv"):
        with (MAP_DIR / fname).open(encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                backfill[row["collection_id"]] = row
    return backfill


def merge_field(hangul_field: str, hanja_field: str) -> str:
    """'경지' + '敬之' -> '경지(敬之)'. ho는 '/'로 나뉜 각 항목을 순서대로 짝짓는다."""
    hangul_parts = [p.strip() for p in hangul_field.split("/") if p.strip()]
    hanja_parts = [p.strip() for p in hanja_field.split("/") if p.strip()] if hanja_field else []
    merged = []
    for i, h in enumerate(hangul_parts):
        hj = hanja_parts[i] if i < len(hanja_parts) and hanja_parts[i] != "?" else ""
        merged.append(f"{h}({hj})" if hj else h)
    return "/".join(merged)


def main():
    backfill = load_backfill()
    print(f"backfill entries loaded: {len(backfill)}")

    with AUTHORS_PATH.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys())

    patched = 0
    for row in rows:
        cid = row["collection_id"]
        if cid not in backfill:
            continue
        bf = backfill[cid]
        changed = False
        if row["ja"] and bf.get("ja_hanja"):
            row["ja"] = merge_field(row["ja"], bf["ja_hanja"])
            changed = True
        if row["ho"] and bf.get("ho_hanja"):
            row["ho"] = merge_field(row["ho"], bf["ho_hanja"])
            changed = True
        if changed:
            patched += 1

    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"rows patched with hanja: {patched}")
    print(f"authors.csv updated in place: {OUT_PATH}")


if __name__ == "__main__":
    main()
