from importlib import reload
from queue import Queue, Empty
import sys, os, bpy, time
import pprint
import blf

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
	sys.path.append(blend_dir)

from StoneEdgeGeneration import main
from StoneEdgeGeneration import process_client
import StoneEdgeGeneration.Communication
from StoneEdgeGeneration.Communication import Communication
import StoneEdgeGeneration.bpyutils as bpyutils
import StoneEdgeGeneration.utils as utils

import execnet
import execnet.multi
from execnet.gateway_base import RemoteError

class Server(bpy.types.Operator):
	"""Operator which runs its self from a timer"""
	bl_idname = "wm.stone_edge_generation_server"
	bl_label = "Stone Edge Generation"

	def __init__(self):
		bpy.types.Operator.__init__(self)
		self.spec = "popen//cmodel=eventle//python=python"
		self.gateway = execnet.makegateway(self.spec)
		self.channels = None
		self.queue = None
		self.timer = None
		self.tasks = Queue()
		self.terminated = 0
		self.individus = []

	def RemoteErrorHandler(self, error):
		e, t = error.formatted.splitlines()[-1].split(':')
		raise getattr(__name__, e)(t)

	def update(self):
		try:
			chan, res = self.queue.get(timeout=0.01)
			if res == -1:
				self.terminated += 1
				if self.terminated >= len(self.channels):
					return {'CANCELLED'}
			else:
				res = Communication.handlemessage(res, {'client': chan, 'server': self, 'basepath': bpyutils.getBasePath(),
														'currentdir': os.getcwd()})
		except Empty:
			pass
		except RemoteError as ex:
			self.RemoteErrorHandler(ex)

		while not self.tasks.empty():
			self.channels.send_each(self.tasks.get_nowait())

		return {'RUNNING_MODAL'}

	def send_each(self,message):
		self.channels.send_each(message)

	def exit(self, context):
		if self.terminated < len(self.channels):
			self.channels.send_each(Communication.command("client.close()"))
		self.cancel(context)
		self.gateway.exit()

	def modal(self, context, event):
		#print(event.type)
		if event.type in {'ESC'}:
			self.exit(context)
			self.cancel(context)
			self.gateway.exit()
			return {'CANCELLED'}

		if event.type in {'RET'}:
			pprint.pprint(event)
			self.exit(context)
			return {'RUNNING_MODAL'}

		if event.type in {'LEFTMOUSE'}:
			pass

		if event.type == 'TIMER':
			return self.update()

		return {'PASS_THROUGH'}

	def execute(self, context):
		wm = context.window_manager
		self.timer = wm.event_timer_add(0.05, context.window)
		wm.modal_handler_add(self)
		ch = self.gateway.remote_exec(process_client)
		self.channels = execnet.multi.MultiChannel([ch])
		self.queue = self.channels.make_receive_queue(endmarker=-1)
		return {'RUNNING_MODAL'}

	def cancel(self, context):
		wm = context.window_manager
		wm.event_timer_remove(self.timer)


def register():
	bpy.utils.register_class(Server)


def unregister():
	bpy.utils.unregister_class(Server)


if __name__ == "__main__":
	reload(main)
	reload(process_client)
	reload(utils)
	reload(bpyutils)
	reload(StoneEdgeGeneration.Communication)

	register()

	bpy.ops.wm.stone_edge_generation_server()
