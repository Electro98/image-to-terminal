
ColorHSV = ColorRGB = tuple[int, int, int]


class ColorConverter:
    @staticmethod
    def rgb_to_hsv(color_rgb: ColorRGB) -> ColorHSV:
        """Convert color from RGB into HSV pallette."""
        red, green, blue = color_rgb
        value = max(red, green, blue)
        chroma = value - min(red, green, blue)
        if not chroma:  # chroma == 0
            hue = 0
        elif value == red:
            hue = 60 * (green - blue) / chroma
        elif value == green:
            hue = 60 * (2 + (blue - red) / chroma)
        else:
            hue = 60 * (4 + (red - green) / chroma)
        saturation = 0 if not value else chroma / value
        return hue, saturation, value

    @staticmethod
    def hsv_to_rgb(h, s, v) -> ColorRGB:
        h %= 360
        c = v * s
        x = c * (1 - abs(h / 60 % 2 - 1))
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        m = v - c
        return round((r + m) * 255), round((g + m) * 255), round((b + m) * 255)

    @staticmethod
    def max_rgb_value(r, g, b):
        v = max(r, g, b)
        if not v:
            return 255, 255, 255
        return round(r / v * 255), round(g / v * 255), round(b / v * 255)

    @staticmethod
    def rgb_to_monochrome(color: ColorRGB) -> int:
        return round(0.2125 * color[0] + 0.7154 * color[1] + 0.0721 * color[2])

    @staticmethod
    def hsv_value_max(pixel_data):
        return tuple(
            ColorConverter.max_rgb_value(*color)
            for color in pixel_data
        )

    @staticmethod
    def bright(color: tuple) -> tuple:
        return tuple(map(lambda x: min((x + 20), 255), color))
