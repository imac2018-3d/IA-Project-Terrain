import bpy, bmesh
import numpy as np
import mathutils
import pickle
import io
import importlib
from StoneEdgeGeneration.Terrain import HeightMap

def saveVertices(originalVertice):
    bpy.context.scene['originalVertice'] = pickle.dumps(originalVertice)

def saveMesh(vertices):
    originalVertices = np.empty((2,len(vertices),3))
    for i in range(len(vertices)):
        originalVertices[0,i] = vertices[i].co
        originalVertices[1,i] = vertices[i].normal
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
    bpy.types.Scene.vct = bpy.props.FloatProperty(name = "Vertices count",
        default = 100,
        min = 4,
        max = 40000)
    
    if "mean" in scn:
        del scn["mean"]
    scn["mean"] = 0.
    bpy.types.Scene.mean = bpy.props.FloatProperty(name = "Mean",
        default = scn["mean"],
        min = -2.,
        max = 2.)
    
    if "scale" in scn:
        del scn["scale"]
    scn["scale"] = 1.
    bpy.types.Scene.scale = bpy.props.FloatProperty(name = "Scale",
        default = scn["scale"],
        min = 0.,
        max = 100.)
        
    if "size" in scn:
        del scn["size"]
    scn["size"] = 1.
    bpy.types.Scene.size = bpy.props.FloatProperty(name = "Size",
        default = scn["size"],
        min = 0.,
        max = 100.)
        
    if "smooth" in scn:
        del scn["smooth"]
    scn["smooth"] = True
    bpy.types.Scene.smooth = bpy.props.BoolProperty(name = "Smooth",
        default = scn["smooth"])

    if "coefMapOne" in scn:
        del scn["coefMapOne"]
    scn["coefMapOne"] = 0.5
    bpy.types.Scene.coefMapOne = bpy.props.FloatProperty(name = "Coef Map1",
        default=scn["coefMapOne"],
        min = 0.,
        max = 1.)
        
    if "coefMapTwo" in scn:
        del scn["coefMapTwo"]
    scn["coefMapTwo"] = 0.5
    bpy.types.Scene.coefMapTwo = bpy.props.FloatProperty(name = "Coef Map2",
        default = scn["coefMapTwo"],
        min = 0.,
        max = 1.)
        
    if "octaves" in scn:
        del scn["octaves"]
    scn["octaves"] = 1
    bpy.types.Scene.octaves = bpy.props.IntProperty(name = "Octaves",
        default = scn["octaves"],
        min = 0,
        max = 100)
        
    if "lacunarity" in scn:
        del scn["lacunarity"]
    scn["lacunarity"] = 2.0
    bpy.types.Scene.lacunarity = bpy.props.FloatProperty(name = "Lacunarity",
        default = scn["lacunarity"],
        min = 1.,
        max = 100.)
        
    if "frequences" in scn:
        del scn["frequences"]
    scn["frequences"] = 5.0
    bpy.types.Scene.frequences = bpy.props.FloatProperty(name = "Frequences",
        default = scn["frequences"],
        min = -50.,
        max = 50.)

    if "randomType" in scn:
        del scn["randomType"]
    scn["randomType"] = 0
    bpy.types.Scene.randomType = bpy.props.IntProperty(name="Random type",
        default = scn["randomType"],
        min = 0,
        max = 10)

    if "seed" in scn:
        del scn["seed"]
    scn["seed"] = 0
    bpy.types.Scene.seed = bpy.props.IntProperty(name="Seed",
        default = scn["seed"],
        min = -1,
        max = 1000)
    
    
class HeightMapPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "HeightGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "vct")
        row = layout.row()
        row.prop(context.scene, "coefMapOne")
        row.prop(context.scene, "coefMapTwo")
        row.prop(context.scene, "size")
        row = layout.row()
        row.prop(context.scene, "lacunarity")
        row.prop(context.scene, "octaves")
        row = layout.row()
        row.prop(context.scene, "frequences")
        row.prop(context.scene, "mean")
        row.prop(context.scene, "scale")
        row = layout.row()
        row.prop(context.scene, "randomType")
        row.prop(context.scene, "seed")
        row.prop(context.scene, "smooth")
        # Big render button
        row = layout.row()
        row.operator("generator.height", text="Generate Map")

def getpoints(vertice):
    return [vertice.co[0], vertice.co[1], vertice.co[2]]

def filter(sizex = 11):
    return np.hamming(sizex)

class OBJECT_OT_GenerateButton(bpy.types.Operator):
    bl_idname = "generator.height"
    bl_label = "Height Generator"


    def generate(self, vertcount, coefMapOne, coefMapTwo,
                smooth, octaves, lacunarity, freq, size,
                mean, scale, randomType, seed):

        obj = bpy.context.edit_object
        mesh = obj.data

        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(mesh)

        vertices = [v for v in bm.verts if v.select]

        count = (vertcount/len(vertices)-1)
        if count >= 0:
            bpy.ops.mesh.subdivide(number_cuts=count)
            originalVertices = saveMesh(vertices)
            bpy.context.scene['lastMapObject'] = bpy.context.object
        else:
            if bpy.context.scene['lastMapObject'] != bpy.context.object:
                originalVertices = saveMesh(vertices)
                bpy.context.scene['lastMapObject'] = bpy.context.object
            else:
                originalVertices = loadVertices()
        
        map = HeightMap.heightmap3(100, 100, 5, originalVertices[0,:,0], originalVertices[0,:,1], originalVertices[0,:,2],
                                   coefMap1=coefMapOne, coefMap2=coefMapTwo,
                                   smooth=True, octaves=octaves, lacunarity=lacunarity,
                                   freq=freq*2, freq2=freq*2, mean=mean, scale=scale,
                                   randomtype=randomType, seed=seed)
        for i in range(0, len(vertices)):
            vertice = vertices[i]
            vertice.co = originalVertices[0,i] + originalVertices[1,i] * map[i] * size

        bmesh.update_edit_mesh(mesh, True)
        bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=1)

    def execute(self, context):
        self.generate(bpy.context.scene["vct"], 
                    bpy.context.scene["coefMapOne"],
                    bpy.context.scene["coefMapTwo"],
                    bpy.context.scene["smooth"],
                    bpy.context.scene["octaves"], 
                    bpy.context.scene["lacunarity"],
                    bpy.context.scene["frequences"],
                    bpy.context.scene["size"],
                    bpy.context.scene["mean"],
                    bpy.context.scene["scale"], 
                    bpy.context.scene["randomType"],
                    bpy.context.scene["seed"])
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(HeightMapPanel)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_class(HeightMapPanel)
    bpy.utils.unregister_module(__name__)

def loadTool():
    initSceneProperties(bpy.context.scene)
    register()    

if __name__ == "__main__":
    importlib.reload(HeightMap)
    loadTool()
    