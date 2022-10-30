from abc import ABC, abstractmethod
from random import choices
from typing import Callable

from PIL import Image

from colors import ColorRGB, ColorConverter
from utils import StringEnum


class TextGenerationModes(StringEnum):
    """Set of modes available for text generation."""
    BLOCKS = "blocks"
    RANDOM_BLOCKS = "rand_blocks"
    HSV_VALUE = "hsv"
    RANDOM_TEXT = "rand_text"


class ImageTextGenerator(ABC):
    """Absctract text generator."""

    @abstractmethod
    def generate(self, width: int, height: int) -> str:
        """Generate text with given length for image."""


class BlockTextGenerator(ImageTextGenerator):
    """Generate rangom string from given characters set."""

    def __init__(self, charset: str) -> None:
        """Create generator with basic/given charset."""
        self.charset: str = charset

    def generate(self, width: int, height: int) -> str:
        """Generate random text from given charset."""
        length = width * height
        text = self.charset * (length // len(self.charset) + 1)
        return text[:length]


class RandomTextGenerator(ImageTextGenerator):
    """Generate rangom string from given characters set."""

    def __init__(self, charset: str | None = None) -> None:
        """Create generator with basic/given charset."""
        self.charset: str = charset or ''.join(map(chr, range(33, 126)))

    def generate(self, width: int, height: int) -> str:
        """Generate random text from given charset."""
        length = width * height
        return ''.join(choices(self.charset, k=length))


class TextImageHSVGenerator(ImageTextGenerator):
    """Generate text with brightness value from image."""

    def __init__(
        self,
        image: Image.Image,
        hsv_charset: str,
        color_converter: Callable[[ColorRGB], int] | None = None,
    ) -> None:
        if image.mode == "L":  # Monochrome
            self._image = image
            self._image_converted = True
        elif color_converter is None:
            raise ValueError(
                "image is not Monochrome and"
                "color converter is not specified",
            )
        else:
            self._image = image.convert("RGB")
            self._image_converted = False
        self.color_converter = color_converter
        self.hsv_charset = hsv_charset

    def generate(self, width: int, height: int) -> str:
        """Generate text by hsv value of char in charset."""
        sized_image: Image.Image = self._image.resize((width, height))
        charset_length = len(self.hsv_charset) - 1
        if self._image_converted:
            return ''.join(
                self.hsv_charset[
                    color * charset_length // 255,
                ] for color in sized_image.getdata()
            )
        return ''.join(
            self.hsv_charset[
                self.color_converter(color) * charset_length // 255
            ] for color in sized_image.getdata()
        )


def create_generator(
    image: Image.Image,
    mode: TextGenerationModes,
    chars: str | None = None,
) -> ImageTextGenerator:
    if mode is TextGenerationModes.BLOCKS:
        return BlockTextGenerator(chars or "▚")
    if mode is TextGenerationModes.RANDOM_BLOCKS:
        return RandomTextGenerator(''.join(map(chr, range(9600, 9632))))
    if mode is TextGenerationModes.HSV_VALUE:
        return TextImageHSVGenerator(
            image,
            " .:-=+*#%@",
            ColorConverter.rgb_to_monochrome,
        )
    if mode is TextGenerationModes.RANDOM_TEXT:
        return RandomTextGenerator(chars)
    raise NotImplementedError(
        f"unknown text generation mode is choosed {mode}",
    )
