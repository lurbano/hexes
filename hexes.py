import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as pltimg
import matplotlib.patches as patches
import os
#from svgInator import defaultPolylineStyle, mergeStyles, textifyStyle
#from svgInator import *

# references
# https://www.redblobgames.com/grids/hexagons/
# https://en.wikipedia.org/wiki/Hexagon

# https://matplotlib.org/3.3.3/tutorials/introductory/images.html

#SETTINGS
"""
imageFile = 'lofi_cali_girl_full_bw2.png'
levels = 3          #number of concentric circles
gridSpacing = 75    #size of hexes in grid
hexScale = 0.9      #scale factor to make hexes
                    #  smaller than the grid size
"""

imageFile = 'lara.png'
levels = 3          #number of concentric circles
gridSpacing = 500    #size of hexes in grid
hexScale = 0.95      #scale factor to make hexes
                    #  smaller than the grid size





###### FROM svgInator
defaultPolylineStyle = {
    "stroke": "#f00",
    "stroke-width": "0.01",
    "fill": "none"
    }

def mergeStyles(inStyle, defStyle):

    style = {}
    for i in defStyle:
        style[i] = defStyle[i]
    for i in inStyle:
        #print i, inStyle[i]
        style[i] = inStyle[i]
    #print style
    return style

def textifyStyle(style):
    '''style is entered as a dictionary'''
    txt = ""
    for i in style:
        txt += i + ":" + style[i] + ";"
    return txt
# END svgInator


class svgWriter:
    def __init__(self, width, height):
        svgHead = """ <svg version="1.1"
             xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
             width="{w}" height="{h}"> \n """
        self.txt = svgHead.format(w=width, h=height)
        self.ng = 0

    def addHexGroup(self, filename, x, y, w, h, hexagon):
        self.ng += 1
        groupId = 'g'+str(self.ng).zfill(2)

        image = """ <image x="0" y="0" width="{w}" height="{h}" transform="'''rotate(45)'''"
           xlink:href="{filename}"/> """
        image = image.format(filename=filename, w=w, h=h, x=x, y=y)

        #hexagon = hexagonTxt

        base = f'<g id="{groupId}" transform="translate({x} {y})">{image}{hexagon} </g> \n'
        self.txt += base

    def addSvgTxt(self, txt):
        self.txt += txt

    def write(self, outFile):
        #close tag
        self.txt += '</svg>'
        with open(outFile, "w") as svgFile:
            svgFile.write(self.txt)
        print(f"written to {outFile}")

class hex:
    def __init__(self, radius=10, pos=(0,0)):
        self.n_sides = 6
        self.r = radius
        self.x = pos[0]
        self.y = pos[1]
        self.rot = -np.pi/6

        self.width = 2*self.r
        self.height = self.r * 3**0.5

    def getNodes(self):
        xa = []
        ya = []
        for i in range(self.n_sides):
            angle = self.rot + i * np.pi / 3
            xa.append(self.x + self.r * np.cos(angle))
            ya.append(self.y + self.r * np.sin(angle))
        #close curve
        angle = self.rot
        #xa.append(xa[0])
        #ya.append(ya[0])
        return xa, ya

    def getNumpyArrayPts(self):
        a = np.zeros((self.n_sides+1, 2))
        xa, ya = self.getNodes()
        for i in range(self.n_sides+1):
            a[i][0] = xa[i]+78
            a[i][1] = ya[i]+95
        return a

    def getSvg(self, style={}):
        svgStyle = mergeStyles(style, defaultPolylineStyle)
        styleTxt = textifyStyle(svgStyle)
        ptxt = ''
        xa, ya = self.getNodes()
        for i in range(len(xa)):
            ptxt += f'{xa[i]},{ya[i]},'

        svgTxt = f'<polygon points="{ptxt}" style="{styleTxt}"/>'
        return svgTxt


    def patch(self, inArray): #WIP
        data = self.getNumpyArrayPts()

        poly = patches.Polygon(data, closed=True)
        print(f"data: {data}")
        #patch = patches
        #subImb = inArray[self.ymin:self.ymax,self.xmin:self.xmax, :]


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

                # Next node
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
        return x, y     # x, y, are cordinates of the centers of the hexes

    def getHexesSvg(self, style={}):
        if (self.hexes == 0):
            self.getHexes()
        txt = ''
        for h in self.hexes:
            txt += h.getSvg(style=style)
        return txt

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
        if (inArray.ndim == 2):
            a = inArray[self.ymin:self.ymax, self.xmin:self.xmax]
        elif (inArray.ndim == 3):
            a = inArray[self.ymin:self.ymax, self.xmin:self.xmax, :]
        return a

    def sliceExtent(self):
        return (self.xmin-0.5, self.xmax-0.5, self.ymax-0.5, self.ymin-0.5)


