import asyncio
import websockets
import quamash
import sys
from PyQt5.QtWidgets import QApplication

from Client.bl.client import Client
from Client.interface.interface import ClientApplication

def main():
	'''
	Quamash is an Implementation of the PEP 3156 Event-Loop with Qt
	it is needed in order to run one event loop and plug all the
	asynchronous python function into it. This allows to run sockets, tasks
	and PyQt5 listening events inside signle event loop.
	'''
	app = QApplication(sys.argv)
	loop = quamash.QEventLoop(app)
	asyncio.set_event_loop(loop)
	with loop:
		application = ClientApplication()
		client = Client(application, loop)
		sys.exit(app.exec())


if __name__ == '__main__':
    main()
