"""Lab0 AES, RSA and hybrid encryption demonstration."""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import asdict, dataclass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass
class AesResult:
    algorithm: str
    key_bits: int
    nonce_bytes: int
    plaintext_bytes: int
    ciphertext_bytes: int
    elapsed_ms: float
    decrypted_text: str
    tamper_detected: bool


@dataclass
class RsaResult:
    algorithm: str
    key_bits: int
    plaintext_bytes: int
    ciphertext_bytes: int
    elapsed_ms: float
    decrypted_text: str


@dataclass
class HybridResult:
    key_transport: str
    data_encryption: str
    rsa_key_bits: int
    aes_key_bits: int
    nonce_bytes: int
    plaintext_bytes: int
    encrypted_key_bytes: int
    ciphertext_bytes: int
    elapsed_ms: float
    decrypted_text: str
    tamper_detected: bool


def aes_demo(message: str) -> AesResult:
    plaintext = message.encode("utf-8")
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    cipher = AESGCM(key)
    started = time.perf_counter()
    ciphertext = cipher.encrypt(nonce, plaintext, None)
    decrypted = cipher.decrypt(nonce, ciphertext, None)
    elapsed_ms = (time.perf_counter() - started) * 1000
    tampered = bytearray(ciphertext)
    tampered[0] ^= 1
    try:
        cipher.decrypt(nonce, bytes(tampered), None)
    except Exception:
        tamper_detected = True
    else:
        tamper_detected = False
    return AesResult(
        algorithm="AES-256-GCM",
        key_bits=256,
        nonce_bytes=len(nonce),
        plaintext_bytes=len(plaintext),
        ciphertext_bytes=len(ciphertext),
        elapsed_ms=round(elapsed_ms, 3),
        decrypted_text=decrypted.decode("utf-8"),
        tamper_detected=tamper_detected,
    )


def rsa_demo(message: str) -> RsaResult:
    plaintext = message.encode("utf-8")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    started = time.perf_counter()
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    decrypted = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    return RsaResult(
        algorithm="RSA-OAEP-SHA256",
        key_bits=2048,
        plaintext_bytes=len(plaintext),
        ciphertext_bytes=len(ciphertext),
        elapsed_ms=round(elapsed_ms, 3),
        decrypted_text=decrypted.decode("utf-8"),
    )


def hybrid_demo(message: str) -> HybridResult:
    plaintext = message.encode("utf-8")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    aes = AESGCM(aes_key)
    started = time.perf_counter()
    ciphertext = aes.encrypt(nonce, plaintext, None)
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    recovered_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    decrypted = AESGCM(recovered_key).decrypt(nonce, ciphertext, None)
    elapsed_ms = (time.perf_counter() - started) * 1000
    tampered = bytearray(ciphertext)
    tampered[-1] ^= 1
    try:
        AESGCM(recovered_key).decrypt(nonce, bytes(tampered), None)
    except Exception:
        tamper_detected = True
    else:
        tamper_detected = False
    return HybridResult(
        key_transport="RSA-OAEP-SHA256",
        data_encryption="AES-256-GCM",
        rsa_key_bits=2048,
        aes_key_bits=256,
        nonce_bytes=len(nonce),
        plaintext_bytes=len(plaintext),
        encrypted_key_bytes=len(encrypted_key),
        ciphertext_bytes=len(ciphertext),
        elapsed_ms=round(elapsed_ms, 3),
        decrypted_text=decrypted.decode("utf-8"),
        tamper_detected=tamper_detected,
    )


def run(message: str) -> dict[str, dict]:
    return {
        "aes": asdict(aes_demo(message)),
        "rsa": asdict(rsa_demo(message)),
        "hybrid": asdict(hybrid_demo(message)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab0 cryptography demonstration")
    parser.add_argument(
        "--message",
        default="大数据安全 Lab0：密码学基础实验",
        help="UTF-8 plaintext used by all demonstrations",
    )
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    results = run(args.message)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print("Lab0 cryptography demonstration")
    for name, result in results.items():
        print(f"\n[{name}] {json.dumps(result, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
