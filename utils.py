import gzip
import defines
import os
import datetime
import re
from contextlib import ContextDecorator
import numpy as np

dt_in_filename_pattern = re.compile('(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})')


def data_file_to_rgb_array(dat_file: str, start_point=(0, 0), size=defines.DIMENSIONS):
    with compressed_reader(dat_file) as reader:
        yield from reader.read_rectangle(start_point, size)


def data_file_to_imageio_array(dat_file: str, start_point=(0, 0), size=defines.DIMENSIONS):
    return np.array(
        list(data_file_to_rgb_array(dat_file, start_point, size)),
        dtype=np.uint8
    ).reshape((size[1], size[0], 3))


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


class compressed_reader(ContextDecorator):
    extra_encoded_byte = None # type: int

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
            yield from self._read_pixels(size[0], more=row_start % 2)

    def _read_pixels(self, n: int, more: bool=False):
        if more:
            yield defines.PALETTE_BY_BYTE[self.fp.read(1)[0] % 16]
            n -= 1

        for compressed in self.fp.read(n // 2):
            yield defines.PALETTE_BY_BYTE[compressed >> 4]
            yield defines.PALETTE_BY_BYTE[compressed % 16]

        if n % 2:
            yield defines.PALETTE_BY_BYTE[self.fp.read(1)[0] >> 4]








