#! /usr/bin/env python

import gzip
import argparse
import defines

from utils import data_file_to_pil_image, GifBuilder, configure_logger, points_to_size, compressed_bytes_reader, \
    get_current_data_response, get_last_data_file
import datetime
import logging

logger = logging.getLogger(__name__)

TWO_BYTES = 256 * 256


def save_as_data(out_file: str):
    data = bytearray()
    for byte_1, byte_2 in get_current_data_response().iter_content(chunk_size=2):
        data.append(byte_1 << 4 | byte_2)

    with gzip.open(out_file, 'wb') as f:
        f.write(data)


def save_as_diff(out_file: str):
    base_file = get_last_data_file()
    with compressed_bytes_reader(base_file) as base_br, gzip.open(out_file, 'wb') as out_fp:
        for i, old_current_byte in enumerate(
                zip(base_br.read_rectangle((0, 0), defines.DIMENSIONS), get_current_data_response().content)
        ):
            if old_current_byte[0] != old_current_byte[1]:
                record = bytes((i // TWO_BYTES, (i % TWO_BYTES) // 256, i % 256 | old_current_byte[1]))
                logger.debug(record)
                out_fp.write(record)


def dat_to_image(dat_file: str, out_file: str, start_point, size, thumbnail):
    data_file_to_pil_image(dat_file, start_point, size, thumbnail).save(out_file)


def diff_to_image(base_file: str, diff_file: str, out_file: str):
    base_image = data_file_to_pil_image(base_file)
    with gzip.open(diff_file, 'rb') as f:
        while True:
            record = f.read(2)
            if not record:
                break
            base_file[x, y] = 0


def create_gif(
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
        start_point: tuple,
        size: tuple,
        thumbnail: float,
        out_file: str):
    GifBuilder(start_dt, end_dt, start_point, size, thumbnail).build(out_file)


if __name__ == '__main__':
    configure_logger()
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
    parser.add_argument('--thumbnail', type=float, dest='thumbnail', help='Set number between 0 and 1')

    args = parser.parse_args()
    size = points_to_size(args.start_point, args.end_point)
    thumbnail = args.thumbnail

    if args.command == 'save-full':
        save_as_data(args.out_file)

    elif args.command == 'save-diff':
        save_as_diff(args.out_file)

    elif args.command == 'to-image':
        dat_to_image(args.in_file, args.out_file, args.start_point, size, thumbnail)

    elif args.command == 'to-gif':
        if args.start_dt:
            start_dt = datetime.datetime.strptime(args.start_dt, defines.API_DATETIME_FORMAT)
        else:
            start_dt = None

        if args.end_dt:
            end_dt = datetime.datetime.strptime(args.end_dt, defines.API_DATETIME_FORMAT)
        else:
            end_dt = None

        create_gif(start_dt, end_dt, args.start_point, size, thumbnail, args.out_file)

    else:
        raise ValueError('Unknown command: {}'.format(args.command))
