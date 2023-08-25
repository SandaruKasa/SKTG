#!/usr/bin/env python3
from PIL import Image, ImageFont, ImageDraw

from SKTools import altdiv


def get_pixels(image: Image) -> list:
    _p = image.load()
    return [[_p[x, y] for x in range(image.size[0])] for y in range(image.size[1])]


def get_column(pixels: list, column_no: int) -> list:
    return [pixels[row_no][column_no] for row_no in range(len(pixels))]


def del_column(pixels: list, column_no: int) -> None:
    for row in pixels:
        del row[column_no]


def crop_bg(image: Image, color='black', crop_top: bool = True, crop_bottom: bool = True,
            crop_left: bool = True, crop_right: bool = True, mode: str = 'RGB') -> Image:
    p = get_pixels(image)
    reserve = Image.new(mode, (1, 1), color)
    color = reserve.load()[0, 0]

    if crop_top:
        while p and p[0] == [color] * len(p[0]):
            del p[0]
        if not p:
            return reserve

    if crop_bottom:
        while p and p[-1] == [color] * len(p[-1]):
            del p[-1]
        if not p:
            return reserve

    if crop_left:
        while p[0] and get_column(p, 0) == [color] * len(p):
            del_column(p, 0)
        if not p[0]:
            return reserve

    if crop_right:
        while p[-1] and get_column(p, -1) == [color] * len(p):
            del_column(p, -1)
        if not p[-1]:
            return reserve

    res = []
    for row in p:
        res += row
    im = Image.new(mode, (len(p[0]), len(p)))
    im.putdata(res)
    return im


def extended_by(image_to_expand: Image, top: int = 0, left: int = 0, right: int = 0, bottom: int = 0,
                bg_color='black', mode: str = 'RGB') -> Image:
    w0, h0 = image_to_expand.size
    expanded_image = Image.new(mode, (w0 + left + right, h0 + top + bottom), bg_color)
    expanded_image.paste(image_to_expand, (left, top))
    return expanded_image


def extended_to(image_to_expand: Image, w: int = 640, h: int = 640, bg_color='black', mode: str = 'RGB') -> Image:
    w0, h0 = image_to_expand.size
    expanded_image = Image.new(mode, (w, h), bg_color)
    expanded_image.paste(image_to_expand, (altdiv(w - w0, 2), altdiv(h - h0, 2)))
    return expanded_image


def vertical_merge(*images: Image, bg_color='black', align: str = 'center', interval: int = 0,
                   mode: str = 'RGB') -> Image:
    if (number_of_images := len(images)) == 0:
        return Image.new(mode, (1, 1), bg_color)
    elif number_of_images == 1:
        return images[0]
    elif number_of_images == 2:
        size = [images[i].size for i in range(2)]
        w_final = max(size[0][0], size[1][0])
        h_final = size[0][1] + size[1][1] + interval
        merged_image = Image.new(mode, (w_final, h_final), color=bg_color)
        if align == 'left':
            w = (0, 0)
        elif align == 'right':
            w = [w_final - size[i][0] for i in range(2)]
        else:
            w = [altdiv(w_final - size[i][0], 2) for i in range(2)]
        merged_image.paste(images[0], (w[0], 0))
        merged_image.paste(images[1], (w[1], size[0][1] + interval))
        return merged_image
    else:
        return vertical_merge(vertical_merge(*images[:2],
                                             bg_color=bg_color, align=align, interval=interval, mode=mode),
                              *images[2:], bg_color=bg_color, align=align, interval=interval, mode=mode)


def horizontal_merge(*images: Image, bg_color='black', align: str = 'center', interval: int = 0,
                     mode: str = 'RGB') -> Image:
    if (number_of_images := len(images)) == 0:
        return Image.new(mode, (1, 1), bg_color)
    elif number_of_images == 1:
        return images[0]
    elif number_of_images == 2:
        size = [images[i].size for i in range(2)]
        w_final = size[0][0] + size[1][0] + interval
        h_final = max(size[0][1], size[1][1])
        merged_image = Image.new(mode, (w_final, h_final), color=bg_color)
        if align in ('top', 'up'):
            h = (0, 0)
        elif align in ('bottom', 'down'):
            h = [h_final - size[i][1] for i in range(2)]
        else:
            h = [altdiv(h_final - size[i][1], 2) for i in range(2)]
        merged_image.paste(images[0], (0, h[0]))
        merged_image.paste(images[1], (size[0][0] + interval, h[1]))
        return merged_image
    else:
        return horizontal_merge(horizontal_merge(*images[:2],
                                                 bg_color=bg_color, align=align, interval=interval, mode=mode),
                                *images[2:], bg_color=bg_color, align=align, interval=interval, mode=mode)


