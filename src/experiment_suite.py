"""Reproducible measurements and failure cases for the Lab0 report."""

from __future__ import annotations

import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    from src.crypto_demo import aes_demo, hybrid_demo, rsa_demo
except ModuleNotFoundError:
    from crypto_demo import aes_demo, hybrid_demo, rsa_demo


def rsa_oaep_limit_case() -> dict[str, object]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    oaep = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )
    accepted = len(public_key.encrypt(b"A" * 190, oaep))
    try:
        public_key.encrypt(b"A" * 191, oaep)
    except ValueError as error:
        rejected = type(error).__name__
    else:
        rejected = "not-rejected"
    return {
        "rsa_key_bits": 2048,
        "oaep_sha256_max_plaintext_bytes": 190,
        "190_bytes_ciphertext_bytes": accepted,
        "191_bytes_result": rejected,
    }


def run_suite() -> dict[str, object]:
    messages = {
        "short": "Lab0",
        "medium": "Big Data Security Lab0: cryptography experiment " * 8,
        "long": "A" * 1024,
    }
    rounds = {}
    for name, message in messages.items():
        rounds[name] = {
            "plaintext_bytes": len(message.encode("utf-8")),
            "aes": aes_demo(message).__dict__,
            "rsa": rsa_demo(message).__dict__ if len(message.encode("utf-8")) <= 190 else "not applicable: RSA-OAEP limit",
            "hybrid": hybrid_demo(message).__dict__,
        }
    return {
        "round_trips": rounds,
        "rsa_limit": rsa_oaep_limit_case(),
        "note": "Timings are indicative single-run measurements, not a benchmark.",
    }


if __name__ == "__main__":
    print(json.dumps(run_suite(), ensure_ascii=False, indent=2))
