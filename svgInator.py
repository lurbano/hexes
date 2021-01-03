from vpython import *

defaultTextStyle = {
    "text-anchor": "middle",
    "stroke": "none",
    "fill":"#000",
    "font-family": "Calibri",
    "font-size": "12pt"
    }

defaultPathStyle = {
    "stroke": "#000",
    "stroke-width": "1pt",
    "fill": "#fac"
    }
defaultPolylineStyle = {
    "stroke": "#000",
    "stroke-width": "1pt",
    "fill": "none"
    }

defaultRectStyle = {
    "stroke-width": "1pt",
    "stroke":"#000",
    "fill":"none"
    }

defaultLineStyle = {
        "stroke": "#000",
        "stroke-width": "1pt",
        "fill": "none"
    }

defaultCircleStyle = {
        "stroke-width": "1pt",
        "stroke":"#f00",
        "fill":"none"
    }



class svgShape:

    def write(self, filename):
        self.getText()
        fh = open(filename, "a")
        fh.write(self.txt)
        fh.close()

    def getText(self):
        styleTxt = textifyStyle(self.style)
        self.txt = '<circle cx="{x}{units}" cy="{y}{units}" r="{r}{units}" style="{style}"/>\n'.format(
            x=self.pos.x, y=self.pos.y, r=self.radius, style=styleTxt, units=self.units)
        return self.txt

class svgCircle(svgShape):
    def __init__(self, pos = vector(0,0,0), radius=10., style={}, units="mm"):
        self.style = mergeStyles(style, defaultCircleStyle) #
        self.pos = pos
        self.radius = radius
        self.units = units

    def getText(self):
        styleTxt = textifyStyle(self.style)
        self.txt = '<circle cx="{x}{units}" cy="{y}{units}" r="{r}{units}" style="{style}"/>\n'.format(
            x=self.pos.x, y=self.pos.y, r=self.radius, style=styleTxt, units=self.units)
        return self.txt

class svgLine(svgShape):
    '''pos is a list ([]) of two vector points'''

    def __init__(self, pos, style={}, units="mm"):
        self.style = mergeStyles(style, defaultLineStyle) #
        self.pos = pos          #
        self.units = units      #

    def getText(self):
        styleTxt = textifyStyle(self.style)
        self.txt = '<line x1="{x1}{units}"  y1="{y1}{units}" x2="{x2}{units}"   y2="{y2}{units}" style="{style}"/>'.format(
                    x1=self.pos[0].x, y1=self.pos[0].y, x2=self.pos[1].x, y2=self.pos[1].y, units=self.units, style=styleTxt)

        return self.txt


class svgRect(svgShape):
    '''pos is a list ([]) of two vector points'''

    def __init__(self, pos = vector(0,0,0), dim=vector(10,10,0), transform="", style={}, units="mm"):
        self.style = mergeStyles(style, defaultRectStyle)
        self.pos = pos
        self.units = units
        self.dim = dim
        self.transform = transform

    def getText(self):
        styleTxt = textifyStyle(self.style)
        self.txt = '<rect x="{x}{units}" y="{y}{units}" height="{h}{units}" width="{w}{units}" transform="{t}" style="{style}"/>\n'.format(
            x=self.pos.x, y=self.pos.y, h=self.dim.y, w=self.dim.x, style=styleTxt, units=self.units, t=self.transform)
        return self.txt


class svgPolyline(svgShape):
    def __init__(self, pos, style={}, units="mm"):
        self.style = mergeStyles(style, defaultPolylineStyle)
        self.pos = pos
        self.units = units
        self.ptxt = ""
        for i in pos:
            if (self.units == "mm"):
                i = i * mm_to_px(1)
            self.ptxt += '{x},{y},'.format(x=i.x, y=i.y)
        self.ptxt = self.ptxt[:-1]
        self.units = units


    def getText(self):
        styleTxt = textifyStyle(self.style)
        self.txt = '<polyline points="{pts}" style="{style}"/>'.format(
            pts=self.ptxt, style=styleTxt)
        return self.txt

