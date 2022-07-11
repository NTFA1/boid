import os
import math
from math import sqrt, floor, atan2, degrees
import pygame
import json
import random
import copy


def loadAssets(path):  # creates a dictionary out of all assets in the assetDirectory
    assetDictionary = {}
    assetDirectory = os.listdir(path)
    for asset in assetDirectory:
        img = pygame.image.load(path + "/" + asset)
        name = asset.split(".", 1)
        assetDictionary[name[0]] = img
    return assetDictionary


def loadAssetAnimations(path):
    assetDictionary = {}
    assetDirectory = os.listdir(path)
    for obj in assetDirectory:
        assetDictionary[obj] = {}
        behaviourDirectory = os.listdir(path + "/" + obj)
        for behaviour in behaviourDirectory:
            assetDictionary[obj][behaviour] = {}
            layerDirectory = os.listdir(path + "/" + obj + "/" + behaviour)
            for layer in layerDirectory:
                assetDictionary[obj][behaviour][layer] = {}
                assetDictionary[obj][behaviour][layer]["images"] = []
                imageDirectory = os.listdir(path + "/" + obj + "/" + behaviour + "/" + layer)
                imgPresent = False
                jsonPresent = False
                for i, image in enumerate(imageDirectory):
                    if ".png" in image:
                        imgPresent = True
                        img = pygame.image.load(
                            path + "/" + obj + "/" + behaviour + "/" + layer + "/" + image).convert_alpha()
                        # img.set_colorkey((0,0,0))
                        assetDictionary[obj][behaviour][layer]["images"].insert(i, img)
                    elif ".json" in image:
                        jsonPresent = True
                        file = open(path + "/" + obj + "/" + behaviour + "/" + layer + "/" + image)
                        fileContent = file.read()
                        animationOptions = json.loads(fileContent)
                        assetDictionary[obj][behaviour][layer]["animationOptions"] = animationOptions
                        file.close()
                    else:
                        if random.choice([0, 1]) == 0:
                            print("Whats that supposed to be:", image)
                        else:
                            print(image, "? I barely know her!")
                if not imgPresent:
                    print(obj, behaviour, layer, "is missing images")
                if not jsonPresent:
                    print(obj, behaviour, layer, "is missing animations")
    return assetDictionary

# swaps oldColor for newColor converts black to transparent
# does not work when there is already transperancy present 
def colorSwap(oldImg, oldColor, newColor):
    imgCopy = oldImg.copy()
    imgNew = pygame.Surface(imgCopy.get_size())
    imgNew.fill(newColor)
    imgCopy.set_colorkey(oldColor)
    imgNew.blit(imgCopy, (0, 0))
    #this line makes black transparent
    imgNew.set_colorkey((0,0,0))

    return imgNew


# swaps oldColor for newColor works with transperancy, bad... maybe
def colorSwapTransparent(oldImg, oldColor, newColor):
    imgCopy = oldImg.copy()
    imgNew = pygame.Surface(imgCopy.get_size())
    #replaces transparent with black
    imgNew.fill((0, 0, 0))
    imgNew.blit(imgCopy, (0, 0))
    #now use the other function
    return colorSwap(imgNew, oldColor, newColor)

#changes all colors by the chosen amount pixel by pixel veeery slow
#values can be negative -> darkens
def changeColorBy(oldImg, colorShift, colorExceptions = [()]):
    imgCopy = oldImg.copy()
    for pixelX in range(imgCopy.get_width()):
        for pixelY in range(imgCopy.get_height()):
            pixelRGB = imgCopy.get_at((pixelX, pixelY))
            if pixelRGB not in colorExceptions and pixelRGB[3] != 0:
                for i in range(3):
                    newColor = pixelRGB[i] + colorShift[i]
                    if newColor > 255:
                        newColor = 255
                    elif newColor < 0:
                        newColor = 0
                    pixelRGB[i] = newColor
                imgCopy.set_at((pixelX, pixelY), pixelRGB)
    return imgCopy

# creates a new asset in assetDicitonary which is an exact copy of the old asset, except that the colors are changed to the newValues
# colorList = [((oldColor), (newColor))] color = ( 0, 0, 0)
def createColorVariants(asset, newAsset, assetDictionary, colorList = [((), ()),((),())]):
    assetDictionary[newAsset] = assetDictionary[asset].copy()

    for animationType in assetDictionary[newAsset]:
        assetDictionary[newAsset][animationType] = assetDictionary[asset][animationType].copy()
        for layer in assetDictionary[newAsset][animationType]:
            assetDictionary[newAsset][animationType][layer] = assetDictionary[asset][animationType][layer].copy()
            assetDictionary[newAsset][animationType][layer]["images"] = assetDictionary[asset][animationType][layer]["images"].copy()
            for i, unused in enumerate(assetDictionary[newAsset][animationType][layer]["images"]):
                img = assetDictionary[newAsset][animationType][layer]["images"][i]
                for colorPair in colorList:
                    img = colorSwapTransparent(img, colorPair[0], colorPair[1])
                assetDictionary[newAsset][animationType][layer]["images"][i] = img

    return assetDictionary

