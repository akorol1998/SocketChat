from __future__ import annotations
import os
import sys
import asyncio
import quamash
from quamash import QEventLoop
from typing import Set, List
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QFormLayout, QSizePolicy
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK, ConnectionClosed

from Client.config import (BASE_DIR, UI_FILES_PATH, CONNECTION_WINDOW,
	CHAT_WINDOW, HOST, PORT, USER_ICON, IMG_PATH, DEVICE_PIXEL_RATION,
	CHAT_WINDOW_OBJECT_NAMES, LABEL_MIN_WIDTH, MSG_LABEL_MAX_WIDTH)
from Client.utils.client import BaseClient
from Client.utils.widgets import CustomPlainTextEdit, MessageLabel
from Client.utils.static import static_data


class Login(QMainWindow):
	switch_window = pyqtSignal()

	def __init__(self, app: ClientApplication, loop: QEventLoop):
		super(Login, self).__init__()
		uic.loadUi(os.path.join(UI_FILES_PATH, CONNECTION_WINDOW), self)
		self.app = app
		self.loop = loop
		self.host = asyncio.Future()
		self.nickname = asyncio.Future()
		self.port = asyncio.Future()
		self.setup()
	
	async def notification_message(self, title: str, msg: str, icon: int):
		qmsg = QMessageBox()
		qmsg.setWindowTitle(title)
		qmsg.setText(msg)
		qmsg.setIcon(icon)
		x = qmsg.exec_()

	async def validate(self, nickname: str, host: str, port: int):
		if not nickname:
			await self.notification_message(
				"Empty nickname",
				f"Nickname can not be empty string",
				QMessageBox.Critical)
			return 0
		elif len(nickname) > 10 or len(nickname) < 3:
			await self.notification_message(
				"Invalid length",
				f"Nickname should be at least 3 characters long",
				QMessageBox.Critical)
			return 0
		ws = await self.app._client.establish_connection(host, port)
		if not ws:
			await self.notification_message(
				"Server does not exist",
				f"Failed connecting to {host}:{port}",
				QMessageBox.Critical)
		response = await self.app._client.validate_nickname(ws, nickname, "connection")
		if response and response['nickname'] and response['max_client']:
			self.switch_window.emit()
			try:
				await self.app._client.start_messaging(ws, host=host, port=port, nick=nickname)
			except ConnectionClosed:
				pass
			except RuntimeError:
				pass
		elif not response['nickname']:
			await self.notification_message(
				"Nickname is taken",
				f"Nickname '{nickname}' is already taken, pick another one",
				QMessageBox.Critical)
		elif not response['max_client']:
			await self.notification_message(
				"Maximum clients",
				f"Maximum limit of clients reached.",
				QMessageBox.Critical)

	async def async_setup(self):
		nickname = await self.nickname
		host = await self.host
		port = await self.port

		self.host = asyncio.Future()
		self.nickname = asyncio.Future()
		self.port = asyncio.Future()

		await self.validate(nickname, host, port)

	def setup(self):
		self.abort_btn.clicked.connect(self.close)
		# self.host_field.setText("192.168.0.195")
		# self.nickname_field.setText('nick')
		# self.port_spinbox.setValue(8080)
		self.connect_btn.clicked.connect(lambda: self.window_change_slot())
	
	def window_change_slot(self):
		self.host.set_result(self.host_field.text())
		self.port.set_result(self.port_spinbox.value())
		self.nickname.set_result(self.nickname_field.text())
		self.loop.create_task(self.async_setup())


