import gzip
import argparse
import defines
import requests

from utils import data_file_to_pil_image, get_gif_frames, configure_logger, points_to_size
import datetime
import imageio
import logging

logger = logging.getLogger(__name__)


def save(out_file: str):
    data = bytearray()
    for byte_1, byte_2 in requests.get(defines.CANVAS_URL, timeout=20).iter_content(chunk_size=2):
        data.append(byte_1 << 4 | byte_2)

    with gzip.open(out_file, 'wb') as f:
        f.write(data)


def to_image(dat_file: str, out_file: str, start_point, size):
    data_file_to_pil_image(dat_file, start_point, size).save(out_file)


def create_gif(
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
        start_point: tuple,
        size: tuple,
        out_file: str):
    imageio.mimwrite(out_file, get_gif_frames(start_dt, end_dt, start_point, size))


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

    args = parser.parse_args()
    size = points_to_size(args.start_point, args.end_point)

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