#n_sides = 6     #hexagons
#r = 10          #distance to node
#rot = np.pi/6      #pi/6 = point up


img = pltimg.imread(imageFile)
print(f'image shape: {img.shape}')
cy = img.shape[0]/2
cx = img.shape[1]/2
print(cx, cy)

grid = hexGrid(levels=levels, pos=(cx, cy), gridSpacing=gridSpacing, hexScale=hexScale)

smallGrid = hexGrid(levels=levels, pos=(cx, cy), gridSpacing=gridSpacing, hexScale=hexScale)
smallHexGroup = '<g id="smallHexes">'
for h in smallGrid.hexes:
    h.x -= (cx-h.height)/2
    h.y -= (cy-h.width)/2
    smallHexGroup += h.getSvg(style={"stroke":"#00f"})
smallHexGroup += '</g>'

outdir = "output"

os.makedirs("output", exist_ok=True)

svgOut = svgWriter(width=cx, height=cy)

for i in range(len(grid.hexes)):
    h = grid.hexes[i]
    b = grid.boxes[i]

    tile = b.sliceImg(img)

    plt.imshow(tile, cmap="gray", extent=b.sliceExtent())

    xp, yp = h.getNodes()
    plt.plot(xp, yp)

    outfile = f'{outdir}/test{str(i).zfill(2)}.png'
    pltimg.imsave(outfile, tile, cmap='gray')

    #(tx, ty, tc) = tile.shape
    tx = tile.shape[0]
    ty = tile.shape[1]

    xbig = h.x - cx/2
    ybig = h.y - cy/2

    h.x = int(ty/2)
    h.y = int(tx/2)


    imgFile = outfile.replace(outdir+'/', "")

    outSvg = outfile.replace(".png", ".svg")
    # with open(outSvg, "w") as svgFile:
    #     svgFile.write(svgText.format(filename=imgFile, w=ty, h=tx, hexagon=h.getSvg()))

    smallSvg = svgWriter(ty, tx)
    smallSvg.addHexGroup(filename=imgFile, x=0, y=0, w=ty, h=tx, hexagon=h.getSvg())
    smallSvg.write(outSvg)

    svgOut.addHexGroup(imgFile, xbig, ybig, ty, tx, h.getSvg())


fullGrid = hexGrid(levels=levels, pos=(cx, cy), gridSpacing=gridSpacing, hexScale=1.0)
# fullSvgs = fullGrid.getHexesSvg(style={"stroke":"#00f"})
# fullHexGroup = f'<g id="fullGrid">{fullSvgs}</g>'

fullHexGroup = '<g id="fullHexes">'
for h in fullGrid.hexes:
    h.x -= (cx-h.height*hexScale)/2
    h.y -= (cy-h.width*hexScale)/2
    fullHexGroup += h.getSvg(style={"stroke":"#00f"})
fullHexGroup += '</g>'




svgOut.addSvgTxt(fullHexGroup)
svgOut.addSvgTxt(smallHexGroup)

bigSvgFile = f"{outdir}/bigHex.svg"
svgOut.write(bigSvgFile)

plt.axis("off")
plt.show()
