import bpy

def saveImage(name):
    bpy.data.scenes['Scene'].render.filepath = 'D:/'+name
    bpy.ops.render.render( write_still=True )