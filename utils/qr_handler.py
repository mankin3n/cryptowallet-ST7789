"""
QR Code Handler.

Generates QR codes and scans them from camera images.
Supports various data types and error correction levels.
"""

import logging
from typing import Optional, List
from PIL import Image
import qrcode
import config

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    logging.warning("pyzbar not available, QR scanning disabled")

logger = logging.getLogger(__name__)


class QRHandler:
    """
    QR code generator and scanner.

    Attributes:
        error_correction: QR error correction level
    """

    def __init__(self) -> None:
        """Initialize QR handler."""
        self.error_correction = qrcode.constants.ERROR_CORRECT_H
        logger.info("QR handler created")

    def generate_qr(
        self,
        data: str,
        size: int = config.QR_MAX_SIZE,
        border: int = config.QR_BORDER
    ) -> Image.Image:
        """
        Generate QR code image.

        Args:
            data: Data to encode
            size: QR code size in pixels
            border: Border size in boxes

        Returns:
            PIL Image of QR code
        """
        try:
            qr = qrcode.QRCode(
                version=config.QR_VERSION,
                error_correction=self.error_correction,
                box_size=config.QR_BOX_SIZE,
                border=border,
            )

            qr.add_data(data)
            qr.make(fit=True)

            # Create image
            qr_image = qr.make_image(fill_color="black", back_color="white")

            # Resize to target size
            qr_image = qr_image.resize((size, size), Image.Resampling.NEAREST)

            logger.debug(f"QR code generated: {len(data)} bytes")
            return qr_image.convert('RGB')

        except Exception as e:
            logger.error(f"QR code generation failed: {e}")
            # Return error placeholder
            error_image = Image.new('RGB', (size, size), config.COLOR_RED)
            return error_image

    def scan_qr(self, image: Image.Image) -> Optional[str]:
        """
        Scan QR code from image.

        Args:
            image: PIL Image containing QR code

        Returns:
            Decoded data string or None if no QR found
        """
        if not PYZBAR_AVAILABLE:
            logger.warning("QR scanning not available (pyzbar missing)")
            return None

        try:
            # Decode QR codes
            decoded_objects = pyzbar.decode(image)

            if not decoded_objects:
                return None

            # Return first QR code data
            qr_data = decoded_objects[0].data.decode('utf-8')
            logger.info(f"QR code scanned: {len(qr_data)} bytes")

            return qr_data

        except Exception as e:
            logger.error(f"QR scanning failed: {e}")
            return None

    def scan_qr_multiple(self, image: Image.Image) -> List[str]:
        """
        Scan multiple QR codes from image.

        Args:
            image: PIL Image containing QR codes

        Returns:
            List of decoded data strings
        """
        if not PYZBAR_AVAILABLE:
            logger.warning("QR scanning not available (pyzbar missing)")
            return []

        try:
            # Decode all QR codes
            decoded_objects = pyzbar.decode(image)

            results = []
            for obj in decoded_objects:
                qr_data = obj.data.decode('utf-8')
                results.append(qr_data)

            logger.info(f"Scanned {len(results)} QR codes")
            return results

        except Exception as e:
            logger.error(f"QR scanning failed: {e}")
            return []

    def validate_bitcoin_address(self, address: str) -> bool:
        """
        Validate Bitcoin address format.

        Args:
            address: Bitcoin address string

        Returns:
            True if valid format, False otherwise
        """
        try:
            # Basic validation
            if not address:
                return False

            # Legacy (P2PKH): starts with 1
            if address.startswith('1'):
                return len(address) >= 26 and len(address) <= 35

            # P2SH: starts with 3
            elif address.startswith('3'):
                return len(address) >= 26 and len(address) <= 35

            # Native SegWit (Bech32): starts with bc1
            elif address.startswith('bc1'):
                return len(address) >= 42 and len(address) <= 62

            # Testnet
            elif address.startswith('m') or address.startswith('n'):
                return len(address) >= 26 and len(address) <= 35

            elif address.startswith('tb1'):
                return len(address) >= 42 and len(address) <= 62

            else:
                return False

        except Exception as e:
            logger.error(f"Address validation failed: {e}")
            return False


# Singleton instance
_qr_handler: Optional[QRHandler] = None


def get_qr_handler() -> QRHandler:
    """
    Get singleton QR handler instance.

    Returns:
        QRHandler instance
    """
    global _qr_handler
    if _qr_handler is None:
        _qr_handler = QRHandler()
    return _qr_handler
