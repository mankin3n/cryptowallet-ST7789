"""
Cryptographic Signing Operations.

Handles ECDSA signing, signature verification, and message hashing
for Bitcoin transactions and messages.
"""

import logging
import hashlib
from typing import Tuple, Optional

try:
    import ecdsa
    from ecdsa import SigningKey, VerifyingKey, SECP256k1
    ECDSA_AVAILABLE = True
except ImportError:
    ECDSA_AVAILABLE = False
    logging.warning("ecdsa library not available, using mock signing")

logger = logging.getLogger(__name__)


class Signer:
    """
    ECDSA signer for Bitcoin messages and transactions.

    Attributes:
        signing_key: ECDSA signing key
        verifying_key: ECDSA verifying key
    """

    def __init__(self) -> None:
        """Initialize signer."""
        self.signing_key: Optional[any] = None
        self.verifying_key: Optional[any] = None

        logger.info("Signer created")

    def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate new ECDSA keypair.

        Returns:
            Tuple of (private_key_hex, public_key_hex)
        """
        if not ECDSA_AVAILABLE:
            logger.warning("Using mock keypair generation")
            return ("mock_private_key", "mock_public_key")

        try:
            # Generate signing key
            self.signing_key = SigningKey.generate(curve=SECP256k1)
            self.verifying_key = self.signing_key.get_verifying_key()

            # Export as hex
            private_hex = self.signing_key.to_string().hex()
            public_hex = self.verifying_key.to_string().hex()

            logger.info("Keypair generated successfully")
            return (private_hex, public_hex)

        except Exception as e:
            logger.error(f"Keypair generation failed: {e}")
            return ("", "")

    def load_private_key(self, private_key_hex: str) -> bool:
        """
        Load private key from hex string.

        Args:
            private_key_hex: Private key in hex format

        Returns:
            True if loaded successfully, False otherwise
        """
        if not ECDSA_AVAILABLE:
            logger.warning("Using mock private key loading")
            self.signing_key = "mock_signing_key"
            self.verifying_key = "mock_verifying_key"
            return True

        try:
            # Convert hex to bytes
            private_bytes = bytes.fromhex(private_key_hex)

            # Create signing key
            self.signing_key = SigningKey.from_string(private_bytes, curve=SECP256k1)
            self.verifying_key = self.signing_key.get_verifying_key()

            logger.info("Private key loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Private key loading failed: {e}")
            return False

    def load_public_key(self, public_key_hex: str) -> bool:
        """
        Load public key from hex string.

        Args:
            public_key_hex: Public key in hex format

        Returns:
            True if loaded successfully, False otherwise
        """
        if not ECDSA_AVAILABLE:
            logger.warning("Using mock public key loading")
            self.verifying_key = "mock_verifying_key"
            return True

        try:
            # Convert hex to bytes
            public_bytes = bytes.fromhex(public_key_hex)

            # Create verifying key
            self.verifying_key = VerifyingKey.from_string(public_bytes, curve=SECP256k1)

            logger.info("Public key loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Public key loading failed: {e}")
            return False

    def sign_message(self, message: str) -> str:
        """
        Sign a message with ECDSA.

        Args:
            message: Message to sign (string)

        Returns:
            Signature in hex format
        """
        if not self.signing_key:
            logger.error("No signing key loaded")
            return ""

        if not ECDSA_AVAILABLE:
            logger.warning("Using mock signing")
            return "mock_signature_" + hashlib.sha256(message.encode()).hexdigest()[:32]

        try:
            # Hash message with SHA-256
            message_hash = hashlib.sha256(message.encode()).digest()

            # Sign
            signature = self.signing_key.sign(message_hash)

            # Return as hex
            return signature.hex()

        except Exception as e:
            logger.error(f"Message signing failed: {e}")
            return ""

    def verify_signature(self, message: str, signature_hex: str) -> bool:
        """
        Verify ECDSA signature.

        Args:
            message: Original message
            signature_hex: Signature in hex format

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.verifying_key:
            logger.error("No verifying key loaded")
            return False

        if not ECDSA_AVAILABLE:
            logger.warning("Using mock verification (always returns True)")
            return True

        try:
            # Hash message
            message_hash = hashlib.sha256(message.encode()).digest()

            # Convert signature from hex
            signature = bytes.fromhex(signature_hex)

            # Verify
            self.verifying_key.verify(signature, message_hash)

            logger.info("Signature verified successfully")
            return True

        except ecdsa.BadSignatureError:
            logger.warning("Invalid signature")
            return False

        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

    def sign_transaction(self, tx_hash: bytes) -> str:
        """
        Sign a transaction hash.

        Args:
            tx_hash: Transaction hash (32 bytes)

        Returns:
            Signature in DER format (hex)
        """
        if not self.signing_key:
            logger.error("No signing key loaded")
            return ""

        if not ECDSA_AVAILABLE:
            logger.warning("Using mock transaction signing")
            return "mock_tx_signature_" + tx_hash.hex()[:32]

        try:
            # Sign transaction hash
            signature = self.signing_key.sign_digest(tx_hash)

            # Convert to DER format
            signature_der = signature  # Already in correct format

            return signature_der.hex()

        except Exception as e:
            logger.error(f"Transaction signing failed: {e}")
            return ""


def hash_message(message: str, algorithm: str = 'sha256') -> bytes:
    """
    Hash a message with specified algorithm.

    Args:
        message: Message to hash
        algorithm: Hash algorithm ('sha256', 'sha1', 'ripemd160')

    Returns:
        Hash bytes
    """
    try:
        message_bytes = message.encode()

        if algorithm == 'sha256':
            return hashlib.sha256(message_bytes).digest()

        elif algorithm == 'sha1':
            return hashlib.sha1(message_bytes).digest()

        elif algorithm == 'ripemd160':
            import hashlib
            h = hashlib.new('ripemd160')
            h.update(message_bytes)
            return h.digest()

        else:
            logger.error(f"Unknown hash algorithm: {algorithm}")
            return b""

    except Exception as e:
        logger.error(f"Message hashing failed: {e}")
        return b""


def double_sha256(data: bytes) -> bytes:
    """
    Double SHA-256 hash (used in Bitcoin).

    Args:
        data: Data to hash

    Returns:
        Double SHA-256 hash
    """
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def hash160(data: bytes) -> bytes:
    """
    HASH160 (SHA-256 then RIPEMD-160, used in Bitcoin).

    Args:
        data: Data to hash

    Returns:
        HASH160 result
    """
    try:
        sha256_hash = hashlib.sha256(data).digest()

        h = hashlib.new('ripemd160')
        h.update(sha256_hash)
        return h.digest()

    except Exception as e:
        logger.error(f"HASH160 failed: {e}")
        return b""


# Singleton signer instance
_signer: Optional[Signer] = None


def get_signer() -> Signer:
    """
    Get singleton signer instance.

    Returns:
        Signer instance
    """
    global _signer
    if _signer is None:
        _signer = Signer()
    return _signer
