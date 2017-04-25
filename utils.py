import gzip
import defines
import os
import datetime
import re
from contextlib import ContextDecorator
import requests
import numpy as np
import settings
from PIL import Image
from itertools import chain
import imageio
from logging.config import dictConfig

import logging
logger = logging.getLogger(__name__)

# Image data file names start with the following patter.
dt_in_filename_pattern = re.compile('(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})')

# GIF with more data than this becomes too detailed.
MAX_GIF_INFO = defines.DIMENSIONS[0] * defines.DIMENSIONS[1] * 90 // 32

SEARCH_FOR_DATA_FILE_BY_PATTERN = '%Y_%m_%d'


def points_to_size(start_point: tuple, end_point: tuple):
    """
    Helper-method to convert left top and right bottom coordinates into (width, height) tuple.
    (5, 5), (5, 5) -> (1, 1)
    (5, 5), (6, 6) -> (2, 2)
    :param start_point: left top point.
    :param end_point: right bottom point.
    """
    return tuple(b - a + 1 for a, b in zip(start_point, end_point))


def get_current_data_response():
    return requests.get(defines.CANVAS_URL, timeout=20, cookies={'pxls-agegate': '1'})


def _data_file_to_rgb_array(dat_file: str, start_point=(0, 0), size=defines.DIMENSIONS):
    with compressed_pixels_reader(dat_file) as reader:
        yield from reader.read_rectangle(start_point, size)


def data_file_to_pil_image(dat_file: str, start_point=(0, 0), size=defines.DIMENSIONS, thumbnail: float=None):
    data = bytes(chain(*_data_file_to_rgb_array(dat_file, start_point, size)))
    im = Image.frombytes('RGB', size, data)
    if thumbnail is None or thumbnail == 1.0:
        return im

    size = tuple(int(x * thumbnail) for x in size)
    if not any(size):
        size = (10, 10)
        logger.info('%s thumbnail was too little. Accepting %dx%d.', thumbnail, size[0], size[1])

    im.thumbnail(size)
    return im


def list_filepaths_in_datetime_range(start_dt, end_dt):
    paths = []
    for file_path in os.listdir(defines.DATA_DIR):
        match = dt_in_filename_pattern.search(file_path)
        if not match:
            continue

        image_dt = datetime.datetime.strptime(match.group(1), defines.DATA_DT_FORMAT)
        if not (start_dt <= image_dt <= end_dt):
            continue

        paths.append(os.path.join(defines.DATA_DIR, file_path))

    return sorted(paths)


class compressed_bytes_reader(ContextDecorator):
    extra_encoded_byte = None   # type: int

    def __init__(self, dat_file: str):
        self.dat_file = dat_file

    def __enter__(self):
        self.fp = gzip.open(self.dat_file, mode='rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fp.close()

    def read_rectangle(self, start: tuple, size: tuple):
        for row in range(start[1], start[1] + size[1]):
            row_start = row * defines.DIMENSIONS[0] + start[0]
            self.fp.seek(row_start // 2)
            yield from self.read_bytes(size[0], more=row_start % 2)

    def read_bytes(self, n: int, more: bool=False):
        if more:
            yield self.fp.read(1)[0] % 16
            n -= 1

        for compressed in self.fp.read(n // 2):
            yield compressed >> 4
            yield compressed % 16

        if n % 2:
            yield self.fp.read(1)[0] >> 4


class compressed_pixels_reader(compressed_bytes_reader):
    def read_rectangle(self, start: tuple, size: tuple):
        return (defines.PALETTE_BY_BYTE[x] for x in super().read_rectangle(start, size))


class GifBuilder:
    step = None         # type: int
    files_count = None  # type: int

    def __init__(self,
                 start_dt: datetime.datetime,
                 end_dt: datetime.datetime,
                 start_point: tuple,
                 size: tuple,
                 thumbnail: float=None):
        self.start_dt = start_dt or defines.START_DATETIME
        self.end_dt = end_dt or datetime.datetime.now()
        self.start_point = start_point
        self.size = size
        self.thumbnail = thumbnail

    def build(self, target):
        file_paths = tuple(list_filepaths_in_datetime_range(self.start_dt, self.end_dt))
        self.files_count = len(file_paths)
        self.step = self.size[0] * self.size[1] * self.files_count // MAX_GIF_INFO + 1
        if self.step < 60:
            self.step = 60

        logger.info('Step %d is chosen for %dx%d gif from %s till %s (potentially %d frames)',
                    self.step, self.size[0], self.size[1], self.start_dt, self.end_dt, self.files_count
                    )

        frames = (self.data_file_to_imageio_array(x) for x in file_paths[::self.step])
        imageio.mimwrite(target, frames, format='gif', subrectangles=True)

    def data_file_to_imageio_array(self, dat_file: str):
        if self.thumbnail is None or self.thumbnail == 1.0:
            pixel_generator = _data_file_to_rgb_array(dat_file, self.start_point, self.size)
            height = self.size[1]
            width = self.size[0]
        else:
            image = data_file_to_pil_image(dat_file, self.start_point, self.size, self.thumbnail)
            height = image.height
            width = image.width
            pixel_generator = image.getdata()

        return np.array(list(pixel_generator), dtype=np.uint8).reshape((height, width, 3))


def configure_logger():
    dictConfig(settings.LOGGING)


def get_nearest_dat_file(target_time: datetime.datetime) -> str:
    today = target_time.date()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    str_dates = tuple(x.strftime(SEARCH_FOR_DATA_FILE_BY_PATTERN) for x in (yesterday, today, tomorrow))

    search_pattern_string = '(' + '|'.join('{}.+'.format(x) for x in str_dates) + ')' + '\.dat'

    search_pattern = re.compile(search_pattern_string)

    logger.debug('Search pattern: %s', search_pattern_string)

    min_delta = datetime.timedelta(days=2)
    file_found = None

    for file_name in os.listdir(defines.DATA_DIR):
        datetime_match = search_pattern.match(file_name)
        if not datetime_match:
            continue

        file_time = datetime.datetime.strptime(datetime_match.group(1), defines.DATA_DT_FORMAT)
        delta = abs(file_time - target_time)
        if delta < min_delta:
            if delta < datetime.timedelta(minutes=1):
                file_found = file_name
                break

            min_delta = delta
            file_found = file_name

    if file_found is None:
        return

    return os.path.join(defines.DATA_DIR, file_found)


def get_last_data_file():
    return os.path.join(defines.DATA_DIR, max(filter(lambda x: x.endswith('.dat'), os.listdir(defines.DATA_DIR))))
