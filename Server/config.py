import os
from socket import gethostname, gethostbyname

LOCAL_HOST = '0.0.0.0'
HOST = gethostbyname(gethostname())
PORT = 8080
WS_URL = f"ws://{HOST}:{PORT}"
NUM_OF_MESSAGES = 20
NUM_OF_CONNECTTIONS = 4
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = 'logfile'
LOG_FILE_PATH = os.path.join(BASE_DIR, LOG_FILE)
