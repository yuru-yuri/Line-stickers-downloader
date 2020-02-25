from requests import get
from argparse import ArgumentParser, Namespace
from lxml.html import document_fromstring, Element, HtmlElement
from typing import List, Tuple
import argcomplete
import re
from pathlib import Path
from progressbar.bar import ProgressBar
import json

arguments = ArgumentParser()
arguments.add_argument('idx', type=int, help='Get info for ids', nargs="*")
arguments.add_argument('--url', type=str, help='Download stickers for url', default='')
arguments.add_argument('-d', '--destination', type=str, help='Destination folder', default='')

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
            name = parser.cssselect('[class$="Top"] [class$="Head"] > *')[0].text
            print('Downloading {}'.format(name))
            static_images, animated_images = self.get_images(parser)
            len(static_images) > 0 and self.download(static_images, name)
            len(animated_images) > 0 and self.download(animated_images, name, True)

    def get_images(self, parser) -> Tuple[List[str], List[str]]:
        elements = parser.cssselect('[class$="Sticker"] [data-preview]')
        static_images = []
        animated_images = []
        for element in elements:  # type: Element element
            try:
                data = json.loads(element.get('data-preview'))
                if 'animation' == data['type']:
                    animated_images.append(data['animationUrl'])
                static_images.append(data['staticUrl'])
            except Exception:
                continue
        return static_images, animated_images

    @staticmethod
    def url2idx(url: str) -> str:
        return re.search(r'/product/(\d+)/', url).group(1)

    def download(self, images, name, animated = False):
        clear_name = re.sub(r'[^a-zA-Z\s]+', '-', name)
        if animated:
            clear_name += '_animated'
        dst = self.destination.joinpath(clear_name)
        if dst.is_dir():
            print('Destination exists. Skip')
            return
        dst.mkdir(parents=True, exist_ok=True)
        progress = ProgressBar(max_value=len(images))
        for idx, url in enumerate(images):
            with open(str(dst.joinpath('{}.png'.format(idx + 1))), 'wb') as file:
                file.write(get(url).content)
            progress.update(idx + 1)


if __name__ == '__main__':
    downloader = Downloader(arguments)
    downloader.run()