# class svgPolyHex(svgPolyline):
#     def __init__(self, pos = vector(0,0,0), radius=10., rotation=0., style={}, units="mm"):
#         self.style = mergeStyles(style, defaultPolylineStyle) #
#         self.pos = pos
#         self.radius = radius
#         self.units = units
#
#         self.pts = []
#         for i in range(n_sides):
#             angle = rotation + i * pi / 3
#             x = r * np.cos(angle)
#             y = r * np.sin(angle)
#             self.pts.append(vector(x,y,0))
#         #close curve
#         angle = rotation
#         x = r * np.cos(angle)
#         y = r * np.sin(angle)
#         self.pts.append(vector(x,y,0))
            #svg.vectorArray_to_path(pts)

class svgText(svgShape):
    def __init__(self, text="Hello", pos= vector(0,0,0), style={}, transform="", units="mm"):
        self.style = mergeStyles(style, defaultTextStyle)
        self.text = text
        self.pos = pos
        self.units = units
        self.transform = transform

    def getText(self):
        styleTxt = textifyStyle(self.style)
        self.txt = '<text transform="{transform}" x="{x}{units}" y="{y}{units}" style="{style}">{text}</text>\n'.format(
            transform=self.transform, x=self.pos.x, y=self.pos.y, text=self.text, style=styleTxt, units=self.units)




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

def restyle_vpython(b):
    style = {}
    c = vector(b.color)*255
    r = int(c.x)
    g = int(c.y)
    b = int(c.z)
    style["fill"] = 'rgb({r},{g},{b}'.format(r=r, g=g, b=b)

    return style



