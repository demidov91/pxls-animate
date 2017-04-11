import gzip
import argparse
import defines
import requests
from PIL import Image


def save(out_file: str):
    data = bytearray()
    for byte_1, byte_2 in requests.get(defines.CANVAS_URL, timeout=20).iter_content(chunk_size=2):
        data.append(byte_1 << 4 | byte_2)

    with gzip.open(out_file, 'wb') as f:
        f.write(data)


def to_image(dat_file: str, out_file: str):
    data = []
    with gzip.open(dat_file, mode='rb') as f:
        for compressed in f.read():
            data.extend(defines.PALETTE_BY_BYTE[compressed >> 4])
            data.extend(defines.PALETTE_BY_BYTE[compressed % 16])

    Image.frombytes('RGB', defines.DIMENSIONS, bytes(data)).save(out_file)


parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, help='Command name')
parser.add_argument('--out', type=str, dest='out_file', help='Output file')
parser.add_argument('--in', type=str, dest='in_file', help='Input file')

args = parser.parse_args()

if args.command == 'save':
    save(args.out_file)
elif args.command == 'to_image':
    to_image(args.in_file, args.out_file)
else:
    raise ValueError()
