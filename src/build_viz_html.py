"""template.html + network_data*.json -> viz/network.html, viz/network_15c.html"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE / "docs" / "template.html"

VARIANTS = [
    {
        "data_file": "network_data.json",
        "out_file": "network.html",
        "title": "한시 증답 네트워크 — 파일럿",
        "h1": "한시 증답(贈答) 네트워크 — 파일럿 99개 문집",
        "subtitle": (
            "고운집~안분당시집(최치원~이희보) 99개 문집, 시 42,748수의 제목에서 "
            "증/기/수답/화답/차운/송별/서간/만사 표현을 규칙 기반으로 추출해 99명 저자 목록과 "
            "대조 매칭한 결과입니다. 정확한 개체명 인식이 아닌 1차 파일럿이라 노이즈가 섞여 있습니다."
        ),
        "extra_stats": (
            '<div class="stat"><b id="statPoems">42,748</b> 시 전체</div>\n'
            '      <div class="stat"><b id="statMatchRate">7.8%</b> 수신자 매칭률</div>'
        ),
    },
    {
        "data_file": "network_data_15c.json",
        "out_file": "network_15c.html",
        "title": "15세기 사대부 한시 교류 네트워크",
        "h1": "15세기 사대부 한시 교류 네트워크",
        "subtitle": (
            "99명 파일럿 저자 중 생몰년이 15세기(1400~1499)에 걸치는 인물 중 실제 교류가 매칭된 "
            "60명 간의 증답 관계만 추려낸 네트워크입니다. 세종~성종대 관각문인·사림파 1세대가 중심입니다. "
            "원본은 99개 문집 시 42,748수에서 규칙 기반으로 추출·매칭한 1차 파일럿이라 노이즈가 섞여 있습니다."
        ),
        "extra_stats": (
            '<div class="stat"><b>15세기</b> (1400–1499) 필터</div>\n'
            '      <div class="stat"><b>99명 파일럿 전체 결과는</b> 별도 네트워크 참고</div>'
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

        data = json.loads((BASE / "output" / v["data_file"]).read_text(encoding="utf-8"))
        html = html.replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
        html = f"<title>{v['title']}</title>\n" + html

        out_path = BASE / "docs" / v["out_file"]
        out_path.write_text(html, encoding="utf-8")
        print(f"{v['out_file']}: {out_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
