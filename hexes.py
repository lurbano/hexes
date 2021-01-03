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

###### FROM svgInator
defaultPolylineStyle = {
    "stroke": "#000",
    "stroke-width": "1pt",
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

# svgHead = """<svg version="1.1"
#      baseProfile="full"
#      width="{width}" height="{height}"
#      xmlns="http://www.w3.org/2000/svg"> """
#
# svgTail = '</svg>'
#
# svgImage = '<image href="{filename}" x="{xp}" y="{yp}" height="{h}" width="{w}"/>'

svgText = """ <svg version="1.1"
     xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{w}" height="{h}">
  <image x="0" y="0" width="{w}" height="{h}" transform="'''rotate(45)'''"
     xlink:href="{filename}"/>{hexagon}
</svg> """

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

        svgTxt = f'<polyline points="{ptxt}" style="{styleTxt}"/>'
        return svgTxt


    # class svgPolyline(svgShape):
    # def __init__(self, pos, style={}, units="mm"):
    #     self.style = mergeStyles(style, defaultPolylineStyle)
    #     self.pos = pos
    #     self.units = units
    #     self.ptxt = ""
    #     for i in pos:
    #         if (self.units == "mm"):
    #             i = i * mm_to_px(1)
    #         self.ptxt += '{x},{y},'.format(x=i.x, y=i.y)
    #     self.ptxt = self.ptxt[:-1]
    #     self.units = units
    #
    #
    # def getText(self):
    #     styleTxt = textifyStyle(self.style)
    #     self.txt = '<polyline points="{pts}" style="{style}"/>'.format(
    #         pts=self.ptxt, style=styleTxt)
    #     return self.txt

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


img = pltimg.imread('lofi_cali_girl_full.jpg')
print(f'image shape: {img.shape}')
cy = img.shape[0]/2
cx = img.shape[1]/2
print(cx, cy)

grid = hexGrid(levels=3, pos=(cx, cy), gridSpacing=50, hexScale=1)

#img = img[50:100, 50:200, :]

#plt.imshow(img)

outdir = "output"

os.makedirs("output", exist_ok=True)

for i in range(len(grid.hexes)):
    h = grid.hexes[i]
    b = grid.boxes[i]

    tile = b.sliceImg(img)

    plt.imshow(tile, extent=b.sliceExtent())

    xp, yp = h.getNodes()
    # print(f"xp: {xp}")
    # print(f"yp: {yp}")
    plt.plot(xp, yp)

    outfile = f'{outdir}/test{str(i).zfill(2)}.png'
    pltimg.imsave(outfile, tile)

    (tx, ty, tc) = tile.shape
    h.x = int(ty/2)
    h.y = int(tx/2)
    outSvg = outfile.replace(".png", ".svg")
    imgFile = outfile.replace(outdir+'/', "")
    with open(outSvg, "w") as svgFile:
        svgFile.write(svgText.format(filename=imgFile, w=ty, h=tx, hexagon=h.getSvg()))



# tile = grid.boxes[-1].sliceImg(img)
# (tx, ty, tc) = tile.shape
# pltimg.imsave("test.png", tile)
#
# basicHex = grid.hexes[-1]
# basicHex.x = int(ty/2)
# basicHex.y = int(tx/2)
#
# # with open("hex.svg", "w") as svgFile:
# #     svgFile.write(svgHead.format(width=ty, height=tx))
# #     svgFile.write(svgImage.format(filename="test.png", xp=0, yp=0, w=ty, h=tx))
# #     svgFile.write(basicHex.getSvg())
# #     svgFile.write(svgTail)
#
# with open("hex2.svg", "w") as testfile:
#     testfile.write(svgtest.format(filename="test.png", w=ty, h=tx, hexagon=basicHex.getSvg()))
#
#
# print(f'basicHex: {basicHex.getSvg()}')
#
# for b in grid.boxes:
#     #print(b.sliceImg(img))
#     plt.imshow(b.sliceImg(img), extent=b.sliceExtent())
#     pltimg.imsave("test.png", b.sliceImg(img))
#
#
# for h in grid.hexes:
#     #h.patch(img)
#     # a = h.getNumpyArrayPts()
#     # # print(f"a: {a}")
#     # im = plt.imshow(img)
#     # patch = patches.Polygon(a, closed=True)
#     # im.set_clip_path(patch)
#
#     xp, yp = h.getNodes()
#     # print(f"xp: {xp}")
#     # print(f"yp: {yp}")
#     plt.plot(xp, yp)
#


# for h in grid.hexes:
#     xp, yp = h.getNodes()
#     plt.plot(xp, yp)

plt.axis("off")
plt.show()

plt.savefig("test.svg")
# svg.close()
