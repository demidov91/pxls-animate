import os

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, 'data')


# Choose one of DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'pxls.log')

try:
    from local_settings import LOG_LEVEL, LOG_FILE
except ImportError as e:
    pass

LOGGING = { 
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_FILE,
            'when': 'midnight',
            'backupCount': 14,  
        },
    },
    'loggers': { 
        '': { 
            'handlers': ['default'],
            'level': LOG_LEVEL,
        },
    } 
}

try:
    from local_settings import *
except ImportError:
    pass
