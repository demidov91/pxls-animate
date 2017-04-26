from flask import Flask, make_response
from utils import configure_logger, data_file_to_pil_image, points_to_size, get_nearest_dat_file, GifBuilder
from flask_util import get_flask_datetime, get_coordinates, get_flask_arg, get_flask_float, get_flask_detailing
from io import BytesIO
import datetime
import logging
import defines

logger = logging.getLogger(__name__)
app = Flask(__name__)
configure_logger()


@app.route('/im')
def get_image():
    start_point = get_coordinates('start-point') or (0, 0)
    end_point = get_coordinates('end-point') or tuple(x - 1 for x in defines.DIMENSIONS)
    thumbnail = get_flask_float('thumbnail')
    for_time = get_flask_datetime('time')
    dat_file = get_nearest_dat_file(for_time or datetime.datetime.now())
    if not dat_file:
        return '404', 404

    image = data_file_to_pil_image(dat_file, start_point, points_to_size(start_point, end_point), thumbnail)
    buffer = BytesIO()
    image.save(buffer, format='png')
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'image/png'

    if not for_time:
        response.headers['Cache-Control'] = 'max-age={}'.format(60)

    if get_flask_arg('file') is not None:
        file_name = '{} {}'.format(start_point, end_point)
        if for_time:
            file_name += ' {}'.format(for_time.strftime('%Y-%m-%d %H:%M'))
        response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)

    return response


@app.route('/gif')
def get_gif():
    start = None    # Time ranges are not supported at the moment.
    end = None      # Time ranges are not supported at the moment.
    start_point = get_coordinates('start-point') or (0, 0)
    end_point = get_coordinates('end-point') or tuple(x - 1 for x in defines.DIMENSIONS)
    thumbnail = get_flask_float('thumbnail')
    detailing = get_flask_detailing('detailing')

    buffer = BytesIO()
    gif_builder = GifBuilder(start, end, start_point, points_to_size(start_point, end_point), thumbnail, detailing)
    gif_builder.build(buffer)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'image/gif'
    if not end:
        response.headers['Cache-Control'] = 'max-age={}'.format(gif_builder.minutes_step * 60 )

    if get_flask_arg('file') is not None:
        start_as_text = start and start.strftime('%Y-%m-%d %H:%M') or 'start'
        end_as_text = end and end.strftime('%Y-%m-%d %H:%M') or 'end'

        file_name = '{} - {} {} - {}.gif'.format(
            start_as_text, end_as_text, start_point, end_point
        )
        response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)

    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0')
