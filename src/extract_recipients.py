"""poems.csv의 title에서 '수신자 표현'을 규칙 기반으로 추출한다.

한시 제목에 흔히 등장하는 증답(贈答) 관련 한자 키워드(贈/寄/酬/和/次韻/留別 등) 뒤에
오는 인명·관직·호 등의 텍스트 조각을 수신자 후보로 뽑아낸다.
정확한 개체명 인식이 아니라, 이후 인물 매칭 단계의 입력이 되는 1차 필터임에 유의.
"""
import csv
import re
from pathlib import Path

IN_PATH = Path(__file__).resolve().parent.parent / "output" / "poems.csv"
OUT_PATH = Path(__file__).resolve().parent.parent / "output" / "title_recipients.csv"

# 우선순위 순서로 정렬 (긴 키워드부터 매칭되도록). 카테고리는 이후 분석에 참고용.
KEYWORDS = [
    ("차운", ["次韻", "奉次韻", "奉次", "次"]),
    ("화답", ["奉和", "和"]),
    ("증정", ["奉呈", "奉贈", "呈贈", "贈", "呈"]),
    ("기증", ["奉寄", "寄"]),
    ("수답", ["酬", "答"]),
    ("송별", ["奉別", "留別", "奉送", "贈別", "送"]),
    ("서간", ["簡", "示"]),
    ("만사", ["輓", "挽"]),
]
# 매칭 시도 순서: 키워드 문자열 길이가 긴 것부터 (부분 겹침 방지)
FLAT_KEYWORDS = sorted(
    ((kw, cat) for cat, kws in KEYWORDS for kw in kws),
    key=lambda x: -len(x[0]),
)

# 캡처된 span 끝을 자를 경계 문자(구두점, 괄호, 숫자, '其' 등)
BOUNDARY_RE = re.compile(r"[。，,\(（其0-9一二三四五六七八九十]")

# span 뒤쪽에 흔히 붙는 군더더기(제목 정형구) — 제거 대상
TRAILING_NOISE = [
    "見寄", "見贈", "見和", "見示", "見招", "見過", "求", "乞", "戱", "兼",
    "并", "序", "韻", "又", "同", "以", "因", "謝", "詩", "作",
]

# 인명이 아니라 대명사/허사인 경우 -> 통째로 버림
PRONOUN_ONLY = {"之", "我", "予", "余", "汝", "爾", "卿", "此", "彼"}


def extract_span(title: str, start: int) -> str:
    """start 위치부터 다음 경계까지의 텍스트를 뽑는다."""
    rest = title[start:]
    m = BOUNDARY_RE.search(rest)
    span = rest[: m.start()] if m else rest
    span = span.strip()
    # 최대 길이 제한 (너무 길면 문장 전체를 잘못 삼킨 것으로 간주)
    span = span[:14]
    # 뒤쪽 군더더기 제거
    changed = True
    while changed:
        changed = False
        for noise in TRAILING_NOISE:
            if span.endswith(noise):
                span = span[: -len(noise)].strip()
                changed = True
    return span.strip()


def find_recipient_candidates(title: str):
    """제목 하나에서 (keyword, category, recipient_raw) 후보 리스트를 반환."""
    results = []
    used_spans = set()
    for kw, cat in FLAT_KEYWORDS:
        idx = title.find(kw)
        if idx == -1:
            continue
        if idx in used_spans:
            continue
        span = extract_span(title, idx + len(kw))
        if span and span not in PRONOUN_ONLY:
            results.append((kw, cat, span))
            used_spans.add(idx)
    return results


def main():
    with IN_PATH.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        poems = list(reader)

    out_rows = []
    titles_with_hit = 0
    for poem in poems:
        title = poem["title"]
        candidates = find_recipient_candidates(title)
        if candidates:
            titles_with_hit += 1
        for kw, cat, span in candidates:
            if not span:
                continue
            out_rows.append({
                "collection_id": poem["collection_id"],
                "collection_name": poem["collection_name"],
                "poem_seq": poem["poem_seq"],
                "title": title,
                "keyword": kw,
                "category": cat,
                "recipient_raw": span,
            })

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["collection_id", "collection_name", "poem_seq", "title",
                        "keyword", "category", "recipient_raw"],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"poems scanned: {len(poems)}")
    print(f"poems with >=1 recipient-keyword hit: {titles_with_hit} ({titles_with_hit/len(poems):.1%})")
    print(f"recipient candidate rows: {len(out_rows)}")
    print(f"written to: {OUT_PATH}")


if __name__ == "__main__":
    main()
