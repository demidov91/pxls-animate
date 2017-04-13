from flask import Flask, make_response
from utils import configure_logger, data_file_to_pil_image, points_to_size, get_nearest_dat_file
from flask_util import get_flask_datetime, get_flask_pair
from io import BytesIO
import datetime
import logging
import defines

logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/im')
def get_image():
    start_point = get_flask_pair('start-point') or (0, 0)
    end_point = get_flask_pair('start-point') or tuple(x-1 for x in defines.DIMENSIONS)
    nearest_time = get_flask_datetime('time') or datetime.datetime.now()
    dat_file = get_nearest_dat_file(nearest_time)
    if not dat_file:
        return '404', 404

    image = data_file_to_pil_image(dat_file, start_point, points_to_size(start_point, end_point))
    buffer = BytesIO()
    image.save(buffer, format='png')
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route('/gif')
def get_gif():
    pass

if __name__ == '__main__':
    configure_logger()
    app.run()
