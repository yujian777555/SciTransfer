"""Download ScienceAgentBench official benchmark_verified.zip from SharePoint."""
import urllib.request
import ssl
import http.cookiejar
import os
import sys
import time
import hashlib


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "sab-artifacts"
    )
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "benchmark_verified.zip")

    ctx = ssl.create_default_context()
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx),
    )
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    ]
    share = "IQB870QrmuqwS5Ck33cHpJfkAVt3LsMeariREIwP3AT7byA"
    url = (
        "https://buckeyemailosu-my.sharepoint.com/:u:/g/personal/"
        f"chen_8336_osu_edu/{share}?download=1"
    )

    # Warm up session cookies on the share page first (required for anonymous link).
    opener.open(url, timeout=30).read(10)

    # Resume-aware download with retries (SharePoint links can drop mid-stream).
    got = 0
    if os.path.exists(out):
        got = os.path.getsize(out)
        print(f"resuming from {got} bytes", flush=True)

    t0 = time.time()
    attempt = 0
    while True:
        attempt += 1
        headers = {"User-Agent": "Mozilla/5.0"}
        if got > 0:
            headers["Range"] = f"bytes={got}-"
        req = urllib.request.Request(url, headers=headers)
        try:
            r = opener.open(req, timeout=180)
            # 206 = partial, 200 = full (restart)
            status = getattr(r, "status", r.getcode())
            if status == 200 and got > 0:
                # server ignored Range; restart safely via truncation
                print(f"  server returned 200 (no Range support); restarting from 0", flush=True)
                got = 0
            content_range = r.headers.get("Content-Range", "")
            if content_range and got > 0:
                # Validate Content-Range start matches our local size
                # Format: "bytes <start>-<end>/<total>"
                try:
                    range_start = int(content_range.split()[1].split("-")[0])
                    if range_start != got:
                        print(
                            f"  Content-Range start {range_start} != local size {got}; "
                            f"resetting to avoid corrupt append",
                            flush=True,
                        )
                        got = 0
                        status = 200  # treat as full restart
                except (IndexError, ValueError):
                    pass
            if content_range:
                total = int(content_range.split("/")[-1])
            else:
                total = int(r.headers.get("Content-Length", 0)) + got
            print(f"attempt {attempt}: status={status} total={total} got={got}", flush=True)

            mode = "ab" if got > 0 else "wb"
            with open(out, mode) as f:
                while True:
                    chunk = r.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if got % (20 * 1024 * 1024) < 1024 * 1024:
                        el = time.time() - t0
                        rate = (got / 1e6 / el) if el > 0 else 0
                        pct = 100.0 * got / total if total else 0
                        print(
                            f"  {got / 1e9:.3f} / {total / 1e9:.3f} GB ({pct:.1f}%)  {rate:.1f} MB/s",
                            flush=True,
                        )
            if total and got >= total:
                break
            if not total:
                # no content-length; single shot done
                break
            print(f"stream ended early at {got}/{total}, retrying...", flush=True)
            if attempt > 40:
                raise RuntimeError(f"gave up after {attempt} attempts at {got}/{total}")
        except Exception as e:
            print(f"attempt {attempt} error: {type(e).__name__}: {e}", flush=True)
            if attempt > 40:
                raise
            time.sleep(2)

    el = time.time() - t0
    print(f"DONE {got} bytes in {el:.1f}s")

    # Hash after complete download (may take a bit for 1.7GB).
    sha = hashlib.sha256()
    with open(out, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            sha.update(chunk)
    digest = sha.hexdigest()
    print(f"SHA256 {digest}")
    with open(out + ".sha256", "w", encoding="utf-8") as f:
        f.write(digest + "  " + os.path.basename(out) + "\n")


if __name__ == "__main__":
    main()
