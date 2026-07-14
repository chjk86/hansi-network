"""template.html + network_data*.json -> viz/network.html, viz/network_15c.html"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE / "docs" / "template.html"

VARIANTS = [
    {
        "data_file": "network_data.json",
        "out_file": "network.html",
        "title": "한시 증답 네트워크 — 651개 문집",
        "h1": "한시 증답(贈答) 네트워크 — 한국문집총간 651개 문집",
        "subtitle": (
            "고운집~암서집(최치원~조긍섭) 651개 문집, 시 362,130수의 제목에서 "
            "증/기/수답/화답/차운/송별/서간/만사 표현을 규칙 기반으로 추출해 651명 저자 목록과 "
            "대조 매칭한 결과입니다. 정확한 개체명 인식이 아닌 규칙 기반 1차 분석이라 노이즈가 섞여 있습니다."
        ),
        "extra_stats": (
            '<div class="stat"><b id="statPoems">362,130</b> 시 전체</div>\n'
            '      <div class="stat"><b id="statMatchRate">14.4%</b> 수신자 매칭률</div>'
        ),
        "footer_limits": (
            "수신자 후보 163,961건 중 14.4%(23,624건)만 이 651명 목록 안에서 매칭되었습니다"
            "(나머지는 목록 밖 인물이거나 추출 노이즈). 모호 매칭 5,303건은 동명이인 등으로 "
            "귀속하지 않고 별도 기록했습니다. 매칭되지 않은/모호한 항목은 저장소의 "
            "unmatched_recipients.csv·ambiguous_matches.csv에서 확인할 수 있습니다."
        ),
    },
    {
        "data_file": "network_data_15c.json",
        "out_file": "network_15c.html",
        "title": "15세기 사대부 한시 교류 네트워크",
        "h1": "15세기 사대부 한시 교류 네트워크",
        "subtitle": (
            "651명 저자 중 생몰년이 15세기(1400~1499)에 걸치는 인물 중 실제 교류가 매칭된 "
            "100명 간의 증답 관계만 추려낸 네트워크입니다. 세종~성종대 관각문인·사림파 1세대가 중심입니다. "
            "원본은 651개 문집 시 362,130수에서 규칙 기반으로 추출·매칭한 결과라 노이즈가 섞여 있습니다."
        ),
        "extra_stats": (
            '<div class="stat"><b>15세기</b> (1400–1499) 필터</div>\n'
            '      <div class="stat"><b>651명 전체 결과는</b> 별도 네트워크 참고</div>'
        ),
        "footer_limits": (
            "이 필터는 651명 전체 결과(위 네트워크와 동일한 매칭 로직)에서 생몰년만 15세기로 "
            "추려낸 것이라, 전체 네트워크와 같은 매칭 한계(14.4% 매칭률, 모호 매칭 등)를 그대로 "
            "가지고 있습니다."
        ),
    },
]

DEFAULT_H1 = "한시 증답(贈答) 네트워크 — 파일럿 99개 문집"
DEFAULT_SUBTITLE_START = '<p class="subtitle">고운집~안분당시집'
DEFAULT_STATS = (
    '<div class="stat"><b id="statPoems">42,748</b> 시 전체</div>\n'
    '      <div class="stat"><b id="statMatchRate">7.8%</b> 수신자 매칭률</div>'
)


def main():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    for v in VARIANTS:
        html = template
        html = html.replace(f"<h1>{DEFAULT_H1}</h1>", f"<h1>{v['h1']}</h1>")
        # subtitle: replace whole <p class="subtitle">...</p>
        start = html.index(DEFAULT_SUBTITLE_START)
        end = html.index("</p>", start) + len("</p>")
        html = html[:start] + f'<p class="subtitle">{v["subtitle"]}</p>' + html[end:]
        html = html.replace(DEFAULT_STATS, v["extra_stats"])
        html = html.replace("__FOOTER_LIMITS__", v["footer_limits"])

        data = json.loads((BASE / "output" / v["data_file"]).read_text(encoding="utf-8"))
        html = html.replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
        html = f"<title>{v['title']}</title>\n" + html

        out_path = BASE / "docs" / v["out_file"]
        out_path.write_text(html, encoding="utf-8")
        print(f"{v['out_file']}: {out_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
