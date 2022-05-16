
import pygame
from PIL import Image, ImageTransform
import numpy as np

im = Image.open("mem.jpg")
imWidth,imHeight = im.size


transform = True

sensitivity = 0.1

z=1
zoom = np.exp(-z)
panfactor = np.exp(2*z)

width,height = 1920,1080

crashed = False
pygame.init()

surface = pygame.display.set_mode((width, height))

x,y = width/2, height/2
oldmx,oldmy = 0,0
pan = False

while not crashed:

    events = pygame.event.get()

    mx, my = pygame.mouse.get_pos()

    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
                transform = not transform

            if event.key == pygame.K_ESCAPE:
                crashed = True

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                pan = True

            if event.button == 4:
                z+=0.1
            if event.button == 5:
                z-=0.1

            zoom = np.exp(-z)
            panfactor = np.exp(0.5*z)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pan = False


    if pan:
        x += panfactor*(mx - oldmx)
        y += panfactor*(my - oldmy)

    camyaw = sensitivity * ((mx - width / 2) / width) * 2 * np.pi
    campitch = sensitivity * -((my - height / 2) / height) * np.pi

    mat = np.array([[1,0],
                    [0,1]])

    wr = imWidth/width
    hr = imHeight/height

    if wr > hr:
        mat = mat*wr
    else:
        mat = mat*hr

    mat = zoom*mat


    a = ImageTransform.AffineTransform((mat[0,0], mat[0,1], width/2 - x, mat[1,0], mat[1,1], height/2 - y))

    Tim = a.transform(size=(1920, 1080), image=im)

    pyim = pygame.image.fromstring(Tim.tobytes(), Tim.size, Tim.mode)

    surface.blit(pyim, (0,0))

    pygame.display.update()

    oldmx,oldmy = mx,my

