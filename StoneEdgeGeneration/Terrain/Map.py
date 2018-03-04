import json
from tempfile import NamedTemporaryFile
import io
import numpy as np

import copy

from StoneEdgeGeneration.Asset.genericgenetic import *
from StoneEdgeGeneration.Terrain.HeightMap import getrandomname
from StoneEdgeGeneration.Terrain.Voronoi import VoronoiMap


class MapGenetic(GenericGenetic):
	"""Représente un individu de cristal avec son génotype"""

	def __init__(self, genotype=None, parent=None):
		GenericGenetic.__init__(self, genotype, parent)

	# Genotype generation --------------------------------------------------------------------------------------------------

	def random_genotype(self):
		"""génère un génotype random. Composition du génotype d'un map :
		   [
			vertcount : int (100 - 2000),
			coefMapOne : float (0-1),
			coefMapTwo : float (0-1),
			smooth : bool,
			octaves : int (1-50),
			lacunarity : float (1-4),
			freq : float (0-20),
			size : float (-10-20),
			mean : float (-5-5),
			scale : float (-10-10),
			randomtype : int (0-10),
			seed : int (0-100)
		   ]
		   """
		return {
			'vertcount' : 100 + int(random.random()*1900),
			'coefMapOne' : random.random(),
			'coefMapTwo' : random.random(),
			'smooth' : int(random.random()*2) % 2 == 0,
			'octaves' : 1 + int(random.random() * 49),
			'lacunarity' : 1.0+random.random() * 3,
			'freq' : random.random() * 20,
			'size' : -3 + random.random() * 10,
			'mean' : -3 + random.random() * 10,
			'scale' : -10 + random.random() * 20,
			'randomtype' : int(random.random()*10),
			'seed' : int(random.random()*100)
		}

	# Phenotype generation -------------------------------------------------------------------------------------------------

	def genotype_as_string(self):
		buf = io.StringIO()
		buf.write("- Begin genotype -\n")
		buf.write("{\n\tvertcount:" + str(self.genotype['vertcount']))
		buf.write("\n\tcoefMapOne:" + str(self.genotype['coefMapOne']))
		buf.write("\n\tcoefMapTwo:" + str(self.genotype['coefMapTwo']))
		buf.write("\n\tsmooth:" + str(self.genotype['smooth']))
		buf.write("\n\toctaves:" + str(self.genotype['octaves']))
		buf.write("\n\tlacunarity:" + str(self.genotype['lacunarity']))
		buf.write("\n\tfreq:" + str(self.genotype['freq']))
		buf.write("\n\tsize:" + str(self.genotype['size']))
		buf.write("\n\tmean:" + str(self.genotype['mean']))
		buf.write("\n\tscale:" + str(self.genotype['scale']))
		buf.write("\n\trandomtype:" + str(getrandomname(self.genotype['randomtype'])))
		buf.write("\n\tseed:" + str(self.genotype['seed']))
		buf.write("\n}\n")
		buf.write("- End genotype -")

		ret = buf.getvalue()
		buf.close()
		return ret

	def process_individual_data(self):
		voromap = VoronoiMap(512,512, pointscount=500)
		image = voromap.toimage()
		with NamedTemporaryFile(suffix=".jpg") as tmp:
			name = tmp.name
			tmp.close()
		name = name.replace('\\','/')
		image.save(name, "JPEG")
		return json.dumps({"genotype": self.genotype, "voronoifile": name})

	@staticmethod
	def camera_position():
		return (-15, -15, 12)

	@staticmethod
	def net_compute_individual(location, data):
		return \
			"from StoneEdgeGeneration.Terrain.Map import MapGenetic\n" \
			"MapGenetic.compute_individual((" + str(location[0]) + "," + str(location[1]) + "," + str(
				location[0]) + "),'" + data + "')"

	@staticmethod
	def compute_individual(location, data):
		import bpy
		from StoneEdgeGeneration.Terrain.HeightMap import heightmap3
		from StoneEdgeGeneration import bpyutils

		values = json.loads(data)
		genotype = values['genotype']
		voronoifile = values['voronoifile']

		bpy.context.scene.cursor_location = [0, 0, 0]

		bpy.ops.mesh.primitive_plane_add(radius=10)
		bpy.context.object.name = 'Terrain' + '%03d' % + GenericGenetic.bobject_unique_id()
		print("\ncompute " + bpy.context.object.name)

		obj = bpy.context.object
		mesh = obj.data

		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.dissolve_limited(angle_limit=0.8)
		count = (genotype['vertcount'] / len(mesh.vertices) - 1)
		if count >= 0:
			bpy.ops.mesh.subdivide(number_cuts=count)
		bpy.ops.mesh.normals_make_consistent()
		bpy.ops.object.mode_set(mode='OBJECT')

		originalVertices = np.empty((2, len(mesh.vertices), 3))
		for i in range(len(mesh.vertices)):
			originalVertices[0, i] = mesh.vertices[i].co
			originalVertices[1, i] = mesh.vertices[i].normal
		map = heightmap3(100, 100, 5, originalVertices[0, :, 0], originalVertices[0, :, 1],
						 originalVertices[0, :, 2],
						 coefMap1=genotype['coefMapOne'], coefMap2=genotype['coefMapTwo'],
						 smooth=genotype['smooth'], octaves=genotype['octaves'], lacunarity=genotype['lacunarity'],
						 freq=genotype['freq'], freq2=genotype['freq'], mean=genotype['mean'], scale=genotype['scale'],
						 randomtype=genotype['randomtype'], seed=genotype['seed'])
		for i in range(0, len(mesh.vertices)):
			vertice = mesh.vertices[i]
			vertice.co = originalVertices[0, i] + originalVertices[1, i] * map[i] * genotype['size']

		if genotype['smooth']:
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=1)
			bpy.ops.object.mode_set(mode='OBJECT')

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
		bpy.ops.object.mode_set(mode='OBJECT')
		mat = bpy.data.materials.new("map_mat")
		mat.ambient = 0.4
		mesh.materials.append(mat)
		tex = bpy.data.textures.new("tex", 'IMAGE')
		slot = mat.texture_slots.add()
		slot.texture = tex

		try:
			img = bpy.data.images.load(voronoifile)
		except:
			print("Cannot load image %s" % voronoifile)
			return
		tex.image = img

		bpyutils.bpydeselect()

