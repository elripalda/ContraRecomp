"""Rebuild the ROM from the CONTRA_ROM_0..7 secrets (see upload-rom-secret.sh).

    python tools/release/restore_rom.py contra.nes [parts.b64]

The release workflow writes the secrets into a file (Windows limits one
environment variable to 32,767 characters, less than a part); without a file
the parts are read from CONTRA_ROM_0..7 environment variables. The result
must be Contra (USA); anything else stops the
build.
"""
import base64
import hashlib
import lzma
import os
import sys

# SHA-256 of the ROM after its 16-byte iNES header (the header varies by dump
# tool; the game data does not).
EXPECTED = "d41e28b1a33b3b6768e7c39c9fdfb1fda4b49940542d14085911fabd399e1ca9"


def main() -> int:
    out = sys.argv[1] if len(sys.argv) > 1 else "contra.nes"
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="ascii") as f:
            text = "".join(f.read().split())
    else:
        parts = [os.environ.get(f"CONTRA_ROM_{i}", "") for i in range(8)]
        text = "".join(p.strip() for p in parts)
    if not text:
        print("No CONTRA_ROM_* secrets: run tools/release/upload-rom-secret.sh first",
              file=sys.stderr)
        return 1
    rom = lzma.decompress(base64.b64decode(text))
    digest = hashlib.sha256(rom[16:]).hexdigest()
    if digest != EXPECTED:
        print(f"The stored ROM is not Contra (USA): {digest}", file=sys.stderr)
        return 1
    with open(out, "wb") as f:
        f.write(rom)
    print(f"ROM restored ({len(rom)} bytes, verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
