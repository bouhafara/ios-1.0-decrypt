#!/usr/bin/env python3
"""Decompress Apple complzss kernelcaches (iOS 1.0 convention).

iOS 1.0 uses an inverted nibble convention compared to the classic docs:
    pos    = ((b2 & 0x0F) << 8) | b1
    length = (b2 >> 4) + 3

Usage: python3 unlzss.py <kernelcache.dec>
Output: <kernelcache.dec>.raw
"""
import sys


def unlzss(data: bytes, start: int = 0, expected_size: int | None = None) -> bytes:
    out = bytearray()
    i = start
    while i < len(data):
        if expected_size and len(out) >= expected_size:
            break
        flags = data[i]
        i += 1
        for bit in range(8):
            if i >= len(data):
                break
            if expected_size and len(out) >= expected_size:
                break
            if flags & (1 << bit):
                out.append(data[i])
                i += 1
            else:
                if i + 1 >= len(data):
                    break
                b1, b2 = data[i], data[i + 1]
                i += 2
                pos = ((b2 & 0x0F) << 8) | b1
                length = (b2 >> 4) + 3
                src = len(out) - pos - 1
                if src < 0:
                    src = 0
                for k in range(length):
                    if expected_size and len(out) >= expected_size:
                        break
                    out.append(out[src + k] if src + k < len(out) else 0)
    return bytes(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: unlzss.py <kernelcache.dec>")
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    data_size = int.from_bytes(data[0x0C:0x10], "big")
    dec = unlzss(data, 0x14, expected_size=data_size)
    print(f"Decompressed: {len(dec)} / {data_size} bytes")
    with open(sys.argv[1] + ".raw", "wb") as f:
        f.write(dec)
