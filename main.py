#!/usr/bin/env python3
"""THE WORLD TODAY - Saturday 21 November 2026 front page.

Copies the pre-rendered front page (news.png, next to this file) to
$MAKEFUN_OUTPUT_DIR/entry.png, byte for byte.

Standard library only, no network. Deterministic: both runs write
identical bytes because the source image is fixed and copied verbatim.
"""

import hashlib
import os
import struct
import sys

SOURCE_NAME = "news.png"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1048576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not output_dir:
        fail("MAKEFUN_OUTPUT_DIR is not set; "
             "run with MAKEFUN_OUTPUT_DIR=out python3 main.py")

    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source_path):
        fail(f"source image not found: {source_path}")

    with open(source_path, "rb") as handle:
        data = handle.read()

    if len(data) > MAX_BYTES:
        fail(f"source image is {len(data)} bytes, over the "
             f"{MAX_BYTES} byte limit")
    if data[:8] != PNG_MAGIC:
        fail("source image is not a PNG (bad magic bytes)")

    # Read width/height from the IHDR chunk (bytes 16..24, big-endian).
    if len(data) < 24:
        fail("source image is too short to hold a PNG header")
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        fail(f"source image is {width}x{height}, over the "
             f"{MAX_DIMENSION}x{MAX_DIMENSION} limit")

    digest = hashlib.sha256(data).hexdigest()
    output_path = os.path.join(output_dir, OUTPUT_NAME)
    with open(output_path, "wb") as handle:
        handle.write(data)
    os.chmod(output_path, 0o644)

    # Integrity check: re-read what was written and compare digests.
    with open(output_path, "rb") as handle:
        written = handle.read()
    written_digest = hashlib.sha256(written).hexdigest()
    if written_digest != digest:
        fail("integrity check failed: entry.png digest differs "
             "from news.png digest")

    print(f"wrote {output_path} ({len(data)} bytes, {width}x{height})")
    print(f"sha256 news.png:  {digest}")
    print(f"sha256 entry.png: {written_digest}")
    print("integrity check: OK (digests match)")


if __name__ == "__main__":
    main()
