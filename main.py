import pygame, sys, math, random, time
from pygame.locals import *
from tkinter import simpledialog
from tkinter import *

import utility, utilclass

pygame.init()
clock = pygame.time.Clock()
fps = 60

#screen/display setup
screenWidth, screenHeight = 1200, 900
screen = pygame.display.set_mode((screenWidth, screenHeight), RESIZABLE, 16)
pygame.display.set_caption("TrashGame")
gameDisplay = pygame.Surface((screenWidth, screenHeight))
displayMultiplier = 0.25 #zoom
zoomBorders = [0.02, 3]

#cam setup
camKeyBindings = {
            "up": {"key": K_UP, "state": False}, "down": {"key": K_DOWN, "state": False},
            "left": {"key": K_LEFT, "state": False}, "right": {"key": K_RIGHT, "state": False},
            "middle": {"key": 2, "state": False}
        }
cam = utilclass.camera(0, 0, gameDisplay)

def resizeScreen(w, d, displayMultiplier, gameDisplay):
    displayWidth = w * displayMultiplier
    displayHeight = d * displayMultiplier

    gameDisplay = pygame.transform.scale(gameDisplay, (int(displayWidth), int(displayHeight)))

    cam.setSurface(gameDisplay)

    return displayWidth, displayHeight, gameDisplay

displayWidth, displayHeight, gameDisplay = resizeScreen(screenWidth, screenHeight, displayMultiplier, gameDisplay)

entityDictionary = {}
entityTileDictionary = {}

m1 = utilclass.mouse()

#moduleSetups
#entities.setDictionary(entityDictionary)
#entities.setEntityTileDictionary(entityTileDictionary)

def updateEntities(surface, coordOffset):
    #moved these two lines from main while to here
    entityTileDictionary = {}
    entities.setEntityTileDictionary(entityTileDictionary)
    for entType in list(entityDictionary):
        # always iterate like this if you might be removing list indeces because of the shifting thingy
        for unused, ent in sorted(enumerate(entityDictionary[entType]), reverse=True):
            ent.update()
            #if entity is visible by camera draw it
            if utility.hitDetectionPoints(ent.x + (ent.w  - ent.asset.img.get_width()) / 2,ent.y + (ent.d - ent.asset.img.get_height()) / 2,
             ent.asset.img.get_width(), ent.asset.img.get_height(), coordOffset[0], coordOffset[1], displayWidth, displayHeight):
                ent.draw(surface, coordOffset)
    #vision and perception handling
    # the gathering of visible entities needs to happen after all entities have been updated otherwise entities that get updated first cant see 
    # entities that get updated later in entDict because they need to register themselves in entityTileDictionary first to be searched for
    # in other words entityVisibilityCheck needs to happen in main updateEntities
    for entType in entityDictionary:
        for ent in entityDictionary[entType]:
            #if hasattr(ent, "hasPerception"):
            if ent.hasPerception:
                # gather visible and surounding entities and tiles
                ent.gatherPerceptionInformation()
            if ent.kind == "enemy" and ent.behaviour == "flying":
                ent.handlePerception()

def debug(surface, coordOffset):
    gameDisplay.lock()

    #debug draws go here
    cam.draw(surface, coordOffset)

    gameDisplay.unlock()

trackedEntity = None

tileSize = 20

placeh = 0

poList = []
for i in range(10):
    po = utilclass.regularPoly([0, 0], 30 - 5 * (i-1), 6, -90 - 90 * (i-1))
    poList.append(po)
    if i % 2 == 1:
        po.color = 0xcc6c35
    else:
        po.color = 0xFFFFFF

lastTime = time.time()

