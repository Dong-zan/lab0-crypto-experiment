"""Reproducible measurements and failure cases for the Lab0 report."""

from __future__ import annotations

import json
import platform

import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

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
    rounds = []
    for name, message in messages.items():
        plaintext_bytes = len(message.encode("utf-8"))
        aes = aes_demo(message)
        hybrid = hybrid_demo(message)
        entry: dict[str, object] = {
            "case": name,
            "plaintext_bytes": plaintext_bytes,
            "aes_ciphertext_bytes": aes.ciphertext_bytes,
            "aes_elapsed_ms": aes.elapsed_ms,
            "hybrid_ciphertext_bytes": hybrid.ciphertext_bytes,
            "hybrid_elapsed_ms": hybrid.elapsed_ms,
        }
        if plaintext_bytes <= 190:
            entry["rsa_ciphertext_bytes"] = rsa_demo(message).ciphertext_bytes
        else:
            entry["rsa_result"] = "not applicable: RSA-OAEP limit"
        rounds.append(entry)

    limit = rsa_oaep_limit_case()
    return {
        "environment": {
            "python": platform.python_version(),
            "cryptography": cryptography.__version__,
        },
        "round_trips": rounds,
        "rsa_limit": {
            "key_bits": limit["rsa_key_bits"],
            "sha256_oaep_max_plaintext_bytes": limit["oaep_sha256_max_plaintext_bytes"],
            "190_bytes": f"accepted, {limit['190_bytes_ciphertext_bytes']}-byte ciphertext",
            "191_bytes": f"rejected with {limit['191_bytes_result']}",
        },
    }


if __name__ == "__main__":
    print(json.dumps(run_suite(), ensure_ascii=False, indent=2))