class svgInator:
    '''default units are mm'''

    def __init__(self, filename="test.svg", width=100, height=100, units="mm", axesZero="topLeft"):
        '''axesZero can be "bottomLeft" or "topLeft". '''
        self.filename = filename
        self.width = width
        self.height = height
        self.units = units
        self.axesZero = axesZero
        self.defaults()
        self.open = '<svg xmlns="http://www.w3.org/2000/svg" '
        self.open += 'xmlns:xlink="http://www.w3.org/1999/xlink" '
        self.open += 'width="{w}{units}" height="{h}{units}" '.format(
            w=self.width, h=self.height, units=self.units)
        self.open += 'viewbox="0 0 {w} {h}" '.format(
            w=self.width, h=self.height)
        self.open += '>\n'

        self.txt = ''
        self.txt += self.open

        #initialize output file
        fh = open(self.filename, "w")
        fh.close()

        #write headers to svg file
        self.writeThis()

    def writeThis(self):
        fh = open(self.filename, "a")
        fh.write(self.txt)
        fh.close()
        self.txt = ""

    def close(self):
        self.txt = '\n</svg>'
        self.writeThis()
        print("Output to: ", self.filename)


    def reposition(self, v):
        if self.axesZero == "bottomLeft":
            v.y = self.height - v.y
        return v

    def vertical_center_text(self, pos, style):
        #print style
        fontSize = style["font-size"][:-2]
        #print "font-size: ", fontSize
        #convert pt to mm

        p=pos*1.0

        adjustment = pt_to_mm(fontSize) / 2.9
        if self.axesZero=="topLeft":
            p.y = pos.y + adjustment
        elif self.axesZero=="bottomLeft":
            p.y = pos.y - adjustment
        return p

    def textify_style(self, style):
        '''style is entered as a dictionary'''
        txt = ""
        for i in style:
            txt += i + ":" + style[i] + ";"
        return txt

    def restyle(self, inStyle, defStyle):
        if inStyle == None:
            return defStyle
        else:
            style = {}
            for i in defStyle:
                style[i] = defStyle[i]
            for i in inStyle:
                #print i, inStyle[i]
                style[i] = inStyle[i]
            #print style
            return style

    def circle(self, pos = vector(0,0,0), radius=10., style={}):
        npos = self.reposition(pos)
        circ = svgCircle(npos, radius, style, units=self.units)
        circ.write(self.filename)

    def line(self, pos, style={}):
        ln = svgLine(pos=pos,  style=style, units=self.units)
        ln.write(self.filename)

    def rect(self, pos = vector(0,0,0), dim=vector(10,10,0), transform="", style={}):
        pos = self.reposition(pos)
        rect = svgRect(pos, dim, transform, style)
        rect.write(self.filename)

    def polyline(self, pos, style={}):
        poly = svgPolyline(pos, style)
        poly.write(self.filename)

    def regularPolygon(self, pos=vector(0,0,0), radius=10.0, rotation=0.0, n_sides=6, style={}):
        pts = []
        for i in range(n_sides):
            angle = rotation + i * pi / 3
            x = radius * cos(angle)
            y = radius * sin(angle)
            pts.append(vector(x,y,0))
        #close curve
        angle = rotation
        x = radius * cos(angle)
        y = radius * sin(angle)
        pts.append(vector(x,y,0))
        poly = svgPolyline(pts, style)
        poly.write(self.filename)

    def text(self, text="Hello", pos= vector(0,0,0), style={}, rotation=0.0):

        npos = self.reposition(pos)

        style = mergeStyles(style, defaultTextStyle)
        npos = self.vertical_center_text(pos=npos, style=style)

        # rotation
        transform = ""
        if rotation != 0.0:
            x = mm_to_px(npos.x)
            y = mm_to_px(npos.y)
            transform = "rotate({rotation},{x},{y})".format(rotation=rotation, x=x, y=y)

        txt = svgText(text, npos, style, units=self.units, transform=transform)
        txt.write(self.filename)


    # write vpython circle
    def writeSphere(self, circ, style={}):
        self.circle(circ.pos, circ.radius, style=style)

    # vpython box
    def writeBox(self, b, style={}):
        rotate_angle = degrees(vector(1,0,0).diff_angle(b.axis))
        transform = "rotate({r} {x} {y})".format(r=rotate_angle, x=mm_to_px(b.pos.x), y=mm_to_px(b.pos.y))
        vStyle = restyle_vpython(b)
        #print vStyle
        self.rect(b.pos-b.size/2.0, b.size, transform, style=vStyle)



    def path(self, pathData, style={}):
        style = self.restyle(style, self.defaultPathStyle)
        style = self.textify_style(style)
        self.txt += '<path d="{pathData}" style="{style}" />\n'.format(
            pathData=pathData, style=style)

        self.writeThis()

    def vectorArray_to_path(self, vectorArray, units="mm", style={}):
        pt = self.reposition(vector(vectorArray[0]))
        txt = "M{x},{y}\n".format(x=mm_to_px(pt.x), y=mm_to_px(pt.y))
        #print txt
        for i in range(1, len(vectorArray)):
            pt = self.reposition(vector(vectorArray[i]))
            if units == "mm":
                pt = vector(mm_to_px(pt.x), mm_to_px(pt.y),0)
            txt += "L{x},{y}\n".format(x=pt.x,y=pt.y)
        self.path(txt, style=style)
        #print txt

    # write vpython curve
    def writeCurve(self, inCurve, units="mm", style={}):
        #print "Hi: in writeCurve"
        #print inCurve.pos
        self.vectorArray_to_path(inCurve.pos, style=style)


    def element_circle(self, element_symbol = "H", radius = 10., pos=vector(0,0,0), textStyle = {}, circleStyle = {}):
        #make viewbox
##        self.txt += '<svg viewBox="{x} {y} {w} {h}" width="{w}{units}" height="{h}{units}"\n'.format(
##            x=pos.x, y=pos.y, w=dim.x, h=dim.y, units=self.units)
        self.circle(pos=pos, radius=radius, style=circleStyle)
        self.text(text=element_symbol, pos=pos, style=textStyle)

    def openGroup(self):
        self.txt += '<g>'
        self.writeThis()

    def closeGroup(self):
        self.txt += '</g>'
        self.writeThis()

    def openSVG(self):
        self.txt += '<SVG>'
        self.writeThis()

    def closeSVG(self):
        self.txt += '</>'
        self.writeThis()


    def write(self, filename = "test.svg"):
        self.txt += self.close
        fh = open(filename, "w")
        fh.write(self.txt)
        fh.close()
        print( "done")

    def defaults(self):

        self.defaultPathStyle = {
            "stroke": "#000",
            "stroke-width": "1pt",
            "fill": "#fac"
            }
        self.defaultPolylineStyle = {
            "stroke": "#000",
            "stroke-width": "1pt",
            "fill": "none"
            }


def pt_to_mm(pt):
    return float(pt)*0.3527777

def mm_to_px(mm):
    return float(mm)*3.543307
