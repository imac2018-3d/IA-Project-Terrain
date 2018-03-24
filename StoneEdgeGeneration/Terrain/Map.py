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
			vertcount : int (300 - 800),
			coef_map_one : float (0-1),
			coef_map_two : float (0-1),
			height_smooth : bool,
			height_octaves : int (1-50),
			height_lacunarity : float (0.5-3),
			height_freq : float (0-20),
			height_size : float (-0.5-6),
			height_mean : float (-0.5-10),
			height_scale : float (-0.5-10),
			randomtype : int (0-10),
			seed : int (0-100),
			temperature : int (-5-35)
			voro_points_count : int (100-300),
			voro_regular : int (0-5),
			voro_land_threshold : float (-0.5-0.5),
			voro_sea_relative_threshold : float (-0.25-0.25),
			voro_radial_bias : float (0-2),
			voro_height_freq : float(0-20),
			voro_height_octaves : int (1-50),
			voro_height_persistance : float (0.5-3),
			voro_height_step : float (0.25-3),
			voro_moisture_start : float(3-13),
			voro_moisture_step : float (0.25-3),
			voro_moisture_freq : float(0-20),
			voro_moisture_octaves : int (1-50),
			voro_moisture_persistance : float(0.5-3)
		   ]
		   """
		return {
			'vertcount' : 100 + int(random.random()*500),
			'coef_map_one' : random.random(),
			'coef_map_two' : random.random(),
			'height_smooth' : int(random.random()*2) % 2 == 0,
			'height_octaves' : 1 + int(random.random() * 49),
			'height_lacunarity' : 0.5+random.random() * 2.5,
			'height_freq' : random.random() * 20,
			'height_size' : -0.5 + random.random() * 6.5,
			'height_mean' : -0.5 + random.random() * 9.5,
			'height_scale' : -0.5 + random.random() * 9.5,
			'randomtype' : int(random.random()*10),
			'seed' : int(random.random()*100),
			'temperature' : int(-5 + random.random()*40),
			'voro_points_count': 100+int(random.random()*200),
			'voro_regular': int(random.random()*6),
			'voro_land_threshold': random.random()-0.5,
			'voro_sea_relative_threshold': random.random()*0.5-0.25,
			'voro_radial_bias': random.random() * 2,
			'voro_height_freq': random.random() * 20,
			'voro_height_octaves': 1 + int(random.random() * 49),
			'voro_height_persistance': 0.5+random.random() * 2.5,
			'voro_height_step': 0.25 + random.random() * 2.75,
			'voro_moisture_start': random.random() * 15,
			'voro_moisture_step': 0.25 + random.random() * 2.75,
			'voro_moisture_freq': random.random() * 20,
			'voro_moisture_octaves': 1 + int(random.random() * 49),
			'voro_moisture_persistance': 0.5+random.random() * 2.5
		}

	# Phenotype generation -------------------------------------------------------------------------------------------------

	def genotype_as_string(self):
		buf = io.StringIO()
		buf.write("- Begin genotype -\n")
		buf.write("{\n\tvertcount:" + str(self.genotype['vertcount']))
		buf.write("\n\tcoef map one:" + str(self.genotype['coef_map_one']))
		buf.write("\n\tcoef map two:" + str(self.genotype['coef_map_two']))
		buf.write("\n\tsmooth:" + str(self.genotype['smooth']))
		buf.write("\n\toctaves:" + str(self.genotype['octaves']))
		buf.write("\n\tlacunarity:" + str(self.genotype['lacunarity']))
		buf.write("\n\tfreq:" + str(self.genotype['freq']))
		buf.write("\n\tsize:" + str(self.genotype['size']))
		buf.write("\n\tmean:" + str(self.genotype['mean']))
		buf.write("\n\tscale:" + str(self.genotype['scale']))
		buf.write("\n\trandomtype:" + str(getrandomname(self.genotype['randomtype'])))
		buf.write("\n\tseed:" + str(self.genotype['seed']))
		buf.write("\n\tvoro land threshold:" + str(self.genotype['voro_land_threshold']))
		buf.write("\n\tvoro moisture start:" + str(self.genotype['voro_moisture_start']))
		buf.write("\n\ttemperature:" + str(self.genotype['temperature']))
		buf.write("\n}\n")
		buf.write("- End genotype -")

		ret = buf.getvalue()
		buf.close()
		return ret

	def process_individual_data(self):
		voromap = VoronoiMap(512,512, pointscount=self.genotype['voro_points_count'], regular=self.genotype['voro_regular'],
							 landthreshold=self.genotype['voro_land_threshold'], radialbias=self.genotype['voro_radial_bias'],
							 heightfreq=self.genotype['voro_height_freq'], heightoctaves=self.genotype['voro_height_octaves'],
							 heightpersistance=self.genotype['voro_height_persistance'], heightstep=self.genotype['voro_height_step'],
							 moisturestart=self.genotype['voro_moisture_start'], moisturestep=self.genotype['voro_moisture_step'],
							 moisturefreq=self.genotype['voro_moisture_freq'], moistureoctaves=self.genotype['voro_moisture_octaves'],
							 moisturepersistance=self.genotype['voro_moisture_persistance'], seed=self.genotype['seed'],
							 temperature=self.genotype['temperature'])

		image = voromap.toimage()
		with NamedTemporaryFile(suffix=".jpg") as tmp:
			colorname = tmp.name
			tmp.close()
		colorname = colorname.replace('\\','/')
		image.save(colorname, "JPEG", quality=90)

		image = voromap.toheightmap()
		with NamedTemporaryFile(suffix=".jpg") as tmp:
			heightname = tmp.name
			tmp.close()
			heightname = heightname.replace('\\','/')
		image.save(heightname, "JPEG", quality=90)

		return json.dumps({"genotype": self.genotype, "voronoifile": colorname, "voronoiheightfile": heightname})

	@staticmethod
	def camera_position():
		return (-15, -15, 12)

	@staticmethod
	def net_compute_individual(location, data):
		return \
			"from StoneEdgeGeneration.Terrain.Map import MapGenetic\n" \
			"from StoneEdgeGeneration.Terrain import Map\n" \
			"reload(Map)\n" \
			"MapGenetic.compute_individual((" + str(location[0]) + "," + str(location[1]) + "," + str(
				location[0]) + "),'" + data + "')"

	@staticmethod
	def compute_individual(location, data):
		import bpy
		import time
		from scipy import misc
		from StoneEdgeGeneration.Terrain.HeightMap import heightmap3
		from StoneEdgeGeneration import bpyutils

		start = time.time()
		values = json.loads(data)
		genotype = values['genotype']
		voronoifile = values['voronoifile']
		voronoiheight = misc.imread(values['voronoiheightfile']) / 100.0 - 0.2
		end = time.time()

		print("loading: ", end - start, "s")

		bpy.context.scene.cursor_location = [0, 0, 0]

		bpy.ops.mesh.primitive_plane_add(radius=10)
		bpy.context.object.name = 'Terrain' + '%03d' % + GenericGenetic.bobject_unique_id()
		print("\ncompute " + bpy.context.object.name + " " + str(genotype['vertcount']) + " vertices")

		obj = bpy.context.object
		mesh = obj.data

		start = time.time()
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		obj.select = True
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.dissolve_limited(angle_limit=0.8)
		count = int(0.5 * (genotype['vertcount']+(len(mesh.vertices) - 1)) / len(mesh.vertices))
		if count >= 0:
			bpy.ops.mesh.subdivide(number_cuts=count)
		bpy.ops.mesh.normals_make_consistent()
		bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
		bpy.ops.object.mode_set(mode='OBJECT')
		end = time.time()

		print("make object : ", end - start, "s")

		start = time.time()
		originalVertices = np.empty((3, len(mesh.vertices), 3))
		for p in mesh.loops:
			if (originalVertices[0, p.vertex_index] == mesh.vertices[p.vertex_index].co).all():
				continue
			originalVertices[0, p.vertex_index] = mesh.vertices[p.vertex_index].co
			originalVertices[1, p.vertex_index] = mesh.vertices[p.vertex_index].normal
			u = mesh.uv_layers.active.data[p.index].uv[0]
			v = mesh.uv_layers.active.data[p.index].uv[1]
			originalVertices[2, p.vertex_index, :2] = (np.array((u,1-v)) * voronoiheight.shape)
			originalVertices[2, p.vertex_index, 2] = voronoiheight[int(originalVertices[2, p.vertex_index, 1]),
																   int(originalVertices[2, p.vertex_index, 0])]
		end = time.time()

		print("get data : ", end - start, "s")

		start = time.time()
		map = heightmap3(100, 100, 5, originalVertices[0, :, 0], originalVertices[0, :, 1],
						 originalVertices[0, :, 2],
						 coefMap1=genotype['coef_map_one'], coefMap2=genotype['coef_map_two'],
						 smooth=genotype['height_smooth'], octaves=genotype['height_octaves'],
						 lacunarity=genotype['height_lacunarity'], freq=genotype['height_freq'],
						 freq2=genotype['height_freq'], mean=genotype['height_mean'], scale=genotype['height_scale'],
						 randomtype=genotype['randomtype'], seed=genotype['seed'])
		for i in range(0, len(mesh.vertices)):
			vertice = mesh.vertices[i]
			vertice.co = originalVertices[0, i] +\
						 originalVertices[1, i] * (genotype['height_size'] * (0.3+0.5*map[i]) * originalVertices[2, i, 2])
		end = time.time()

		print("make height map : ", end - start, "s")

		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=1)
		if genotype['height_smooth']:
			bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=2)
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
		chance1 = 80
		chance2 = 80
		rand = random.random() * 100
		if rand > chance1:
			self.genotype['vertcount'] = max(50, min(900, self.genotype['vertcount'] + -50 + random.random() * 100))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_points_count'] = max(100, min(400, self.genotype['voro_points_count'] + -20 + random.random() * 40))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['coef_map_one'] = max(0.1, min(1., self.genotype['coef_map_one'] + -0.2 + random.random() * 0.4))
			self.genotype['coef_map_two'] = max(0.1, min(1., self.genotype['coef_map_two'] + -0.2 + random.random() * 0.4))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_regular'] = max(0, min(6, int(self.genotype['voro_regular'] + -1 + random.random() * 2)))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_smooth'] = not self.genotype['height_smooth']
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_land_threshold'] = max(-0.5, min(0.5, self.genotype['voro_land_threshold'] + -0.1 + random.random() * 0.2))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_octaves'] = max(1, min(50, int(self.genotype['height_octaves'] + -5 + random.random()*10)))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_sea_relative_threshold'] = max(-0.25, min(0.25, self.genotype['voro_sea_relative_threshold']
																		  + -0.05 + random.random() * 0.1))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_lacunarity'] = max(0.5, min(3, self.genotype['height_lacunarity'] + -0.25 + random.random()*0.5))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_radial_bias'] = max(0, min(2, self.genotype['voro_radial_bias'] + -0.25 + random.random() * 0.5))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_freq'] = max(0.1, min(20, self.genotype['height_freq'] + -2 + random.random()*4))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_height_freq'] = max(0.1, min(20, self.genotype['voro_height_freq'] + -2 + random.random()*4))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_size'] = max(-1, min(7, self.genotype['height_size'] + -0.5 + random.random()*1))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_height_octaves'] =  max(1, min(50, int(self.genotype['voro_height_octaves'] + -5 + random.random()*10)))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance2:
			self.genotype['temperature'] = max(-10, min(40, self.genotype['temperature'] + -2 + random.random()*4))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_mean'] = max(-0.5, min(10, self.genotype['height_mean'] + -0.5 + random.random()*1))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_height_persistance'] = max(0.5, min(3, self.genotype['voro_height_persistance'] + -0.25 + random.random()*0.5))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['height_scale'] = max(-10, min(10, self.genotype['height_scale'] + -1 + random.random()*2))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5
		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_height_step'] = max(0.25, min(3, self.genotype['voro_height_step'] + -0.25 + random.random()*0.5))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_moisture_start'] = max(-1, min(13, self.genotype['voro_moisture_start'] + -1 + random.random()*2))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_moisture_step'] = max(0.25, min(3, self.genotype['voro_moisture_step'] + -0.25 + random.random()*0.5))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance2:
			self.genotype['voro_moisture_freq'] = max(0.1, min(20, self.genotype['voro_moisture_freq'] + -2 + random.random()*4))
			chance2 = chance2 + 10
		else:
			chance2 = chance2 - 5

		rand = random.random() * 100
		if rand > chance1:
			self.genotype['seed'] = max(0, min(100, int(self.genotype['seed'] + -2 + random.random()*4)))
			chance1 = chance1 + 10
		else:
			chance1 = chance1 - 5

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
		coefMapOne = geno1['coef_map_one'] * 0.5 + geno2['coef_map_one'] * 0.5
		coefMapTwo = geno1['coef_map_two'] * 0.5 + geno2['coef_map_two'] * 0.5
		octaves = int(geno1['height_octaves'] * 0.5 + geno2['height_octaves'] * 0.5)
		lacunarity = int(geno1['height_lacunarity'] * 0.5 + geno2['height_lacunarity'] * 0.5)
		freq = geno1['height_freq'] * 0.5 + geno2['height_freq'] * 0.5
		size = geno1['height_size'] * 0.5 + geno2['height_size'] * 0.5
		mean = geno1['height_mean'] * 0.5 + geno2['height_mean'] * 0.5
		scale = geno1['height_scale'] * 0.5 + geno2['height_scale'] * 0.5
		voro_points_count = int(geno1['voro_points_count'] * 0.5 + geno2['voro_points_count'] * 0.5)
		voro_regular = int(geno1['voro_regular'] * 0.5 + geno2['voro_regular'] * 0.5)
		voro_land_threshold = geno1['voro_land_threshold'] * 0.5 + geno2['voro_land_threshold'] * 0.5
		voro_sea_relative_threshold = geno1['voro_sea_relative_threshold'] * 0.5 + geno2['voro_sea_relative_threshold'] * 0.5
		voro_radial_bias = geno1['voro_radial_bias'] * 0.5 + geno2['voro_radial_bias'] * 0.5
		voro_height_freq = geno1['voro_height_freq'] * 0.5 + geno2['voro_height_freq'] * 0.5
		voro_height_octaves = int(geno1['voro_height_octaves'] * 0.5 + geno2['voro_height_octaves'] * 0.5)
		voro_height_persistance = geno1['voro_height_persistance'] * 0.5 + geno2['voro_height_persistance'] * 0.5
		voro_height_step = geno1['voro_height_step'] * 0.5 + geno2['voro_height_step'] * 0.5
		voro_moisture_start = geno1['voro_moisture_start'] * 0.5 + geno2['voro_moisture_start'] * 0.5
		voro_moisture_step = geno1['voro_moisture_step'] * 0.5 + geno2['voro_moisture_step'] * 0.5
		voro_moisture_freq = geno1['voro_moisture_freq'] * 0.5 + geno2['voro_moisture_freq'] * 0.5
		voro_moisture_octaves = int(geno1['voro_moisture_octaves'] * 0.5 + geno2['voro_moisture_octaves'] * 0.5)
		voro_moisture_persistance = geno1['voro_moisture_persistance'] * 0.5 + geno2['voro_moisture_persistance'] * 0.5
		temperature = geno1['temperature'] * 0.5 + geno2['temperature'] * 0.5


		child.append({
			'vertcount': vertcount,
			'coef_map_one': coefMapOne,
			'coef_map_two': coefMapTwo,
			'height_smooth': geno1['smooth'] if random.randint() % 2 == 0 else geno2['smooth'],
			'height_octaves': octaves,
			'height_lacunarity': lacunarity,
			'height_freq': freq,
			'height_size': size,
			'height_mean': mean,
			'height_scale': scale,
			'randomtype': geno1['randomtype'] if random.randint() % 2 == 0 else geno2['randomtype'],
			'seed': geno1['seed'] if random.randint() % 2 == 0 else geno2['seed'],
			'temperature' : temperature,
			'voro_points_count': voro_points_count,
			'voro_regular': voro_regular,
			'voro_land_threshold': voro_land_threshold,
			'voro_sea_relative_threshold': voro_sea_relative_threshold,
			'voro_radial_bias': voro_radial_bias,
			'voro_height_freq': voro_height_freq,
			'voro_height_octaves': voro_height_octaves,
			'voro_height_persistance': voro_height_persistance,
			'voro_height_step': voro_height_step,
			'voro_moisture_start': voro_moisture_start,
			'voro_moisture_step': voro_moisture_step,
			'voro_moisture_freq': voro_moisture_freq,
			'voro_moisture_octaves': voro_moisture_octaves,
			'voro_moisture_persistance': voro_moisture_persistance
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