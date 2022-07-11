from math import ceil, floor, sin, cos, radians

from utility import *

class poly:
    __slots__ = ("color", "coords", "pointListRel", "angle")

    def __init__(self, coords, pointListRel = [(0,-10), (-5,-5), (0,10), (5,-5)], angle = 0):
        self.color, self.coords, self.pointListRel, self.angle = 0x000000, coords, pointListRel, angle

    def setAngle(self, newAngle):
        tempList = []
        angleDiff = self.angle - newAngle
        for point in self.pointListRel:
            value = sqrt(point[0] ** 2 + point[1] ** 2)
            angle = radians(degrees(atan2(point[1], point[0])) + angleDiff)
            xValue, yValue = cos(angle) * value, sin(angle) * value
            tempList.append((xValue, yValue))
        """
        tempList = [(cos(radians(degrees(atan2(point[1], point[0])) + angleDiff)) * sqrt(point[0] ** 2 + point[1] ** 2) , 
            sin(radians(degrees(atan2(point[1], point[0])) + angleDiff)) * sqrt(point[0] ** 2 + point[1] ** 2)) for point in self.pointListRel]
        """

        self.pointListRel = tempList
        self.angle = newAngle % 360

    def getAngle(self):
        return self.angle

    def setSize(self, size):
        self.pointListRel = [(point[0] * size, point[1] * size) for point in self.pointListRel]

    def drawCenter(self, surface, coordOffset = [0, 0]):
        pygame.draw.rect(surface, 0xFFFFFF, [self.coords[0] - coordOffset[0], self.coords[1] - coordOffset[1], 1, 1])

    def draw(self, surface, coordOffset = [0, 0]):
        offsetCoords = [self.coords[0] - coordOffset[0], self.coords[1] - coordOffset[1]]
        offsetList = [(point[0] + offsetCoords[0], point[1] + offsetCoords[1]) for point in self.pointListRel]
        pygame.draw.polygon(surface, self.color, offsetList)
        #self.drawCenter(surface,coordOffset)


class regularPoly(poly):
    __slots__ = ("radius", "corners", "angle", "cornerSegmentation")

    def __init__(self, coords, radius, corners, angle = 0):
        self.radius, self.corners, self.angle, self.cornerSegmentation = radius, corners, angle, 360 / corners

        super().__init__(coords, self.cornerPoints())

    def cornerPoints(self):
        cornerSegments = [radians(self.cornerSegmentation * corner + self.angle) for corner in range(self.corners)]
        return [(cos(cornerSegment) * self.radius, sin(cornerSegment) * self.radius)
                for cornerSegment in cornerSegments]

    def setRadius(self, newRadius):
        self.radius = newRadius
        self.pointListRel = self.cornerPoints()

    def setCorners(self, newCorners):
        self.corners = newCorners
        self.cornerSegmentation = 360 / self.corners
        self.pointListRel = self.cornerPoints()


