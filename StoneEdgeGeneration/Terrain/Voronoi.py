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


class VoronoiMap:
    class Region:

        def __init__(self, region_index, vertices_index, point):
            self.point = point
            self.region_index = region_index
            self.vertices_index = vertices_index
            if len(vertices_index) == 0 or min(vertices_index) < 0:
                self.type = RegionType.END
            else:
                self.type = RegionType.UNDEFINED

        def defineType(self, freq=5, octaves=1, persistance=0.5, lacunarity=2.0, repeat=1024, base=0):
            if self.type == RegionType.UNDEFINED and self.point is not None:
                octaves = max(1, int(octaves))
                base = int(base)
                potential = noise.pnoise2(self.point[0] * freq, self.point[1] * freq, octaves, persistance, lacunarity,
                                          repeat, base)
                if potential > 0:
                    self.type = RegionType.LAND
                else:
                    self.type = RegionType.WATER

        def draw(self, draw, map, scale=(1, 1)):
            if self.point is None or self.type == RegionType.END:
                return

            if self.type == RegionType.WATER:
                color = (25, 125, 255)
            elif self.type == RegionType.LAND:
                color = (170, 148, 50)
            else:
                color = (255, 255, 255)
            points = []
            for point in (map.vertices[self.vertices_index] * scale):
                points.append((point[0], point[1]))
            draw.polygon(points[:], fill=color)

        def drawindex(self, draw, map, scale=(1, 1)):
            if self.point is None or self.type == RegionType.END:
                return

            color = (self.region_index + 1) / 1000.
            points = []
            for point in (map.vertices[self.vertices_index] * scale):
                points.append((point[0], point[1]))
            draw.polygon(points[:], fill=color)

    def __init__(self, sizex, sizey, xx=None, yy=None, pointscount=200, regular=0):
        self.sizex = sizex
        self.sizey = sizey
        if xx is None or yy is None:
            xmin, xmax, ymin, ymax = 0, 1, 0, 1
        else:
            xmin, xmax, ymin, ymax = xx.min(), xx.max(), yy.min(), yy.max()
        XX, YY = np.mgrid[xmin:xmax:sizex * 1j, ymin:ymax:sizey * 1j]
        pointscount = max(1000,int(pointscount))

        index = np.array([(0, 0), (0, sizey * 0.5), (0, sizey - 1),
                          (sizex * 0.5, 0), (sizex * 0.5, sizey * 0.5), (sizex * 0.5, sizey - 1),
                          (sizex - 1, 0), (sizex - 1, sizey * 0.5), (sizex - 1, sizey - 1)], dtype=int)

        while index.shape[0] < pointscount:
            index = np.vstack((index, (np.random.random((pointscount, 2)) * (sizex, sizey)).astype(int)))
            index = np.unique(index, axis=0)
        index = index[:pointscount]
        points = np.stack((XX[index[:, 0], 0], YY[0, index[:, 1]]), axis=-1)
        points = points[np.argsort(points[:, 0])]

        self.voronoimap = Voronoi(points)
        self.regulax(regular)

        self.regions = [None] * len(self.voronoimap.regions)
        for i in range(len(self.voronoimap.point_region)):
            self.regions[self.voronoimap.point_region[i]] = \
                VoronoiMap.Region(self.voronoimap.point_region[i], self.voronoimap.regions[self.voronoimap.point_region[i]], self.voronoimap.points[i])
            self.regions[self.voronoimap.point_region[i]].defineType(10)
        for i in range(len(self.regions)):
            if self.regions[i] is None:
                self.regions[i] = VoronoiMap.Region(i, self.voronoimap.regions[i], None)

    def regulax(self, level=1):
        points = self.voronoimap.points
        xmin, xmax, ymin, ymax = points[:,0].min(), points[:,0].max(), points[:,1].min(), points[:,1].max()
        while level > 0:
            regionPerPoint = np.array(self.voronoimap.regions[:])[self.voronoimap.point_region[:].astype(int)]
            for i in range(len(regionPerPoint)):
                if regionPerPoint[i] in regionPerPoint[i+1:]:
                    points[i] = (np.random.random((1, 2)) * np.array((xmax-xmin,ymax-ymin)) + np.array((xmin,ymin)))
                else:
                    isIn = (min(regionPerPoint[i]) >= 0) if (len(regionPerPoint[i]) > 0) else False
                    if isIn:
                        points[i] = self.voronoimap.vertices[np.array(regionPerPoint[i])].mean(axis=0)
                points[i, 0] = min(xmax, max(xmin, points[i, 0]))
                points[i, 1] = min(ymax, max(ymin, points[i, 1]))
            points = np.unique(points, axis=0)
            self.voronoimap = Voronoi(points)
            level = level - 1

    def toimage(self):
        image = Image.new('RGB', (self.sizex, self.sizey), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for region in self.regions:
            region.draw(draw, self.voronoimap, image.size)
        return image

    def togrid(self):
        image = Image.new('F', (self.sizex, self.sizey), 0)
        draw = ImageDraw.Draw(image)
        for region in self.regions:
            region.drawindex(draw, self.voronoimap, image.size)
        return np.asarray(image)

def main():
    matplotlib.interactive(True)
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.ion()

    xx, yy, zz = np.mgrid[0:1:10j, 0:1:10j, -1:1:2j]
    map = VoronoiMap(50,50,xx,yy,20)
    voronoi_plot_2d(map.voronoimap)
    plt.show()
    plt.pause(1)
    map = VoronoiMap(300,300,xx,yy,200,5)
    voronoi_plot_2d(map.voronoimap)
    plt.show()
    plt.pause(1)


    image = map.toimage()
    image.save("yolo.jpg", "JPEG")

    plt.figure()
    imageArr = np.asarray(image)  # Get array back
    imgplot = plt.imshow(imageArr)
    plt.show()

    plt.pause(1)

    plt.figure()
    imgplot = plt.imshow(map.togrid())
    plt.show()

    plt.pause(1)


if __name__ == "__main__":
    main()
