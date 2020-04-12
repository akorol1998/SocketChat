from PyQt5.QtWidgets import QPlainTextEdit, QLabel, QSizePolicy
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt

# Redundant
class CustomPlainTextEdit(QPlainTextEdit):
	pressed_enter = pyqtSignal()

	def __init__(self):
		super().__init__()
	
	def keyPressEvent(self, keyEvent):
		super(CustomPlainTextEdit, self).keyPressEvent(keyEvent)
		if keyEvent.key() == Qt.Key_Return:
			self.pressed_enter.emit()
		elif keyEvent.key() == Qt.Key_Enter:
			pass


class MessageLabel(QLabel):
	def __init__(self, string: str):
		super(MessageLabel, self).__init__(string)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
	
	def resizeEvent(self, event: QResizeEvent):
		super().resizeEvent(event)
		if self.wordWrap() and self.sizePolicy().verticalPolicy() == QSizePolicy.Minimum:
			self.setMinimumHeight(self.sizeHint().height())
