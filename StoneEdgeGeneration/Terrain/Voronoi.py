import numpy as np
import noise
import random
from PIL import Image, ImageDraw, ImageFilter
from scipy.spatial import voronoi_plot_2d
from scipy.spatial import Voronoi
from scipy.ndimage import filters
from enum import Enum

class RegionType(Enum):
	END = -2
	UNDEFINED = -1
	SEA = 0
	WATER = 1
	LAND = 2
	BARE = 3
	SNOW = 4
	GRASS = 5
	FOREST = 6
	JUNGLE = 7
	SAND = 8
	ROCK = 9
	ICE = 10
	KARBON = 11


def array2RGB(arr, size):
	arr = np.asarray(arr.reshape(arr.shape[0] * arr.shape[1], -1), np.uint8)
	return Image.frombuffer('RGB', size, arr, 'raw', 'RGB', 0, 1)

def array2L(arr, size):
	arr = np.asarray(arr.reshape(arr.shape[0] * arr.shape[1], -1), np.uint8)
	return Image.frombuffer('L', size, arr, 'raw', 'L', 0, 1)


class VoronoiMap:
	class Region:

		def __init__(self, region_index, vertices_index, point, point_index):
			self.point = point
			self.region_index = region_index
			self.vertices_index = vertices_index
			self.point_index = point_index
			self.neighbours = set()
			self.moisture = -1
			self.height = -1
			self.temperature = 20
			if len(vertices_index) == 0:
				self.type = RegionType.END
			elif any(v < 0 for v in vertices_index):
				self.type = RegionType.END
				# TODO: make a finite region
			else:
				self.type = RegionType.UNDEFINED

		def addneighbour(self, otherregion):
			self.neighbours.add(otherregion.region_index)

		def define_neighbours_type(self, regions, landthreshold=0, searelativethreashold=0.1, radialbias=1.0,
									freq=5, octaves=1, persistance=1.0):
			octaves = int(octaves)
			for neighbourindex in self.neighbours:
				neighbour = regions[neighbourindex]
				if neighbour.type == RegionType.UNDEFINED:
					if self.type == RegionType.END:
						neighbour.type = RegionType.SEA
						continue
					elif self.type == RegionType.UNDEFINED:
						self.type = RegionType.SEA
						neighbour.type = RegionType.SEA
						continue
					height = noise.pnoise2(self.point[0] * freq, self.point[1] * freq, octaves, persistance,1.0, 512, 0)
					height = height + (0.25 - abs(self.point[0]-0.5) + 0.25 - abs(self.point[1] - 0.5))*radialbias
					if self.type == RegionType.SEA:
						if height > landthreshold:
							neighbour.type = RegionType.LAND
						else:
							neighbour.type = RegionType.SEA
					elif self.type == RegionType.LAND:
						if height < landthreshold-searelativethreashold:
							neighbour.type = RegionType.SEA
						if height > landthreshold:
							neighbour.type = RegionType.LAND

		def checklake(self, regions):
			if self.type != RegionType.SEA and self.type != RegionType.WATER:
				return False
			self.type = RegionType.UNDEFINED
			islake = False
			for neighbour in self.neighbours:
				n = regions[neighbour]
				if n.type != RegionType.UNDEFINED:
					islake = n.checklake(regions) or n.type == RegionType.LAND
					if not islake:
						break
			if islake:
				self.type = RegionType.WATER
			else:
				self.type = RegionType.SEA
				for neighbour in self.neighbours:
					n = regions[neighbour]
					if n.type == RegionType.WATER:
						n.type = RegionType.SEA
			return islake

		def setheight(self, height):
			self.height = height

		def setmoisture(self, moisture, freq=5, octaves=1, persistance=1.0):
			octaves = int(octaves)
			if self.point is not None:
				self.moisture = max(0, moisture + int(noise.pnoise2(self.point[0] * freq, self.point[1] * freq, octaves,
																	persistance, 1.5, 400, 0)*5))
			else:
				self.moisture = moisture + int(-1+np.random.random()*2)

		def settemperature(self, temperature):
			self.temperature = temperature + int(-1 + np.random.random() * 2)

		def updatetype(self):
			if self.type.value >= RegionType.LAND.value:
				if self.height > 3:
					if self.moisture > 3:
						if self.temperature < 15:
							self.type = RegionType.SNOW
						elif self.temperature > 20:
							self.type = RegionType.GRASS
						else:
							self.type = RegionType.BARE
					else:
						if self.temperature < 15:
							self.type = RegionType.ICE
						elif self.temperature > 20:
							self.type = RegionType.KARBON
						else:
							self.type = RegionType.BARE
				elif self.height > 1:
					if self.temperature < 8:
						if self.moisture > 3:
							self.type = RegionType.SNOW
						else:
							self.type = RegionType.ICE
					else:
						if self.moisture > 4:
							self.type = RegionType.JUNGLE
						elif self.moisture > 2:
							self.type = RegionType.FOREST
						elif self.moisture > 0:
							self.type = RegionType.GRASS
						else:
							self.type = RegionType.ROCK
				else:
					if self.temperature < 5:
						if self.moisture > 3:
							self.type = RegionType.SNOW
						else:
							self.type = RegionType.ICE
					else:
						if self.moisture > 4:
							self.type = RegionType.SAND
						elif self.moisture > 2:
							self.type = RegionType.GRASS
						else:
							self.type = RegionType.ROCK

		def draw(self, draw, map, scale=(1, 1), maxheight=10):
			if self.point is None or self.type == RegionType.END:
				return

			r, g, b = 0, 0, 0
			if self.type == RegionType.WATER:
				r, g, b = 25, 125, 255
			elif self.type.value >= RegionType.LAND.value:
				heightcoef = (self.height+1) / maxheight
				r = 140 * 1/heightcoef
				g = 120 * 1/heightcoef
				b = 50 * 1/heightcoef
				if self.type == RegionType.BARE:
					r = (r + g + b) / 3 + (-10 + random.random() * 20)
					g = (r + g + b) / 3
					b = (r + g + b) / 4
				if self.type == RegionType.KARBON:
					r = (r + g + b) / 4 + (-10 + random.random() * 20)
					g = (r + g + b) / 4
					b = (r + g + b) / 6
				elif self.type == RegionType.ROCK:
					r = (r + g + b) / 4 + (-10 + random.random() * 20)
					g = (r + g + b) / 5 + (-10 + random.random() * 20)
					b = (r + g + b) / 5 + (-10 + random.random() * 20)
				elif self.type == RegionType.SNOW:
					r = r + 200 * heightcoef
					g = g + 200 * heightcoef
					b = b + 200 * heightcoef
				elif self.type == RegionType.ICE:
					r = r + 50 * heightcoef
					g = g + 50 * heightcoef
					b = b + 250 * heightcoef
				elif self.type == RegionType.GRASS:
					r = r - 150 + (-20 + random.random() * 20)
					g = g + 70 + (-10 + random.random() * 20)
					b = b + 20 + (random.random() * 20)
				elif self.type == RegionType.FOREST:
					r = r - 50
					g = g + 10 + (-10 + random.random() * 20)
					b = b + 10 + (-10 + random.random() * 20)
				elif self.type == RegionType.JUNGLE:
					r = r - 200
					g = g - 20 + (-10 + random.random() * 20)
					b = b - 10
				elif self.type == RegionType.SAND:
					b = (r + g + b) / 4 + (-10 + random.random() * 40)
					r = (r + g + b) / 3 + (-10 + random.random() * 40)
					g = (r + g + b) / 3 + (-10 + random.random() * 40)
			elif self.type == RegionType.SEA:
				r, g, b = 10, 12, 50
			color = (max(0, min(255,int(r))), min(255,int(g)), min(255,int(b)))
			if len(map.vertices[self.vertices_index]):
				points = []
				for p in (map.vertices[self.vertices_index] * scale):
					points.append((p[0], scale[1] - p[1]))
				draw.polygon(points[:], fill=color)

		def drawheight(self, draw, map, scale=(1, 1), maxheight=10):
			if self.point is None or self.type == RegionType.END:
				return

			if self.type == RegionType.WATER:
				color = 30
			elif self.type.value >= RegionType.LAND.value:
				color = int(min(255.0, 50.0 + 230.0 * self.height / maxheight))
			elif self.type == RegionType.SEA:
				color = 15
			else:
				color = 0
			points = []
			for point in (map.vertices[self.vertices_index] * scale):
				points.append((point[0], scale[1] - point[1]))
			draw.polygon(points[:], fill=color)

		def drawmoisture(self, draw, map, scale=(1, 1)):
			if self.point is None or self.type == RegionType.END:
				return

			color = int(self.moisture)
			points = []
			for point in (map.vertices[self.vertices_index] * scale):
				points.append((point[0], 1.0 * scale[1] - point[1]))
			draw.polygon(points[:], fill=color)

		def drawindex(self, draw, map, scale=(1, 1)):
			if self.point is None or self.type == RegionType.END:
				return

			color = int(len(self.neighbours))
			points = []
			for point in (map.vertices[self.vertices_index] * scale):
				points.append((point[0], 1.0*scale[1] - point[1]))
			draw.polygon(points[:], fill=color)

	def __init__(self, sizex, sizey, xx=None, yy=None, pointscount=200, regular=0, landthreshold=0,
				searelativethreshold=0.1, radialbias=1.0, heightfreq=5, heightoctaves=1, heightpersistance=1.0,
				 heightstep=1.0, moisturestart=10.0, moisturestep=1.0, moisturefreq=5, moistureoctaves=1, moisturepersistance=1.0,
				 seed=1, temperature=20):
		if seed < 0:
			np.random.seed(None)
		else:
			np.random.seed(seed)
		self.sizex = sizex
		self.sizey = sizey
		if xx is None or yy is None:
			xmin, xmax, ymin, ymax = 0, 1, 0, 1
		else:
			xmin, xmax, ymin, ymax = xx.min(), xx.max(), yy.min(), yy.max()

		pointscount = min(1000, int(pointscount))
		points = np.array((xmin, ymin)) + np.random.rand(int(pointscount/2), 2) * np.array((xmax - xmin, ymax - ymin))
		points = np.asarray(points*10000, int)
		while points.shape[0] < pointscount:
			newpoints = np.array((xmin, ymin)) + np.random.rand(int(pointscount - points.shape[0]), 2)\
						* np.array((xmax - xmin, ymax - ymin))
			points = np.vstack((newpoints, np.asarray(newpoints * 10000, int)))
			points = np.unique(points, axis=0)
		points = points * 0.0001

		self.voronoimap = Voronoi(points)
		self.regulax(regular)

		self.regions = [None] * len(self.voronoimap.regions)
		for i in range(len(self.voronoimap.point_region)):
			self.regions[self.voronoimap.point_region[i]] = \
				VoronoiMap.Region(
					self.voronoimap.point_region[i],
					self.voronoimap.regions[self.voronoimap.point_region[i]],
					self.voronoimap.points[i],
					i
				)
		for i in range(len(self.regions)):
			if self.regions[i] is None:
				self.regions[i] = VoronoiMap.Region(i, self.voronoimap.regions[i], None, -1)

		self.noisylines()
		self.makeislands(landthreshold, searelativethreshold, radialbias, heightfreq, heightoctaves, heightpersistance)
		self.checklake()
		self.setheight(heightstep)
		self.setmoisture(moisturestart, moisturestep, moisturefreq, moistureoctaves, moisturepersistance)
		self.settemperature(temperature)
		self.updatetypes()

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

	def noisylines(self):
		for region in self.regions:
			pass

	def makeislands(self, landthreshold=0, searelativethreshold=0.1, radialbias=1.0, freq=5, octaves=1, persistance=1.0):
		nextregions = set()

		for link in self.voronoimap.ridge_points:
			self.regions[self.voronoimap.point_region[link[0]]].addneighbour(self.regions[self.voronoimap.point_region[link[1]]])
			self.regions[self.voronoimap.point_region[link[1]]].addneighbour(self.regions[self.voronoimap.point_region[link[0]]])

		for region in self.regions:
			if region.type == RegionType.END:
				nextregions.add(region)

		while len(nextregions) > 0:
			regions = nextregions.copy()
			nextregions.clear()
			for region in regions:
				for neighbourindex in region.neighbours:
					neighbour = self.regions[neighbourindex]
					if neighbour.type == RegionType.UNDEFINED:
						nextregions.add(neighbour)
				region.define_neighbours_type(self.regions, landthreshold, searelativethreshold, radialbias,
											  freq, octaves, persistance)


	def checklake(self):
		for region in self.regions:
			if region.type == RegionType.LAND:
				for neighbourindex in region.neighbours:
					neighbour = self.regions[neighbourindex]
					neighbour.checklake(self.regions)

	def setheight(self, heightstep=1.0):
		nextregions = set()
		for region in self.regions:
			if region.type.value < RegionType.WATER.value:
				region.setheight(0)
				nextregions.add(region)

		while len(nextregions) > 0:
			regions = nextregions.copy()
			nextregions.clear()
			for region in regions:
				for neighbourindex in region.neighbours:
					neighbour = self.regions[neighbourindex]
					if neighbour.height == -1:
						if neighbour.type == RegionType.LAND:
							neighbour.setheight(region.height+heightstep)
						else:
							neighbour.setheight(0)
						nextregions.add(neighbour)

	def setmoisture(self, moisturestart=5.0, moisturestep=1.0, freq=5.0, octaves=1, persistance=1.0):
		nextregions = set()
		for region in self.regions:
			if region.type.value < RegionType.LAND.value:
				region.setmoisture(moisturestart+np.random.random()*moisturestep*2-moisturestep)
				nextregions.add(region)

		while len(nextregions) > 0:
			regions = nextregions.copy()
			nextregions.clear()
			for region in regions:
				for neighbourindex in region.neighbours:
					neighbour = self.regions[neighbourindex]
					if neighbour.moisture == -1:
						if neighbour.type == RegionType.LAND:
							neighbour.setmoisture(region.moisture - moisturestep, freq, octaves, persistance)
						else:
							neighbour.setmoisture(moisturestart+np.random.random()*moisturestep*2-moisturestep)
						nextregions.add(neighbour)

	def settemperature(self, temperature=20.0):
		for region in self.regions:
			if region.type.value >= RegionType.LAND.value:
				region.settemperature(temperature)

	def updatetypes(self):
		for region in self.regions:
			region.updatetype()

	def toimage(self):
		from PIL import Image, ImageDraw
		image = Image.new('RGB', (self.sizex, self.sizey), (10, 12, 50))
		draw = ImageDraw.Draw(image)
		maxheight = 0
		for region in self.regions:
			maxheight = max(maxheight, region.height)
		for region in self.regions:
			region.draw(draw, self.voronoimap, image.size, maxheight)
		size = image.size
		image = np.minimum(np.asarray(image) + (np.random.random((self.sizex, self.sizey))[:,:,None] * [50,50,50]),
						   255)
		image = filters.median_filter(image, size=(5,5,1))
		image = array2RGB(image, size)
		#image.filter(ImageFilter.GaussianBlur)
		return image

	def togrid(self):
		from PIL import Image, ImageDraw
		image = Image.new('L', (self.sizex, self.sizey), 0)
		draw = ImageDraw.Draw(image)
		for region in self.regions:
			region.drawindex(draw, self.voronoimap, image.size)
		return np.asarray(image)

	def toheightmap(self):
		from PIL import Image, ImageDraw

		image = Image.new('L', (self.sizex, self.sizey), 0)
		draw = ImageDraw.Draw(image)
		maxheight = 0
		for region in self.regions:
			maxheight = max(maxheight, region.height)
		for region in self.regions:
			region.drawheight(draw, self.voronoimap, image.size, maxheight)
		size = image.size
		image = np.maximum(np.asarray(image) - (np.random.random((self.sizex, self.sizey))[:,:] * 50), 0)
		image = filters.gaussian_filter(image, sigma=(3,3))
		image = array2L(image, size)
		return image

	def tomoisturemap(self):
		image = Image.new('L', (self.sizex, self.sizey), 0)
		draw = ImageDraw.Draw(image)
		for region in self.regions:
			region.drawmoisture(draw, self.voronoimap, image.size)
		return image

def main():
	import matplotlib
	matplotlib.interactive(True)
	matplotlib.use('Qt5Agg')
	import matplotlib.pyplot as plt
	plt.ion()

	xx, yy, zz = np.mgrid[0:1:10j, 0:1:10j, -1:1:2j]
	map = VoronoiMap(50,50,xx,yy,20)
	#voronoi_plot_2d(map.voronoimap)
	#plt.show()
	#plt.pause(1)
	map = VoronoiMap(512,512,xx,yy,600,5,moisturestart=2)
	voronoi_plot_2d(map.voronoimap)
	plt.show()
	plt.pause(1)


	image = map.toimage()
	image.save("yolo.jpg", "JPEG", quality=90)

	plt.figure()
	imageArr = np.asarray(image)  # Get array back
	imgplot = plt.imshow(imageArr)
	plt.show()

	plt.pause(3)

	plt.figure()
	imageArr = np.asarray(map.toheightmap())  # Get array back
	imgplot = plt.imshow(imageArr)
	plt.show()

	plt.pause(3)

	plt.figure()
	imageArr = np.asarray(map.tomoisturemap())
	imgplot = plt.imshow(imageArr)
	plt.show()

	plt.pause(15)


if __name__ == "__main__":
	main()
