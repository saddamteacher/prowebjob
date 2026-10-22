"""Draw desktop/prowebhr.ico (PROWEB HR brand: lime "HR" on near-black)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).with_name("prowebhr.ico")
BG = (11, 12, 16, 255)
ACCENT = (201, 243, 28, 255)
SIZE = 256


def font(size: int):
    for name in ("arialbd.ttf", "seguisb.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((8, 8, SIZE - 8, SIZE - 8), radius=56, fill=BG,
                           outline=(201, 243, 28, 90), width=6)
    text_font = font(130)
    box = draw.textbbox((0, 0), "HR", font=text_font)
    w, h = box[2] - box[0], box[3] - box[1]
    draw.text(((SIZE - w) / 2 - box[0], (SIZE - h) / 2 - box[1]), "HR", font=text_font, fill=ACCENT)
    img.save(OUT, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Icon written: {OUT}")


if __name__ == "__main__":
    main()