# creates a new asset in assetDicitonary which is an exact copy of the old asset, except that the colors are changed by the given amount
# colorExceptions = [(colorRGB)]
def createColorVariantsShift(asset, newAsset, assetDictionary, colorShift, colorExceptions = [()]):
    assetDictionary[newAsset] = assetDictionary[asset].copy()

    for animationType in assetDictionary[newAsset]:
        assetDictionary[newAsset][animationType] = assetDictionary[asset][animationType].copy()
        for layer in assetDictionary[newAsset][animationType]:
            assetDictionary[newAsset][animationType][layer] = assetDictionary[asset][animationType][layer].copy()
            assetDictionary[newAsset][animationType][layer]["images"] = assetDictionary[asset][animationType][layer]["images"].copy()
            for i, unused in enumerate(assetDictionary[newAsset][animationType][layer]["images"]):
                img = assetDictionary[newAsset][animationType][layer]["images"][i]
                img = changeColorBy(img, colorShift, colorExceptions)
                assetDictionary[newAsset][animationType][layer]["images"][i] = img

    return assetDictionary

def createOutlinedVersion(asset, newAsset, assetDictionary):
    assetDictionary[newAsset] = assetDictionary[asset].copy()

    for animationType in assetDictionary[newAsset]:
        assetDictionary[newAsset][animationType] = assetDictionary[asset][animationType].copy()
        for layer in assetDictionary[newAsset][animationType]:
            assetDictionary[newAsset][animationType][layer] = assetDictionary[asset][animationType][layer].copy()
            assetDictionary[newAsset][animationType][layer]["images"] = assetDictionary[asset][animationType][layer]["images"].copy()
            for i, unused in enumerate(assetDictionary[newAsset][animationType][layer]["images"]):
                imgNew = pygame.Surface(imgCopy.get_size())
                self.referenceObject.surface.blit(mask_surf,(0, 1))
                pass

    return assetDictionary


def getDistance(object1, object2):
    return sqrt((object1.x - object2.x) ** 2 + (object1.y - object2.y) ** 2)


def getDistanceCenter(object1, object2):
    centerx1, centery1 = getObjectCenter(object1)
    centerx2, centery2 = getObjectCenter(object2)
    return sqrt((centerx1 - centerx2) ** 2 + (centery1 - centery2) ** 2)


def getDistancePoints(x1, y1, x2, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def getAngle(object1, object2):
    centerx1, centery1 = getObjectCenter(object1)
    centerx2, centery2 = getObjectCenter(object2)

    xdiff, ydiff = centerx1 - centerx2, centery2 - centery1

    return degrees(atan2(ydiff, xdiff))


def getAnglePoints(x1, y1, x2, y2):
    xdiff, ydiff = x1 - x2, y2 - y1
    return degrees(atan2(ydiff, xdiff))


# returns smaller angledifference of two angles
def getAngleDiff(angle1, angle2):
    anglediff = angle1 % 360 - angle2 % 360
    # calculate shortest should be somewhere between 180 and -180
    if anglediff < -180:
        anglediff = anglediff % 360
    elif anglediff > 180:
        anglediff = anglediff % -360
    return anglediff


# simple hit detection to check if two rectangle overlap not that useful on its own
def hitDetection(object1, object2):  # correct
    if object2.y + object2.d > object1.y and object2.y < object1.y + object1.d and object2.x + object2.w > object1.x and object2.x < object1.x + object1.w:
        return True
    return False


# long sausage
def hitDetectionPoints(object1x, object1y, object1w, object1d, object2x, object2y, object2w, object2d):  # correct
    if object2y + object2d >= object1y and object2y <= object1y + object1d and object2x + object2w >= object1x and object2x <= object1x + object1w:
        return True
    return False


def hitDetectionAdvanced(object1, object2):
    if hitDetection(object1, object2):
        angle = getAngle(object1, object2)
        hitSides = {"Top": False, "Bottom": False, "Left": False, "Right": False}
        if 45 < angle < 135:
            hitSides["Top"] = True
        if 135 < angle < 225:
            hitSides["Left"] = True
        if 225 < angle < 315:
            hitSides["Bottom"] = True
        if angle > 315 or angle < 45:
            hitSides["Right"] = True
        return hitSides
    return False


# basically returns the x and y difference of two objects
def getObjectCoordsRelative(object1, object2):
    return object2.x - object1.x, object2.y - object1.y


def getObjectCoordsRelativePoints(object1x, object1y, object2x, object2y):
    return object2x - object1x, object2y - object1y


def getObjectCenter(object1):
    return object1.x + floor(object1.w / 2 + 0.5), object1.y + floor(object1.d / 2 + 0.5)


def getObjectCenterPoints(object1x, object1y, object1w, object1d):
    return object1x + floor(object1w / 2 + 0.5), object1y + floor(object1d / 2 + 0.5)


def getObjectCenterRelative(object1):
    return floor(object1.w / 2 + 0.5), floor(object1.d / 2 + 0.5)


def getObjectCenterRelativePoints(object1w, object1d):
    return floor(object1w / 2 + 0.5), floor(object1d / 2 + 0.5)


def getCenterOffset(object1, object2):
    object1XCenter, object1YCenter = getObjectCenter(object1)
    object2XCenter, object2YCenter = getObjectCenter(object2)

    return object2XCenter - object1XCenter, object2YCenter - object1YCenter


def getSegments(segmentAmount):
    return [360 / segmentAmount * segment for segment in range(segmentAmount)]

def cutOff(number, floatingPoint = 9):
    return round(number, floatingPoint)