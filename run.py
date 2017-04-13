import gzip
import argparse
import defines
import requests
from PIL import Image
from utils import data_file_to_rgb_array, list_filepaths_in_datetime_range, data_file_to_imageio_array
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
        start_point: tuple,
        size: tuple,
        out_file: str):
    if start_dt is None:
        start_dt = defines.START_DATETIME

    if end_dt is None:
        end_dt = datetime.datetime.now()

    file_paths = tuple(list_filepaths_in_datetime_range(start_dt, end_dt))

    step = len(file_paths) // 90 + 1

    print('With step {}'.format(step))

    frames = (data_file_to_imageio_array(x, start_point, size) for x in file_paths[::step])

    imageio.mimwrite(out_file, frames)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', type=str, help='Command name')
    parser.add_argument('--out', type=str, dest='out_file', help='Output file')
    parser.add_argument('--in', type=str, dest='in_file', help='Input file')
    parser.add_argument('--start', type=str, dest='start_dt', help='Start datetime')
    parser.add_argument('--end', type=str, dest='end_dt', help='End datetime')
    parser.add_argument('--start-point', type=int, dest='start_point', nargs=2,
                        help='Left top point of the image.', default=(0, 0))
    parser.add_argument('--end-point', type=int, dest='end_point', nargs=2,
                        default=tuple(x - 1 for x in defines.DIMENSIONS), help='Image dimensions. Width and height.')

    args = parser.parse_args()
    size = tuple(b - a + 1 for a, b in zip(args.start_point, args.end_point))

    if args.command == 'save':
        save(args.out_file)

    elif args.command == 'to_image':
        to_image(args.in_file, args.out_file, args.start_point, size)

    elif args.command == 'to_gif':
        if args.start_dt:
            start_dt = datetime.datetime.strptime(args.start_dt, defines.API_DATETIME_FORMAT)
        else:
            start_dt = None

        if args.end_dt:
            end_dt = datetime.datetime.strptime(args.end_dt, defines.API_DATETIME_FORMAT)
        else:
            end_dt = None

        create_gif(start_dt, end_dt, args.start_point, size, args.out_file)

    else:
        raise ValueError('Unknown command: {}'.format(args.command))