while 1:
    # multiply movements by dt for frame independence 
    # might cause some glitches when moving (skipping tiles etc) 
    dt = time.time() - lastTime
    dt *= 60
    lastTime = time.time()

    # track the player do this before drawing otherwise weird lagging happens
    if trackedEntity:
        entityXCenter, entityYCenter = utility.getObjectCenter(trackedEntity)
        cam.setDestination(entityXCenter, entityYCenter - 10)

    coordOffset = cam.getCoords()
    #needed cause of gap stretching issue
    coordOffset = [int(coordOffset[0]), int(coordOffset[1])]
    #mouseStuff
    m1.update()
    m1.x = m1.x * displayMultiplier + coordOffset[0]
    m1.y = m1.y * displayMultiplier + coordOffset[1]

    #update background
    gameDisplay.fill(0xcec8c1)
    for po in poList:
        po.draw(gameDisplay, coordOffset)

    # Update Objects / debug
    debug(gameDisplay, coordOffset)
    #updateEntities(gameDisplay, coordOffset)

    #update foreground
    #layeredForeground.draw(gameDisplay, coordOffset)

    #update cam duh
    cam.update(dt)

        
    if placeh <= 2:
        placeh += 1
    else:
        if m1.left:
            for i in range(1):
                #spawn stuff maybe
                pass
            placeh = 0

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.dict['size'], RESIZABLE)
            screenWidth, screenHeight = event.dict['size'][0], event.dict['size'][1]
            displayWidth, displayHeight, gameDisplay = resizeScreen(screenWidth, screenHeight, displayMultiplier, gameDisplay)

        if event.type == pygame.MOUSEWHEEL:
            if event.y < 0 and displayMultiplier < zoomBorders[1]:
                displayMultiplier *= 2
            elif event.y > 0 and displayMultiplier > zoomBorders[0]:
                displayMultiplier /= 2
            preCenterX, preCenterY = utility.getObjectCenterPoints(cam.x, cam.y, displayWidth, displayHeight)
            destinyX, destinyY = cam.getDestination()
            #maybe wrap this
            displayWidth, displayHeight, gameDisplay = resizeScreen(screenWidth, screenHeight, displayMultiplier, gameDisplay)

            postCenterX, postCenterY = utility.getObjectCenterPoints(cam.x, cam.y, displayWidth, displayHeight)

            xDiff, yDiff = math.floor(cam.x + preCenterX - postCenterX), math.floor(cam.y + preCenterY - postCenterY)
            cam.setCoords(xDiff, yDiff)
            cam.setDestination(destinyX, destinyY)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == camKeyBindings["middle"]["key"]:
                camKeyBindings["middle"]["state"] = True

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == camKeyBindings["middle"]["key"]:
                camKeyBindings["middle"]["state"] = False

        if event.type == pygame.KEYDOWN:
            if event.key == K_1:
                # spawns a weapon
                root = Tk()
                root.withdraw()

                string = simpledialog.askstring(title="", prompt="boidName", parent=root)
                if string:
                    if hasattr(weapon, string):
                        entities.weaponEntity(m1.x, m1.y, None, None, getattr(weapon, string),
                                              getattr(weapon, string).textures)
                    else:
                        print(string + " not in " + str(weapon))
            if event.key == K_2:
                tempList = [entity for entType in entityDictionary for entity in entityDictionary[entType]]
                
                if trackedEntity in tempList:
                    trackIndex = tempList.index(trackedEntity)

                    if trackIndex < len(tempList) - 1:
                        trackedEntity = tempList[trackIndex + 1]
                    else:
                        trackedEntity = tempList[0]
                elif len(tempList) > 0:
                    trackedEntity = tempList[0]

            if event.key == K_f:
                total = 0
                for entType in entityDictionary:
                    total += len(entityDictionary[entType])
                print(
                    "fps/dt: " + str(math.floor(clock.get_fps() + 0.5))+ "/" + str(round(dt,2)) + 
                    "  Entities: " + str(total) +
                    "  Zoom: " + str(displayMultiplier)
                    )

            #cammoving
            if event.key == camKeyBindings["up"]["key"]:
                camKeyBindings["up"]["state"] = True
            if event.key == camKeyBindings["down"]["key"]:
                camKeyBindings["down"]["state"] = True
            if event.key == camKeyBindings["left"]["key"]:
                camKeyBindings["left"]["state"] = True
            if event.key == camKeyBindings["right"]["key"]:
                camKeyBindings["right"]["state"] = True

        #cammoving
        elif event.type == pygame.KEYUP:
            if event.key == camKeyBindings["up"]["key"]:
                camKeyBindings["up"]["state"] = False
            if event.key == camKeyBindings["down"]["key"]:
                camKeyBindings["down"]["state"] = False
            if event.key == camKeyBindings["left"]["key"]:
                camKeyBindings["left"]["state"] = False
            if event.key == camKeyBindings["right"]["key"]:
                camKeyBindings["right"]["state"] = False
    
    if camKeyBindings["up"]["state"]:
        x, y = cam.getDestination()
        cam.setDestination(x,y-2 * dt)
    if camKeyBindings["down"]["state"]:
        x, y = cam.getDestination()
        cam.setDestination(x,y+2 * dt)
    if camKeyBindings["right"]["state"]:
        x, y = cam.getDestination()
        cam.setDestination(x+2 * dt,y)
    if camKeyBindings["left"]["state"]:
        x, y = cam.getDestination()
        cam.setDestination(x-2 * dt,y)

    if camKeyBindings["middle"]["state"]:
        if trackedEntity:
            trackedEntity = None
        cam.setDestination(m1.x, m1.y)


    screen.blit(pygame.transform.scale(gameDisplay, (screenWidth, screenHeight)), (0, 0))
    pygame.display.update()
    clock.tick(fps)
