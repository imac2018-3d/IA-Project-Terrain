import os, sys
from importlib import reload

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QTimer

from StoneEdgeGeneration.UI.BaseWindow import BaseWindow

import StoneEdgeGeneration.Communication.Communication
from StoneEdgeGeneration.Communication.Communication import *

import logging
from logging.handlers import RotatingFileHandler

class Client:
	def __init__(self):
		self.app = QtWidgets.QApplication(sys.argv)
		self.app.setApplicationName("Stone Edge Generation")
		self.app.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.realpath('./StoneEdgeGeneration/Resources/Icons/StoneEdge.png'))))
		QtGui.QFontDatabase.addApplicationFont(os.path.abspath(os.path.realpath('./StoneEdgeGeneration/Resources/Fonts/open-sans.ttf')))
		QtGui.QFontDatabase.addApplicationFont(os.path.abspath(os.path.realpath('./StoneEdgeGeneration/Resources/Fonts/cinzel.otf')))
		stylesheet = open(os.path.abspath(os.path.realpath('./StoneEdgeGeneration/Resources/Stylesheets/app.qss'))).read()
		self.app.setStyleSheet(stylesheet)
		self.app.setQuitOnLastWindowClosed(True)
		self.timer = QTimer()

		self.logger = logging.getLogger()
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

		file_handler = RotatingFileHandler('client.log', 'a', 1000000, 1)

		file_handler.setLevel(logging.DEBUG)
		file_handler.setFormatter(formatter)
		self.logger.addHandler(file_handler)

		# def launchasset():
		#     self.launch(loadAsset())
		#
		# def launchterrain():
		#     self.launch(loadTerrain())
		# self.window = MainMenu(actions=[
		#     Action("Assets", launchasset),
		#     Action("Terrains", launchterrain)
		# ])

		self.window = BaseWindow()

	def launch(self, window):
		old = self.window
		self.window = window
		window.show()
		old.close()


	def listen(self):
		try:
			res = Communication.receive(0.05, {"client": self})
		except EOFError as e:
			self.close()
		except Exception as e:
			self.logger.exception("Exception occurred: \n")

	def execute(self):
		self.logger.info("Start client")
		self.logger.info("Channel:" + str(channel))
		Communication.setchannel(channel)
		Communication.setlogger(self.logger)
		self.timer.timeout.connect(self.listen)
		self.timer.start(200)
		self.window.show()
		try:
			self.app.exec()
		except Exception as e:
			self.logger.exception("Exception occurred: \n")
		self.logger.info("End client")

	def close(self):
		self.app.closeAllWindows()

	def __del__(self):
		pass

def main():
	client = Client()
	client.execute()


if __name__ == '__channelexec__':
	reload(StoneEdgeGeneration.Communication)
	main()

elif __name__ == '__main__':
	main()
