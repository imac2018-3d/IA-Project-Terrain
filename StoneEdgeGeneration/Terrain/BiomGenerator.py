import bpy
import numpy as np
import mathutils
import os.path
from tempfile import NamedTemporaryFile
import pickle
import io
import importlib
#from StoneEdgeGeneration.Terrain import Voronoi
#from StoneEdgeGeneration.utils import getImagePath

import Voronoi
from utils import BASE_PATH

def saveVertices(originalVertice):
    bpy.context.scene['originalVertice'] = pickle.dumps(originalVertice)

def saveMesh(mesh):
    originalVertices = np.empty((2, len(mesh.vertices), 3))
    for i in range(len(mesh.vertices)):
        originalVertices[0, i] = mesh.vertices[i].co
        originalVertices[1, i] = mesh.vertices[i].normal
    saveVertices(originalVertices)
    return originalVertices


def loadVertices():
    return pickle.loads(bpy.context.scene['originalVertice'])

def initSceneProperties(scn):
    originalVertice = np.array([])
    saveVertices(originalVertice)
    bpy.context.scene['lastMapObject'] = None
    if "vct" in scn:
        del scn["vct"]
    scn["vct"] = 100.
    bpy.types.Scene.vct = bpy.props.FloatProperty(name="Vertices count",
                                                  default=100,
                                                  min=4,
                                                  max=40000)

class BiomMapPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "BiomGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    mapObject = bpy.data.objects.new("Map", None)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self.mapObject, "parent", text="Map")
        row = layout.row()
        row.prop(context.scene, "vct")
        # Big render button
        row = layout.row()
        row.operator("generator.biom", text="Generate Biom")


def getpoints(vertice):
    return [vertice.co[0], vertice.co[1], vertice.co[2]]


def filter(sizex=11):
    return np.hamming(sizex)


class OBJECT_OT_GenerateButton(bpy.types.Operator):
    bl_idname = "generator.biom"
    bl_label = "Biom Generator"

    def generate(self, vertcount, mapObject):
        if mapObject is None:
            return

        mesh = mapObject.data

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        mapObject.select = True
        count = (vertcount / len(mesh.vertices) - 1)
        if count >= 0:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.subdivide(number_cuts=count)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.scene['lastMapObject'] = mapObject
        else:
            if bpy.context.scene['lastMapObject'] != mapObject:
                bpy.context.scene['lastMapObject'] = mapObject

        voromap = Voronoi.VoronoiMap(512,512, pointscount=500)
        image = voromap.toimage()
        with NamedTemporaryFile(suffix=".jpg", dir=BASE_PATH) as tmp:
            name = tmp.name
            tmp.close()
        image.save(name, "JPEG")

        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.material.new()
        tex = bpy.data.textures.new("SomeName", 'IMAGE')
        bpy.context.object.active_material.name = "map_mat"
        mat = bpy.context.object.active_material
        slot = mat.texture_slots.add()
        slot.texture = tex
        mesh.materials.append(mat)

        try:
            img = bpy.data.images.load(name)
        except:
            print("Cannot load image %s" % name)
            return
        tex.image = img

    def execute(self, context):
        self.generate(bpy.context.scene["vct"],
                      BiomMapPanel.mapObject.parent)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BiomMapPanel)
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_class(BiomMapPanel)
    bpy.utils.unregister_module(__name__)


def loadTool():
    initSceneProperties(bpy.context.scene)
    register()


if __name__ == "__main__":
    importlib.reload(Voronoi)
    loadTool()
