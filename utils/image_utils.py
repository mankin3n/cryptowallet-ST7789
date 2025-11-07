"""
Image Utilities.

Image processing functions for resizing, cropping, overlaying text,
and manipulating camera frames.
"""

import logging
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import config

logger = logging.getLogger(__name__)


def resize_image(
    image: Image.Image,
    target_size: Tuple[int, int],
    maintain_aspect: bool = True
) -> Image.Image:
    """
    Resize image to target size.

    Args:
        image: Source PIL Image
        target_size: (width, height) tuple
        maintain_aspect: Whether to maintain aspect ratio

    Returns:
        Resized PIL Image
    """
    try:
        if maintain_aspect:
            # Calculate aspect ratio
            img_ratio = image.width / image.height
            target_ratio = target_size[0] / target_size[1]

            if img_ratio > target_ratio:
                # Image is wider, fit to width
                new_width = target_size[0]
                new_height = int(new_width / img_ratio)
            else:
                # Image is taller, fit to height
                new_height = target_size[1]
                new_width = int(new_height * img_ratio)

            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create canvas and center image
            canvas = Image.new('RGB', target_size, config.COLOR_BLACK)
            x_offset = (target_size[0] - new_width) // 2
            y_offset = (target_size[1] - new_height) // 2
            canvas.paste(resized, (x_offset, y_offset))

            return canvas

        else:
            # Direct resize
            return image.resize(target_size, Image.Resampling.LANCZOS)

    except Exception as e:
        logger.error(f"Image resize failed: {e}")
        return image


def crop_to_square(image: Image.Image) -> Image.Image:
    """
    Crop image to square (center crop).

    Args:
        image: Source PIL Image

    Returns:
        Cropped PIL Image
    """
    try:
        width, height = image.size

        if width == height:
            return image

        # Find smaller dimension
        size = min(width, height)

        # Calculate crop box
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size

        return image.crop((left, top, right, bottom))

    except Exception as e:
        logger.error(f"Image crop failed: {e}")
        return image


def overlay_text(
    image: Image.Image,
    text: str,
    position: Tuple[int, int],
    font_size: int = 16,
    color: Tuple[int, int, int] = config.COLOR_WHITE,
    background: Optional[Tuple[int, int, int]] = None
) -> Image.Image:
    """
    Overlay text on image.

    Args:
        image: Source PIL Image
        text: Text to overlay
        position: (x, y) position
        font_size: Font size in pixels
        color: Text color RGB tuple
        background: Optional background color RGB tuple

    Returns:
        Image with text overlaid
    """
    try:
        # Create copy
        result = image.copy()
        draw = ImageDraw.Draw(result)

        # Load font
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', font_size)
        except:
            font = ImageFont.load_default()

        # Draw background box if specified
        if background:
            bbox = draw.textbbox(position, text, font=font)
            padding = 5
            draw.rectangle(
                [(bbox[0] - padding, bbox[1] - padding),
                 (bbox[2] + padding, bbox[3] + padding)],
                fill=background
            )

        # Draw text
        draw.text(position, text, font=font, fill=color)

        return result

    except Exception as e:
        logger.error(f"Text overlay failed: {e}")
        return image


def create_thumbnail(image: Image.Image, size: int = 80) -> Image.Image:
    """
    Create thumbnail of image.

    Args:
        image: Source PIL Image
        size: Thumbnail size (square)

    Returns:
        Thumbnail PIL Image
    """
    try:
        # Crop to square first
        square = crop_to_square(image)

        # Resize to thumbnail size
        thumbnail = square.resize((size, size), Image.Resampling.LANCZOS)

        return thumbnail

    except Exception as e:
        logger.error(f"Thumbnail creation failed: {e}")
        return image


def blend_images(
    image1: Image.Image,
    image2: Image.Image,
    alpha: float = 0.5
) -> Image.Image:
    """
    Blend two images together.

    Args:
        image1: First PIL Image
        image2: Second PIL Image
        alpha: Blend factor (0.0 to 1.0)

    Returns:
        Blended PIL Image
    """
    try:
        # Ensure same size
        if image1.size != image2.size:
            image2 = image2.resize(image1.size, Image.Resampling.LANCZOS)

        # Ensure same mode
        if image1.mode != image2.mode:
            image2 = image2.convert(image1.mode)

        # Blend
        return Image.blend(image1, image2, alpha)

    except Exception as e:
        logger.error(f"Image blend failed: {e}")
        return image1


def rotate_image(image: Image.Image, angle: int) -> Image.Image:
    """
    Rotate image by angle.

    Args:
        image: Source PIL Image
        angle: Rotation angle in degrees (0, 90, 180, 270)

    Returns:
        Rotated PIL Image
    """
    try:
        if angle == 0:
            return image
        elif angle == 90:
            return image.rotate(-90, expand=True)
        elif angle == 180:
            return image.rotate(180, expand=True)
        elif angle == 270:
            return image.rotate(90, expand=True)
        else:
            logger.warning(f"Unsupported rotation angle: {angle}")
            return image

    except Exception as e:
        logger.error(f"Image rotation failed: {e}")
        return image


def convert_to_grayscale(image: Image.Image) -> Image.Image:
    """
    Convert image to grayscale.

    Args:
        image: Source PIL Image

    Returns:
        Grayscale PIL Image
    """
    try:
        return image.convert('L')

    except Exception as e:
        logger.error(f"Grayscale conversion failed: {e}")
        return image


def apply_brightness(image: Image.Image, factor: float) -> Image.Image:
    """
    Adjust image brightness.

    Args:
        image: Source PIL Image
        factor: Brightness factor (1.0 = no change, <1 = darker, >1 = brighter)

    Returns:
        Adjusted PIL Image
    """
    try:
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    except Exception as e:
        logger.error(f"Brightness adjustment failed: {e}")
        return image


def apply_contrast(image: Image.Image, factor: float) -> Image.Image:
    """
    Adjust image contrast.

    Args:
        image: Source PIL Image
        factor: Contrast factor (1.0 = no change)

    Returns:
        Adjusted PIL Image
    """
    try:
        from PIL import ImageEnhance

        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    except Exception as e:
        logger.error(f"Contrast adjustment failed: {e}")
        return image


def create_gradient(
    size: Tuple[int, int],
    color1: Tuple[int, int, int],
    color2: Tuple[int, int, int],
    vertical: bool = True
) -> Image.Image:
    """
    Create gradient image.

    Args:
        size: (width, height) tuple
        color1: Start color RGB tuple
        color2: End color RGB tuple
        vertical: Whether gradient is vertical (True) or horizontal (False)

    Returns:
        Gradient PIL Image
    """
    try:
        image = Image.new('RGB', size)
        draw = ImageDraw.Draw(image)

        if vertical:
            # Vertical gradient
            for y in range(size[1]):
                ratio = y / size[1]
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)

                draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        else:
            # Horizontal gradient
            for x in range(size[0]):
                ratio = x / size[0]
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)

                draw.line([(x, 0), (x, size[1])], fill=(r, g, b))

        return image

    except Exception as e:
        logger.error(f"Gradient creation failed: {e}")
        return Image.new('RGB', size, color1)
