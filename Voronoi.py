import matplotlib
import numpy as np
import noise
from PIL import Image, ImageDraw
from scipy.spatial import voronoi_plot_2d
from scipy.spatial import Voronoi
from enum import Enum

class RegionType(Enum):
    WATER = 0
    LAND = 1
    UNDEFINED = -1
    END = -2

class VoronoiIA(Voronoi):

    def __init__(self, voronoimap):
        Voronoi.__init__(self)
        self.points = voronoimap.points
        self.vertices = voronoimap.vertices

class Region:

    def __init__(self, vertices_index, point):
        self.point = point
        self.vertices_index = vertices_index
        if len(vertices_index) == 0 or min(vertices_index) < 0:
            self.type = RegionType.END
        else:
            self.type = RegionType.UNDEFINED

    def defineType(self, freq=5, octaves=1, persistance=0.5,lacunarity=2.0, repeat=1024, base=0):
        if self.type == RegionType.UNDEFINED and self.point is not None:
            octaves = max(1, int(octaves))
            base = int(base)
            potential = noise.pnoise2(self.point[0] * freq, self.point[1] * freq, octaves, persistance, lacunarity, repeat, base)
            if potential > 0:
                self.type = RegionType.LAND
            else:
                self.type = RegionType.WATER

    def draw(self, draw, map, scale=(1,1)):
        if self.point is None or self.type == RegionType.END:
            return

        if self.type == RegionType.WATER:
            color = (25, 125, 255)
        elif self.type == RegionType.LAND:
            color = (170, 148, 50)
        else:
            color = (255, 255, 255)
        points = []
        for point in (map.vertices[self.vertices_index]*scale):
            points.append((point[0],point[1]))
        draw.polygon(points[:], fill=color)


def regulax(map, level=1):
    points = map.points
    xmin, xmax, ymin, ymax = points[:,0].min(), points[:,0].max(), points[:,1].min(), points[:,1].max()
    while level > 0:
        regionPerPoint = np.array(map.regions[:])[map.point_region[:].astype(int)]
        for i in range(len(regionPerPoint)):
            if regionPerPoint[i] in regionPerPoint[i+1:]:
                points[i] = (np.random.random((1, 2)) * np.array((xmax-xmin,ymax-ymin)) + np.array((xmin,ymin)))
            else:
                isIn = (min(regionPerPoint[i]) >= 0) if (len(regionPerPoint[i]) > 0) else False
                if isIn:
                    points[i] = map.vertices[np.array(regionPerPoint[i])].mean(axis=0)
            points[i, 0] = min(xmax, max(xmin, points[i, 0]))
            points[i, 1] = min(ymax, max(ymin, points[i, 1]))
        points = np.unique(points, axis=0)
        map = Voronoi(points)
        level = level - 1
    return map

def voronoimap(sizex, sizey, xx, yy, pointscount, regular=0):
    xmin, xmax, ymin, ymax = xx.min(), xx.max(), yy.min(), yy.max()
    XX, YY = np.mgrid[xmin:xmax:sizex*1j, ymin:ymax:sizey*1j]

    index = np.array([(0,0),(0,sizey*0.5),(0,sizey-1),
                      (sizex*0.5,0),(sizex*0.5,sizey*0.5),(sizex*0.5,sizey-1),
                      (sizex - 1, 0), (sizex - 1, sizey * 0.5), (sizex - 1, sizey - 1)], dtype=int)

    while index.shape[0] < pointscount:
        index = np.vstack((index, (np.random.random((pointscount, 2)) * (sizex, sizey)).astype(int)))
        index = np.unique(index, axis=0)
    index = index[:pointscount]
    points = np.stack((XX[index[:, 0], 0], YY[0, index[:, 1]]), axis=-1)
    points = points[np.argsort(points[:, 0])]

    map = Voronoi(points)
    map = regulax(map, regular)

    for i in range(len(map.point_region)):
        if type(map.regions[map.point_region[i]]) is list:
            map.regions[map.point_region[i]] = Region(map.regions[map.point_region[i]], map.points[i])
            map.regions[map.point_region[i]].defineType(10)
    for i in range(len(map.regions)):
        if type(map.regions[i]) is list:
            map.regions[i] = Region(map.regions[i], None)


    return map

def main():
    matplotlib.interactive(True)
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.ion()

    xx, yy, zz = np.mgrid[0:1:10j, 0:1:10j, -1:1:2j]
    map = voronoimap(50,50,xx,yy,20)
    voronoi_plot_2d(map)
    plt.show()
    plt.pause(1)
    map = voronoimap(300,300,xx,yy,200,5)
    voronoi_plot_2d(map)
    plt.show()
    plt.pause(1)


    image = Image.new('RGB', (200,200), (255,255,255))
    draw = ImageDraw.Draw(image)
    for region in map.regions:
        region.draw(draw, map, image.size)
    image.save("yolo.jpg", "JPEG")

    fig = plt.figure(figsize=(6,6))
    ax=plt.subplot(1,1,1)
    plt.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0)
    imageArr = np.asarray(image)  # Get array back
    imgplot = plt.imshow(imageArr)

    plt.pause(1)


if __name__ == "__main__":
    main()
