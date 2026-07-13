"""hansi_database_cleaned/*.txt 파일들을 파싱해 poems.csv로 통합한다.

파일명 형식: 0001.계원필경집.txt
내용 형식: <title>...</title> 다음 줄에 <text>...</text> 가 반복.
"""
import csv
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "collections"
OUT_PATH = Path(__file__).resolve().parent.parent / "output" / "poems.csv"

FILENAME_RE = re.compile(r"^(\d{4})\.(.+)\.txt$")
ENTRY_RE = re.compile(r"<title>(.*?)</title>\s*<text>(.*?)</text>", re.DOTALL)


def parse_file(path: Path):
    m = FILENAME_RE.match(path.name)
    if not m:
        raise ValueError(f"unexpected filename: {path.name}")
    collection_id, collection_name = m.group(1), m.group(2)

    content = path.read_text(encoding="utf-8", errors="replace")
    entries = ENTRY_RE.findall(content)

    rows = []
    for idx, (title, text) in enumerate(entries, start=1):
        rows.append({
            "collection_id": collection_id,
            "collection_name": collection_name,
            "poem_seq": idx,
            "title": title.strip(),
            "text": text.strip(),
        })
    return rows


def main():
    files = sorted(DATA_DIR.glob("*.txt"))
    if not files:
        raise SystemExit(f"no .txt files found in {DATA_DIR}")

    all_rows = []
    parse_errors = []
    for f in files:
        try:
            rows = parse_file(f)
            if not rows:
                parse_errors.append((f.name, "no <title>/<text> entries found"))
            all_rows.extend(rows)
        except Exception as e:
            parse_errors.append((f.name, str(e)))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["collection_id", "collection_name", "poem_seq", "title", "text"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"files parsed: {len(files)}")
    print(f"poems extracted: {len(all_rows)}")
    print(f"written to: {OUT_PATH}")
    if parse_errors:
        print(f"\n{len(parse_errors)} file(s) had issues:")
        for name, err in parse_errors:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
