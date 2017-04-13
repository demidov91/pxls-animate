
# Choose one of DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = 'INFO'


try:
    from local_settings import *
except ImportError:
    pass
