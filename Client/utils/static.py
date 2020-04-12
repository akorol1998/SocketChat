import os

from Client.config import STYLE_PATH, CHATWINDOW_STYLESHEET

class StaticData:
	def __init__(self):
		with open(os.path.join(STYLE_PATH, CHATWINDOW_STYLESHEET)) as f:
			self.chat_window_stylesheet = f.read()


static_data = StaticData()
