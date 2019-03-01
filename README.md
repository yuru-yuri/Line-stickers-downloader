# Line-stickers-downloader

### Download grabber:
Use git:
git clone https://github.com/yuru-yuri/Line-stickers-downloader.git

OR
Download zip https://github.com/yuru-yuri/Line-stickers-downloader/archive/master.zip


### Usage:

Go to https://store.line.me/stickershop/showcase/top/en page
Go to the page with your favorite stickers
Copy page url (exaple: https://store.line.me/stickershop/product/10801/en)

Run grabber:

python Line-stickers-downloader/dl.py 10801 10805 10811

OR

python Line-stickers-downloader/dl.py --url https://store.line.me/stickershop/product/10801/en

#### Help:

```bash
python Line-stickers-downloader/dl.py -h

usage: Line-stickers-downloader/dl.py [-h] [--url URL] [-d DESTINATION] [idx [idx ...]]

positional arguments:
  idx                   Get manga info from ids

optional arguments:
  -h, --help            show this help message and exit
  --url URL             Get manga info from ids
  -d DESTINATION, --destination DESTINATION
                        Destination folder
```
