import gzip
import argparse
import defines
import requests
from PIL import Image
from typing import Tuple
from utils import data_file_to_rgb_array, list_filepaths_in_datetime_range
import datetime
import imageio
from itertools import chain
import numpy as np


def save(out_file: str):
    data = bytearray()
    for byte_1, byte_2 in requests.get(defines.CANVAS_URL, timeout=20).iter_content(chunk_size=2):
        data.append(byte_1 << 4 | byte_2)

    with gzip.open(out_file, 'wb') as f:
        f.write(data)


def to_image(dat_file: str, out_file: str, start_point, size):
    data = bytes(chain(*data_file_to_rgb_array(dat_file, start_point, size)))
    Image.frombytes('RGB', size, data).save(out_file)


def create_gif(
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
        start_point: Tuple[int, int],
        size: Tuple[int, int],
        out_file: str):
    frames = (
        np.array(list(data_file_to_rgb_array(x, start_point, size)), dtype=np.uint8).reshape((size[1], size[0], 3))
        for x in list_filepaths_in_datetime_range(start_dt, end_dt)[::5]
    )
    imageio.mimwrite(out_file, frames)


parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, help='Command name')
parser.add_argument('--out', type=str, dest='out_file', help='Output file')
parser.add_argument('--in', type=str, dest='in_file', help='Input file')
parser.add_argument('--start', type=str, dest='start_dt', help='Start datetime')
parser.add_argument('--end', type=str, dest='end_dt', help='End datetime')
parser.add_argument('--start-point', type=int, dest='start_point', nargs=2, help='Left top point of the image.')
parser.add_argument('--end-point', type=int, dest='end_point', nargs=2, help='Image dimensions. Width and height.')

args = parser.parse_args()

if args.start_dt:
    start_dt = datetime.datetime.strptime(args.start_dt, defines.API_DATETIME_FORMAT)

if args.end_dt:
    end_dt = datetime.datetime.strptime(args.end_dt, defines.API_DATETIME_FORMAT)

start_point = args.start_point or (0, 0)
end_point = args.end_point or tuple(x - 1 for x in defines.DIMENSIONS)
size = end_point[0] - start_point[0] + 1, end_point[1] - start_point[1] + 1

if args.command == 'save':
    save(args.out_file)
elif args.command == 'to_image':
    to_image(args.in_file, args.out_file, start_point, size)
elif args.command == 'to_gif':
    create_gif(start_dt, end_dt, start_point, size, args.out_file)
else:
    raise ValueError()
