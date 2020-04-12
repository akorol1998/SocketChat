import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT = 'client'
INTERFACE = 'interface'
UI = 'ui_files'
STATIC = 'static'
IMG = 'img'
STYLE = 'style'

CHAT_WINDOW = 'main_window.ui'
CONNECTION_WINDOW = 'connection_window.ui'
USER_ICON = 'user-icon.png'
CHATWINDOW_STYLESHEET = 'msg_style.css'

UI_FILES_PATH = os.path.join(BASE_DIR, INTERFACE, UI)
STATIC_FILES_PATH = os.path.join(BASE_DIR, INTERFACE, STATIC)
IMG_PATH = os.path.join(STATIC_FILES_PATH, IMG)
STYLE_PATH = os.path.join(STATIC_FILES_PATH, STYLE)

HOST = "127.0.0.1"
PORT = 8080
DEVICE_PIXEL_RATION = {"user_icon": 8}
CHAT_WINDOW_OBJECT_NAMES = {
	"msg_label_member": 'member',
	"msg_label_client": 'client',
	"msg_groupbox": "msg_goupBox",
	"chat_notification": "notification"
	}
LABEL_MIN_WIDTH = 100
MSG_LABEL_MAX_WIDTH = 250
