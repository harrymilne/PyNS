from PyQt4 import QtGui, QtCore
from serverThread import *
import sys
from random import randint

#good test IP: 96.126.112


class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("PyNS")

		self.initLayout()
		self.initMenuBar()
		self.threads = []
		self.data = []

	def initLayout(self):
		self.dataInputWidget = QtGui.QWidget()
		self.dataInputLayout = QtGui.QGridLayout()

		##Widgets
		self.console = QtGui.QTextEdit()
		self.console.setReadOnly(True)
		self.hostInput = QtGui.QLineEdit()
		self.hostInput.setText(self.randomID())
		self.serverType = QtGui.QComboBox()
		self.launchButton = QtGui.QPushButton("GO")
		self.launchButton.setMaximumWidth(40)
		self.stopButton = QtGui.QPushButton("STOP")
		self.stopButton.setMaximumWidth(40)
		self.stopButton.setDisabled(True)

		self.dataInputLayout.addWidget(self.console,0,0,1,4)
		self.dataInputLayout.addWidget(self.hostInput, 1, 0)
		self.dataInputLayout.addWidget(self.serverType, 1, 1)
		self.dataInputLayout.addWidget(self.launchButton, 1, 2)
		self.dataInputLayout.addWidget(self.stopButton, 1, 3)

		##add server type items
		self.serverType.addItems(["HTTP","FTP"])

		self.dataInputWidget.setLayout(self.dataInputLayout)
		self.setCentralWidget(self.dataInputWidget)

		self.connect(self.launchButton, QtCore.SIGNAL("clicked()"), self.launchThread)
		self.connect(self.stopButton, QtCore.SIGNAL("clicked()"), self.stopThreads)
		self.connect(self.hostInput, QtCore.SIGNAL("returnPressed()"), self.launchThread)

                
	def initMenuBar(self):
		##actions
		clearConsole = QtGui.QAction("Clear Console",self)
		clearConsole.setShortcut("F4")
		clearConsole.triggered.connect(self.console.clear)

		randomIP = QtGui.QAction("Generate RandIP", self)
		randomIP.setShortcut("F5")
		randomIP.triggered.connect()

		exitAction = QtGui.QAction("Quit", self)
		exitAction.setShortcut("Alt+F4")
		exitAction.triggered.connect(QtGui.qApp.quit)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu("File")
		fileMenu.addAction(clearConsole)
		fileMenu.addAction(exitAction)

	def launchThread(self):
		if len(self.threads) < 3:
			if self.checkIP():

				if self.serverType.currentText() == "HTTP":
					requester = HTTPrequest(self.hostInput.text())
					requester.httpReply.connect(self.handleData)
					self.threads.append(requester)
					requester.start()
				elif "FTP":
					requester = FTPrequest(self.hostInput.text())
					requester.ftpReply.connect(self.handleData)
					self.threads.append(requester)
					requester.start()
				self.stopButton.setDisabled(False)
		else:
			self.console.append('<span style=color:"#FE2E2E">3 threads already active</span>')


	def stopThreads(self):
		for thread in self.threads:
			thread.terminate()
		self.threads = []
		self.stopButton.setDisabled(True)


	def checkIP(self):
		numList = self.hostInput.text().split(".")
		if self.hostInput.text().count(".") > 3:
			self.console.append("Invalid IP format, (255.255.255)")
			return False
		if len(numList) < 3:
			self.console.append("Invalid IP format, (255.255.255)")
			return False
		for num in numList:
			try:
				if int(num) > 255 or int(num) < 0:
					self.console.append("Invalid IP format, (255.255.255)")
					return False
			except ValueError:
				self.console.append("Invalid IP format, (255.255.255)")
				return False
		return True

	def randomID(self):
		return ".".join([str(randint(0,255)),str(randint(0,255)),str(randint(0,255))])

	def handleData(self, data):
		self.console.append(data)
		self.data.append(data)

def eventLoop():
	app = QtGui.QApplication(sys.argv)
	mainWindow = MainWindow()
	mainWindow.show()
	sys.exit(app.exec_())

eventLoop()
