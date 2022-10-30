#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple image to text converter for purpose of fun.

Developed by Electro98.
"""
import argparse
import os

from typing import Generator

import sty
from PIL import Image, ImageDraw, ImageFont

from colors import ColorRGB
from text_generators import (
    ImageTextGenerator,
    TextGenerationModes,
    create_generator,
)


class TextImage:
    """Image with ability to turn into text."""

    def __init__(
        self,
        image: Image.Image,
        text_generator: ImageTextGenerator,
    ) -> None:
        """Create new TextImage."""
        self._image = image.convert("RGB")
        self._text_gen = text_generator

    @staticmethod
    def from_mode(
        image: Image.Image,
        mode: TextGenerationModes,
        symbols: str | None = None,
    ):
        """Create new TextImage with given text generation mode."""
        return TextImage(
            image,
            create_generator(
                image,
                mode,
                symbols,
            ),
        )

    def get_text_repr(self, width: int, bg_color: ColorRGB = (5, 5, 5)) -> str:
        """Return text representation of image."""
        height = round(self._image.height * width / (self._image.width * 2))
        shrinked_img = self._image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

        color_data = shrinked_img.getdata()
        filler_text = self._text_gen.generate(width, height)
        background = sty.bg(*bg_color)
        text_image = "".join(
            f"{sty.fg(*color)}{char}" if i % width or not i else f"{sty.fg(*color)}{char}\n"
            for i, (char, color) in enumerate(zip(filler_text, color_data), 1)
        )
        return f"{background}{text_image}{sty.rs.all}"

    def save(
        self,
        path: str,
        width: int,
        symbol_size: tuple[int, int] = (6, 8),
        font: ImageFont.ImageFont | None = None,
        background_color: ColorRGB = (5, 5, 5),
    ) -> None:
        """Convert to image that is written in text and save it."""
        image = self.to_image(
            width,
            symbol_size,
            font,
            background_color,
        )
        image.save(path)

    def to_image(
        self,
        width: int,
        symbol_size: tuple[int, int] = (6, 8),
        font: ImageFont.ImageFont | None = None,
        background_color: ColorRGB = (5, 5, 5),
    ) -> Image.Image:
        """Convert to image that is written in text."""
        if font is None:
            font = ImageFont.FreeTypeFont("DejaVu-Sans-Mono.ttf", 10)

        # trying to predict user needs
        if width >= 1000:  # I think <1000 pixels is too small for images
            width = width // symbol_size[0] + 1  # converting to symbols width
        height = round(
            self._image.height * (
                width * symbol_size[0] / self._image.width
            ) / symbol_size[1],
        )
        shrinked_img = self._image.resize(
            (width, height),
            Image.Resampling.LANCZOS,
        )

        color_data = shrinked_img.getdata()
        filler_text = self._text_gen.generate(width, height)

        new_image = Image.new(
            "RGB",
            (width * symbol_size[0], height * symbol_size[1] + 3),
            background_color,
        )
        canvas = ImageDraw.Draw(new_image)

        for i, (color, char) in enumerate(zip(color_data, filler_text)):
            canvas.text(
                (i % width * 6, i // width * 8),
                char,
                color,
                font,
                anchor="la",
            )

        return new_image.crop((0, 3, width * 6, height * 8 + 3))


class TextGif:
    """Gif that can be converted to text written gif."""

    def __init__(
        self,
        gif_image: Image.Image,
        mode: TextGenerationModes,
        symbols: str | None = None,
    ):
        """Create new TextGif."""
        assert gif_image.tile[0][0] == "gif", "this is not gif image"
        self._gif = gif_image
        self._text_mode = mode
        self._symbols = symbols
        self._load_palette()

    def _load_palette(self):
        """Load palette and convert it to convenient format."""
        palette_data = self._gif.global_palette.palette
        self._palette = tuple(
            tuple(map(int, palette_data[i:i + 3]))
            for i in range(0, len(palette_data), 3)
        )

    def get_durations(self) -> int:
        """Return durations of frames in gif."""
        try:
            return self._gif.info["duration"]
        except KeyError as exs:
            raise ValueError("there is no duration in gif") from exs

    def looped(self) -> int:
        """Return how many times gif should be looped."""
        try:
            return self._gif.info["loop"]
        except KeyError:
            return 0

    def get_text_images(self) -> list[TextImage]:
        """Return all frames in like TextImage objects."""
        frames: list[TextImage] = []
        for i in range(self._gif.n_frames):
            self._gif.seek(i)
            frames.append(TextImage.from_mode(
                self._gif.convert("RGB"),
                self._text_mode,
                self._symbols,
            ))
        self._gif.seek(0)
        return frames

    def text_repr(
        self,
        width: int,
    ) -> tuple[str, ...]:
        """Return text representation for every frame in gif."""
        background_color: ColorRGB = self._palette[
            self._gif.info["background"]
        ]

        return tuple(
            frame.get_text_repr(
                width,
                background_color,
            ) for frame in self.get_text_images()
        )

    def to_images(
        self,
        width: int,
        symbol_size: tuple[int, int] = (6, 8),
        font: ImageFont.ImageFont | None = None,
    ) -> Generator[Image.Image, None, None]:
        """Convert all frames of gif into image that is written in text."""
        background_color: ColorRGB = self._palette[
            self._gif.info["background"]
        ]

        frames: list[TextImage] = self.get_text_images()
        return (frame.to_image(
            width,
            symbol_size,
            font,
            background_color,
        ) for frame in frames)

    def save(
        self,
        path: str,
        width: int,
        symbol_size: tuple[int, int] = (6, 8),
        font: ImageFont.ImageFont | None = None,
    ):
        """Convert all frames of gif into image that is written in text and save as gif."""
        frames: list[Image.Image] = list(self.to_images(
            width,
            symbol_size,
            font,
        ))

        frames[0].save(
            path,
            "GIF",
            append_images=frames[1:],
            save_all=True,
            duration=self.get_durations(),
            loop=self.looped(),
            optimize=True,
        )


def help_modes(user_mode: str) -> None:
    """Print help about text modes in this program."""
    print("There is a few modes to use in this program.")
    print("Currently available modes:")
    print(f"-- {'enter this':12}-- {'Internal name':14} --")
    for mode in TextGenerationModes:
        print(f" - {mode.value:12} - {mode.name:14}  -")
    print(f"You entered: {user_mode}")


def main() -> int:
    """Parse args and print/save images."""
    # For support mingw64
    os.system("")
    parser = argparse.ArgumentParser(description='Convert image to text')
    parser.add_argument('src',
                        help='Converted image')
    parser.add_argument('--width', '-w', default=80, type=int,
                        help='Width of image in terminal(in chars)')
    parser.add_argument('--mode', '-m', default='rand_text',
                        help='Convertion image mode')
    parser.add_argument('--png_width', '-pw', default=0, type=int,
                        help='Width of saved image(in chars). '
                        + 'If 0(by default) image isn\'t saving')
    parser.add_argument('--symbols', '-s', default=None,
                        help='If you want to use your pull of chars')
    args = parser.parse_args()
    with Image.open(args.src) as input_img:
        try:
            image_text_mode = TextGenerationModes[args.mode]
        except KeyError:
            help_modes(args.mode)
            return -1
        if args.src.split('.')[-1] == 'gif':
            # Experimental feature
            # be ready for MASSIVE gif and slow processing
            print("This is experimetal feature. You're warned!")
            gif = TextGif(input_img, image_text_mode, args.symbols)

            gif.save(
                f"{args.src.split('.')[0]}_{args.mode}_result.gif",
                args.width,
            )
        else:
            text_generator = create_generator(
                input_img,
                image_text_mode,
                args.symbols,
            )
            text_image = TextImage(input_img, text_generator)
            print(text_image.get_text_repr(args.width))
            if args.png_width:
                text_image.save(
                    f"{args.src.split('.')[0]}_{args.mode}_result.png",
                    args.png_width,
                )
    return 0


if __name__ == "__main__":
    main()
