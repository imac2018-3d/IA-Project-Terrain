import bpy
import numpy as np
import mathutils
import pickle
import io
from HeightMap import *

def saveVertices(originalVertice):
    bpy.context.scene['originalVertice'] = pickle.dumps(originalVertice)

def saveMesh(mesh):
    originalVertices = np.empty((2,len(mesh.vertices),3))
    for i in range(len(mesh.vertices)):
        originalVertices[0,i] = mesh.vertices[i].co
        originalVertices[1,i] = mesh.vertices[i].normal
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
        max = 4000000)

    
    if "paramone" in scn:
        del scn["paramone"]
    scn["paramone"] = 1.
    bpy.types.Scene.paramone = bpy.props.FloatProperty(name = "Param 1",
        default = 1.,
        min = 0.,
        max = 100.)
    
    if "paramtwo" in scn:
        del scn["paramtwo"]
    scn["paramtwo"] = 1.
    bpy.types.Scene.paramtwo = bpy.props.FloatProperty(name = "Param 2",
        default = 1.,
        min = 0.,
        max = 100.)
        
    if "size" in scn:
        del scn["size"]
    scn["size"] = 1.
    bpy.types.Scene.size = bpy.props.FloatProperty(name = "Size",
        default = 1.,
        min = 0.,
        max = 100.)
    
class HeightMapPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "HeightGenerator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    mapObject = bpy.data.objects.new("Map", None)        

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self.mapObject, "parent", text="Map")
        row = layout.row()
        row.prop(context.scene, "vct")
        row = layout.row()
        row.prop(context.scene, "paramone")
        row.prop(context.scene, "paramtwo")
        row.prop(context.scene, "size")
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


    def generate(self, vertcount, param1, param2, size, mapObject):
        if mapObject == None:
            lastMapObject = None
            return
    
        mesh = mapObject.data

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        mapObject.select = True
        count = (vertcount/len(mesh.vertices)-1)
        if count >= 0:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.subdivide(number_cuts=count)
            bpy.ops.object.mode_set(mode='OBJECT')
            originalVertices = saveMesh(mesh)
            bpy.context.scene['lastMapObject'] = mapObject
        else:
            if bpy.context.scene['lastMapObject'] != mapObject:
                originalVertices = saveMesh(mesh)
                bpy.context.scene['lastMapObject'] = mapObject
            else:
                originalVertices = loadVertices()
        
        print(originalVertices[0,:,:2],'\n',len(originalVertices[0,:]))
        map = heightmap2(60, 60, True, originalVertices[0,:,0], originalVertices[0,:,1])
        for i in range(0, len(mesh.vertices)):
            vertice = mesh.vertices[i]
            vertice.co = originalVertices[0,i] + originalVertices[1,i] * map[i] * size
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.vertices_smooth(factor=0.7, repeat=2)
        bpy.ops.object.mode_set(mode='OBJECT')
    
    def execute(self, context):
        self.generate(bpy.context.scene["vct"], 
                    bpy.context.scene["paramone"], 
                    bpy.context.scene["paramtwo"], 
                    bpy.context.scene["size"], 
                    HeightMapPanel.mapObject.parent)
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(HeightMapPanel)
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_class(HeightMapPanel)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    initSceneProperties(bpy.context.scene)
    register()
    