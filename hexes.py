import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as pltimg

# references
# https://www.redblobgames.com/grids/hexagons/
# https://en.wikipedia.org/wiki/Hexagon

# https://matplotlib.org/3.3.3/tutorials/introductory/images.html

class hex:
    def __init__(self, radius=10, pos=(0,0)):
        self.n_sides = 6
        self.r = radius
        self.x = pos[0]
        self.y = pos[1]
        self.rot = np.pi/6

        self.width = 2*self.r
        self.height = self.r * 3**0.5
        #self.side = self.r


    def getNodes(self):
        xa = []
        ya = []
        for i in range(n_sides):
            angle = self.rot + i * pi / 3
            xa.append(self.x + self.r * np.cos(angle))
            ya.append(self.y + self.r * np.sin(angle))
        #close curve
        angle = rot
        xa.append(xa[0])
        ya.append(ya[0])
        return xa, ya

class hexGrid:
    def __init__(self, levels=2, gridSpacing=10., hexScale=1.0, pos=(0,0)):
        self.n_sides = 6
        self.gridR = gridSpacing
        self.hexR = gridSpacing * hexScale
        self.hexScale = hexScale
        self.hexSide = self.gridR * 3**0.5
        self.levels = levels
        # center point
        self.xc = pos[0]
        self.yc = pos[1]

        self.sideAngle = 2 * np.pi / self.n_sides

        self.hexes = []
        self.boxes = []
        self.getHexes()


    def getHexes(self):
        x = []
        y = []
        self.hexes.append( hex(pos=(0,0), radius=self.hexR))
        for i in range(1, self.levels):
            # get corner hexes
            d = self.hexSide * i
            for j in range(self.n_sides):
                angle = self.sideAngle * j
                xc = d * np.cos(angle)
                yc = d * np.sin(angle)

                xn = d * np.cos(angle + self.sideAngle)
                yn = d * np.sin(angle + self.sideAngle)

                x.append(xc)
                y.append(yc)
                self.hexes.append( hex(pos=(xc, yc), radius=self.hexR))
                for k in range(i-1):
                    #print(f'k={k}')
                    xm = (k+1)*(1/(i)) * (xn-xc) + xc
                    ym = (k+1)*(1/(i)) * (yn-yc) + yc
                    x.append(xm)
                    y.append(ym)
                    self.hexes.append( hex(pos=(xm, ym), radius=self.hexR))

        self.translateHexes(self.xc, self.yc)
        return x, y

    def translateHexes(self, x, y):
        for h in self.hexes:
            h.x += x
            h.y += y
        self.getBounds()

    def getBounds(self):
        for h in self.hexes:
            xa, ya = h.getNodes()
            xmin = np.min(xa)
            xmax = np.max(xa)
            ymin = np.min(ya)
            ymax = np.max(ya)
            self.boxes.append(boundingBox(xmin, xmax, ymin, ymax))

class boundingBox:
    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = int(np.floor(xmin))
        self.xmax = int(np.ceil(xmax))
        self.ymin = int(np.floor(ymin))
        self.ymax = int(np.ceil(ymax))

    def sliceImg(self, inArray):
        return inArray[self.ymin:self.ymax,self.xmin:self.xmax, :]

    def sliceExtent(self):
        return (self.xmin-0.5, self.xmax-0.5, self.ymax-0.5, self.ymin-0.5)



pi = np.pi

n_sides = 6     #hexagons
r = 10          #distance to node
rot = pi/6      #pi/6 = point up


img = pltimg.imread('c-14-final.png')
print(f'image shape: {img.shape}')
cy = img.shape[0]/2
cx = img.shape[1]/2
print(cx, cy)

grid = hexGrid(levels=4, pos=(cx, cy), gridSpacing=20, hexScale=0.9)

#img = img[50:100, 50:200, :]

#plt.imshow(img)



for b in grid.boxes:
    #print(b.sliceImg(img))
    plt.imshow(b.sliceImg(img), extent=b.sliceExtent())

for h in grid.hexes:
    xp, yp = h.getNodes()
    plt.plot(xp, yp)
plt.show()

# svg.close()
