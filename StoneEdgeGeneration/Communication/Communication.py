import execnet
from importlib import import_module, reload

class Communication:
	channel = None
	logger = None

	@staticmethod
	def setchannel(chan):
		Communication.channel=chan

	@staticmethod
	def setlogger(log):
		Communication.logger=log

	@staticmethod
	def receive(timeout, globalvalues={}):
		try:
			message=Communication.channel.receive(timeout)
			res=Communication.handlemessage(message, globalvalues)
			return res
		except Communication.channel.TimeoutError as e:
			pass
		except EOFError as e:
			raise e
		return None

	@staticmethod
	def receivedata(timeout):
		try:
			res=Communication.channel.receive(timeout)
			if type(res) is bytes:
				res = execnet.loads(res)
			Communication.log("data: "+str(res))
			return res
		except Communication.channel.TimeoutError as e:
			pass
		return None

	@staticmethod
	def command(cmd):
		return execnet.dumps(("cmd", cmd))

	@staticmethod
	def data(dataitem):
		return execnet.dumps(("value", dataitem))

	@staticmethod
	def senddata(dataitem):
		if Communication.channel is None:
			Communication.log("no channel")
			return
		Communication.channel.send(Communication.data(dataitem))

	@staticmethod
	def sendcommand(cmd):
		if Communication.channel is None:
			Communication.log("no channel")
			return
		Communication.channel.send(Communication.command(cmd))

	@staticmethod
	def handlemessage(message, globalvalues):
		try:
			l, g = locals().copy(), globals().copy()
			for key, value in globalvalues.items():
				g[key] = value
			res = execnet.loads(message)

			if type(res) is not tuple:
				Communication.log("message is not a tuple:" + str(res))
				return None
			if len(res) <= 1:
				return None

			if res[0] == "value":
				Communication.log("value:" + res[1])
				return res[1]
			else:
				Communication.log("cmd:\n" + res[1])
				exec(res[1], g, l)
				return None
		except Exception as e:
			Communication.exception(e)

	@staticmethod
	def log(message):
		if Communication.logger is not None:
			Communication.logger.debug(message)
		else:
			print(message)

	@staticmethod
	def print(message):
		Communication.log(message)

	@staticmethod
	def exception(error):
		if Communication.logger is not None:
			Communication.logger.exception("Exception occurred: \n")
		else:
			raise error