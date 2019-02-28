from requests import get
from argparse import ArgumentParser, Namespace
from lxml.html import document_fromstring, Element, HtmlElement
from tinycss import make_parser
import argcomplete
import re
from pathlib import Path
from progressbar.bar import ProgressBar

arguments = ArgumentParser()
arguments.add_argument('idx', type=int, help='Get manga info from ids', nargs="*")
arguments.add_argument('--url', type=str, help='Get manga info from ids', default='')
arguments.add_argument('-d', '--destination', type=str, help='Destination folder', default='')
arguments.add_argument(
    '-a', '--animate', help='Download animate version', action='store_const', const=True, default=False
)

argcomplete.autocomplete(arguments)


class Downloader:
    args = None  # type: Namespace indexes
    base_url = 'https://store.line.me/stickershop/product/{}/en'  # type: str base_url
    indexes = []  # type: list indexes
    destination = ''  # type: Path destination

    def __init__(self, args: ArgumentParser):
        self.args = args.parse_args()
        self.indexes += self.args.idx
        if len(self.args.url) > 0:
            self.indexes.append(self.url2idx(self.args.url))
        self.destination = Path(__file__).resolve().parent
        if len(self.args.destination):
            self.destination = Path(self.args.destination).resolve()

    def run(self):
        for idx in self.indexes:  # type: int idx
            content = get(self.base_url.format(idx)).text
            parser = document_fromstring(content)  # type: HtmlElement parser
            name = parser.cssselect('p + h3')[0].text
            print('Downloading {}'.format(name))
            images = self.get_images(parser)
            self.download(images, name)

    def get_images(self, parser):
        elements = parser.cssselect('section[id] ul > li span[style]')
        images = []
        for element in elements:  # type: Element element
            value = self.get_image_url_from_style(element.get('style'))
            if value is not None:
                images.append(value)
        return images

    @staticmethod
    def url2idx(url: str) -> str:
        return re.search(r'/product/(\d+)/', url).group(1)

    @staticmethod
    def get_image_url_from_style(style: str):
        css = make_parser()
        value = None
        for declaration in css.parse_style_attr(style)[0]:
            if declaration.name == 'background':
                for token in declaration.value:
                    if token.type == 'URI':
                        value = token.value
                        break
            if declaration.name == 'background-image':
                value = declaration.value[0].value
                break
        return value

    def download(self, images, name):
        clear_name = re.sub(r'[^a-zA-Z\s]+', '-', name)
        dst = self.destination.joinpath(clear_name)
        if dst.is_dir():
            print('Destination exists. Skip')
            return
        dst.mkdir(parents=True)
        progress = ProgressBar(max_value=len(images))
        for idx, image in enumerate(images):
            url = self.sticker_url(image)
            with open(str(dst.joinpath('{}.png'.format(idx + 1))), 'wb') as file:
                file.write(get(url).content)
            progress.update(idx + 1)

    def sticker_url(self, url):
        animate_suffix = '/IOS/sticker_popup.png;compress=true'
        if not self.args.animate:
            return url
        return re.sub(r'(.+?/\d+)/\w+/sticker.+', r'\1', url) + animate_suffix


if __name__ == '__main__':
    downloader = Downloader(arguments)
    downloader.run()
