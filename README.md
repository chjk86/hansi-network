# 한시 증답(贈答) 네트워크

고전 한시(漢詩) 문집 텍스트에서 "누가 누구에게 시를 보내고 주고받았는가"를 규칙 기반으로 추출해, 인물 간 교류 네트워크로 시각화하는 파이프라인입니다. [한국문집총간 텍스트(hansi-database)](https://github.com/chjk86/hansi-database) 중 99개 문집(고운집~안분당시집, 최치원~이희보)을 파일럿으로 분석했습니다.

## 결과 보기

- [`viz/network.html`](viz/network.html) — 파일럿 99명 전체 네트워크
- [`viz/network_15c.html`](viz/network_15c.html) — 15세기(1400~1499) 사대부만 필터링한 네트워크

GitHub Pages로 배포된 경우 브라우저에서 바로 열립니다. 카테고리(증정/기증/수답/화답/차운/송별/서간/만사)·동시대 여부 필터, 인물 검색, 표 보기를 지원합니다.

## 파이프라인

```
data/collections/*.txt          한시 원문 (문집별, <title>/<text> 쌍)
        │  src/parse_collections.py
        ▼
output/poems.csv                시 42,748수 (collection_id, title, text)
        │  src/extract_recipients.py
        ▼
output/title_recipients.csv     제목에서 증답 키워드 + 수신자 후보 추출 (18,433건)

data/mapping/authors.csv        문집명→저자/자/호/생몰년 매핑 (99명, 조사 기반)
        │
        ▼  src/build_network.py  (수신자 후보 ↔ 저자 별칭 매칭)
output/edges.csv                저자↔수신자 교류 빈도
        │  src/add_contemporary_flag.py
        ▼
output/edges_annotated.csv      생몰년 기반 동시대 여부 태깅 추가
        │  src/build_viz_data.py + src/build_viz_html.py
        ▼
viz/network.html, viz/network_15c.html
```

`src/merge_hanja_backfill.py`는 저자 조사 과정에서 호/자에 한자가 누락된 경우를 보완하는 1회성 스크립트입니다.

## 한계 (있는 그대로)

- **매칭률 7.8%**: 수신자 후보 18,433건 중 99명 저자 목록 안에서 매칭된 것은 1,433건뿐입니다. 나머지는 목록 밖 인물(승려·관료·미수록 문인 등)이거나 규칙 기반 추출의 노이즈입니다. → `output/unmatched_recipients.csv`
- **모호 매칭 83건**은 동명이인 등으로 인해 귀속하지 않고 `output/ambiguous_matches.csv`에 별도 기록했습니다.
- **'차운(次韻)'은 실시간 교류가 아닐 수 있습니다** — 후대 사람이 옛 시인의 운을 빌려 짓는 문학적 오마주인 경우가 흔합니다. `contemporary_status` 컬럼으로 동시대(`contemporary`) / 비동시대(`non_contemporary`) / 시간 역행(`impossible`, 매칭 오류 의심)을 구분했습니다.
- 저자/호/자 매핑은 AKS 인물종합시스템·한국고전종합DB 스크래핑이 아니라(둘 다 로봇 배제 정책상 제한적) 웹 조사를 통해 직접 구축했습니다.
- 99개 문집은 전체 한국문집총간(약 2,600여 종) 중 일부이며, 원본 저장소에는 651개 문집이 정리되어 있습니다. 이 파이프라인은 검증된 방법론이며 확장 가능합니다.

## 재현하기

```bash
cd src
python parse_collections.py
python extract_recipients.py
python build_network.py
python add_contemporary_flag.py
python build_viz_data.py
python build_viz_html.py
```

`data/mapping/authors.csv`는 이미 조사되어 포함되어 있습니다. 새 문집을 추가하려면 `data/collections/`에 동일한 `<title>/<text>` 형식의 텍스트를 넣고 `authors.csv`에 저자 정보를 추가하면 됩니다.
