from lib import *

class Material(object):
    def __init__(self, diffuse=color(255, 255, 255), albedo=(1,0), spec=0):
        self.diffuse = diffuse
        self.albedo = albedo
        self.spec = spec

#albedo (color base, especular)
#spec = Intensidad con la que baja la luz

