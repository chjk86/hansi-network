import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

path = Path(__file__).resolve().parent.parent / "output" / "poems.csv"
with path.open(encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    titles = [row["title"] for row in r]

print("total titles:", len(titles))
keywords = ["贈", "寄", "酬", "和", "次韻", "次", "留別", "奉呈", "奉贈", "奉寄",
            "簡", "示", "輓", "挽", "送", "答", "奉和", "奉次", "奉送", "呈"]
for kw in keywords:
    cnt = sum(1 for t in titles if kw in t)
    print(f"{kw}: {cnt}")

print("\n--- sample titles containing 贈 ---")
samples = [t for t in titles if "贈" in t][:15]
for s in samples:
    print(s)

print("\n--- sample titles containing 寄 ---")
samples = [t for t in titles if "寄" in t][:15]
for s in samples:
    print(s)

print("\n--- sample titles containing 次韻 ---")
samples = [t for t in titles if "次韻" in t][:15]
for s in samples:
    print(s)
