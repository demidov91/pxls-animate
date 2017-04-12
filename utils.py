import gzip
import defines
from typing import Iterable
import os
import datetime
import re

dt_in_filename_pattern = re.compile('(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})')


def data_file_to_rgb_array(dat_file: str):
    data = []
    with gzip.open(dat_file, mode='rb') as f:
        for compressed in f.read():
            data.append(defines.PALETTE_BY_BYTE[compressed >> 4])
            data.append(defines.PALETTE_BY_BYTE[compressed % 16])

    return data


def list_filepaths_in_datetime_range(start_dt, end_dt) -> Iterable[str]:
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


