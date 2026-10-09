"""Certificate-backed RSA+AES hybrid encryption demonstration."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509.oid import NameOID


def create_alice_certificate() -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Lab0 Demo"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Alice"),
        ]
    )
    now = datetime.now(timezone.utc)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )
    return private_key, certificate


def hybrid_encrypt_with_certificate(message: str) -> dict[str, object]:
    alice_private_key, certificate = create_alice_certificate()
    plaintext = message.encode("utf-8")
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, None)
    oaep = padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )
    encrypted_key = certificate.public_key().encrypt(aes_key, oaep)
    recovered_key = alice_private_key.decrypt(encrypted_key, oaep)
    decrypted = AESGCM(recovered_key).decrypt(nonce, ciphertext, None)
    return {
        "certificate_subject": certificate.subject.rfc4514_string(),
        "certificate_issuer": certificate.issuer.rfc4514_string(),
        "certificate_serial": str(certificate.serial_number),
        "certificate_public_key_bits": certificate.public_key().key_size,
        "certificate_signature": certificate.signature_hash_algorithm.name,
        "plaintext_bytes": len(plaintext),
        "encrypted_key_bytes": len(encrypted_key),
        "ciphertext_bytes": len(ciphertext),
        "decrypted_text": decrypted.decode("utf-8"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Certificate-backed hybrid encryption demo")
    parser.add_argument("--message", default="Certificate-backed Lab0 message")
    args = parser.parse_args()
    print(json.dumps(hybrid_encrypt_with_certificate(args.message), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
