#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Developed by Electr98
'''
import argparse
import os

from sty import fg, bg, rs
from PIL import Image, ImageDraw, ImageFont
from random import randint, choice


def bright(color: tuple) -> tuple:
    return tuple(map(lambda x: min((x + 20), 255), color))


def load_palette_from_gif(gif: Image):
    palette_data = gif.global_palette.palette
    return [tuple(map(int, palette_data[i:i + 3])) for i in range(0, len(palette_data), 3)]


def load_frames_from_gif(gif: Image, width: int, height: int):
    frames = []
    for i in range(gif.n_frames):
        gif.seek(i)
        frames.append(gif.resize((width, height), Image.ANTIALIAS).getdata())
    return frames


def load_data_from_gif(gif: Image, width: int, height: int):
    palette = load_palette_from_gif(gif)
    return [[palette[pix] for pix in frame] for frame in load_frames_from_gif(gif, width, height)]


class FillerGenerator(object):
    """class FillerGenerator:
        - Presents simple text generator to fill images.
    """
    @classmethod
    def generate_random_text(cls, width: int, chars=None) -> str:
        return ''.join((choice(chars) if chars else chr(randint(33, 126)) for _ in range(width)))

    @classmethod
    def generate_blocks(cls, width: int, chars=None) -> str:
        return (chars * width)[:width] if chars else '▚' * width

    @classmethod
    def generate_random_block(cls, width: int) -> str:
        return ''.join((chr(randint(9600, 9631)) for _ in range(width)))

    @classmethod
    def generate(cls, width: int, mode: str, chars=None) -> str:
        if mode == 'b':
            return cls.generate_blocks(width, chars)
        elif mode == 'rb':
            return cls.generate_random_block(width)
        else:
            return cls.generate_random_text(width, chars)


def image_data_to_text(pixel_data, width: int, height: int, filler_text: str) -> str:
    buff = f'{bg(10, 10, 10)}'
    for j in range(height):
        for i in range(width):
            color = pixel_data[j * width + i]
            buff = f'{buff}{fg(*color)}{filler_text[j * width + i]}{rs.fg}'
        buff = f'{buff}\n'
    return f'{buff}{rs.bg}'


def image_to_text(image: Image, width: int, mode='r', chars=None) -> str:
    height = round(image.height * width / (image.width * 2))
    shrinked_img = image.resize((width, height), Image.ANTIALIAS)
    random_text = FillerGenerator.generate(width * height, mode, chars)
    pixel_data = shrinked_img.getdata()
    return image_data_to_text(pixel_data, width, height, random_text)


def image_data_to_timage(pixel_data, width: int, height: int, filler_text: str) -> Image:
    font = ImageFont.FreeTypeFont('DejaVu-Sans-Mono.ttf', 10)
    new_image = Image.new('RGB', (width * 6, height * 8 + 3), (20, 20, 20))
    canvas = ImageDraw.Draw(new_image)
    for j in range(height):
        for i in range(width):
            color = pixel_data[j * width + i]
            canvas.text((i * 6, j * 8), filler_text[j * width + i], bright(color), font, anchor='la')
    return new_image.crop((0, 3, width * 6, height * 8 + 3))


def image_to_timage(image: Image, width: int, mode='r', chars=None) -> Image:
    height = round(image.height * (width * 6 / image.width) / 8)
    shrinked_img = image.resize((width, height), Image.ANTIALIAS)
    pixel_data = shrinked_img.getdata()
    random_text = FillerGenerator.generate(width * height, mode, chars)
    return image_data_to_timage(pixel_data, width, height, random_text)


if __name__ == '__main__':
    # For support mingw64
    os.system("")
    parser = argparse.ArgumentParser(description='Convert image to text')
    parser.add_argument('src',
                        help='Converted image')
    parser.add_argument('--width', '-w', default=80, type=int,
                        help='Width of image in terminal(in chars)')
    parser.add_argument('--mode', '-m', default='r',
                        help='Convertion image mode')
    parser.add_argument('--png_width', '-pw', default=0, type=int,
                        help='Width of saved image(in chars). '
                        + 'If 0(by default) image isn\'t saving')
    parser.add_argument('--symbols', '-s', default=None,
                        help='If you want to use your pull of chars')
    args = vars(parser.parse_args())
    with Image.open(args['src']) as input_img:
        if args['src'].split('.')[-1] == 'gif':
            # Experimental feature
            # be ready for MASSIVE gif and slow processing
            print('This is experimetal feature. You\'re warned!')
            width = args['width']
            height = round(input_img.height * width / input_img.width)
            pixel_datas = load_data_from_gif(input_img, width, height)
            frames = []
            for pixel_data in pixel_datas:
                text = FillerGenerator.generate(width * height, args['mode'], args['symbols'])
                frames.append(image_data_to_timage(pixel_data, width, height, text))
            frames[0].save(f'{args["src"].split(".")[0]}_{args["mode"]}_result.gif',
                           'GIF', append_images=frames[1:], save_all=True,
                           duration=input_img.info['duration'], loop=0,
                           optimize=True)
        else:
            str_img = image_to_text(input_img, args['width'], args['mode'], args['symbols'])
            print(str_img)
            if args['png_width']:
                result_img = image_to_timage(input_img, args['png_width'], args['mode'], args['symbols'])
                result_img.save(f'{args["src"].split(".")[0]}_{args["mode"]}_result.png', 'PNG')
