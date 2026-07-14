# 한시 증답(贈答) 네트워크

고전 한시(漢詩) 문집 텍스트에서 "누가 누구에게 시를 보내고 주고받았는가"를 규칙 기반으로 추출해, 인물 간 교류 네트워크로 시각화하는 파이프라인입니다. [한국문집총간 텍스트(hansi-database)](https://github.com/chjk86/hansi-database)의 `hansi_database_cleaned` 전체 651개 문집(고운집~암서집, 최치원~조긍섭, 9세기~20세기 초)을 분석했습니다.

## 결과 보기

GitHub Pages: **https://chjk86.github.io/hansi-network/**

- [`docs/network.html`](docs/network.html) — 전체 651명 네트워크
- [`docs/network_15c.html`](docs/network_15c.html) — 15세기(1400~1499) 사대부만 필터링한 네트워크

카테고리(증정/기증/수답/화답/차운/송별/서간/만사)·동시대 여부 필터, 인물 검색, 표 보기를 지원합니다. 전체 네트워크는 노드/엣지가 많아 기본적으로 교류 3회 이상만 표시하도록 필터가 걸려 있습니다(슬라이더로 조정 가능).

## 파이프라인

```
data/collections/*.txt          한시 원문 (문집 651개, <title>/<text> 쌍)
        │  src/parse_collections.py
        ▼
output/poems.csv                시 362,130수 (collection_id, title, text)
        │  src/extract_recipients.py
        ▼
output/title_recipients.csv     제목에서 증답 키워드 + 수신자 후보 추출 (163,961건)

data/mapping/authors.csv        문집명→저자/자/호/생몰년 매핑 (651명, 조사 기반)
        │
        ▼  src/build_network.py  (수신자 후보 ↔ 저자 별칭 매칭)
output/edges.csv                저자↔수신자 교류 빈도
        │  src/add_contemporary_flag.py
        ▼
output/edges_annotated.csv      생몰년 기반 동시대 여부 태깅 추가
        │  src/build_viz_data.py + src/build_viz_html.py
        ▼
docs/network.html, docs/network_15c.html
```

`src/download_collections.py`는 hansi-database 저장소에서 문집 원문을 내려받는 스크립트입니다(재시도 로직 포함).
`src/merge_hanja_backfill.py`는 저자 조사 초기(99개 파일럿 단계)에 호/자에 한자가 누락된 경우를 보완했던 1회성 스크립트입니다.

## 한계 (있는 그대로)

- **매칭률 14.4%**: 수신자 후보 163,961건 중 651명 저자 목록 안에서 매칭된 것은 23,624건입니다. 나머지는 목록 밖 인물(승려·관료·여성·미수록 문인 등)이거나 규칙 기반 추출의 노이즈입니다. → `output/unmatched_recipients.csv`
- **모호 매칭 5,303건(3.2%)**은 동명이인(같은 호를 쓰는 서로 다른 인물)으로 인해 귀속하지 않고 `output/ambiguous_matches.csv`에 별도 기록했습니다. 651명 규모에서는 호가 겹치는 경우가 드물지 않습니다(예: '눌재', '성재', '손재' 등은 각각 시대가 다른 2인 이상이 사용).
- **'차운(次韻)'은 실시간 교류가 아닐 수 있습니다** — 후대 사람이 옛 시인의 운을 빌려 짓는 문학적 오마주인 경우가 흔합니다. `contemporary_status` 컬럼으로 동시대(`contemporary`, 6,428건) / 비동시대(`non_contemporary`, 2,196건) / 시간 역행(`impossible`, 1,001건 — 저자가 수신자보다 먼저 사망, 매칭 오류 의심)을 구분했습니다.
- 저자/호/자 매핑은 AKS 인물종합시스템·한국고전종합DB 스크래핑이 아니라(둘 다 로봇 배제 정책상 크롤링이 제한적) 웹 조사를 통해 직접 구축했습니다. 여러 리서치 에이전트가 나눠 조사한 결과라 개별 인물 단위로 오류가 있을 수 있습니다(각 배치 조사 과정에서 발견된 동명이인·연대 불일치는 `note` 컬럼에 기록해뒀습니다).

## 재현하기

```bash
cd src
python download_collections.py
python parse_collections.py
python extract_recipients.py
python build_network.py
python add_contemporary_flag.py
python build_viz_data.py
python build_viz_html.py
```

`data/mapping/authors.csv`는 이미 조사되어 포함되어 있습니다(`authors_chunk*.csv`, `authors_batch*.csv`는 조사 과정에서 나온 원본 배치 파일). 새 문집을 추가하려면 `data/collections/`에 동일한 `<title>/<text>` 형식의 텍스트를 넣고 `authors.csv`에 저자 정보를 추가하면 됩니다.
