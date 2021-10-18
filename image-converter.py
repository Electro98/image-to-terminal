#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Developed by Electr98
'''
import sys

from sty import fg, bg, rs
from PIL import Image, ImageDraw, ImageFont
from random import randint


def bright(color: tuple) -> tuple:
    return tuple(map(lambda x: min((x + 20), 255), color))


def generate_random_text(width: int) -> str:
    return ''.join([chr(randint(33, 126)) for _ in range(width)])


def generate_random_block(width: int) -> str:
    return ''.join([chr(randint(9600, 9631)) for _ in range(width)])


def generate_blocks(width: int) -> str:
    return '▚' * width


def generate_filler_text(width: int, mode: str) -> str:
    if mode == 'b':
        return generate_blocks(width)
    elif mode == 'rb':
        return generate_random_block(width)
    else:
        return generate_random_text(width)


def image_to_text(image: Image, width: int, mode='r') -> str:
    shrink_factor = image.width // width
    shrinked_img = image.reduce((shrink_factor, shrink_factor * 2))
    width, height = shrinked_img.size
    random_text = generate_filler_text(width * height, mode)
    buff = f'{bg(10, 10, 10)}'
    for j in range(height):
        for i in range(width):
            color = shrinked_img.getpixel((i, j))
            buff = f'{buff}{fg(*color)}{random_text[j * width + i]}{rs.fg}'
        buff = f'{buff}\n'
    return f'{buff}{rs.bg}'


def convert_image(image: Image, width: int, mode='r') -> Image:
    shrink_factor_x = image.width / width
    shrink_factor_y = int(shrink_factor_x * 4 / 3)
    shrinked_img = image.reduce((int(shrink_factor_x), shrink_factor_y))
    width, height = shrinked_img.size
    image_text = image_to_text(image, width)
    font = ImageFont.FreeTypeFont('DejaVu-Sans-Mono.ttf', 10)
    new_image = Image.new('RGB', (width * 6, height * 8 + 3), (20, 20, 20))
    canvas = ImageDraw.Draw(new_image)
    random_text = generate_filler_text(width * height, mode)
    for j in range(height):
        for i in range(width):
            color = shrinked_img.getpixel((i, j))
            canvas.text((i * 6, j * 8), random_text[j * width + i], bright(color), font, anchor='la')
    return new_image.crop((0, 3, width * 6, height * 8 + 3))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'USAGE: {sys.argv[0]} <image_file> <width_text(optional)>')
        exit(1)
    args = sys.argv[1:]
    with Image.open(args[0]) as input_img:
        str_img = image_to_text(input_img,
                                80 if len(args) < 2 else int(args[1]),
                                '' if len(args) < 3 else args[2])
        print(str_img)
        if len(args) >= 4:
            result_img = convert_image(input_img, int(args[3]), args[2])
            result_img.save(f'{args[0].split(".")[0]}_{args[2]}_result.png', 'PNG')
