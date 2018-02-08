import bpy, sys, os

BASE_PATH = os.path.dirname(bpy.data.filepath)

def saveImage(name):
    bpy.data.scenes['Scene'].render.filepath = getImagePath(name)
    bpy.ops.render.render( write_still=True )

def getImagePath(imageName=""):
    folder = BASE_PATH + "/StoneEdgeGeneration/Resources/Images/"
    if imageName:
        return os.path.normpath(os.path.join(folder, imageName + ".png"))
    else:
        return folder

def getModelsPath(modelName=""):
    folder = BASE_PATH + "/StoneEdgeGeneration/Resources/Images/"
    if modelName:
        return os.path.normpath(os.path.join(folder, modelName + ".png"))
    else:
        return folder