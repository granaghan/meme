from PIL import Image, ImageDraw, ImageFont, ImageSequence
import argparse

parser = argparse.ArgumentParser(description='Make a meme!')
parser.add_argument('--input', type=str, help='original file')
parser.add_argument('--output', type=str, help='where to save the output')
parser.add_argument('--top', type=str, default='', help='top text')
parser.add_argument('--mid', type=str, default='', help='middle text')
parser.add_argument('--bot', type=str, default='', help='bottom text')

ALIGN_TOP = 0
ALIGN_MID = 1
ALIGN_BOT = 2
FONT_SCALE = 5
FONT_PADDING = 2


def text_outline(img, text, align, outline_size=2):
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

  xpos = img_size[0] / 2 - w / 2 - xoffset

  if (w > img_size[0]):
    print "Overfull!"

  ypos = -1 * yoffset + outline_size
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


def main():
  args = parser.parse_args()

  img = Image.open(args.input)
  text_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
  text_outline(text_img, args.top, ALIGN_TOP)
  text_outline(text_img, args.mid, ALIGN_MID)
  text_outline(text_img, args.bot, ALIGN_BOT)

  print img.format

  if img.format == 'GIF':
    output = []
    for frame in ImageSequence.Iterator(img):
      frame = frame.convert('RGBA')
      frame.paste(text_img, text_img)
      output.append(frame)

    output[0].save(
      args.output,
      save_all=True,
      append_images=output[1:],
      duration=img.info['duration'],
      loop=0)
  else:
    img.convert('RGBA')
    img.paste(text_img, text_img)
    img.save(args.output)
  text_img.save('test_text.gif')


if __name__ == "__main__":
  main()
