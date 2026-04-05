

class line(object):
    def __init__(self, direction, point):
        self.d = direction
        self.p = point

    def getpoint(self, k):
        return self.p + self.d * k

