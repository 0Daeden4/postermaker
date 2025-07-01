from enum import Enum
from PIL import ImageColor, ImageDraw, ImageOps, ImageFont, Image
from argparse import ArgumentParser, Namespace
from pathlib import Path
from dataclasses import dataclass
import re
import qrcode
from qrcode.constants import ERROR_CORRECT_M


@dataclass
class EventInformation():
    title: tuple[str, str, int]
    desc: tuple[str, str, int]
    place: tuple[str, str, int]
    date: tuple[str, str, int]


class Posts(Enum):
    IG_POST = (1080, 1350)
    IG_STORY = (1080, 1920)
    IG_REELS = (1080, 1920)
    FB_POST = (1200, 1200)
    FB_STORY = (1080, 1920)
    FB_REELS = (1080, 1920)
    X_POST = (1200, 675)


class PostMaker():

    def _create_gradient_map(self, length: float, canvas_size: tuple[int, int],
                             color: tuple[int, int, int] | tuple[int, int, int, int]) -> Image.Image:
        gradient_canvas = Image.new("RGBA", canvas_size)
        draw = ImageDraw.Draw(gradient_canvas)

        width = gradient_canvas.size[0]
        height = gradient_canvas.size[1]
        for i in range(height):
            alpha = int(255*(i/length))
            draw.line([(0, i), (width, i)], fill=(
                color[0], color[1], color[2], alpha))
        return gradient_canvas

    def _get_padding(self, canvas_type: Posts) -> tuple[int, int]:
        canvas_name = canvas_type.name
        if canvas_name == "IG_STORY" or canvas_name == "FB_STORY":
            return (100, 120)
        elif canvas_name == "IG_POST":
            return (0, 135)
        else:
            return (0, 0)

    def _place_bg_image(self, canvas: Image.Image, bg_image: Image.Image, padding: tuple[int, int]):
        c_width = canvas.width
        c_height = canvas.height
        desired_size = (c_width, c_height - (2 * padding[1]))
        resized_bg_image = ImageOps.fit(
            bg_image, desired_size, centering=(0.5, 0.5))
        canvas.paste(resized_bg_image, (0, padding[1]))

    def _generate_qr(self, link: str,
                     size: tuple[int, int] = (300, 300),
                     *,
                     fill: str = "black",
                     back: str = "white",
                     error=ERROR_CORRECT_M,
                     border: int = 4,
                     box_size: int = 10) -> Image.Image:

        qr = qrcode.QRCode(
            version=None,
            error_correction=error,
            box_size=box_size,
            border=border,
        )
        qr.add_data(link)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill, back_color=back).convert("RGB")

        img = img.resize(size, Image.NEAREST)
        return img

    def _place_logo(self, canvas: Image.Image, logo_image: Image.Image, link: str):
        c_width = canvas.width
        c_height = canvas.height
        if link != "PlaceholderLink":
            qr_image = self._generate_qr(link, logo_image.size)
            temp_canvas = Image.new(
                "RGBA", ((logo_image.width*2), logo_image.height))
            temp_canvas.paste(logo_image, (logo_image.width, 0))
            temp_canvas.paste(qr_image, (0, 0))
            logo_image = temp_canvas
        if not self.place_bbox or not self.date_bbox:
            desired_size = (c_width//5, int(c_height//5.4))
        else:
            x_space = c_width - \
                int(max(self.date_bbox[2], self.place_bbox[2]) + 10)
            inverse_ratio = logo_image.height/logo_image.width
            y_space = c_height - min(self.place_bbox[1], self.place_bbox[3])
            if y_space/x_space < inverse_ratio:
                x_space = int((1/inverse_ratio) * y_space)

            y_space = x_space * inverse_ratio
            desired_size = (x_space, int(y_space))

        resized_logo_image = ImageOps.cover(logo_image, desired_size)
        # max_width = int(max(self.place_bbox[2], self.date_bbox[2]))
        # (max_width + int((c_width - max_width)/2))
        canvas.alpha_composite(
            resized_logo_image, (c_width-(resized_logo_image.width+5), c_height - resized_logo_image.height))

    def _resolve_font(self, font_path: str, font_size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
        if font_path == "PlaceholderFont":
            font = ImageFont.load_default_imagefont()
        else:
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                try:
                    font = ImageFont.load(font_path)
                except:
                    raise OSError("Font dosyası bulunamadı!")
        return font

    def _write_with_box(self, canvas: Image.Image, text: str, font_path: str, tex_pos: tuple[int, int],
                        color: tuple[int, int, int] | tuple[int, int, int, int], font_size=20):
        draw = ImageDraw.Draw(canvas)
        text = text.replace(r'\n', '\n').replace(r'\t', '\t')
        font = self._resolve_font(font_path, font_size)
        if type(font) == ImageFont.FreeTypeFont:
            draw.multiline_text(tex_pos, text, font=font,
                                fill=color)
        else:
            draw.multiline_text(tex_pos, text, font=font,
                                fill=color, font_size=font_size)

    def _get_bbox(self, canvas: Image.Image, pos: tuple[int, int], text: str, font_path: str, font_size: int):
        draw = ImageDraw.Draw(canvas)
        font = self._resolve_font(font_path, font_size)
        text = text.replace(r'\n', '\n').replace(r'\t', '\t')
        return draw.multiline_textbbox(
            pos, text, font=font, font_size=font_size)

    def _write_event_info(self, canvas: Image.Image, event_info: EventInformation, color_1: tuple[int, int, int] | tuple[int, int, int, int],
                          color_2: tuple[int, int, int] | tuple[int, int, int, int], padding: tuple[int, int]):
        title, title_font, title_size = event_info.title
        place, place_font, place_size = event_info.place
        date, date_font, date_size = event_info.date
        desc, desc_font, desc_size = event_info.desc
        c_h = canvas.height
        p_x = padding[0]
        p_y = padding[1]
        bottom_padding = (c_h - p_y)
        left_padding = (p_x + 55)

        # Title preloc
        title_y = p_y + title_size
        title_loc = (left_padding, title_y)
        self.title_bbox = self._get_bbox(
            canvas, title_loc, title, title_font, title_size)

        # Place preloc
        place_loc = (left_padding, bottom_padding - (place_size))
        self.place_bbox = self._get_bbox(
            canvas, place_loc, place, place_font, place_size)

        # Date preloc
        date_loc = (left_padding, int(self.place_bbox[3] + 5))
        self.date_bbox = self._get_bbox(
            canvas, date_loc, date, date_font, date_size)

        bottom_delta = (c_h-25) - self.date_bbox[3]
        if bottom_delta < 0:
            place_loc = (left_padding, bottom_padding - int(
                (self.place_bbox[3] - self.place_bbox[1]) - bottom_delta))
            self.place_bbox = self._get_bbox(
                canvas, place_loc, place, place_font, place_size)
            date_loc = (left_padding, int(self.place_bbox[3]))
            self.date_bbox = self._get_bbox(
                canvas, date_loc, date, date_font, date_size)

            # Desc preloc
        desc_y = int((self.title_bbox[3] - self.title_bbox[1]) +
                     title_y + desc_size + 15)
        desc_loc = (left_padding, desc_y)
        self.description_bbox = self._get_bbox(
            canvas, desc_loc, desc, desc_font, desc_size)

        # Title
        self._write_with_box(canvas, title, title_font,
                             title_loc, color_1, font_size=title_size)
        # Place
        self._write_with_box(canvas, place, place_font,
                             place_loc, color_2, font_size=place_size)
        # Date
        self._write_with_box(canvas, date, date_font,
                             date_loc, color_2, font_size=date_size)
        # Description
        self._write_with_box(canvas, desc, desc_font,
                             desc_loc, color_1, font_size=desc_size)

    def create(self, canvas_type: Posts, bg_color_hex: str, fg_color_hex: str,
               event_information: EventInformation, link: str,
               bg_image: Image.Image | None = None, logo_image: Image.Image | None = None) -> Image.Image:
        bg_color = ImageColor.getrgb(bg_color_hex)
        fg_color = ImageColor.getrgb(fg_color_hex)
        bg_canvas = Image.new("RGBA", canvas_type.value, bg_color)

        padding = self._get_padding(canvas_type)
        upper_space = (0, padding[1])

        if bg_image:
            self._place_bg_image(bg_canvas, bg_image, padding)

        fade_length = bg_canvas.size[1] * 0.80
        # Draw gradient over background image
        upper_gradient = self._create_gradient_map(
            fade_length, (bg_canvas.width, bg_canvas.height - 2*padding[1]), fg_color)
        upper_gradient_rotated = upper_gradient.rotate(180)
        bg_canvas.alpha_composite(upper_gradient_rotated, upper_space)
        lower_gradient = self._create_gradient_map(
            fade_length, (bg_canvas.width, bg_canvas.height - 2*padding[1]), bg_color)
        bg_canvas.alpha_composite(lower_gradient, (0, padding[1]))

        # Draw rectangle over background image
        draw = ImageDraw.Draw(bg_canvas)
        draw.rectangle([(0, 0), (bg_canvas.width, padding[1])], fill=fg_color)

        self._write_event_info(bg_canvas, event_information,
                               bg_color, fg_color, padding)
        if logo_image:
            self._place_logo(bg_canvas, logo_image, link)
        return bg_canvas


def save_image(image: Image.Image, even_information: EventInformation, canvas_type: str, save_path: str):
    def _safer(s: str):
        return re.sub(r'[^A-Za-z0-9._-]', '_', s)
    file_name = f"{_safer(even_information.title[0])}_{_safer(even_information.date[0])}_{_safer(canvas_type)}"
    file_name_png = file_name + ".png"
    file_path_png = Path(save_path).resolve(
    ) / file_name_png
    image.save(file_path_png, format="PNG", optimize=True)


def main(args: Namespace):
    postmaker = PostMaker()

    background_image = None

    if args.background:
        path = Path(args.background)
        try:
            background_image = Image.open(path.absolute())
        except:
            raise ValueError("Arkaplan için girilen dosya bir resim değil!")

    logo_image = None
    if args.logo:
        path = Path(args.logo)
        try:
            logo_image = Image.open(path.absolute())
        except:
            raise ValueError("Logo için girilen dosya bir resim değil!")

    event_information = EventInformation(
        title=(args.title, args.title_font, args.title_size),
        desc=(args.description, args.description_font, args.description_size),
        date=(args.date, args.date_font, args.date_size),
        place=(args.place, args.place_font, args.place_size),
    )

    if args.canvas:
        image = postmaker.create(Posts[args.canvas], args.bgcolor,
                                 args.fgcolor, event_information, args.link, background_image, logo_image)
        save_image(image, event_information, args.canvas, args.savedir)
        image.show()
    else:
        for canvas_type in Posts:
            image = postmaker.create(canvas_type, args.bgcolor,
                                     args.fgcolor, event_information, args.link, background_image, logo_image)
            save_image(image, event_information,
                       canvas_type.name, args.savedir)
            image.show()
    return


if __name__ == "__main__":
    parser = ArgumentParser(description="Sosyal medya için post hazırlayıcı.")
    parser.add_argument(
        "--canvas", "-c",
        type=str,
        choices=["IG_POST", "IG_STORY", "IG_REELS",
                 "FB_POST", "FB_STORY", "FB_REELS", "X_POST"]
    )
    parser.add_argument(
        "--background", "-bg",
        type=str,
        help="Logo resminin bilgisayardaki konumu"
    )
    parser.add_argument(
        "--logo", "-l",
        type=str,
        help="Arka plan resminin bilgisayardaki konumu"
    )
    parser.add_argument(
        "--bgcolor", "-bgc",
        type=str,
        default="#ffffff",
        help="Arka plan rengi"
    )
    parser.add_argument(
        "--fgcolor", "-fgc",
        type=str,
        default="#eb4034",
        help="Ön plan rengi"
    )
    parser.add_argument(
        "--place", "-p",
        type=str,
        default="Place: Not decided yet",
        help="Etkinliğin yapılacağı mekan"
    )
    parser.add_argument(
        "--place_font", "-pf",
        type=str,
        default="PlaceholderFont",
        help="Mekanın fontu"
    )
    parser.add_argument(
        "--place_size", "-ps",
        type=int,
        default=75,
        help="Mekanın font boyutu"
    )
    parser.add_argument(
        "--date", "-da",
        type=str,
        default="Date: Not decided yet",
        help="Etkinliğin yapılacağı zaman"
    )
    parser.add_argument(
        "--date_font", "-daf",
        type=str,
        default="PlaceholderFont",
        help="Zamanın fontu"
    )
    parser.add_argument(
        "--date_size", "-das",
        type=int,
        default=60,
        help="Zamanın font boyutu"
    )
    parser.add_argument(
        "--title", "-t",
        type=str,
        default="Title: Not decided yet",
        help="Etkinliğin başlığı"
    )
    parser.add_argument(
        "--title_font", "-tf",
        type=str,
        default="PlaceholderFont",
        help="Başlığın fontu"
    )
    parser.add_argument(
        "--title_size", "-ts",
        type=int,
        default=100,
        help="Başlığın font boyutu"
    )
    parser.add_argument(
        "--description", "-desc",
        type=str,
        default="Description: Not decided yet",
        help="Etkinliğin açıklaması"
    )
    parser.add_argument(
        "--description_font", "-descf",
        type=str,
        default="PlaceholderFont",
        help="Açıklamanın fontu"
    )
    parser.add_argument(
        "--description_size", "-descs",
        type=int,
        default=54,
        help="Açıklamanın font boyutu"
    )
    parser.add_argument(
        "--savedir", "-sd",
        type=str,
        default=".",
        help="Dosyaların kaydedileceği yer"
    )
    parser.add_argument(
        "--link", "-li",
        type=str,
        default="PlaceholderLink",
        help="QR kodu oluşturulacak olan link"
    )
    args = parser.parse_args()
    main(args)