# Pillow 10.0 removes the deprecated `getsize` method for `ImageFont.FreeTypeFont`.
# As a replacement they recommend using
# ```python
# left, top, right, bottom = font.getbbox("Hello world")
# width, height = right - left, bottom - top
# ```
# https://github.com/hugovk/Pillow/pull/99/files#diff-aa52e563b22c10084fd5eb71464d011202f831331048679f5a8b42f17143f553
# However, this exhibits completely different behavior, lmao.
# So instead here's a simplified version of the removed implementation:
# https://github.com/hugovk/Pillow/pull/99/files#diff-1e7ed0fef8a87b1055695d739fb65a2fb08227df84c872938244d9857aaf63cfL466-L470
def getsize(font: ImageFont.FreeTypeFont, text: str):
    size, offset = font.font.getsize(text, "L")
    return size[0], size[1] + offset[1]


def draw_line_no_wrap(text: str, font: ImageFont.FreeTypeFont, bg_color='black', text_color=(255, 255, 255),
                      mode: str = 'RGB') -> Image:
    if not text:
        text = ' '
    text_img = Image.new(mode, getsize(font, text), bg_color)
    text_draw = ImageDraw.Draw(text_img)
    text_draw.text((0, 0), text, text_color, font=font)
    return text_img


def draw_line_with_wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int = -1, bg_color='black',
                        text_color=(255, 255, 255), align: str = 'center',
                        allow_word_breaking: bool = True, carry_over_symbol: str = '-', mode: str = 'RGB') -> Image:
    if max_width <= 0:
        return draw_line_no_wrap(text, font, bg_color, text_color, mode=mode)

    def fits(test_line: str) -> bool:
        return getsize(font, test_line)[0] <= max_width

    def carried_over(line_to_carry_over: str) -> str:
        return f'{line_to_carry_over}{"" if line_to_carry_over.endswith(carry_over_symbol) else carry_over_symbol}'

    def joined(prefix: str, suffix: str) -> str:
        return f'{prefix} {suffix}' if prefix else suffix

    words = text.strip().split()
    if not words and text:
        words = [text.strip()]
    lines = []
    current_line = ''
    while words:
        word = words.pop(0)
        if fits(newline := joined(current_line, word)):
            current_line = newline
        else:
            if allow_word_breaking:
                if fits(word):
                    if current_line:
                        lines.append(current_line)
                    current_line = word
                else:
                    j = 1
                    while j < len(word) and fits(joined(current_line, carried_over(word[:j]))):
                        j += 1
                    if fits(second_part := word[j - 1:]):
                        lines.append(joined(current_line, carried_over(word[:j - 1])))
                        current_line = second_part
                    else:
                        if current_line:
                            lines.append(current_line)
                        j = 1
                        while j < len(word) and fits(carried_over(word[:j])):
                            j += 1
                        lines.append(carried_over(word[:j - 1]))
                        current_line = ''
                        words = [word[j - 1:]] + words

            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
    lines.append(current_line)
    return vertical_merge(*map(lambda line: draw_line_no_wrap(line, font, bg_color, text_color, mode=mode), lines),
                          align=align, mode=mode)


def draw_text_with_wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int = -1, bg_color='black',
                        text_color=(255, 255, 255), align: str = 'center', allow_word_breaking: bool = True,
                        mode: str = 'RGB') -> Image:
    return vertical_merge(
        *(draw_line_with_wrap(line, font, max_width, bg_color, text_color, align, allow_word_breaking,
                              mode=mode) for line in text.splitlines(keepends=True)),
        align=align, mode=mode) \
        if max_width > 0 else draw_line_no_wrap(text, font, bg_color, text_color, mode=mode)
