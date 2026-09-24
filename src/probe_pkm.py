"""Sonda de un archivo .pkm de FM24 (spike INV-01).

No decodifica el formato: responde si vale la pena intentarlo.
Informa cabecera, entropía por bloque y si hay tramos que zlib/gzip/lzma
puedan descomprimir. Uso:

    python src/probe_pkm.py "C:/Users/<usuario>/Documents/Sports Interactive/Football Manager 2024/matches/partido.pkm"
"""
import lzma
import math
import sys
import zlib
from collections import Counter
from pathlib import Path

BLOCK = 64 * 1024


def entropy(data):
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def try_decompress(data):
    """Busca offsets donde arranca un stream comprimido conocido."""
    hits = []
    for offset in range(0, min(len(data), 4096)):
        chunk = data[offset:offset + BLOCK]
        for name, wbits in (("zlib", 15), ("gzip", 31), ("deflate crudo", -15)):
            try:
                out = zlib.decompressobj(wbits).decompress(chunk)
            except zlib.error:
                continue
            if len(out) > 256:
                hits.append((offset, name, len(out)))
        if chunk[:6] == b"\xfd7zXZ\x00":
            try:
                out = lzma.decompress(data[offset:])
                hits.append((offset, "xz", len(out)))
            except lzma.LZMAError:
                pass
    return hits


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    path = Path(sys.argv[1])
    data = path.read_bytes()

    print(f"Archivo: {path.name}")
    print(f"Tamaño:  {len(data) / (1024 * 1024):.2f} MB")
    print(f"Cabecera (64 bytes): {data[:64].hex(' ')}")
    print(f"Cabecera ASCII:      {data[:64].decode('ascii', errors='replace')}")

    print("\nEntropía por bloque de 64 KB (8.0 = comprimido o cifrado):")
    for i in range(0, len(data), BLOCK):
        if i // BLOCK >= 10:
            print("  ...")
            break
        print(f"  offset {i:>10}: {entropy(data[i:i + BLOCK]):.3f}")
    print(f"  archivo completo: {entropy(data):.3f}")

    print("\nStreams descomprimibles en los primeros 4 KB:")
    hits = try_decompress(data)
    if not hits:
        print("  ninguno (formato propio o cifrado)")
    for offset, name, size in hits[:20]:
        print(f"  offset {offset}: {name} -> {size} bytes")


if __name__ == "__main__":
    main()
