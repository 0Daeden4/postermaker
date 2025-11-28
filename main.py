from PIL import Image
from argparse import ArgumentParser, Namespace
from pathlib import Path
from postermakerClass import PostMaker, EventInformation, PostInformation, Posts


def main(args: Namespace):
    postmaker = PostMaker()

    background_image = None

    if args.background:
        background_image = Path(args.background)
        try:
            Image.open(background_image.absolute())
        except:
            raise ValueError("Arkaplan için girilen dosya bir resim değil!")

    logo_image = None
    if args.logo:
        logo_image = Path(args.logo)
        try:
            Image.open(logo_image.absolute())
        except:
            raise ValueError("Logo için girilen dosya bir resim değil!")

    event_information = EventInformation(
        title=(args.title, args.title_font, args.title_size),
        desc=(args.description, args.description_font, args.description_size),
        date=(args.date, args.date_font, args.date_size),
        place=(args.place, args.place_font, args.place_size),
    )

    if args.width and args.height:
        postmaker.create(PostInformation(args.width, args.height, args.text_padding, args.xpadding, args.ypadding), args.bgcolor,
                         args.fgcolor, event_information, args.qr, background_image, logo_image, args.savedir)
    elif args.canvas:
        postmaker.create(Posts[args.canvas], args.bgcolor,
                         args.fgcolor, event_information, args.qr, background_image, logo_image, args.savedir)
    else:
        for canvas_type in Posts:
            postmaker.create(canvas_type, args.bgcolor,
                             args.fgcolor, event_information, args.qr, background_image, logo_image, args.savedir)
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
        "--qr", "-li",
        type=str,
        default="",
        help="QR kodu oluşturulacak olan yazı"
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        help="Görsel'in genişliği"
    )
    parser.add_argument(
        "--height", "-he",
        type=int,
        help="Görselin yüksekliği"
    )
    parser.add_argument(
        "--xpadding", "-xp",
        type=int,
        default=0,
        help="Görselin x paddingi"
    )
    parser.add_argument(
        "--ypadding", "-yp",
        type=int,
        default=0,
        help="Görselin y paddingi"
    )
    parser.add_argument(
        "--text_padding", "-tp",
        type=int,
        default=0,
        help="Görseldeki yazılar arasındaki mesafe (px). Pre-made Canvas'lar ile çalısmaz."
    )
    args = parser.parse_args()
    main(args)
