from PIL import Image, ImageDraw, ImageFont


def draw_board(
        board_path, glyph_list, W, H, glyph_w, glyph_h,
        fontfilename='ipaexg.ttf'):
    board_width = (W + 1) * glyph_w
    board_height = (H + 1) * glyph_h

    im = Image.new('RGB', (board_width, board_height))
    draw = ImageDraw.Draw(im, 'RGBA')

    for x in range(W + 1):
        xx = x * glyph_w + glyph_w
        draw.line((xx, 0, xx, board_height), fill=(128, 128, 128), width=2)
    for y in range(H + 1):
        yy = y * glyph_h + glyph_h
        draw.line((0, yy, board_width, yy), fill=(128, 128, 128), width=2)

    font = ImageFont.truetype(fontfilename, int(glyph_w / 2))

    draw.rectangle(
        ((0, 0), (board_width, board_height)), fill=(0x2f, 0x36, 0x3d))
    for x in range(W):
        text = '{}'.format(chr(65 + x))
        sz = draw.textsize(text, font)
        xx = x * glyph_w + glyph_w + glyph_w / 2 - sz[0] / 2
        yy = glyph_h / 2 - sz[1] / 2
        draw.text((xx, yy), text, fill=(255, 255, 255), font=font)

    for y in range(H):
        text = '{}'.format(y + 1)
        sz = draw.textsize(text, font)
        xx = glyph_w / 2 - sz[0] / 2
        yy = y * glyph_h + glyph_h + glyph_h / 2 - sz[1] / 2
        draw.text((xx, yy), text, fill=(255, 255, 255), font=font)

    i = 0
    for y in range(H):
        for x in range(W):
            if i < len(glyph_list) and glyph_list[i] != '':
                g = Image.open(
                    'resources/{}.jpg'.format(
                        glyph_list[i])).resize((glyph_w, glyph_h))
            else:
                g = None
            i += 1
            xx = x * glyph_w + glyph_w
            yy = y * glyph_h + glyph_h
            if g is not None:
                im.paste(g, (xx, yy))

    im.save(board_path)
