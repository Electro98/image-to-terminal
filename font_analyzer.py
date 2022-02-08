from PIL import Image, ImageDraw, ImageFont
from itertools import groupby


SYMBOLS_RANGES = (32, 126), (176, 190), (9472, 9727)

SYMBOLS = ''.join(''.join(map(chr, range(up, to + 1))) for up, to in SYMBOLS_RANGES)


def generate_image(font):
    width, height = 256, 256
    new_image = Image.new('RGB', (width * 6, height * 8 + 3), (20, 20, 20))
    canvas = ImageDraw.Draw(new_image)
    text = ''.join(map(chr, range(0, width * height)))
    for i in range(height):
        canvas.text((0, i * 8), text[i * width: i * width + width], (0xFF, 0xFF, 0xFF), font, anchor='la')
    return new_image.crop((0, 3, width * 6, height * 8 + 3))


def main():
    font = ImageFont.FreeTypeFont('DejaVu-Sans-Mono.ttf', 10)
    symbols = []
    chars = []
    for symbol in SYMBOLS:
        char = tuple(color for color in font.getmask(symbol, 'l'))
        if (len(char) < 48) == (sum(char) <= 6059) or ((len(char) < 48) != (sum(char) <= 6059)):
            symbols.append(symbol)
            chars.append(sum(char))
    max_char = max(chars)
    print(max_char)
    brightness = tuple(round(char / max_char, 2) for char in chars)
    print(''.join(symbols))
    s_brg = sorted(brightness)
    s_zipped = sorted(zip(brightness, symbols), key=lambda x: x[0])
    s_chr = ''.join(map(lambda x: x[1], s_zipped))
    print(s_brg)
    print(s_chr)
    with open('font_settings.py', 'w', encoding='utf-8') as file:
        file.write('hsv_chars = (\n')
        for _, elem in groupby(s_zipped, lambda x: x[0]):
            elem = tuple(elem)
            print(f'{elem}: {elem}')
            file.write(f'    \'{"".join(map(lambda x: x[1], elem))}\',\n')
        file.write(')\n')
    # result = generate_image(font)
    # result.save('result.png', 'PNG')


if __name__ == '__main__':
    main()
