from PyQt4.QtCore import *
from http.client import *
from time import ctime
import socket, ftplib, os

_RED = '<span style=color:"#FE2E2E">'
_GREEN = '<span style=color:"#74DF00">'
_GREY = '<span style=color:"#A4A4A4">'
_SPAN = '</span>'

class HTTPrequest(QThread):
	httpReply = pyqtSignal(object)
	def __init__(self, IP):
		super().__init__()

		self.prefs, found = getPrefs()
		self.httpReply.emit(found)
		self.IP = IP
		self.log = []

	def run(self):

		for i in range(256):
			host = self.IP + ".{0}:80".format(i)
			try:
				code, data = self.getResponse(host)
				if code == 200:
					title = self.getTitle(data)
				else:
					title = "unknown"
				self.httpReply.emit('{3}HTTP:{5} {0} at {4}{1}{5} with {2}.'.format(code, host, title, _GREEN, _GREY, _SPAN))
			except socket.error:
				self.httpReply.emit('{1}HTTP:{3} GET from {2}{0}{3} timed out.'.format(host, _RED, _GREY, _SPAN))


	def getResponse(self, host):
		try:
			conn = HTTPConnection(host, timeout = 0.2)
			conn.request("GET", "/")
			response = conn.getresponse()
			code = response.status
			data = response.read()
			conn.close()
			return code, data
		except HTTPException:
			raise socket.error

	def getTitle(self, data):
		try:
			data = data.decode()
			start = data.index("<title>") + 7
			end = data.index("</title>")
			return data[start:end]
		except ValueError:
			return "Title Not Found"


class FTPrequest(QThread):
	ftpReply = pyqtSignal(object)

	def __init__(self, IP):
		super().__init__()
		self.prefs, found = getPrefs()
		self.ftpReply.emit(found)
		self.IP = IP
		self.log = []

	def run(self):
		for i in range(256):
			host = self.IP + ".{0}".format(i)
			try:
				conn = ftplib.FTP(host, timeout = 0.2)
				emitString = "{1}FTP:{3} Alive at {2}{0}{3}.".format(host, _GREEN, _GREY, _SPAN)
				welcomeString = conn.getwelcome()
				conn.close()
			except ftplib.all_errors:
				emitString = "{1}FTP:{3} Dead at {2}{0}{3}.".format(host, _RED, _GREY, _SPAN)
				welcomeString = None

			self.ftpReply.emit(emitString)
			if welcomeString:
				self.ftpReply.emit(welcomeString)
		try:
			if self.prefs["logs"]:
				saveLog("FTP", self.IP, self.log, self.prefs["folder"])
		except ValueError:
			pass



def getPrefs():
	prefs = {}
	if os.path.exists("prefs"):
		with open("html.cfg", mode = "r") as configFile:
			rawConfig = configFile.read().splitlines()
		found = ">Loading prefs."
		for line in rawConfig:
			equalsIndex = line.index("=")
			prefs[line[:equalsIndex]] = line[equalsIndex+1:]
	else:
		prefs = {"data":"data", "logs":"false"}
		found = ">No prefs found, using default config."

	return prefs, found


def saveLog(servType, IP, log, folder):
	fileName = IP+"."+ctime()[11:19]+".log"
	path = folder+"/"+servType+"/"+fileName

	with open(path, mode = "w") as log:
		log.writelines(log)

	return fileName