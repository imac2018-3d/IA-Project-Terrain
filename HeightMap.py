import matplotlib
import numpy as np
import noise
import scipy
import scipy.interpolate
import scipy.ndimage

def griddata(points, xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax):
    XX = ((points.shape[0]-1) * ((xx - xmin) / (xmax - xmin))).astype(int)
    if abs(ymax - ymin) > 0.0001:
        YY = ((points.shape[1] - 1) * ((yy - ymin) / (ymax - ymin))).astype(int)
    else:
        YY = np.zeros(yy.size)
    if abs(zmax - zmin) > 0.0001:
        ZZ = ((points.shape[2]-1) * ((zz - zmin) / (zmax - zmin))).astype(int)
    else:
        ZZ = np.zeros((zz.size), dtype=int)
    result = points[XX,YY,ZZ]
    return result

def initheightmap(sizex, sizey, sizez, xx, yy, zz):
    points = np.empty((sizex,sizey,sizez))
    if xx is None or yy is None or zz is None:
        xx, yy, zz = np.mgrid[0:1:sizex * 1j, 0:1:sizey * 1j, 0:1:sizez * 1j]
        xx = xx.flatten()
        yy = yy.flatten()
        zz = zz.flatten()
    xmin, xmax, ymin, ymax, zmin, zmax = xx.min(), xx.max(), yy.min(), yy.max(), zz.min(), zz.max()

    """
    for i in range(sizex):
        for j in range(sizey):
            for k in  range(sizez):
                points[i][j][k] = 0
    """
    return xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax, points

def smooth3D(points):
    result = scipy.ndimage.gaussian_filter(points, [3,3,2], mode="constant")
    return result


def heightmap1(sizex, sizey, sizez, xx = None, yy = None, zz=None, smooth=True,
               octaves=1, persistance=0.5,lacunarity=2.0, repeat=1024, base=0.0, freq=4.5):
    xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax, points = initheightmap(sizex, sizey, sizez, xx, yy, zz)
    octaves = max(1, int(octaves))
    base = int(base)
    coefX, coefY, coefZ = 1/sizex, 1/sizey, 1/sizez
    for i in range(points.shape[0]):
        for j in range(points.shape[1]):
            for k in range(points.shape[2]):
                value = noise.pnoise3(freq*(i*coefX-0.5), freq*(j*coefY-0.5), freq*(k*coefZ-0.5),
                                     octaves, persistance, lacunarity,
                                     repeat, repeat, repeat, base)
                points[i][j][k] = value
    if smooth:
        smooth3D(points)
    return griddata(points, xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax)


def filter(sizex = 11, mode='hamming', arg=32):
    if mode == 'hamming':
        return np.hamming(sizex)
    else:
        return np.kaiser(sizex, arg)

def getrandomfunc(randomtype=0, seed=-1):
    if seed < 0:
        np.random.seed(None)
    else:
        np.random.seed(seed)

    if randomtype == 1:
        def wald(mean, scale, shape=1):
            return np.random.wald(mean, scale, shape)
        return wald
    elif randomtype == 2:
        def vonmises(mean, scale, shape=1):
            return np.random.vonmises(mean, scale, shape)
        return vonmises
    elif randomtype == 3:
        def uniform(mean, scale, shape=1):
            return np.random.uniform(mean-0.5*scale, mean+0.5*scale, shape)
        return uniform
    elif randomtype == 4:
        def poisson(mean, scale, shape=1):
            return np.random.poisson((mean+0.5) * 100, shape) / 100 - 0.5
        return poisson
    elif randomtype == 5:
        def rayleigh(mean, scale, shape=1):
            rayleighCoef = np.sqrt(2 / np.pi)
            modevalue = rayleighCoef * (mean+0.5) * 100
            return np.random.rayleigh(modevalue, shape) / 100 - 0.5
        return rayleigh
    elif randomtype == 6:
        def normal(mean, scale, shape=1):
            return np.random.normal(mean * 100, scale, shape) / 100
        return normal
    elif randomtype == 7:
        def laplace(mean, scale, shape=1):
            return np.random.laplace(mean * 100, scale, shape) / 100
        return laplace

    def gamma(mean, scale, shape=1):
        return np.random.gamma((mean+0.5) * 100 / scale, scale, shape) / 100 - 0.5
    return gamma


