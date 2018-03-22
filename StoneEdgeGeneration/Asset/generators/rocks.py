from StoneEdgeGeneration.Asset.genericgenetic import *
import json

import io
import numpy as np
import copy

class RockGenetic(GenericGenetic):
	"""Représente un individu de cristal avec son génotype"""

	min_subrocks = 1
	max_subrocks = 4

	min_cuts = 0
	max_cuts = 50

	def __init__(self, genotype=None, parent=None):
		GenericGenetic.__init__(self, genotype, parent)

	# Genotype generation --------------------------------------------------------------------------------------------------

	def random_genotype(self):
		"""génère un génotype random. Composition du génotype d'un rocher :
		   [subcrytals (1-4):
				Cuts: [Cuts (0 - 50):
					(phi, theta, r)
				]
				Scale : (x, y, z)
				Orientation : (phi, theta)
				Offset : (w)
		   ]
		   """
		return [self.random_subrock_genotype() for a in range(self.min_subrocks,
																 random.randint(self.min_subrocks,
																				self.max_subrocks) + 1)]

	def random_subrock_genotype(self):
		return {
			'cuts': [self.random_cut_genotype() for b in range(self.min_cuts,
															   random.randint(self.min_cuts,
																			  self.max_cuts) + 1)],
			'scale': self.random_scale_genotype(),
			'orientation': self.random_orientation_genotype(),
			'offset': self.random_offset_genotype()
		}

	def random_cut_genotype(self):
		return [
			random.random() * 2 * math.pi,
			random.random() * 2 * math.pi,
			random.uniform(0.5, 0.9)
		]

	def random_scale_genotype(self):
		return [
			random.uniform(0.5, 1),
			random.uniform(0.5, 1),
			random.uniform(1, 3)
		]

	def random_orientation_genotype(self):
		return [
			random.uniform(0, math.pi * 2),
			random.uniform(0, math.pi / 2),  # ici c'est seulement un quart de cercle
		]

	def random_offset_genotype(self):
		return random.uniform(-2, 0)  # c'est en gros l'enfoncement du rock dans le sol (donc négatif)

	# Phenotype generation -------------------------------------------------------------------------------------------------

	def genotype_as_string(self):
		buf = io.StringIO()
		buf.write("- Begin genotype (" + str(len(self.genotype)) + " subrocks) -\n")
		for idx, subcrystal in enumerate(self.genotype):
			buf.write("#" + str(idx) + ": {\n\tcuts: [\n")
			for cut in subcrystal['cuts']:
				buf.write("\t\t" + str(cut[0]) + " " + str(cut[1]) + " " + str(cut[2]) + "\n")
			buf.write("\t]\n\tscale: "
					  + str(subcrystal['scale'][0]) + " "
					  + str(subcrystal['scale'][1]) + " "
					  + str(subcrystal['scale'][2])
					  + "\n")
			buf.write("\torientation: "
					  + str(subcrystal['orientation'][0]) + " "
					  + str(subcrystal['orientation'][1]) + "\n")
			buf.write("\toffset: " + str(subcrystal['offset']) + "\n")
			buf.write("}\n")
		buf.write("- End genotype -")

		ret = buf.getvalue()
		buf.close()
		return ret

	def process_individual_data(self):
		return json.dumps({"genotype": self.genotype})

	@staticmethod
	def net_compute_individual(location, data):
		return \
			"from StoneEdgeGeneration.Asset.generators.crystals import CrystalGenetic\n" \
			"CrystalGenetic.compute_individual(("+str(location[0])+","+str(location[1])+","+str(location[0])+"),'" \
			+ data + "')"

	@staticmethod
	def compute_individual(location, data):
		import bpy
		import StoneEdgeGeneration.bpyutils as bpyutils
		"""Génère un cristal"""

		values = json.loads(data)
		genotype = values['genotype']

		print('compute individuals')
		bpy.context.scene.cursor_location = [0, 0, 0]

		bpy.ops.object.add(type='EMPTY')
		bpy.context.object.name = 'Crystal' + '%03d' % + GenericGenetic.bobject_unique_id()
		print("\ncompute " + bpy.context.object.name)

		parent_obj = bpy.context.object
		for idx, subcrystal in enumerate(genotype):
			bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=1,view_align=False,location=(0, 0, 0),
												  enter_editmode=False)
			bpy.context.object.parent = parent_obj
			bpy.context.object.name = 'Sub' + parent_obj.name + '-' + str(idx)
			object_ref = bpy.context.object

			for cut in subcrystal['cuts']:
				plane_co = bpyutils.spherical_to_xyz(cut[0], cut[1],cut[2])
				plane_no = list(plane_co)
				plane_no_magnitude = math.sqrt(sum([x ** 2 for x in plane_no]))
				plane_no = [x / plane_no_magnitude for x in plane_no]
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.bisect(plane_co=plane_co,plane_no=plane_no,use_fill=True,
									clear_inner=False, clear_outer=True, xstart=-100, xend=100,ystart=-100, yend=100)
				bpy.ops.object.mode_set(mode='OBJECT')
				object_ref.scale = (subcrystal['scale'][0], subcrystal['scale'][1], subcrystal['scale'][2])
				bpy.context.object.rotation_euler[0] = subcrystal['orientation'][1]
				bpy.context.object.rotation_euler[2] = subcrystal['orientation'][0]
				object_ref.location = (
					(subcrystal['scale'][2] + subcrystal['offset']) * math.sin(subcrystal['orientation'][0]) * math.sin(subcrystal['orientation'][1]),
					(subcrystal['scale'][2] + subcrystal['offset']) * -math.cos(subcrystal['orientation'][0]) * math.sin(subcrystal['orientation'][1]),
					(subcrystal['scale'][2] + subcrystal['offset']) * math.cos(subcrystal['orientation'][1])
				)
			parent_obj.location = location
			bpyutils.bpydeselect()



	# Genotype mutation ----------------------------------------------------------------------------------------------------

	def mutate_genotype(self):
		"""Création d'une mutation : va au hasard modifier un des attributs. Possibilités :
		- Ajouter un sous-crystal
		- Supprimer un sous-crystal
		- Ajouter un cut
		- Retirer un cut
		- Modifier un cut
		- Modifier un scale
		- Modifier une orientation
		- Modifier un offset
		"""
		done = False  # Evitons les mutations illégales et retentons s'il y a une erreur
		while not done:
			randomid = random.randint(0, 7)
			if randomid == 0:  # Ajouter un sous-crystal
				if len(self.genotype) < self.max_subcrystals:
					self.genotype.append(self.random_subcrystal_genotype())
					done = True
			elif randomid == 1:  # Supprimer un sous-crystal
				if len(self.genotype) > self.min_subcrystals:
					self.genotype.pop(random.randint(0, len(self.genotype) - 1))
					done = True
			elif randomid == 2:  # Ajouter un cut
				sc = self.random_subcrystal()
				if len(sc['cuts']) < self.max_cuts:
					sc['cuts'].append(self.random_cut_genotype())
					done = True
			elif randomid == 3:  # Retirer un cut
				sc = self.random_subcrystal()
				if len(sc['cuts']) > self.min_cuts:
					sc['cuts'].pop(random.randint(0, len(sc['cuts']) - 1))
					done = True
			elif randomid == 4:  # Modifier un cut
				sc = self.random_subcrystal()
				if len(sc['cuts']) > 0:
					sc['cuts'][random.randint(0, len(sc['cuts']) - 1)] = self.random_cut_genotype()
					done = True
			elif randomid == 5:  # Modifier un scale
				sc = self.random_subcrystal()
				sc['scale'] = self.random_scale_genotype()
				done = True
			elif randomid == 6:  # Modifier une orientation
				sc = self.random_subcrystal()
				sc['orientation'] = self.random_orientation_genotype()
				done = True
			elif randomid == 7:  # Modifier un offset
				sc = self.random_subcrystal()
				sc['offset'] = self.random_offset_genotype()
				done = True

	def random_subcrystal(self):
		"""returns a random subcrystal in genotype (reference, so mutable in place)"""
		return self.genotype[random.randint(0, len(self.genotype) - 1)]

	# Genotype cross generation --------------------------------------------------------------------------------------------

	@staticmethod
	def cross_genotypes(geno1, geno2):
		"calcule trois enfants différents : moyenne, moitié 1 et moitié 2"
		return [
			CrystalGenetic.cross_genotype_mean(geno1, geno2),
			CrystalGenetic.cross_genotype_firsthalf(geno1, geno2),
			CrystalGenetic.cross_genotype_lasthalf(geno1, geno2)
		]

	@staticmethod
	def cross_genotype_mean(geno1, geno2):
		"""Calcule le génotype moyen des deux parents"""
		child = []
		# le nombre de subcrystals est le minimum des deux parents
		for sc1, sc2 in zip(geno1, geno2):
			cuts = []
			for c1, c2 in zip(sc1['cuts'], sc2['cuts']):
				cuts.append(np.average([c1, c2], axis=0).tolist())
			scale = np.average([sc1['scale'], sc2['scale']], axis=0).tolist()
			orientation = np.average([sc1['orientation'], sc2['orientation']], axis=0).tolist()
			offset = np.average([sc1['offset'], sc2['offset']])
			child.append({
				'cuts': cuts,
				'scale': scale,
				'orientation': orientation,
				'offset': offset
			})
		return CrystalGenetic(child)

	@staticmethod
	def cross_genotype_firsthalf(geno1, geno2):
		"""Créée un enfant composé de la moitié des subcristaux de chaque parent"""
		child = []
		for sc in geno1[:1 + (len(geno1)-1)//2]:
			child.append(copy.deepcopy(sc))
		for sc in geno2[len(geno2)//2:]:
			child.append(copy.deepcopy(sc))
		return CrystalGenetic(child)

	@staticmethod
	def cross_genotype_lasthalf(geno1, geno2):
		"""Créée un enfant composé de la moitié des subcristaux de chaque parent (inversé par rapport à firsthalf)"""
		child = []
		for sc in geno2[:1 + (len(geno2) - 1) // 2]:
			child.append(copy.deepcopy(sc))
		for sc in geno1[len(geno1) // 2:]:
			child.append(copy.deepcopy(sc))
		return CrystalGenetic(child)


	# Fitness computation --------------------------------------------------------------------------------------------------

	def compute_fitness(self):
		"""Le fitness ne retourne rien. Il est établi arbitrairement par l'utilisateur."""
		return None

	# Destructor -----------------------------------------------------------------------------------------------------------

	def __del__(self):
		"""Quand le génotype est suprimmé, on vire aussi son phénotype s'il existe."""
		if self.generated is not None:
			import bpy
			import StoneEdgeGeneration.bpyutils as bpyutils
			bpyutils.bpydeselect()
			for child in bpy.data.objects[self.generated].children:
				child.select = True
			bpy.ops.object.delete()
			bpy.data.objects[self.generated].select = True
			bpy.ops.object.delete()

# ======================================================================================================================
# TOOLS
# ======================================================================================================================
