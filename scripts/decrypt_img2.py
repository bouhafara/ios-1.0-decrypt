#!/usr/bin/env python3
"""Decrypt IMG2 containers from S5L8900 (iPhone 2G / iOS 1.0).

Usage: python3 decrypt_img2.py <file.img2>
Output: <file.img2>.dec
"""
import sys
import struct

try:
    from Crypto.Cipher import AES
except ImportError:
    sys.exit("Install pycryptodome: pip install pycryptodome")

KEY_0x837 = bytes.fromhex("188458A6D15034DFE386F23B61D43774")
HEADER_SIZE = 0x800


def decrypt_img2(path: str) -> None:
    with open(path, "rb") as f:
        data = f.read()

    size_of_data = struct.unpack("<I", data[0x0C:0x10])[0]
    fmt = data[0x07]
    print(f"Format: 0x{fmt:02x} ({'encrypted' if fmt == 0x03 else 'cleartext'})")

    if fmt == 0x04:
        decrypted = data[HEADER_SIZE:HEADER_SIZE + size_of_data]
    elif fmt == 0x03:
        payload = data[HEADER_SIZE:HEADER_SIZE + size_of_data]
        cipher = AES.new(KEY_0x837, AES.MODE_CBC, b"\x00" * 16)
        decrypted = cipher.decrypt(payload)
    else:
        sys.exit(f"Unsupported format byte: 0x{fmt:02x}")

    out = path + ".dec"
    with open(out, "wb") as f:
        f.write(decrypted)
    print(f"OK {out} ({len(decrypted)} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: decrypt_img2.py <file.img2>")
    decrypt_img2(sys.argv[1])
