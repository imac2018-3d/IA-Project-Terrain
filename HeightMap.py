import matplotlib
import matplotlib.image as mpimg
import numpy as np
import noise
from scipy.interpolate import griddata
import scipy
import scipy.ndimage


def heightmap1(sizex, sizey, xx = None, yy = None):
    points = np.empty((sizex*sizey,3))
    id = 0
    if xx is None or yy is None:
        xx, yy = np.mgrid[-1:1:sizex * 1j, -1:1:sizey * 1j]
    xmin = xx.min()
    xmax = xx.max()
    ymin = yy.min()
    ymax = yy.max()
    for i in np.mgrid[0:1:sizex*1j]:
        for j in np.mgrid[0:1:sizey*1j]:
            points[id] = np.array((xmin + i*(xmax-xmin), ymin+j*(ymax-ymin), noise.pnoise2(4.5*i, 4.5*j)))
            id = id + 1
    print (points)
    result = griddata(points[:,:2], points[:,2], (xx, yy), fill_value=0, method="cubic")
    print (result)
    result = (result - result.min()) / (result.max() - result.min())
    return result

def filter(sizex = 11, mode='hamming', arg=32):
    if mode == 'hamming':
        return np.hamming(sizex)
    else:
        return np.kaiser(sizex, arg)


def heightmap2(sizex, sizey, smooth=True, xx = None, yy = None):
    points = np.empty((sizex*sizey,3))
    id = 0
    if xx is None or yy is None:
        xx, yy = np.mgrid[-1:1:sizex * 1j, -1:1:sizey * 1j]
    xmin = xx.min()
    xmax = xx.max()*1.1
    ymin = yy.min()
    ymax = yy.max()*1.1
    def func(x, y):
        result = np.cos(x*(2+np.random.gamma(0.4, 0.23))+np.random.gamma(0.5, 0.23)*0.5) *\
                 np.sin(y*(2+np.random.gamma(0.4, 0.23))+np.random.gamma(0.5, 0.23)*0.5)
        if result < 0.5:
            result = result * result * 0.1
        elif result > 0.8:
            result = result * 1.5
        return result
    for i in np.mgrid[0:1:sizex*1j]:
        for j in np.mgrid[0:1:sizey*1j]:
            points[id] = np.array((xmin + i*(xmax-xmin), ymin+j*(ymax-ymin), func(4.5*i, 4.5*j)))
            id = id + 1

    random = np.random.gamma(1, 1, len(points)) * 0.3
    random = random + np.random.gamma(1, 1, len(points)) * 0.05
    random = random - np.random.gamma(1, 1, len(points)) * 0.15
    data = points[:,2] + random
    XX, YY = np.mgrid[-10:10:sizex * 1j, -10:10:sizey * 1j]
    result = griddata(points[:len(data),:2], data, (XX,YY))
    if smooth:
        result = scipy.ndimage.gaussian_filter(result, [2,2], mode="constant")
    points = np.empty((sizex,sizey,2))
    for i in range(0, sizex):
        for j in range(0, sizey):
            points[i,j] = np.array((XX[i,j], YY[i,j]))
    result = griddata(points.reshape(-1,2), result.reshape(-1), (xx,yy), method="cubic")
    result = (result - result.min()) / (result.max() - result.min())
    return result

def heightmap3(sizex, sizey, smooth=True, xx = None, yy = None):
    return (heightmap1(sizex, sizey,xx,yy) + heightmap2(sizex, sizey, smooth,xx,yy)) * 0.5

def main():
    matplotlib.interactive(True)
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    plt.ion()

    while True:
        xx, yy = np.mgrid[-10:10:100j, -10:10:100j]
        data = heightmap1(250,250, xx, yy)
        imgplot = plt.imshow(data)
        plt.clim(data.min(), data.max())
        plt.pause(8)
        data = heightmap2(60,60, True, xx, yy)
        imgplot = plt.imshow(data)
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap2(60, 60, False, xx, yy)
        imgplot = plt.imshow(data)
        plt.clim(data.min(), data.max())
        plt.pause(1)
        data = heightmap3(60, 60, True, xx, yy)
        imgplot = plt.imshow(data)
        plt.clim(data.min(), data.max())
        plt.pause(1)

if __name__ == "__main__":
    main()
    pass
