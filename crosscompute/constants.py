import re
from os.path import dirname, join

from .macros.web import format_slug


PACKAGE_FOLDER = dirname(__file__)
TEMPLATES_FOLDER = join(PACKAGE_FOLDER, 'templates')
ID_LENGTH = 16


AUTOMATION_NAME = 'Automation X'
AUTOMATION_VERSION = '0.0.0'
AUTOMATION_PATH = 'automate.yml'


HOST = '127.0.0.1'
PORT = 7000
DISK_POLL_IN_MILLISECONDS = 1000
DISK_DEBOUNCE_IN_MILLISECONDS = 1000


AUTOMATION_ROUTE = '/a/{automation_slug}'
BATCH_ROUTE = '/b/{batch_slug}'
FILE_ROUTE = '/{file_path}'
MODE_ROUTE = '/{mode_name}'
RUN_ROUTE = '/r/{run_slug}'
STYLE_ROUTE = '/s/{style_name}'
STREAMS_ROUTE = '/streams'


MODE_NAMES = 'input', 'output', 'log', 'debug'


FUNCTION_BY_NAME = {
    'slug': format_slug,
    'title': str.title,
}
VARIABLE_ID_PATTERN = re.compile(r'{\s*([^}]+?)\s*}')
VARIABLE_CACHE = {}
