"""hansi-database 저장소에서 아직 없는 문집 텍스트를 내려받는다.
raw.githubusercontent.com이 연속 요청 시 간헐적으로 404를 반환하는 경우가 있어
재시도 로직을 넣었다."""
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "data" / "collections"
LIST_URL = "https://api.github.com/repos/chjk86/hansi-database/contents/hansi_database_cleaned"
RAW_BASE = "https://raw.githubusercontent.com/chjk86/hansi-database/main/hansi_database_cleaned/"


def fetch_full_list():
    import json
    req = urllib.request.Request(LIST_URL, headers={"User-Agent": "hansi-network-pipeline"})
    with urllib.request.urlopen(req) as resp:
        items = json.loads(resp.read().decode("utf-8"))
    return [item["name"] for item in items]


def download_one(name, max_retries=5):
    url = RAW_BASE + urllib.parse.quote(name)
    dest = OUT_DIR / name
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "hansi-network-pipeline"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            if data.startswith(b"404:") or len(data) < 20:
                raise ValueError(f"suspicious short response ({len(data)} bytes)")
            dest.write_bytes(data)
            return True
        except Exception as e:
            wait = 1.5 * (attempt + 1)
            time.sleep(wait)
    return False


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full_list = fetch_full_list()
    have = {p.name for p in OUT_DIR.glob("*.txt")}
    missing = [n for n in full_list if n not in have]
    print(f"total: {len(full_list)}, have: {len(have)}, missing: {len(missing)}")

    ok, fail = 0, []
    for i, name in enumerate(missing, 1):
        success = download_one(name)
        if success:
            ok += 1
        else:
            fail.append(name)
        if i % 50 == 0:
            print(f"  progress: {i}/{len(missing)} (ok={ok}, fail={len(fail)})")
        time.sleep(0.15)

    print(f"\ndone. downloaded={ok}, failed={len(fail)}")
    if fail:
        print("failed files:")
        for n in fail:
            print(" ", n)


if __name__ == "__main__":
    main()
