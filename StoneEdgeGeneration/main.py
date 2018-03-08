from StoneEdgeGeneration.UI import TerrainWindow, AssetWindow, Parameter, Individual

def loadAsset():
    return AssetWindow.AssetWindow()

def loadTerrain():
    window = TerrainWindow.TerrainWindow()
    
    # EXAMPLE OF SLIDER PARAMETER
    nbGeneration = Parameter.SliderParameter("Number of generations", 15, 10, 20)
    window.addSlider(nbGeneration)

    return window