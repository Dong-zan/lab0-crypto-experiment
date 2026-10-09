import unittest

from src.crypto_demo import aes_demo, hybrid_demo, rsa_demo
from src.certificate_demo import hybrid_encrypt_with_certificate


MESSAGE = "测试明文：confidential message"


class CryptoDemoTests(unittest.TestCase):
    def test_aes_round_trip_and_integrity(self):
        result = aes_demo(MESSAGE)
        self.assertEqual(result.decrypted_text, MESSAGE)
        self.assertTrue(result.tamper_detected)
        self.assertEqual(result.key_bits, 256)

    def test_rsa_round_trip(self):
        result = rsa_demo(MESSAGE)
        self.assertEqual(result.decrypted_text, MESSAGE)
        self.assertEqual(result.ciphertext_bytes, 256)

    def test_hybrid_round_trip_and_integrity(self):
        result = hybrid_demo(MESSAGE)
        self.assertEqual(result.decrypted_text, MESSAGE)
        self.assertTrue(result.tamper_detected)
        self.assertEqual(result.encrypted_key_bytes, 256)

    def test_certificate_backed_hybrid_round_trip(self):
        result = hybrid_encrypt_with_certificate(MESSAGE)
        self.assertEqual(result["decrypted_text"], MESSAGE)
        self.assertEqual(result["certificate_public_key_bits"], 2048)
        self.assertEqual(result["certificate_signature"], "sha256")


if __name__ == "__main__":
    unittest.main()
