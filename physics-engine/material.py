
class colour(object):
   def __init__(self, colour = (255,255,255), brightness = 100):

        self.colour = colour
        self.brightness = brightness

class BLACK(colour):

    def __init__(self):
        super().__init__((0,0,0))

class WHITE(colour):

    def __init__(self):
        super().__init__((0,0,0))


class BLUE(colour):

    def __init__(self):
        super().__init__((0,0,255))

class GREEN(colour):

    def __init__(self):
        super().__init__((0,255,0))

class RED(colour):

    def __init__(self):
        super().__init__((255,0,0))




class triangle(object):
  def __init__(self):
    pass
  
  def project(self):
    pass


class texture(object):
  def __init__(self, image):
    self.image = image
  
  def getTriangles():
    pass
    # rasturize the texture into triangles