# Genotype mutation ----------------------------------------------------------------------------------------------------

	def mutate_genotype(self):
		"""
		Création d'une mutation : va au hasard modifier un ou plusieurs attributs d'une map
		"""
		chance = 80
		rand = random.random() * 100
		if rand > chance:
			self.genotype['vertcount'] = max(100, min(2000, self.genotype['vertcount'] + -100 + random.random() * 200))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['coefMapOne'] = max(0.1, min(1., self.genotype['coefMapOne'] + -0.5 + random.random()))
			self.genotype['coefMapTwo'] = max(0.1, min(1., self.genotype['coefMapTwo'] + -0.5 + random.random()))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['smooth'] = not self.genotype['smooth']
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['octaves'] = max(1, min(100, int(self.genotype['octaves'] + -5 + random.random()*10)))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['lacunarity'] = max(1, min(100, self.genotype['lacunarity'] + -0.5 + random.random()*1))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['freq'] = max(0.1, min(20, self.genotype['freq'] + -2 + random.random()*4))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['size'] = max(-3, min(10, self.genotype['size'] + -2 + random.random()*4))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['mean'] = max(-5, min(5, self.genotype['mean'] + -1 + random.random()*2))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['scale'] = max(-10, min(10, self.genotype['scale'] + -1 + random.random()*2))
			chance = chance + 10
		else:
			chance = chance - 5

		rand = random.random() * 100
		if rand > chance:
			self.genotype['seed'] = max(0, min(100, int(self.genotype['seed'] + -2 + random.random()*4)))

	# Genotype cross generation --------------------------------------------------------------------------------------------

	@staticmethod
	def cross_genotypes(geno1, geno2):
		"calcule trois enfants différents : moyenne, moitié 1 et moitié 2"
		return [
			MapGenetic.cross_genotype_mean(geno1, geno2),
			MapGenetic.cross_genotype_firsthalf(geno1, geno2),
			MapGenetic.cross_genotype_lasthalf(geno1, geno2)
		]

	@staticmethod
	def cross_genotype_mean(geno1, geno2):
		"""Calcule le génotype moyen des deux parents"""
		child = []
		vertcount = geno1['vertcount'] * 0.5 + geno2['vertcount'] * 0.5
		coefMapOne = geno1['coefMapOne'] * 0.5 + geno2['coefMapOne'] * 0.5
		coefMapTwo = geno1['coefMapTwo'] * 0.5 + geno2['coefMapTwo'] * 0.5
		octaves = int(geno1['octaves'] * 0.5 + geno2['octaves'] * 0.5)
		lacunarity = int(geno1['lacunarity'] * 0.5 + geno2['lacunarity'] * 0.5)
		freq = geno1['freq'] * 0.5 + geno2['freq'] * 0.5
		size = geno1['size'] * 0.5 + geno2['size'] * 0.5
		mean = geno1['mean'] * 0.5 + geno2['mean'] * 0.5
		scale = geno1['scale'] * 0.5 + geno2['scale'] * 0.5

		child.append({
			'vertcount': vertcount,
			'coefMapOne': coefMapOne,
			'coefMapTwo': coefMapTwo,
			'smooth': geno1['smooth'] if random.randint() % 2 == 0 else geno2['smooth'],
			'octaves': octaves,
			'lacunarity': lacunarity,
			'freq': freq,
			'size': size,
			'mean': mean,
			'scale': scale,
			'randomtype': geno1['randomtype'] if random.randint() % 2 == 0 else geno2['randomtype'],
			'seed': geno1['seed'] if random.randint() % 2 == 0 else geno2['seed']
		})
		return MapGenetic(child)

	@staticmethod
	def cross_genotype_firsthalf(geno1, geno2):
		"""Créée un enfant composé de la moitié des subcristaux de chaque parent"""
		child = []
		for sc in geno1[:1 + (len(geno1)-1)//2]:
			child.append(copy.deepcopy(sc))
		for sc in geno2[len(geno2)//2:]:
			child.append(copy.deepcopy(sc))
		return MapGenetic(child)

	@staticmethod
	def cross_genotype_lasthalf(geno1, geno2):
		"""Créée un enfant composé de la moitié des subcristaux de chaque parent (inversé par rapport à firsthalf)"""
		child = []
		for sc in geno2[:1 + (len(geno2) - 1) // 2]:
			child.append(copy.deepcopy(sc))
		for sc in geno1[len(geno1) // 2:]:
			child.append(copy.deepcopy(sc))
		return MapGenetic(child)


	# Fitness computation --------------------------------------------------------------------------------------------------

	def compute_fitness(self):
		"""Le fitness ne retourne rien. Il est établi arbitrairement par l'utilisateur."""
		return None

	# Destructor -----------------------------------------------------------------------------------------------------------

	def __del__(self):
		"""Quand le génotype est suprimmé, on vire aussi son phénotype s'il existe."""
		if self.generated is not None:
			import bpy
			from StoneEdgeGeneration import bpyutils
			bpyutils.bpydeselect()
			for child in bpy.data.objects[self.generated].children:
				child.select = True
			bpy.ops.object.delete()
			bpy.data.objects[self.generated].select = True
			bpy.ops.object.delete()