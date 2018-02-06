import matplotlib
import numpy as np
import noise
from scipy.interpolate import griddata
import scipy
import scipy.ndimage

def initheightmap(sizex, sizey, sizez, xx, yy, zz):
    points = np.empty((sizex*sizey*sizez, 4))
    if xx is None or yy is None or zz is None:
        xx, yy, zz = np.mgrid[-1:1:sizex * 1j, -1:1:sizey * 1j, -1:1:sizez * 1j]
    xmin, xmax, ymin, ymax, zmin, zmax = xx.min(), xx.max(), yy.min(), yy.max(), zz.min(), zz.max()
    xl, yl, zl = xmax - xmin, ymax - ymin, zmax - zmin
    index = 0
    for i in np.mgrid[0:1:sizex * 1j]:
        for j in np.mgrid[0:1:sizey * 1j]:
            for k in np.mgrid[0:1:sizez * 1j]:
                points[index] = np.array((xmin + i * xl, ymin + j * yl, zmin + k * zl, 0))
                index = index + 1
    return xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax, points

def smooth3D(points, sizex, sizey, sizez, xmin, xmax, ymin, ymax, zmin, zmax):
    XX, YY, ZZ = np.mgrid[xmin:xmax:sizex * 1j, ymin:ymax:sizey * 1j, zmin:zmax:sizez*1j]
    result = griddata(points[:,:3], points[:,3], (XX,YY,ZZ), fill_value=0, method="nearest")
    result = scipy.ndimage.gaussian_filter(result, [2,2,2], mode="constant")
    index = 0
    for i in range(0, sizex):
        for j in range(0, sizey):
            for k in range(0, sizez):
                points[index] = np.array((XX[i,j,k], YY[i,j,k], ZZ[i,j,k], result[i,j,k]))
                index = index + 1
    return points


def heightmap1(sizex, sizey, sizez, xx = None, yy = None, zz=None, smooth=True,
               octaves=1, persistance=0.5,lacunarity=2.0, repeat=1024, base=0.0, freq=4.5):
    xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax, points = initheightmap(sizex, sizey, sizez, xx, yy, zz)
    index = 0
    octaves = max(1, int(octaves))
    base = int(base)
    for i in np.mgrid[0:1:sizex*1j]:
        for j in np.mgrid[0:1:sizey*1j]:
            for k in np.mgrid[0:1:sizez*1j]:
                points[index][3] = noise.pnoise3(freq*i, freq*j, freq*k,
                                                 octaves, persistance, lacunarity,
                                                 repeat, repeat, repeat, base)
                index = index + 1
    if smooth:
        smooth3D(points,sizex,sizey,sizez,xmin,xmax,ymin,ymax,zmin,zmax)
    if abs(zmin-zmax) < 0.001:
        result = griddata(points[:,:2], points[:,3], (xx,yy), method="cubic")
    else:
        result = griddata(points[:,:3], points[:,3], (xx,yy,zz), method="linear")
    return result


def filter(sizex = 11, mode='hamming', arg=32):
    if mode == 'hamming':
        return np.hamming(sizex)
    else:
        return np.kaiser(sizex, arg)


def getrandomfunc(randomtype=0):
    if randomtype == 1:
        return np.random.wald
    elif randomtype == 2:
        return np.random.vonmises
    elif randomtype == 3:
        return np.random.uniform
    elif randomtype == 4:
        return np.random.poisson
    elif randomtype == 5:
        return np.random.pareto
    elif randomtype == 6:
        return np.random.exponential
    elif randomtype == 7:
        return np.random.normal
    return np.random.gamma


def heightmap2(sizex, sizey, sizez, xx = None, yy = None, zz=None, smooth=True,
               freq=5.0, mean=0.5, scale=0.6, randomtype=0):
    xx, yy, zz, xmin, xmax, ymin, ymax, zmin, zmax, points = initheightmap(sizex, sizey, sizez, xx, yy, zz)
    randomfunc = getrandomfunc(10)

    def func(x, y, z):
        value = np.cos(x*(randomfunc(mean, scale)*freq)+randomfunc(mean, scale)*0.5) *\
                    np.sin(y*(randomfunc(mean, scale)*freq)+randomfunc(mean, scale)*0.5) *\
                    max(-1,min(1, np.tan(z*(randomfunc(mean, scale)*freq)+randomfunc(mean, scale)*0.5))) * 2
        if abs(value) < 0.4:
            value = value * value * 0.1 * np.sign(value)
        elif abs(value) > 1.0:
            value = value * value * np.sign(value)
        return value

    index = 0
    for i in np.mgrid[0:1:sizex*1j]:
        for j in np.mgrid[0:1:sizey*1j]:
            for k in np.mgrid[0:1:sizez*1j]:
                points[index][3] = func(i, j, k)
                index = index + 1

    randvalue = np.random.uniform(0, 1, len(points)) * 0.4
    randvalue = randvalue + np.random.uniform(0, 1, len(points)) * 0.1
    randvalue = randvalue - np.random.uniform(0, 1, len(points)) * 0.2
    points[:,3] = points[:,3] + randvalue
    if smooth:
        smooth3D(points, sizex, sizey, sizez, xmin, xmax, ymin, ymax, zmin, zmax)
    if abs(zmin-zmax) < 0.001:
        result = griddata(points[:,:2], points[:,3], (xx,yy), method="cubic")
    else:
        result = griddata(points[:,:3], points[:,3], (xx,yy,zz), method="linear")
    return result

def heightmap3(sizex, sizey, sizez, xx = None, yy = None, zz=None, smooth=True,
               octaves=1, persistance=0.5,lacunarity=2.0, repeat=1024, base=0.0, freq=4.5,
               freq2=5.0, mean=0.5, scale=0.8, randomtype=0):
    return (heightmap1(sizex, sizey, sizez, xx, yy, zz, smooth, octaves, persistance, lacunarity,
                       repeat, base, freq) +
            heightmap2(sizex, sizey, sizez, xx, yy, zz, smooth, freq2, mean, scale)) * 0.5

def main():
    matplotlib.interactive(True)
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.ion()

    while True:
        xx, yy, zz = np.mgrid[-10:10:100j, -10:10:100j, -1:1:2j]
        data = heightmap1(50,50,2, xx, yy, zz, octaves=0.5+np.random.random_sample()*5,
                          lacunarity=0.5+np.random.random_sample()*5)
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap1(50,50,2, xx, yy, zz, smooth=True, octaves=0.5+np.random.random_sample()*5,
                          lacunarity=0.5+np.random.random_sample()*5)
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap2(50,50,2, xx, yy, zz, True)
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap2(60, 60, 2, xx, yy, zz, True)
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap3(60, 60, 2, xx, yy, zz, True)
        imgplot = plt.imshow(data[:,:,0])
        plt.clim(data.min(), data.max())
        plt.pause(1)


if __name__ == "__main__":
    main()
