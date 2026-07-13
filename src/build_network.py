"""저자 매핑(authors.csv) + 제목 수신자 후보(title_recipients.csv)를 대조해
저자<->수신자 교류 빈도 네트워크(edges.csv)를 만든다.
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

# "한글(漢字)" 형태로 온 필드에서 한글/한자 조각을 모두 별칭 후보로 뽑아낸다.
# 한시 원문은 한자로만 적혀 있으므로, 괄호 안 한자만 실제 매칭에 쓸모가 있다.
PAREN_RE = re.compile(r"^(.*?)\(([^)]*)\)\s*$")


def split_aliases(raw: str):
    tokens = []
    for part in raw.split("/"):
        part = part.strip()
        if not part:
            continue
        m = PAREN_RE.match(part)
        if m:
            outer, inner = m.group(1).strip(), m.group(2).strip()
            if outer:
                tokens.append(outer)
            if inner:
                tokens.append(inner)
        else:
            tokens.append(part)
    return tokens

BASE = Path(__file__).resolve().parent.parent
AUTHORS_PATH = BASE / "data" / "mapping" / "authors.csv"
RECIPIENTS_PATH = BASE / "output" / "title_recipients.csv"
EDGES_OUT = BASE / "output" / "edges.csv"
UNMATCHED_OUT = BASE / "output" / "unmatched_recipients.csv"
AMBIGUOUS_OUT = BASE / "output" / "ambiguous_matches.csv"

MIN_ALIAS_LEN = 2  # 한 글자짜리 성씨만으로는 매칭하지 않음 (오탐 방지)


def load_authors():
    with AUTHORS_PATH.open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    return rows


HANJA_RE = re.compile(r"[一-鿿]")


def build_alias_index(authors):
    """alias(문자열) -> set(collection_id) 인덱스.
    한시 원문이 한자로만 적혀 있으므로 한자가 하나라도 포함된 별칭만 채택한다."""
    index = defaultdict(set)
    for row in authors:
        cid = row["collection_id"]
        aliases = set()

        hanja_name = (row.get("author_name_hanja") or "").strip()
        if hanja_name:
            aliases.add(hanja_name)

        for field in ("ja", "ho"):
            raw = (row.get(field) or "").strip()
            if raw:
                aliases.update(split_aliases(raw))

        for alias in aliases:
            if len(alias) >= MIN_ALIAS_LEN and HANJA_RE.search(alias):
                index[alias].add(cid)
    return index


def match_recipient(raw: str, alias_index):
    """recipient_raw 문자열 안에 등록된 별칭이 포함되어 있는지 찾는다.
    가장 긴 별칭이 매치되는 것을 우선시한다. 여러 인물이 동일 별칭을 쓰면 모호 처리."""
    candidates = []  # (alias_len, alias, set(cid))
    for alias, cids in alias_index.items():
        if alias in raw:
            candidates.append((len(alias), alias, cids))
    if not candidates:
        return None, None
    candidates.sort(key=lambda x: -x[0])
    best_len = candidates[0][0]
    best = [c for c in candidates if c[0] == best_len]
    if len(best) > 1:
        # 같은 길이의 서로 다른 별칭이 동시에 매치 -> 모호
        merged_cids = set()
        for _, _, cids in best:
            merged_cids |= cids
        if len(merged_cids) > 1:
            return "AMBIGUOUS", merged_cids
    _, alias, cids = best[0]
    if len(cids) > 1:
        return "AMBIGUOUS", cids
    return alias, cids


def main():
    authors = load_authors()
    id_to_name = {r["collection_id"]: r["author_name_ko"] for r in authors}
    alias_index = build_alias_index(authors)
    print(f"authors loaded: {len(authors)}, alias index size: {len(alias_index)}")

    with RECIPIENTS_PATH.open(encoding="utf-8-sig") as f:
        recipient_rows = list(csv.DictReader(f))
    print(f"recipient candidate rows: {len(recipient_rows)}")

    edge_counts = defaultdict(int)  # (author_id, recipient_id, category) -> count
    unmatched_counts = defaultdict(int)  # raw string -> count
    ambiguous_rows = []
    matched = 0
    self_matches = 0

    for row in recipient_rows:
        author_id = row["collection_id"]
        raw = row["recipient_raw"]
        category = row["category"]
        alias, cids = match_recipient(raw, alias_index)

        if alias is None:
            unmatched_counts[raw] += 1
            continue
        if alias == "AMBIGUOUS":
            ambiguous_rows.append({**row, "candidate_ids": ";".join(sorted(cids))})
            continue

        (recipient_id,) = cids
        if recipient_id == author_id:
            self_matches += 1
            continue

        edge_counts[(author_id, recipient_id, category)] += 1
        matched += 1

    edges = []
    for (a_id, r_id, cat), cnt in sorted(edge_counts.items(), key=lambda x: -x[1]):
        edges.append({
            "author_id": a_id,
            "author_name": id_to_name.get(a_id, ""),
            "recipient_id": r_id,
            "recipient_name": id_to_name.get(r_id, ""),
            "category": cat,
            "count": cnt,
        })

    EDGES_OUT.parent.mkdir(parents=True, exist_ok=True)
    with EDGES_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["author_id", "author_name", "recipient_id",
                                                 "recipient_name", "category", "count"])
        writer.writeheader()
        writer.writerows(edges)

    with UNMATCHED_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["recipient_raw", "count"])
        for raw, cnt in sorted(unmatched_counts.items(), key=lambda x: -x[1]):
            writer.writerow([raw, cnt])

    with AMBIGUOUS_OUT.open("w", encoding="utf-8-sig", newline="") as f:
        if ambiguous_rows:
            writer = csv.DictWriter(f, fieldnames=list(ambiguous_rows[0].keys()))
            writer.writeheader()
            writer.writerows(ambiguous_rows)

    total = len(recipient_rows)
    print(f"\nmatched (resolved to a known author): {matched} ({matched/total:.1%})")
    print(f"ambiguous (multiple authors share alias): {len(ambiguous_rows)} ({len(ambiguous_rows)/total:.1%})")
    print(f"self-matches discarded: {self_matches}")
    print(f"unmatched (no known author alias found): {sum(unmatched_counts.values())} "
          f"({sum(unmatched_counts.values())/total:.1%})")
    print(f"\nunique author-recipient-category edges: {len(edges)}")
    print(f"edges written to: {EDGES_OUT}")
    print(f"unmatched raw strings written to: {UNMATCHED_OUT}")
    print(f"ambiguous matches written to: {AMBIGUOUS_OUT}")


if __name__ == "__main__":
    main()
