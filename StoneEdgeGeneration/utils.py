import os

def _defaultdirpath(dirpath):
    if len(dirpath) == 0:
        if 'basepath' in globals():
            dirpath = basepath
        else:
            from StoneEdgeGeneration.bpyutils import getBasePath
            dirpath = getBasePath()
    return dirpath

def getImagePath(imageName="", dirpath=""):
    dirpath=_defaultdirpath(dirpath)
    folder = dirpath + "/StoneEdgeGeneration/Resources/Images/"
    if imageName:
        return os.path.normpath(os.path.join(folder, imageName + ".png")).replace("\\","/")
    else:
        return folder.replace("\\","/")

def getModelPath(modelName="", dirpath=""):
    dirpath = _defaultdirpath(dirpath)
    folder = dirpath + "/StoneEdgeGeneration/Resources/Models/"
    if modelName:
        return os.path.normpath(os.path.join(folder, modelName + ".obj")).replace("\\","/")
    else:
        return folder.replace("\\","/")