import bpy, random, math, os

def getBasePath():
	return os.path.dirname(bpy.data.filepath)


def saveImage(name, camerapos=(-5,-5,5)):
	from StoneEdgeGeneration.utils import getImagePath
	bpy.ops.object.lamp_add(type='POINT', location=(camerapos[0]-1,camerapos[1]-1,camerapos[2]+5))
	light = bpy.context.object
	light.data.energy = 2.5
	light.data.distance = 40
	bpy.ops.object.camera_add(view_align=True, location=camerapos, rotation=(math.pi/3,0,-math.pi/4))
	bpy.context.scene.camera = bpy.context.object
	if name[-4:] == ".png":
		name = name[:-4]
	bpy.context.scene.render.filepath = getImagePath(name)
	bpy.ops.render.render(write_still=True)
	bpy.ops.object.delete()
	bpy.context.scene.objects.active = light
	bpy.ops.object.delete()

def saveModel(name):
	from StoneEdgeGeneration.utils import getModelPath
	bpy.ops.export_scene.obj(filepath=getModelPath(name))

def bpydeselect():
	bpy.ops.object.select_all(action='DESELECT')


def bpyselectall():
	bpy.ops.object.select_all(action='SELECT')


def bpyeditdeselect():
	bpy.ops.node.select_all(action='DESELECT')


def bpyeditselectall():
	bpy.ops.node.select_all(action='SELECT')


def bpydeleteall():
	bpyselectall()
	bpy.ops.object.delete(use_global=False)


def ensure_delete_all():
	"""The bpydeleteall helper doesn't work if scene is already empty. Use this instead."""
	bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,  # l'ajout d'objet sert uniquement à ce que le reste ne
										  size=1,  # plante pas si la scène est vide au départ.
										  view_align=False,
										  location=(0, 0, 0),
										  enter_editmode=False)
	bpy.ops.object.mode_set(mode='OBJECT')
	bpydeleteall()


def random_inside_unit_sphere(r = None):
	phi = random.uniform(0, 2 * math.pi)
	costheta = random.uniform(-1, 1)
	theta = math.acos(costheta)
	if r is None:
		u = random.uniform(0, 1) if r is None else r
		r = u**(1./3.)

	x = r * math.sin(theta) * math.cos(phi)
	y = r * math.sin(theta) * math.sin(phi)
	z = r * math.cos(theta)

	return [x, y, z]


def spherical_to_xyz(phi, theta, r):
	x = r * math.sin(theta) * math.cos(phi)
	y = r * math.sin(theta) * math.sin(phi)
	z = r * math.cos(theta)

	return [x, y, z]