class mouse:
    def __init__(self):
        self.x, self.y, self.w, self.d = 0, 0, 0, 0

        self.left, self.middle, self.right = False, False, False

    def getPosition(self):
        self.update()
        return self.x, self.y

    def update(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.left, self.middle, self.right = pygame.mouse.get_pressed()


class camera:
    def __init__(self, x, y, surface):
        self.surface = surface
        self.x, self.y = x, y
        self.destinationX, self.destinationY = x, y
        self.motion = vectorClass(0, 0)
        self.positionDeltaVector = vectorClass(getDistancePoints(self.x, self.y, self.destinationX, self.destinationY), 
                                            getAnglePoints(self.x, self.y, self.destinationX, self.destinationY))

    def move(self, dt):
        xChange, yChange = self.motion.getDimension()
        self.x += xChange * dt
        self.y -= yChange * dt

    def track(self, dt):
        if self.positionDeltaVector.value > 0.1:
            self.motion.transformingTurn(self.positionDeltaVector.angle, 180, 1, 1 * dt, 0, self.positionDeltaVector.value / 5, 180)
            #self.motion.transformingTurn(self.positionDeltaVector.angle, 30, 1 * dt, 1 * dt, 0, self.positionDeltaVector.value / 10, 180)
            #transformingTurn(self, newAngle, maxRate, minRate = 0, valueChangeRate = 1, minValue = 0, maxValue = None, angleRadius = 90):
        else:
            self.motion.value = 0
        self.move(dt)

    def getCoords(self):
        return self.x, self.y

    def setCoords(self, x, y):
        self.x, self.y = x, y

    def getDestination(self):
        return self.destinationX + self.surface.get_width() / 2, self.destinationY + self.surface.get_height() / 2

    def setDestination(self, x, y):
        self.destinationX, self.destinationY = x - self.surface.get_width() / 2, y - self.surface.get_height() / 2

    def setSurface(self, surface):
        self.surface = surface

    def draw(self, surface = None, coordOffset = [0, 0]):
        x, y = self.x + surface.get_width() / 2, self.y + surface.get_height() / 2
        self.positionDeltaVector.draw(x, y, surface, 1, 0xebdb34, coordOffset)
        self.motion.draw(x, y, surface, 1, 0x0000FF, coordOffset)

    def update(self, dt):
        self.positionDeltaVector.setDimension(self.destinationX - self.x , self.y - self.destinationY)
        #instant
        #self.x, self.y = self.destinationX, self.destinationY
        self.track(dt)



class ticks:
    __slots__ = ("ticksMax", "ticksCurrent", "tickSpeed", "iterations", "finished")
    
    def __init__(self, ticksMax, ticksCurrent = 0, tickSpeed = 1):
        self.ticksMax, self.ticksCurrent, self.tickSpeed, self.iterations = ticksMax, ticksCurrent, tickSpeed, 0
        self.finished = False

    # resets itself
    def tick(self):
        if self.ticksCurrent < self.ticksMax:
            self.ticksCurrent += self.tickSpeed
        else:
            self.reset()
            self.iterations += 1
            return True
        return False

    # does not
    def tock(self):
        if self.ticksCurrent < self.ticksMax:
            self.ticksCurrent += self.tickSpeed
        else:
            if not self.finished:
                self.iterations += 1
            self.finished = True
            return True
        return False

    def check(self):
        return self.finished

    def getProgress(self, inv=False):
        if self.ticksCurrent == 0:
            return 0
        if inv:
            return 1 - self.ticksCurrent / self.ticksMax
        return self.ticksCurrent / self.ticksMax

    def getIterations(self):
        return self.iterations

    def reset(self):
        self.ticksCurrent = 0
        self.finished = False


# add vectors by adding their x/yValues and setting the new dimensions
class vectorClass:
    #might make class creation faster
    __slots__ = ("value", "angle", "xValue", "yValue")

    def __init__(self, value, angle):
        self.value, self.angle = value, angle
        self.xValue, self.yValue = self.getDimension()

    def setVector(self, value, angle):
        self.__init__(value, angle)

    def getVector(self):
        self.xValue, self.yValue = self.getDimension()
        return self.value, self.angle, self.xValue, self.yValue

    # set vector angle/value via x/y coords
    def setDimension(self, xValue, yValue):
        self.xValue, self.yValue = round(xValue, 9), round(yValue, 9)
        self.value, self.angle = sqrt(self.xValue ** 2 + self.yValue ** 2), degrees(atan2(self.yValue, self.xValue))


    def getDimension(self):
        self.xValue, self.yValue = round(cos(radians(self.angle)) * self.value, 9), round(sin(radians(self.angle)) * self.value, 9)
        return self.xValue, self.yValue

    def getPointOnVector(self, distance):
        # x,y
        return cos(radians(self.angle)) * distance, sin(radians(self.angle)) * distance

    # Geradengleichung
    def getDimensionX(self, y):
        incline = self.getIncline()
        if incline != 0:
            return y / incline
        return 0

    # Geradengleichung
    def getDimensionY(self, x):
        return x * self.getIncline()

    def getIncline(self):
        if self.xValue != 0:
            return self.yValue / self.xValue
        return 0

    # returns 0-4; 0 if angle == 0 | offset "rotates" the Quadrants
    def getQuadrant(self, offset = 0, quadrants = 4):
        return ceil((self.angle - offset) % 360 / (360 / quadrants))

    # removes specified Axis value, vector length stays intact | True sets yAxis to 0
    def setAxisValue(self, Axis):
        x, y = self.getDimension()
        # self.value,self.angle = self.getVector()
        if Axis:
            if x > 0 + accuracy:
                self.setDimension(self.value, 0)
            elif x < 0 - accuracy:
                self.setDimension(-self.value, 0)
        else:
            if y > 0 + accuracy:
                self.setDimension(0, self.value)
            elif y < 0 - accuracy:
                self.setDimension(0, -self.value)

    # removes specified Axis value | True sets yAxis to 0
    def setAxis(self, Axis):
        x, y = self.getDimension()
        if Axis:
            if x > 0:
                self.setDimension(x, 0)
            elif x < 0:
                self.setDimension(-x, 0)
        else:
            if y > 0:
                self.setDimension(0, y)
            elif y < 0:
                self.setDimension(0, -y)

    def addVector(self, otherVector, multiplier = 1, dimension = None):
        ownXValue, ownYValue = self.getDimension()
        otherXValue, otherYValue = otherVector.getDimension()
        if not dimension:
            self.setDimension((ownXValue + otherXValue) * multiplier, (ownYValue + otherYValue) * multiplier)
        elif dimension == "x":
            self.setDimension((ownXValue + otherXValue) * multiplier, ownYValue)
        elif dimension == "y":
            self.setDimension(ownXValue, (ownYValue + otherYValue) * multiplier)

    def subVector(self, otherVector, multiplier = 1, dimension = None):
        ownXValue, ownYValue = self.getDimension()
        otherXValue, otherYValue = otherVector.getDimension()
        if not dimension:
            self.setDimension((ownXValue - otherXValue) * multiplier, (ownYValue - otherYValue) * multiplier)
        elif dimension == "x":
            self.setDimension((ownXValue - otherXValue) * multiplier, ownYValue)
        elif dimension == "y":
            self.setDimension(ownXValue, (ownYValue - otherYValue) * multiplier)



    # works
    def incrementalTurn(self, newAngle, rate):
        anglediff = getAngleDiff(self.angle, newAngle)

        if abs(anglediff) > rate:
            if anglediff > 0:
                self.angle -= rate
            elif anglediff < 0:
                self.angle += rate
        else:
            self.angle = newAngle
            return True
        return False

    # same as above except that maxRate gets smaller the closer angle is to newAngle | rate cant fall below minRate
    def convergingTurn(self, newAngle, maxRate = 1, minRate = 0):
        anglediff = getAngleDiff(self.angle, newAngle)
        rate = maxRate * anglediff / 180

        if abs(rate) > minRate:
            self.angle -= rate
        else:
            if abs(anglediff) > minRate:
                if anglediff > 0:
                    self.angle -= minRate
                elif anglediff < 0:
                    self.angle += minRate
            else:
                self.angle = newAngle
                return True
        return False
    #very useful
    def transformingTurn(self, newAngle, maxRate = 1, minRate = 0, valueChangeRate = 1, minValue = 0, maxValue = None,
                         angleRadius = 90, dt = 1):
        anglediff = getAngleDiff(self.angle, newAngle)
        rate = maxRate * anglediff / 180 * dt

        if abs(anglediff) > angleRadius:
            valuediff = self.value - minValue
            if valuediff > valueChangeRate:
                self.value -= valueChangeRate
            else:
                self.value = minValue
        else:
            if maxValue:
                valuediff = maxValue - self.value
                if valuediff > valueChangeRate:
                    self.value += valueChangeRate
                else:
                    self.value = maxValue
            else:
                self.value += valueChangeRate

        if abs(rate) > minRate:
            self.angle -= rate
        else:
            if abs(anglediff) > minRate:
                if anglediff > 0:
                    self.angle -= minRate
                elif anglediff < 0:
                    self.angle += minRate
            else:
                self.angle = newAngle
                return True
        return False

    def incrementalTransform(self, newAngle, valueChangeRate = 1, minValue = 0, maxValue = None, angleRadius = 90):
        anglediff = getAngleDiff(self.angle, newAngle)

        if abs(anglediff) > angleRadius:
            valuediff = self.value - minValue
            if valuediff > valueChangeRate:
                self.value -= valueChangeRate
            else:
                self.value = minValue
        else:
            if maxValue:
                valuediff = maxValue - self.value
                if valuediff > valueChangeRate:
                    self.value += valueChangeRate
                else:
                    self.value = maxValue
            else:
                self.value += valueChangeRate

    # can be used incremental if maxRate == minRate
    def convergingTransform(self, newValue, maxRate = 1, minRate = 0):
        valueDiff = newValue - self.value
        valueRate = maxRate * valueDiff / newValue

        if abs(valueRate) > minRate:
            self.value += valueRate
        else:
            if abs(valueDiff) > minRate:
                if valueDiff > 0:
                    self.value += minRate
                elif valueDiff < 0:
                    self.value -= minRate
            else:
                self.value = newValue
                return True
        return False

    def nullification(self):
        pass

    def draw(self, x, y, surface, multiplier = 1, color = 0xeb3455, coordOffset = [0, 0]):
        endx = x + cos(radians(self.angle)) * self.value * multiplier
        endy = y - sin(radians(self.angle)) * self.value * multiplier

        pygame.draw.line(surface, color, (x - coordOffset[0], y - coordOffset[1]), (floor(endx + 0.5) - coordOffset[0], floor(endy + 0.5) - coordOffset[1]))