class ChatWindow(QMainWindow):

	def __init__(self, app: ClientApplication, loop: QEventLoop):
		super(ChatWindow, self).__init__()
		uic.loadUi(os.path.join(UI_FILES_PATH, CHAT_WINDOW), self)
		self.__user_list: set = set()
		self.app = app
		self.loop = loop
		self.msg_field = CustomPlainTextEdit()
		self.text_layout.addWidget(self.msg_field)
		self.setup()
	
	def msg_groupBox_setup(self):
		self.msg_groupBox.setObjectName(CHAT_WINDOW_OBJECT_NAMES["msg_groupbox"])
		self.msg_groupBox.setTitle("")
		self.msg_groupBox.setFlat(True)

	def scroll_to_bottom(self, min: int, max: int):
		self.msg_scrollArea.verticalScrollBar().setValue(
			self.msg_scrollArea.verticalScrollBar().maximum()
		)

	def setup(self):
		self.msg_layout.setAlignment(Qt.AlignTop)
		self.msg_scrollArea.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)
		self.setStyleSheet(static_data.chat_window_stylesheet)
		self.msg_groupBox_setup()
		self.msg_field.pressed_enter.connect(lambda: self.fetch_message(True))
		self.send_btn.clicked.connect(lambda: self.fetch_message(False))
	
	def fetch_message(self, clear_enter: bool=False):
		''' Slot for eclicking and pressing Return key.
		Method fetches plaintext from the Widget and calls
		the send_message to handle message.
		>>> Note: self.msg_field.repaint() is called due to the Qt bug on Mac Machines
		>>> Thew widget has to be repainted.
		'''

		text: str = self.msg_field.toPlainText()
		if clear_enter:
			text = text.strip(' \t\n')
		if text:
			self.msg_field.clear()
			self.msg_field.repaint()
			self.loop.create_task(self.app._client.send_message(message=text))
	
	def setup_member_message_layout(self, layout: QFormLayout):
		layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignTop)
		layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

	def setup_client_message_layout(self, layout: QFormLayout):
		layout.setLabelAlignment(Qt.AlignRight | Qt.AlignTop)
		layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop)

	def mount_client_message(self, msg_layout: QFormLayout,t_label: QLabel, msg_lable: QLabel):
		self.setup_client_message_layout(msg_layout)
		msg_lable.setObjectName(CHAT_WINDOW_OBJECT_NAMES["msg_label_client"])
		msg_lable.setWordWrap(True)
		msg_lable.setMaximumWidth(MSG_LABEL_MAX_WIDTH)
		msg_layout.addRow(msg_lable, t_label)

	def mount_member_message(self, msg_layout: QFormLayout, t_label: QLabel, msg_lable: QLabel):
		self.setup_member_message_layout(msg_layout)
		msg_lable.setObjectName(CHAT_WINDOW_OBJECT_NAMES["msg_label_member"])
		msg_lable.setWordWrap(True)
		msg_lable.setMaximumWidth(MSG_LABEL_MAX_WIDTH)
		msg_layout.addRow(t_label, msg_lable)
	
	def create_msg_form(self):
		msg_form = QFormLayout()
		self.msg_layout.addLayout(msg_form)
		return msg_form

	# TODO Replace Hardcoded values
	def create_message(self, client: dict):
		t_label = QLabel(f"{client['time']}: {client['nick']}")
		t_label.setMinimumWidth(LABEL_MIN_WIDTH)
		nick_label = QLabel(f"{client['nick']}")
		msg_lable = MessageLabel(client['message'])
		msg_form = self.create_msg_form()
		if self.app._client._nick == client['nick']:
			t_label = QLabel(f" :{client['time']}")
			self.mount_client_message(msg_layout=msg_form, t_label=t_label, msg_lable=msg_lable)
		else:
			self.mount_member_message(msg_layout=msg_form, t_label=t_label, msg_lable=msg_lable)

	def add_notification(self, msg: str):
		notification = QLabel(msg)
		notification.setObjectName(CHAT_WINDOW_OBJECT_NAMES["chat_notification"])
		font = QFont("Arial", 12, italic=True)
		notification.setFont(font)
		notification.setAlignment((Qt.AlignHCenter | Qt.AlignVCenter))
		self.msg_layout.addWidget(notification)
	
	def display_user_list(self):
		for user in self.__user_list:
			self.mount_user(user)
	
	def mount_user(self, user: str):
		new_user = QLabel()
		pixmap = QPixmap(os.path.join(IMG_PATH, USER_ICON))
		pixmap.setDevicePixelRatio(DEVICE_PIXEL_RATION['user_icon'])
		new_user.setPixmap(pixmap)
		new_user.setAlignment(Qt.AlignLeft)

		label = QLabel(user)
		label.setAlignment(Qt.AlignCenter)
		self.formLayout.addRow(new_user, label)
	
	def unmount_user(self, user: str):
		index = self.formLayout.count()
		while index >= 0:
			index-=1
			if self.formLayout.itemAt(index).widget().text() == user:
				self.formLayout.itemAt(index-1).widget().setParent(None)
				self.formLayout.itemAt(index-1).widget().setParent(None)
				break

	def new_user(self, user: str):
		msg = f"{user} has joinde the chat"
		self.mount_user(user)
		self.__user_list.add(user)
		self.add_notification(msg)
	
	def left_user(self, user: str):
		msg = f"{user} has left the chat"
		print(self.__user_list)
		self.unmount_user(user)
		print(self.__user_list)
		self.__user_list.remove(user)
		self.add_notification(msg)
		
	async def freeze_chat(self):
		self.msg_field.setEnabled(False)
		msg = QMessageBox()
		msg.setWindowTitle("Connection closed")
		msg.setText(f"Connection with the server was closed.")
		msg.setIcon(QMessageBox.Critical)
		x = msg.exec_()

	@property
	def user_list(self):
		return self.__user_list

	@user_list.setter
	def user_list(self, user_list: Set[str]):
		self.__user_list = user_list


class ClientApplication(QMainWindow):

	def __init__(self):
		super(ClientApplication, self).__init__()
		self._client = None
		self._login = None
		self._chat_window = None

	def setup(self, client: BaseClient, loop: QEventLoop):
		self._client = client
		self._login = Login(self, loop)
		self._chat_window = ChatWindow(self, loop)
		self._login.switch_window.connect(self.change_window)
		self._login.show()

	def change_window(self):
		self._login.close()
		self._chat_window.show()
	
	def handle_user_list(self, user_list: List[str]):
		self._chat_window.user_list = set(user_list)
		self._chat_window.display_user_list()
	
	def print_message(self, client: dict):
		self._chat_window.create_message(client)
	
	def handle_message_log(self, msg_log: List[dict]):
		for client in msg_log:
			self._chat_window.create_message(client)
	
	def handle_new_user(self, user: str):
		self._chat_window.new_user(user)

	def handle_left_user(self, user: str):
		self._chat_window.left_user(user)
	
	async def connection_lost_handler(self):
		await self._chat_window.freeze_chat()



def main():
	app = QApplication(sys.argv)
	loop = quamash.QEventLoop(app)
	asyncio.set_event_loop(loop)
	with loop:
		application = ClientApplication()
		application.setup(loop)
		sys.exit(app.exec())

if "__main__" == __name__:
	main()
