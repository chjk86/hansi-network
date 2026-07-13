"""edges.csv에 저자<->수신자가 생몰년상 동시대인인지 여부를 덧붙인다.

'차운(次韻)' 등은 수백 년 전 인물의 시에 운을 맞춰 짓는 경우가 흔해
실제 교류(생전 왕래)와는 성격이 다르다. 이를 구분해서 보여주기 위한 전처리.
"""
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUTHORS_PATH = BASE / "data" / "mapping" / "authors.csv"
EDGES_PATH = BASE / "output" / "edges.csv"
OUT_PATH = BASE / "output" / "edges_annotated.csv"
ANACHRONISTIC_OUT = BASE / "output" / "anachronistic_chaun.csv"

YEAR_RE = re.compile(r"\d+")


def parse_year(s: str):
    if not s:
        return None
    m = YEAR_RE.search(s)
    return int(m.group()) if m else None


def main():
    with AUTHORS_PATH.open(encoding="utf-8-sig") as f:
        authors = {r["collection_id"]: r for r in csv.DictReader(f)}

    lifespan = {}
    for cid, r in authors.items():
        b, d = parse_year(r["birth_year"]), parse_year(r["death_year"])
        lifespan[cid] = (b, d)

    with EDGES_PATH.open(encoding="utf-8-sig") as f:
        edges = list(csv.DictReader(f))

    annotated = []
    anachronistic = []
    counts = {"contemporary": 0, "non_contemporary": 0, "unknown": 0, "impossible": 0}

    for e in edges:
        b1, d1 = lifespan.get(e["author_id"], (None, None))
        b2, d2 = lifespan.get(e["recipient_id"], (None, None))

        if None in (b1, d1, b2, d2):
            status = "unknown"
        elif b1 <= d2 and b2 <= d1:
            status = "contemporary"
        elif d1 is not None and b2 is not None and d1 < b2:
            # 저자가 수신자 출생 이전에 사망 -> 시간 역행, 매칭 오류일 가능성이 높음
            status = "impossible"
        else:
            status = "non_contemporary"

        counts[status] = counts.get(status, 0) + 1
        e["contemporary_status"] = status
        e["author_years"] = f"{b1 or '?'}-{d1 or '?'}"
        e["recipient_years"] = f"{b2 or '?'}-{d2 or '?'}"
        annotated.append(e)

        if status in ("non_contemporary", "impossible") and e["category"] == "차운":
            anachronistic.append(e)

    fieldnames = list(annotated[0].keys())
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(annotated)

    with ANACHRONISTIC_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        if anachronistic:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(anachronistic)

    print(f"edges annotated: {len(annotated)}")
    print(f"  contemporary: {counts['contemporary']}")
    print(f"  non_contemporary: {counts['non_contemporary']}")
    print(f"  impossible (시간 역행 -> 매칭 오류 의심): {counts['impossible']}")
    print(f"  unknown (생몰년 정보 부족): {counts['unknown']}")
    print(f"\n'차운' 이면서 non_contemporary(동시대 아님)인 edge: {len(anachronistic)}")
    print(f"written to: {OUT_PATH}")
    print(f"anachronistic 차운 list: {ANACHRONISTIC_OUT}")


if __name__ == "__main__":
    main()
