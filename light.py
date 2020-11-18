from lib import *

class Light(object):
    def __init__(self, color=color(255, 255, 255), position=V3(0, 0, 0), intensity=1):
        self.position = position
        self.intensity = intensity
        self.color = color