def heightmap2(sizex, sizey, sizez, xx = None, yy = None, zz=None, smooth=True,
               freq=5.0, mean=0., scale=5., seed=-1, randomtype=0):
    xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax, points = initheightmap(sizex, sizey, sizez, xx, yy, zz)
    randomfunc = getrandomfunc(int(randomtype), seed)

    freqx = freq*(1+randomfunc(0., scale)+randomfunc(0., scale))
    freqy = freq*(1+randomfunc(0., scale)+randomfunc(0., scale))
    freqz = freq*(1+randomfunc(0., scale)+randomfunc(0., scale))

    def func(x, y, z):
        i = x*freqx
        j = y*freqy
        k = z*freqz+randomfunc(mean, scale) * 0.2
        value = (np.cos(i) + np.sin(j) + np.cos(k) * np.sin(k)) / 3
        if abs(value) < 0.4:
            value = value * value * np.sign(value)
        return value

    coefX, coefY, coefZ = 1/sizex, 1/sizey, 1/sizez
    for i in range(points.shape[0]):
        for j in range(points.shape[1]):
            for k in range(points.shape[2]):
                value = func(i*coefX-0.5, j*coefY-0.5, k*coefZ-0.5)
                points[i][j][k] = value

    randvalue = randomfunc(mean, scale, points.shape) * 0.3
    randvalue = randvalue + randomfunc(mean, scale, points.shape) * 0.1
    randvalue = randvalue - randomfunc(mean, scale, points.shape) * 0.2
    points = (points + randvalue * 0.5) / 1.5

    if smooth:
        smooth3D(points)
    return griddata(points, xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax)


def heightmap3(sizex, sizey, sizez, xx = None, yy = None, zz=None, smooth=True, coefMap1=0.5, coefMap2=0.5,
               octaves=1, persistance=0.5,lacunarity=2.0, repeat=1024, base=0.0, freq=4.5,
               freq2=5.0, mean=0.5, scale=0.8, randomtype=0, seed=0):
    return (heightmap1(sizex, sizey, sizez, xx, yy, zz, smooth, octaves, persistance, lacunarity,
                       repeat, base, freq) * coefMap1 +
            heightmap2(sizex, sizey, sizez, xx, yy, zz, smooth, freq2, mean, scale, seed, randomtype) * coefMap2)

def main():
    matplotlib.interactive(True)
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.ion()

    while True:
        xx, yy, zz = np.mgrid[-10:10:50j, -10:10:50j, -1:1:3j]
        data = heightmap1(50,50,2, xx.flatten(), yy.flatten(), zz.flatten(), octaves=0.5+np.random.random_sample()*5,
                          lacunarity=0.5+np.random.random_sample()*5)
        points = np.stack((xx.flatten(),yy.flatten(),zz.flatten()), axis=-1)
        data = scipy.interpolate.griddata(points, data, (xx,yy,zz))
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap1(50,50,2, xx.flatten(), yy.flatten(), zz.flatten(), smooth=True, octaves=0.5+np.random.random_sample()*5,
                          lacunarity=0.5+np.random.random_sample()*5)
        data = scipy.interpolate.griddata(points, data, (xx,yy,zz))
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap2(50,50,2, xx.flatten(), yy.flatten(), zz.flatten(), True, randomtype=int(np.random.random_sample()*10))
        data = scipy.interpolate.griddata(points, data, (xx,yy,zz))
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap2(60, 60, 2, xx.flatten(), yy.flatten(), zz.flatten(), True)
        data = scipy.interpolate.griddata(points, data, (xx,yy,zz))
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap3(60, 60, 2, xx.flatten(), yy.flatten(), zz.flatten(), True)
        data = scipy.interpolate.griddata(points, data, (xx,yy,zz))
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)


if __name__ == "__main__":
    main()
