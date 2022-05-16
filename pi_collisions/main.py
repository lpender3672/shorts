
import pygame, math


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def drawCube(display, x,y,l):

  R = pygame.Rect(x, y-l, l, l)
  pygame.draw.rect(display, BLACK, R)





width = 600
height = 200

display = pygame.display.set_mode((width, height))

pygame.display.set_caption("PI from counting collisions")

clock = pygame.time.Clock()
TicksLastFrame = 0

crashed = False
m1 = 1
m2 = 100**2

v1 = 0
v2 = -5

x1 = 10
x2 = 70

l1 = 50
l2 = 100

collisions = 0










while not crashed:

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            crashed = True

    
    t = pygame.time.get_ticks()
    deltaTime = (t - TicksLastFrame) / 1000.0  # seconds
    TicksLastFrame = t

    # calc new dda

    x1 = x1 + v1*deltaTime
    x2 = x2 + v2*deltaTime

    if x2 <= x1+l1:
      x2 = x1+l1

      # calcv1 and v2
      M = m1+m2

      u1,u2 = v1,v2
      v1 = ((m1-m2)*u1 + (2*m2)*u2)/M
      v2 = ((2*m1)*u1  + (m2-m1)*u2)/M

      if abs(v1) < abs(v2) and collisions > 0:

        print(collisions)
        crashed = True

      collisions+=1

      print(collisions)

    if x1 < 0:
      x1=0
      v1*=-1

      collisions+=1

      print(collisions)
      # collision


    
    display.fill(WHITE)

    # draw line

    drawCube(display, x1, 190, l1)
    drawCube(display, x2, 190, l2)
    pygame.display.update()

    clock.tick(1000)

pygame.quit()


# compute pi code
# move to my maths code
def computePI(digits):
  m1 = 1
  m2 = 100**digits

  M = m1+m2

  v1 = 0
  v2 = -1

  collisions = 0

  while abs(v1) > abs(v2) or collisions == 0:

    u1,u2 = -v1,v2

    v1 = ((m1-m2)*u1 + (2*m2)*u2)/M
    v2 = ((2*m1)*u1  + (m2-m1)*u2)/M
    
    if abs(v1) > abs(v2):
      collisions +=1

    collisions += 1
  

  return collisions/(10**digits)



print(computePI(1))
