import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from pathlib import Path
from postermakerClass import PostMaker, EventInformation, PostInformation, Posts


def display_generated_image(generated_posters_path: Path):

    extensions = {".png", ".jpg", ".jpeg", ".webm"}
    files = [f for f in generated_posters_path.iterdir() if f.suffix.lower()
             in extensions]

    if files:
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        st.image(str(latest_file), caption="Üretilen Posteriniz")
    else:
        st.warning("No images found in the directory.")


def save_file(file: UploadedFile, directory: str) -> None:
    save_path: Path = Path("__file__").parent / directory
    save_path.mkdir(exist_ok=True)
    file_path = save_path / file.name

    with open(file_path, "wb") as f:
        f.write(file.getvalue())


def upload_image(label: str, upload_desc: str, display_desc, file_directory_name: str) -> None:
    st.file_uploader(
        upload_desc,
        ["webm", "jpg", "jpeg", "png"],
        accept_multiple_files=False,
        key=label
    )
    if st.session_state[label]:
        save_file(st.session_state[label], file_directory_name)
        print(
            f"Saved {st.session_state[label].name} to {file_directory_name}")
        st.image(st.session_state[label],
                 caption=display_desc)


def get_fonts() -> dict[str, Path] | None:
    fonts_path: Path = Path("__file__").parent / "Fonts"
    if fonts_path.exists():
        fonts: dict[str, Path] = {}
        for font in fonts_path.iterdir():
            if font.is_file():
                fonts[font.name] = font.resolve()
    else:
        return None
    return fonts


class Text_Field():

    def __call__(self, label: str, title: str, size_value: int = 1) -> None:
        """
        sets:
            st.session_state[label]_content
            st.session_state[label]_size_int
            st.session_state[label]_font
        """
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_area(
                f"Etkinlik için {title}",
                key=label+"_content"
            )
        with col2:
            st.number_input(
                title + " Boyutu",
                key=label+"_size_int",
                value=size_value,
                min_value=1
            )
        with col3:
            fonts = get_fonts()
            if not fonts:
                st.error("No fonts were found in the Fonts folder!")
            else:
                st.selectbox(
                    "Fontlar",
                    fonts.keys(),
                    key=label+"_font")


def execute_script():
    generated_posters_directory_name: str = "generated_posters"
    save_path: Path = Path("__file__").parent / \
        generated_posters_directory_name
    save_path.mkdir(exist_ok=True)

    for key, value in st.session_state.items():
        if "_int" in str(key) and value and int(value) < 0:
            st.error(f"{value} 0'dan küçük olamaz!")

    postmaker = PostMaker()
    ss = st.session_state
    fonts = get_fonts()
    if fonts:
        event_information = EventInformation(
            title=(
                ss.title_content,
                str(fonts[ss.title_font].absolute()),
                ss.title_size_int
            ),
            desc=(
                ss.description_content,
                str(fonts[ss.description_font].absolute()),
                ss.description_size_int
            ),
            date=(
                ss.date_content,
                str(fonts[ss.date_font].absolute()),
                ss.date_size_int
            ),
            place=(
                ss.place_content,
                str(fonts[ss.place_font].absolute()),
                ss.place_size_int
            )
        )
        if ss.background_image and ss.logo:
            with st.spinner("Posteriniz oluşturuluyor...", show_time=True):
                postmaker.create(
                    PostInformation(
                        ss.poster_width_int,
                        ss.poster_height_int,
                        ss.text_padding_int,
                        ss.x_padding_int,
                        ss.y_padding_int
                    ),
                    ss.bgcolor,
                    ss.fgcolor,
                    event_information,
                    ss.qr_code,
                    ss.background_image,
                    ss.logo,
                    str(save_path.absolute())
                )
                display_generated_image(save_path.absolute())
                st.success(
                    f"Dosya {save_path.absolute()} adresine kaydedildi. Dosyanın PDF'ine aynı klasörden ulaşabilirsiniz. ")
    return


if __name__ == "__main__":

    st.title("Poster Yapıcı")

    text_input = Text_Field()
    text_input("title", "Başlık", 200)
    text_input("description", "Açıklama", 90)
    text_input("place", "Adres", 100)
    text_input("date", "Tarih", 120)

    st.text_input("QR Kodu için Link", key="qr_code")

    l_col, r_col = st.columns(2)
    with l_col:
        st.color_picker("Arka Plan Rengi", "#ffffff", key="bgcolor")
    with r_col:
        st.color_picker("Ön Plan Rengi", "#b83232", key="fgcolor")

    upload_image(
        "background_image",
        "Arka Plan Resmi Yükleyin",
        "Yüklenen Arka Plan Resmi",
        "file_uploads"
    )

    upload_image(
        "logo",
        "Logo Yükleyin",
        "Yüklenen Logo",
        "file_uploads"
    )

    st.number_input(
        "Poster Genişliği",
        key="poster_width_int",
        value=2100,
        min_value=1,
        step=1
    )

    st.number_input(
        "Poster Yüksekliği",
        key="poster_height_int",
        value=2700,
        min_value=1,
        step=1
    )

    st.number_input(
        "Poster Kenarlarından Uzaklık (Yatay)",
        key="x_padding_int",
        value=110,
        min_value=0,
        step=1
    )

    st.number_input(
        "Poster Kenarlarından Uzaklık (Dikey)",
        key="y_padding_int",
        value=270,
        min_value=0,
        step=1
    )

    st.number_input(
        "Satırlar Arasındaki Uzaklık",
        key="text_padding_int",
        value=15,
        min_value=0,
        step=1
    )

    if st.button("Posteri Oluştur"):
        execute_script()
