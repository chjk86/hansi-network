"""edges_annotated.csv + authors.csv -> viz용 JSON (전체 / 15세기 필터)."""
import csv
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
AUTHORS_PATH = BASE / "data" / "mapping" / "authors.csv"
EDGES_PATH = BASE / "output" / "edges_annotated.csv"

YEAR_RE = re.compile(r"\d+")


def parse_year(s):
    if not s:
        return None
    m = YEAR_RE.search(s)
    return int(m.group()) if m else None


def build_json(authors, edges, node_ids, out_path):
    nodes = []
    for cid in sorted(node_ids):
        a = authors[cid]
        nodes.append({
            "id": cid, "name": a["author_name_ko"], "hanja": a["author_name_hanja"],
            "ho": a["ho"], "dynasty": a["dynasty"], "birth": a["birth_year"],
            "death": a["death_year"], "collection": a["collection_name"],
        })
    edge_out = [{
        "source": e["author_id"], "target": e["recipient_id"],
        "category": e["category"], "count": int(e["count"]), "status": e["contemporary_status"],
    } for e in edges]
    data = {"nodes": nodes, "edges": edge_out}
    out_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"{out_path.name}: nodes={len(nodes)} edges={len(edge_out)}")


def main():
    with AUTHORS_PATH.open(encoding="utf-8-sig") as f:
        authors = {r["collection_id"]: r for r in csv.DictReader(f)}
    with EDGES_PATH.open(encoding="utf-8-sig") as f:
        edges = list(csv.DictReader(f))

    # 전체 파일럿
    all_ids = set()
    for e in edges:
        all_ids.add(e["author_id"]); all_ids.add(e["recipient_id"])
    build_json(authors, edges, all_ids, BASE / "output" / "network_data.json")

    # 15세기(1400-1499)에 생몰년이 걸치는 인물만
    c15_ids = set()
    for cid, a in authors.items():
        b, d = parse_year(a["birth_year"]), parse_year(a["death_year"])
        if b is None and d is None:
            continue
        b = b if b is not None else d
        d = d if d is not None else b
        if b <= 1499 and d >= 1400:
            c15_ids.add(cid)

    c15_edges = [e for e in edges if e["author_id"] in c15_ids and e["recipient_id"] in c15_ids]
    c15_node_ids = set()
    for e in c15_edges:
        c15_node_ids.add(e["author_id"]); c15_node_ids.add(e["recipient_id"])
    build_json(authors, c15_edges, c15_node_ids, BASE / "output" / "network_data_15c.json")


if __name__ == "__main__":
    main()
