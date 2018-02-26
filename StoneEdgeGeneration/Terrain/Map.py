from StoneEdgeGeneration.Asset.assgenutils import *
from StoneEdgeGeneration.Asset.genericgenetic import *

from StoneEdgeGeneration.Terrain.HeightMap import *

import io
import numpy as np

import copy

import bpy

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
            octaves : int (1-100),
            lacunarity : int (1-100),
            freq : float (0-20),
            size : float (-10-20),
            mean : float (-5-5),
            scale : float (-10-10),
            randomType : int (0-10),
            seed : int (0-100)
           ]
           """
        return {
            'vertcount' : 100 + int(random.random()*1900),
            'coefMapOne' : random.random(),
            'coefMapTwo' : random.random(),
            'smooth' : int(random.random()*2) % 2 == 0,
            'octaves' : 1 + int(random.random() * 99),
            'lacunarity' : 1 + int(random.random() * 99),
            'freq' : random.random() * 20,
            'size' : -10 + random.random() * 30,
            'mean' : -5 + random.random() * 10,
            'scale' : -10 + random.random() * 20,
            'randomType' : int(random.random()*10),
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
        buf.write("\n\trandomType:" + str(getrandomname(self.genotype['randomType'])))
        buf.write("\n\tseed:" + str(self.genotype['seed']))
        buf.write("\n}\n")
        buf.write("- End genotype -")

        ret = buf.getvalue()
        buf.close()
        return ret

    def compute_individual(self, location):
        """Génère une map"""

        bpy.context.scene.cursor_location = [0, 0, 0]

        if self.generated is not None:  # on supprime les anciens submaps s'il y en avait
            print("re-compute " + self.generated)
            bpydeselect()
            bpy.data.objects[self.generated].select = True
            bpy.context.object.location = (0, 0, 0)
        else:  # ou on créée un nouveau container s'il n'y en a pas
            bpy.ops.mesh.primitive_plane_add(radius=10)
            bpy.context.object.name = "Map" + '%03d' % GenericGenetic.bobject_unique_id()
            self.generated = bpy.context.object.name
            print("compute " + self.generated)

        obj = bpy.data.objects[self.generated]
        mesh = obj.data

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.dissolve_limited(angle_limit=0.8)
        count = (self.genotype['vertcount'] / len(mesh.vertices) - 1)
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
                        coefMap1=self.genotype['coefMap1'], coefMap2=self.genotype['coefMap2'],
                        smooth=self.genotype['smooth'], octaves=self.genotype['octaves'], lacunarity=self.genotype['lacunarity'],
                        freq=self.genotype['freq'], freq2=self.genotype['freq'], mean=self.genotype['mean'], scale=self.genotype['scale'],
                        randomtype=self.genotype['randomtype'], seed=self.genotype['seed'])
        for i in range(0, len(mesh.vertices)):
            vertice = mesh.vertices[i]
            vertice.co = originalVertices[0, i] + originalVertices[1, i] * map[i] * self.genotype['size']

        if self.genotype['smooth']:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=1)
            bpy.ops.object.mode_set(mode='OBJECT')
        bpydeselect()

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
            self.genotype['octaves'] = max(1, min(100, int(self.genotype['octaves'] + -10 + random.random()*20)))
            chance = chance + 10
        else:
            chance = chance - 5

        rand = random.random() * 100
        if rand > chance:
            self.genotype['lacunarity'] = max(1, min(100, int(self.genotype['lacunarity'] + -10 + random.random()*20)))
            chance = chance + 10
        else:
            chance = chance - 5

        rand = random.random() * 100
        if rand > chance:
            self.genotype['freq'] = max(0.1, min(20, self.genotype['freq'] + -5 + random.random()*10))
            chance = chance + 10
        else:
            chance = chance - 5

        rand = random.random() * 100
        if rand > chance:
            self.genotype['size'] = max(0.1, min(20, self.genotype['size'] + -5 + random.random()*10))
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
            'randomType': geno1['randomType'] if random.randint() % 2 == 0 else geno2['randomType'],
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
            bpydeselect()
            for child in bpy.data.objects[self.generated].children:
                child.select = True
            bpy.ops.object.delete()
            bpy.data.objects[self.generated].select = True
            bpy.ops.object.delete()


# ======================================================================================================================
# TOOLS
# ======================================================================================================================

# ======================================================================================================================
# GESTION DU map MUTATE MODAL OPERATOR
# ======================================================================================================================


class MapMutateModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.map_mutate_modal_operator"
    bl_label = "map Mutate Modal Operator"

    def __init__(self):
        self.genotype = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.genotype.mutate_genotype()
            self.genotype.compute_individual((0, 0, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        ensure_delete_all()
        self.genotype = MapGenetic()
        self.genotype.compute_individual((0, 0, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


# ======================================================================================================================
# GESTION DU map GENERATE MODAL OPERATOR
# ======================================================================================================================


class MapGenerateModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.map_generate_modal_operator"
    bl_label = "map Generate Modal Operator"

    def __init__(self):
        self.genotype = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            ensure_delete_all()
            self.genotype = MapGenetic()
            self.genotype.compute_individual((0, 0, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        bpydeleteall()
        self.genotype = MapGenetic()
        self.genotype.compute_individual((0, 0, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# ======================================================================================================================
# GESTION DU map CROSS MODAL OPERATOR
# ======================================================================================================================


class MapCrossModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.map_cross_modal_operator"
    bl_label = "map Cross Modal Operator"

    def __init__(self):
        self.genotype1 = None
        self.genotype2 = None
        self.genotypeChildren = None

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            ensure_delete_all()
            self.genotype1 = MapGenetic()
            self.genotype2 = MapGenetic()
            self.genotypeChildren = MapGenetic.cross_genotypes(self.genotype1.genotype, self.genotype2.genotype)
            self.genotype1.compute_individual((-8, 0, 0))
            self.genotype2.compute_individual((8, 0, 0))
            for i, g in enumerate(self.genotypeChildren):
                g.compute_individual((0, -5 + 5 * i, 0))
            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        ensure_delete_all()
        self.genotype1 = MapGenetic()
        self.genotype2 = MapGenetic()
        self.genotypeChildren = MapGenetic.cross_genotypes(self.genotype1.genotype, self.genotype2.genotype)
        self.genotype1.compute_individual((-8, 0, 0))
        self.genotype2.compute_individual((8, 0, 0))
        for i, g in enumerate(self.genotypeChildren):
            g.compute_individual((0, -5 + 5 * i, 0))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# ======================================================================================================================
# GESTION DU map GENERATIONAL MODAL
# ======================================================================================================================


class MapGenerationalModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.map_generational_modal_operator"
    bl_label = "Map Generational Modal Operator"

    def __init__(self):
        return

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':

            self.generator.next_generation()
            self.generator.genotypes[2].fitness = 0.8
            self.generator.genotypes[4].fitness = 0.8
            self.generator.genotypes[8].fitness = 0.8
            self.generator.genotypes[0].fitness = 0.8
            print("")
            print(repr(self.generator))

            return {'RUNNING_MODAL'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (context,)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(self.draw_callback_text, args, 'WINDOW', 'POST_PIXEL')
        ensure_delete_all()

        self.generator = AssetGeneticsController(
            genetic_class=MapGenetic,
            max_genotypes=9,
            selection_type="number",
            selection_type_param=4,
            show_mode='all'
        )

        self.generator.genotypes[2].fitness = 0.8
        self.generator.genotypes[4].fitness = 0.8
        self.generator.genotypes[8].fitness = 0.8
        self.generator.genotypes[0].fitness = 0.8

        print(repr(self.generator))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

# ======================================================================================================================
# REGISTER MODALS
# ======================================================================================================================


def register():
    bpy.utils.register_class(MapMutateModalOperator)
    bpy.utils.register_class(MapGenerateModalOperator)
    bpy.utils.register_class(MapCrossModalOperator)
    bpy.utils.register_class(MapGenerationalModalOperator)


def unregister():
    bpy.utils.unregister_class(MapMutateModalOperator)
    bpy.utils.unregister_class(MapGenerateModalOperator)
    bpy.utils.unregister_class(MapCrossModalOperator)
    bpy.utils.unregister_class(MapGenerationalModalOperator)

if __name__ == "__main__":
    register()

    bpy.ops.object.map_generational_modal_operator('INVOKE_DEFAULT')

    #unregister()
