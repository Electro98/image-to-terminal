#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Developed by Electr98
'''
import argparse

from sty import fg, bg, rs
from PIL import Image, ImageDraw, ImageFont
from random import randint, choice


def bright(color: tuple) -> tuple:
    return tuple(map(lambda x: min((x + 20), 255), color))


def generate_random_text(width: int, chars=None) -> str:
    return ''.join((choice(chars) if chars else chr(randint(33, 126)) for _ in range(width)))


def generate_random_block(width: int) -> str:
    return ''.join((chr(randint(9600, 9631)) for _ in range(width)))


def generate_blocks(width: int, chars=None) -> str:
    return (chars * width)[:width] if chars else '▚' * width


def generate_filler_text(width: int, mode: str, chars=None) -> str:
    if mode == 'b':
        return generate_blocks(width, chars)
    elif mode == 'rb':
        return generate_random_block(width)
    else:
        return generate_random_text(width, chars)


def image_to_text(image: Image, width: int, mode='r', chars=None) -> str:
    shrink_factor = image.width // width
    shrinked_img = image.reduce((shrink_factor, shrink_factor * 2))
    width, height = shrinked_img.size
    random_text = generate_filler_text(width * height, mode, chars)
    buff = f'{bg(10, 10, 10)}'
    for j in range(height):
        for i in range(width):
            color = shrinked_img.getpixel((i, j))
            buff = f'{buff}{fg(*color)}{random_text[j * width + i]}{rs.fg}'
        buff = f'{buff}\n'
    return f'{buff}{rs.bg}'


def convert_image(image: Image, width: int, mode='r', chars=None) -> Image:
    shrink_factor_x = image.width / width
    shrink_factor_y = int(shrink_factor_x * 4 / 3)
    shrinked_img = image.reduce((int(shrink_factor_x), shrink_factor_y))
    width, height = shrinked_img.size
    font = ImageFont.FreeTypeFont('DejaVu-Sans-Mono.ttf', 10)
    new_image = Image.new('RGB', (width * 6, height * 8 + 3), (20, 20, 20))
    canvas = ImageDraw.Draw(new_image)
    random_text = generate_filler_text(width * height, mode, chars)
    for j in range(height):
        for i in range(width):
            color = shrinked_img.getpixel((i, j))
            canvas.text((i * 6, j * 8), random_text[j * width + i], bright(color), font, anchor='la')
    return new_image.crop((0, 3, width * 6, height * 8 + 3))


if __name__ == '__main__':
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
        str_img = image_to_text(input_img, args['width'], args['mode'], args['symbols'])
        print(str_img)
        if args.get('png_width'):
            result_img = convert_image(input_img, args['png_width'], args['mode'], args['symbols'])
            result_img.save(f'{args["src"].split(".")[0]}_{args["mode"]}_result.png', 'PNG')
