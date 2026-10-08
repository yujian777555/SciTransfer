"""Download ScienceAgentBench benchmark_verified.zip with safe resume semantics.

R2 fixes:
- Single-writer file lock (refuses concurrent download)
- Strict Content-Range validation on 206 (must match requested start byte)
- Reject mismatched/missing Content-Range WITHOUT writing body
- HTTP 200 on resume → download to a new staged file, then atomically replace
- HTTP 416 → validate full file, never silently append
- Staged .part file with atomic rename after validation
- Final validation: exact byte length + ZIP central directory test
- Bounded retries with explicit error reporting
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
import ssl
import http.cookiejar
from pathlib import Path

EXPECTED_SIZE = 1_769_478_786  # benchmark_verified.zip
SHARE_URL = (
    "https://buckeyemailosu-my.sharepoint.com/:u:/g/personal/"
    "chen_8336_osu_edu/IQB870QrmuqwS5Ck33cHpJfkAVt3LsMeariREIwP3AT7byA?download=1"
)
LOCK_SUFFIX = ".download.lock"
PART_SUFFIX = ".part"
MAX_RETRIES = 50
CHUNK_SIZE = 1024 * 1024  # 1 MB


def acquire_lock(lock_path: Path) -> bool:
    """Try to acquire an exclusive lock file. Returns True if acquired."""
    try:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False


def release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def validate_zip(path: Path, password: str | None = None) -> tuple[bool, str]:
    """Check ZIP central directory and basic integrity. Returns (ok, message).

    If password is provided, also test extraction. For encrypted archives
    without password, we verify the central directory can be read (which
    proves the file is a structurally valid ZIP).
    """
    import zipfile

    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            if not names:
                return False, "ZIP has no entries"
            # Check central directory is readable (this proves structural validity)
            infos = zf.infolist()
            if len(infos) != len(names):
                return False, f"Entry count mismatch: {len(infos)} vs {len(names)}"
            # Try to test integrity. For encrypted archives, testzip will fail
            # on extraction but that's expected without password.
            try:
                bad = zf.testzip()
                if bad is not None:
                    return False, f"Corrupt entry: {bad}"
            except RuntimeError as e:
                if "password" in str(e).lower() or "encrypted" in str(e).lower():
                    # Expected for password-protected archives
                    return True, f"ZIP OK: {len(names)} entries (encrypted, password required for extraction)"
                raise
            return True, f"ZIP OK: {len(names)} entries (tested)"
    except zipfile.BadZipFile as e:
        return False, f"BadZipFile: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def parse_content_range(value: str) -> tuple[int, int, int] | None:
    """Parse 'bytes start-end/total' → (start, end, total)."""
    try:
        # e.g. "bytes 100-199/1000"
        parts = value.split()[1]  # "100-199/1000"
        range_part, total_part = parts.split("/")
        start_str, end_str = range_part.split("-")
        return int(start_str), int(end_str), int(total_part)
    except (IndexError, ValueError):
        return None


def download(url: str, out_path: Path) -> dict:
    """Download with safe resume. Returns status dict."""
    out_path = Path(out_path)
    lock_path = out_path.with_suffix(out_path.suffix + LOCK_SUFFIX)
    part_path = out_path.with_suffix(out_path.suffix + PART_SUFFIX)

    # --- Single-writer lock ---
    if not acquire_lock(lock_path):
        return {
            "status": "LOCKED",
            "error": f"Another download holds the lock: {lock_path}. "
            f"Remove it only if the process is confirmed dead.",
        }
    try:
        return _do_download(url, out_path, part_path)
    finally:
        release_lock(lock_path)


def _do_download(url: str, out_path: Path, part_path: Path) -> dict:
    # --- Initialize: if .part exists use it; if final exists but wrong size, move to .part ---
    if part_path.exists():
        got = part_path.stat().st_size
    elif out_path.exists():
        size = out_path.stat().st_size
        if size == EXPECTED_SIZE:
            ok, msg = validate_zip(out_path)
            if ok:
                return {"status": "ALREADY_COMPLETE", "size": size, "validation": msg}
        # Partial or oversized final → rename to .part for resume
        got = size
        out_path.rename(part_path)
    else:
        got = 0

    ctx = ssl.create_default_context()
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=ctx),
    )
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    ]
    # Warm up session cookies (SharePoint needs this for anonymous links).
    # SSL errors can occur due to proxy MITM; retry with brief backoff.
    for warmup_try in range(5):
        try:
            opener.open(url, timeout=30).read(10)
            break
        except Exception as e:
            print(f"  warmup attempt {warmup_try + 1}: {type(e).__name__}: {e}", flush=True)
            time.sleep(2)
    else:
        return {
            "status": "FAILED",
            "error": f"Could not establish session after 5 attempts: network/SSL error",
            "got": got,
        }

    attempt = 0
    t0 = time.time()
    total = EXPECTED_SIZE

    while True:
        attempt += 1
        if attempt > MAX_RETRIES:
            return {
                "status": "FAILED",
                "error": f"Gave up after {MAX_RETRIES} attempts. got={got}/{total}",
                "got": got,
            }

        headers = {"User-Agent": "Mozilla/5.0"}
        if got > 0:
            headers["Range"] = f"bytes={got}-"

        req = urllib.request.Request(url, headers=headers)
        try:
            r = opener.open(req, timeout=180)
            status = getattr(r, "status", r.getcode())
        except urllib.error.HTTPError as e:
            if e.code == 416:
                # Range not satisfiable — check if we have the full file
                if got == EXPECTED_SIZE:
                    ok, msg = validate_zip(part_path)
                    if ok:
                        part_path.rename(out_path)
                        return {
                            "status": "ALREADY_COMPLETE",
                            "size": got,
                            "validation": msg,
                        }
                    else:
                        return {
                            "status": "FAILED",
                            "error": f"416 but validation failed: {msg}",
                            "got": got,
                        }
                else:
                    # Reset and retry from scratch
                    part_path.unlink(missing_ok=True)
                    got = 0
                    continue
            else:
                print(f"  attempt {attempt}: HTTP {e.code}: {e.reason}", flush=True)
                time.sleep(3)
                continue
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}"
            print(f"  attempt {attempt}: {err_msg}", flush=True)
            # SSL/proxy errors: retry with backoff
            time.sleep(3)
            continue

        # --- HTTP 200: full response (server ignored Range) ---
        if status == 200:
            if got > 0:
                # Server ignored our Range request. Download to a STAGED new file.
                print(f"  Server returned 200 (no Range support). Restarting to staged file.", flush=True)
                # Don't touch existing .part; write to a temp name
                staged = part_path.with_suffix(".restart")
                got2 = 0
                content_length = int(r.headers.get("Content-Length", 0))
                if content_length and content_length != EXPECTED_SIZE:
                    print(f"  Content-Length {content_length} != expected {EXPECTED_SIZE}", flush=True)

                with staged.open("wb") as f:
                    while True:
                        chunk = r.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        got2 += len(chunk)
                        if got2 % (20 * CHUNK_SIZE) < CHUNK_SIZE:
                            el = time.time() - t0
                            rate = got2 / 1e6 / el if el > 0 else 0
                            print(f"  {got2 / 1e6:.1f} / {EXPECTED_SIZE / 1e6:.1f} MB ({100 * got2 / EXPECTED_SIZE:.1f}%) {rate:.1f} MB/s", flush=True)

                if got2 == EXPECTED_SIZE:
                    staged.replace(part_path)  # atomic replace old partial
                    got = got2
                    break
                else:
                    print(f"  Incomplete download: {got2}/{EXPECTED_SIZE}", flush=True)
                    staged.unlink(missing_ok=True)
                    continue
            else:
                # Fresh full download
                content_length = int(r.headers.get("Content-Length", 0))
                print(f"  Full download starting. Content-Length={content_length}", flush=True)
                with part_path.open("wb") as f:
                    while True:
                        chunk = r.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        if got % (20 * CHUNK_SIZE) < CHUNK_SIZE:
                            el = time.time() - t0
                            rate = got / 1e6 / el if el > 0 else 0
                            print(f"  {got / 1e6:.1f} / {EXPECTED_SIZE / 1e6:.1f} MB ({100 * got / EXPECTED_SIZE:.1f}%) {rate:.1f} MB/s", flush=True)

                if got == EXPECTED_SIZE:
                    break
                else:
                    print(f"  Incomplete download: {got}/{EXPECTED_SIZE}", flush=True)
                    continue

        # --- HTTP 206: partial response ---
        elif status == 206:
            content_range = r.headers.get("Content-Range", "")
            if not content_range:
                print(f"  attempt {attempt}: 206 but missing Content-Range. Rejecting body.", flush=True)
                r.read(1)  # drain a bit then discard
                r.close()
                time.sleep(2)
                continue

            parsed = parse_content_range(content_range)
            if parsed is None:
                print(f"  attempt {attempt}: 206 but unparseable Content-Range: {content_range!r}. Rejecting.", flush=True)
                r.close()
                time.sleep(2)
                continue

            range_start, range_end, range_total = parsed
            if range_start != got:
                print(
                    f"  attempt {attempt}: Content-Range start {range_start} != local {got}. Rejecting body.",
                    flush=True,
                )
                r.close()
                time.sleep(2)
                continue

            if range_total != EXPECTED_SIZE:
                print(
                    f"  attempt {attempt}: Content-Range total {range_total} != expected {EXPECTED_SIZE}. Rejecting.",
                    flush=True,
                )
                r.close()
                time.sleep(2)
                continue

            total = range_total
            content_length = int(r.headers.get("Content-Length", 0))
            expected_chunk = range_end - range_start + 1
            if content_length and content_length != expected_chunk:
                print(
                    f"  attempt {attempt}: Content-Length {content_length} != range size {expected_chunk}. Continuing with caution.",
                    flush=True,
                )

            print(f"  attempt {attempt}: 206 OK, resuming from {got} to {range_end + 1}", flush=True)

            with part_path.open("ab") as f:
                written = 0
                while written < expected_chunk:
                    chunk = r.read(min(CHUNK_SIZE, expected_chunk - written))
                    if not chunk:
                        break
                    f.write(chunk)
                    written += len(chunk)
                    got += len(chunk)
                    if got % (20 * CHUNK_SIZE) < CHUNK_SIZE:
                        el = time.time() - t0
                        rate = got / 1e6 / el if el > 0 else 0
                        print(f"  {got / 1e6:.1f} / {total / 1e6:.1f} MB ({100 * got / total:.1f}%) {rate:.1f} MB/s", flush=True)

            if written < expected_chunk:
                print(f"  Premature EOF: wrote {written}/{expected_chunk}. Will retry.", flush=True)

            if got >= total:
                break
        else:
            print(f"  attempt {attempt}: Unexpected status {status}", flush=True)
            time.sleep(3)

    # --- Final validation ---
    final_size = part_path.stat().st_size
    if final_size != EXPECTED_SIZE:
        return {
            "status": "FAILED",
            "error": f"Final size {final_size} != expected {EXPECTED_SIZE}",
            "got": final_size,
        }

    ok, msg = validate_zip(part_path)
    if not ok:
        return {
            "status": "FAILED",
            "error": f"ZIP validation failed: {msg}",
            "got": final_size,
        }

    # Atomic rename
    part_path.rename(out_path)

    # SHA256
    sha = hashlib.sha256()
    with out_path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            sha.update(chunk)

    return {
        "status": "COMPLETE",
        "size": final_size,
        "sha256": sha.hexdigest(),
        "validation": msg,
        "duration_s": round(time.time() - t0, 1),
    }


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../sab-artifacts")
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "benchmark_verified.zip"

    print(f"Target: {out_path}")
    print(f"Expected size: {EXPECTED_SIZE:,} bytes")
    print(f"Current state: {out_path.stat().st_size if out_path.exists() else 0:,} bytes")

    result = download(SHARE_URL, out_path)
    print(f"\nResult: {json.dumps(result, indent=2)}")

    if result["status"] in ("COMPLETE", "ALREADY_COMPLETE"):
        sha_path = out_path.with_suffix(".zip.sha256")
        sha_path.write_text(result.get("sha256", "") + "  " + out_path.name + "\n")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
