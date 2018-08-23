from PIL import Image, ImageDraw, ImageFont, ImageSequence
import argparse

parser = argparse.ArgumentParser(description='Make a meme!')
parser.add_argument('--input', type=str, help='original file')
parser.add_argument('--output', type=str, help='where to save the output')
parser.add_argument('--top', type=str, default='', help='top text')
parser.add_argument('--mid', type=str, default='', help='middle text')
parser.add_argument('--bot', type=str, default='', help='bottom text')
parser.add_argument(
    '--top_align',
    type=str,
    default='center',
    choices=['left', 'center', 'right'],
    help='top text horizontal alignment')
parser.add_argument(
    '--mid_align',
    type=str,
    default='center',
    choices=['left', 'center', 'right'],
    help='mid text horizontal alignment')
parser.add_argument(
    '--bot_align',
    type=str,
    default='center',
    choices=['left', 'center', 'right'],
    help='bot text horizontal alignment')

ALIGN_TOP = 0
ALIGN_MID = 1
ALIGN_BOT = 2
HALIGN_LEFT = 0
HALIGN_CENTER = 1
HALIGN_RIGHT = 2

FONT_SCALE = 5
FONT_PADDING = 2


class Meme(object):
    def __init__(self, input=None):
        self.input = input
        self.top = ''
        self.mid = ''
        self.bot = ''
        self.top_align = HALIGN_CENTER
        self.mid_align = HALIGN_CENTER
        self.bot_align = HALIGN_CENTER

    def set_input(self, input):
        self.input = input

    def set_top(self, top):
        self.top = top

    def set_mid(self, mid):
        self.mid = mid

    def set_bot(self, bot):
        self.bot = bot

    def set_top_align(self, align):
        if isinstance(align, basestring):
            self.top_align = self._str_to_align(align)
        else:
            self.top_align = align

    def set_mid_align(self, align):
        if isinstance(align, basestring):
            self.mid_align = self._str_to_align(align)
        else:
            self.mid_align = align

    def set_bot_align(self, align):
        if isinstance(align, basestring):
            self.bot_align = self._str_to_align(align)
        else:
            self.bot_align = align

    @staticmethod
    def _str_to_align(align):
        if align == 'left':
            return HALIGN_LEFT
        elif align == 'center':
            return HALIGN_CENTER
        elif align == 'right':
            return HALIGN_RIGHT
        else:
            raise ValueError()

    def render(self, output_file=None):
        img = Image.open(self.input)
        text_img = make_meme_text(img.size, self.top.upper(), self.mid.upper(),
                                  self.bot.upper(), self.top_align,
                                  self.mid_align, self.bot_align)
        if img.format == 'GIF':
            output_img = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGBA')
                frame.paste(text_img, text_img)
                output_img.append(frame)

            if output_file is not None:
                output_img[0].save(
                    output_file,
                    save_all=True,
                    append_images=output_img[1:],
                    duration=img.info['duration'],
                    loop=0)
            return output_img[0]
        else:
            img.convert('RGBA')
            img.paste(text_img, text_img)
            if output_file is not None:
                img.save(output_file)
            return img

    # This should be greatly simplified
    def render_no_text(self, output_file=None):
        img = Image.open(self.input)
        if img.format == 'GIF':
            output_img = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGBA')
                output_img.append(frame)

            if output_file is not None:
                output_img[0].save(
                    output_file,
                    save_all=True,
                    append_images=output_img[1:],
                    duration=img.info['duration'],
                    loop=0)
            return output_img[0]
        else:
            img.convert('RGBA')
            if output_file is not None:
                img.save(output_file)
            return img

    def render_text_image(self, output_file):
        img = Image.open(self.input)
        text_img = make_meme_text(img.size, self.top.upper(), self.mid.upper(),
                                  self.bot.upper(), self.top_align,
                                  self.mid_align, self.bot_align)
        text_img.save(output_file)



def text_outline(img, text, align, halign, outline_size=2):
    img_size = img.size
    font_size = int(img_size[1] / FONT_SCALE)
    font = ImageFont.truetype("/Library/Fonts/Impact.ttf", font_size)
    draw = ImageDraw.Draw(img)
    w, h = draw.textsize(text, font=font)

    while w > img_size[0]:
        font_size = font_size - 1
        font = ImageFont.truetype("/Library/Fonts/Impact.ttf", font_size)
        draw = ImageDraw.Draw(img)
        w, h = draw.textsize(text, font=font)

    xoffset, yoffset = font.getoffset(text)

    if halign == HALIGN_LEFT:
        xpos = 0
    elif halign == HALIGN_CENTER:
        xpos = img_size[0] / 2 - w / 2 - xoffset
    elif halign == HALIGN_RIGHT:
        xpos = img_size[0] - w
    else:
        raise ValueError()

    ypos = outline_size - yoffset / 2
    if align == ALIGN_TOP:
        ypos += FONT_PADDING
    elif align == ALIGN_MID:
        ypos += img_size[1] / 2 - h / 2 - FONT_PADDING / 2
    elif align == ALIGN_BOT:
        ypos += img_size[1] - h
    else:
        assert (False)

    for xdelta in range(-outline_size, outline_size + 1):
        for ydelta in range(-outline_size, outline_size + 1):
            draw.text(
                ((xpos + xdelta), ypos + ydelta),
                text, (0, 0, 0, 255),
                font=font)
    draw.text((xpos, ypos), text, (255, 255, 255, 255), font=font)


def make_meme_text(img_size, top, mid, bot, top_align, mid_align, bot_align):
    text_img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    text_outline(text_img, top, ALIGN_TOP, top_align)
    text_outline(text_img, mid, ALIGN_MID, mid_align)
    text_outline(text_img, bot, ALIGN_BOT, bot_align)
    return text_img


def make_meme(input, output, top, mid, bot, top_align, mid_align, bot_align):
    meme = Meme(input)
    meme.set_top(top)
    meme.set_mid(mid)
    meme.set_bot(bot)
    meme.set_top_align(top_align)
    meme.set_mid_align(mid_align)
    meme.set_bot_align(bot_align)
    meme.render(output)


def main():
    args = parser.parse_args()
    make_meme(args.input, args.output, args.top, args.mid, args.bot,
              args.top_align, args.mid_align, args.bot_align)


if __name__ == "__main__":
    main()
