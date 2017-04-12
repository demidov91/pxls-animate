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


def to_image(dat_file: str, out_file: str):
    data = bytes(chain(*data_file_to_rgb_array(dat_file)))
    Image.frombytes('RGB', defines.DIMENSIONS, data).save(out_file)


def create_gif(
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
        rectangle: Tuple[Tuple[int, int], Tuple[int, int]],
        out_file: str):
    frames = (
        np.array(data_file_to_rgb_array(x), dtype=np.uint8).reshape(defines.DIMENSIONS + (3, ))
        for x in list_filepaths_in_datetime_range(start_dt, end_dt)[::5]
    )
    imageio.mimwrite(out_file, frames)


parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, help='Command name')
parser.add_argument('--out', type=str, dest='out_file', help='Output file')
parser.add_argument('--in', type=str, dest='in_file', help='Input file')
parser.add_argument('--start', type=str, dest='start_dt', help='Start datetime')
parser.add_argument('--end', type=str, dest='end_dt', help='End datetime')

args = parser.parse_args()

if args.command == 'save':
    save(args.out_file)
elif args.command == 'to_image':
    to_image(args.in_file, args.out_file)
elif args.command == 'to_gif':
    start_dt = datetime.datetime.strptime(args.start_dt, defines.API_DATETIME_FORMAT)
    end_dt = datetime.datetime.strptime(args.end_dt, defines.API_DATETIME_FORMAT)
    create_gif(start_dt, end_dt, defines.DIMENSIONS, args.out_file)
else:
    raise ValueError()
