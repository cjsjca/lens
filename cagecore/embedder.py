
"""
Embedder (deterministic placeholder embedding)
Converts text to 8-dimensional vectors using stable hashing.
"""

import hashlib


def vector(text: str):
    """Convert text to 8-dimensional vector using deterministic hashing"""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vals = []
    for i in range(8):
        # two bytes -> int -> map to [-1,1]
        n = int.from_bytes(h[2*i:2*i+2], "big")
        vals.append((n % 2001)/1000.0 - 1.0)
    return vals
