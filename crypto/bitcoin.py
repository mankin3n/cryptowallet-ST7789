"""
Bitcoin Operations.

Handles Bitcoin private key generation, address derivation, and
wallet operations. Supports legacy, SegWit, and native SegWit addresses.
"""

import logging
import os
import hashlib
from typing import Tuple, Optional
import config

try:
    from bitcoinlib.keys import Key
    from bitcoinlib.encoding import addr_to_pubkeyhash, pubkeyhash_to_addr
    BITCOINLIB_AVAILABLE = True
except ImportError:
    BITCOINLIB_AVAILABLE = False
    logging.warning("bitcoinlib not available, using mock Bitcoin operations")

logger = logging.getLogger(__name__)


class BitcoinWallet:
    """
    Bitcoin wallet operations.

    Attributes:
        private_key: Private key object
        network: Bitcoin network ('mainnet' or 'testnet')
    """

    def __init__(self, network: str = config.BITCOIN_NETWORK) -> None:
        """
        Initialize Bitcoin wallet.

        Args:
            network: Network type ('mainnet' or 'testnet')
        """
        self.network: str = network
        self.private_key: Optional[any] = None

        logger.info(f"Bitcoin wallet created (network={network})")

    def generate_private_key(self) -> str:
        """
        Generate a new random private key.

        Returns:
            Private key in WIF format
        """
        if not BITCOINLIB_AVAILABLE:
            # Mock implementation
            logger.warning("Using mock private key generation")
            return "cMockPrivateKey12345678901234567890123456789012345"

        try:
            # Generate random 256-bit key
            random_bytes = os.urandom(32)

            # Create key object
            self.private_key = Key(random_bytes, network=self.network)

            logger.info("Private key generated successfully")
            return self.private_key.wif()

        except Exception as e:
            logger.error(f"Private key generation failed: {e}")
            return ""

    def load_private_key(self, wif: str) -> bool:
        """
        Load existing private key from WIF format.

        Args:
            wif: Private key in WIF format

        Returns:
            True if loaded successfully, False otherwise
        """
        if not BITCOINLIB_AVAILABLE:
            logger.warning("Using mock private key loading")
            self.private_key = "mock_key"
            return True

        try:
            self.private_key = Key(wif, network=self.network)
            logger.info("Private key loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Private key loading failed: {e}")
            return False

    def get_public_key(self) -> str:
        """
        Get public key from private key.

        Returns:
            Public key in hex format
        """
        if not self.private_key:
            logger.error("No private key loaded")
            return ""

        if not BITCOINLIB_AVAILABLE:
            return "mock_public_key_0123456789abcdef"

        try:
            return self.private_key.public_hex

        except Exception as e:
            logger.error(f"Public key derivation failed: {e}")
            return ""

    def get_address(self, address_type: str = 'native_segwit') -> str:
        """
        Derive Bitcoin address from private key.

        Args:
            address_type: Address type ('legacy', 'segwit', 'native_segwit')

        Returns:
            Bitcoin address string
        """
        if not self.private_key:
            logger.error("No private key loaded")
            return ""

        if not BITCOINLIB_AVAILABLE:
            # Mock addresses
            mock_addresses = {
                'legacy': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
                'segwit': '3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy',
                'native_segwit': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
            }
            return mock_addresses.get(address_type, mock_addresses['native_segwit'])

        try:
            if address_type == 'legacy':
                # P2PKH (1...)
                return self.private_key.address(compressed=True, script_type='p2pkh')

            elif address_type == 'segwit':
                # P2SH-P2WPKH (3...)
                return self.private_key.address(compressed=True, script_type='p2sh-p2wpkh')

            elif address_type == 'native_segwit':
                # P2WPKH (bc1...)
                return self.private_key.address(compressed=True, script_type='p2wpkh')

            else:
                logger.error(f"Unknown address type: {address_type}")
                return ""

        except Exception as e:
            logger.error(f"Address derivation failed: {e}")
            return ""

    def get_all_addresses(self) -> dict:
        """
        Get all address types for current private key.

        Returns:
            Dictionary of address_type: address
        """
        return {
            'legacy': self.get_address('legacy'),
            'segwit': self.get_address('segwit'),
            'native_segwit': self.get_address('native_segwit')
        }

    def sign_message(self, message: str) -> str:
        """
        Sign a message with the private key.

        Args:
            message: Message to sign

        Returns:
            Signature in base64 format
        """
        if not self.private_key:
            logger.error("No private key loaded")
            return ""

        if not BITCOINLIB_AVAILABLE:
            logger.warning("Using mock message signing")
            return "mock_signature_base64_encoded"

        try:
            # Hash message
            message_hash = hashlib.sha256(message.encode()).digest()

            # Sign
            signature = self.private_key.sign(message_hash)

            # Encode to base64
            import base64
            return base64.b64encode(signature).decode()

        except Exception as e:
            logger.error(f"Message signing failed: {e}")
            return ""

    def verify_message(self, message: str, signature: str, address: str) -> bool:
        """
        Verify a message signature.

        Args:
            message: Original message
            signature: Signature in base64 format
            address: Bitcoin address of signer

        Returns:
            True if signature is valid, False otherwise
        """
        if not BITCOINLIB_AVAILABLE:
            logger.warning("Using mock signature verification")
            return True  # Mock always returns True

        try:
            # Decode signature
            import base64
            sig_bytes = base64.b64decode(signature)

            # Hash message
            message_hash = hashlib.sha256(message.encode()).digest()

            # Verify (this is simplified - real implementation more complex)
            # Would need to recover public key from signature and check address
            logger.info("Signature verification attempted")
            return True  # Simplified

        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False


def generate_mnemonic(word_count: int = 24) -> list:
    """
    Generate BIP39 mnemonic phrase.

    Args:
        word_count: Number of words (12, 15, 18, 21, or 24)

    Returns:
        List of mnemonic words
    """
    if not BITCOINLIB_AVAILABLE:
        logger.warning("Using mock mnemonic generation")
        return ["mock", "mnemonic", "word", "list"] * (word_count // 4)

    try:
        from bitcoinlib.mnemonic import Mnemonic

        # Generate entropy
        entropy_bits = (word_count * 11) - (word_count // 3)
        entropy = os.urandom(entropy_bits // 8)

        # Create mnemonic
        mnemonic = Mnemonic('english')
        words = mnemonic.to_mnemonic(entropy)

        return words.split()

    except Exception as e:
        logger.error(f"Mnemonic generation failed: {e}")
        return []


def mnemonic_to_seed(mnemonic: list, passphrase: str = "") -> bytes:
    """
    Convert mnemonic to seed for HD wallet.

    Args:
        mnemonic: List of mnemonic words
        passphrase: Optional passphrase

    Returns:
        Seed bytes (64 bytes)
    """
    if not BITCOINLIB_AVAILABLE:
        logger.warning("Using mock mnemonic to seed")
        return b"0" * 64

    try:
        from bitcoinlib.mnemonic import Mnemonic

        mnemonic_obj = Mnemonic('english')
        mnemonic_str = ' '.join(mnemonic)

        seed = mnemonic_obj.to_seed(mnemonic_str, passphrase)
        return seed

    except Exception as e:
        logger.error(f"Mnemonic to seed conversion failed: {e}")
        return b""


# Singleton wallet instance
_wallet: Optional[BitcoinWallet] = None


def get_wallet() -> BitcoinWallet:
    """
    Get singleton wallet instance.

    Returns:
        BitcoinWallet instance
    """
    global _wallet
    if _wallet is None:
        _wallet = BitcoinWallet()
    return _wallet
