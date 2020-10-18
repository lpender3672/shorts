


class material(object):
    def __init__(self, colour = (255,255,255), brightness = 100):

        self.colour = colour
        self.brightness = brightness

class BLACK(material):

    def __init__(self):
        super().__init__((0,0,0))

class WHITE(material):

    def __init__(self):
        super().__init__((0,0,0))


class BLUE(material):

    def __init__(self):
        super().__init__((0,0,255))

class GREEN(material):

    def __init__(self):
        super().__init__((0,255,0))

class RED(material):

    def __init__(self):
        super().__init__((255,0,0))

