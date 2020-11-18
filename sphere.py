from lib import *

class Intersect(object):
  def __init__(self, distance=0, point=None, normal= None, texCoords = None):
    self.distance = distance
    self.point = point
    self.normal = normal
    self.texCoords = texCoords

class Sphere(object):
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def ray_intersect(self, orig, direction):
        L = sub(self.center, orig)
        tca = dot(L, direction)
        l = length(L)
        d2 = l**2 - tca**2

        if d2 > self.radius**2:
            return None

        thc = (self.radius**2 - d2) ** 0.5
        t0 = tca - thc
        t1 = tca + thc

        #Casos
        if t0 < 0:
            t0 = t1
        if t0 < 0:
            return None

        hit = sum(orig, mul(direction, t0))
        normal = norm(sub(hit, self.center))

        return Intersect(
            distance=t0,
            point=hit,
            normal=normal
        )

class Plane(object):
    def __init__(self, position, normal, material):
        self.position = position
        self.normal = norm(normal)
        self.material = material

    def ray_intersect(self, orig, dir):
        denom = dot(dir, self.normal)
        if abs(denom) > 0.0001:
            t = dot(self.normal, sub(self.position, orig)) / denom
            if t > 0:
                hit = sum(orig, mul(dir, t))
                return Intersect(distance=t, point=hit,normal=self.normal)

        return None

class Cube(object):
    def __init__(self, position, size, material):
        self.position = position
        self.size = size
        self.material = material
        mid_size = size / 2

        self.planes = [
              Plane(sum(position, V3(mid_size, 0, 0)), V3(1, 0, 0), material),
              Plane(sum(position, V3(-mid_size, 0, 0)), V3(-1, 0, 0), material),
              Plane(sum(position, V3(0, mid_size, 0)), V3(0, 1, 0), material),
              Plane(sum(position, V3(0, -mid_size, 0)), V3(0, -1, 0), material),
              Plane(sum(position, V3(0, 0, mid_size)), V3(0, 0, 1), material),
              Plane(sum(position, V3(0, 0, -mid_size)), V3(0, 0, -1), material)
          ]

    def ray_intersect(self, orig, direction):
        epsilon = 0.001
        minBounds = [0, 0, 0]
        maxBounds = [0, 0, 0]

        for i in range(3):
            minBounds[i] = self.position[i] - (epsilon + self.size / 2)
            maxBounds[i] = self.position[i] + (epsilon + self.size / 2)

        t = float('inf')
        intersect = None

        for plane in self.planes:
            planeInter = plane.ray_intersect(orig, direction)

            if planeInter is not None:
                if planeInter.point[0] >= minBounds[0] and planeInter.point[0] <= maxBounds[0]:
                    if planeInter.point[1] >= minBounds[1] and planeInter.point[1] <= maxBounds[1]:
                        if planeInter.point[2] >= minBounds[2] and planeInter.point[2] <= maxBounds[2]:
                            if planeInter.distance < t:
                                t = planeInter.distance
                                intersect = planeInter

                                if abs(plane.normal[0]) > 0:
                                    u = (planeInter.point[1] - minBounds[1]) / (maxBounds[1] - minBounds[1])
                                    v = (planeInter.point[2] - minBounds[2]) / (maxBounds[2] - minBounds[2])

                                elif abs(plane.normal[1]) > 0:
                                    u = (planeInter.point[0] - minBounds[0]) / (maxBounds[0] - minBounds[0])
                                    v = (planeInter.point[2] - minBounds[2]) / (maxBounds[2] - minBounds[2])

                                elif abs(plane.normal[2]) > 0:
                                    u = (planeInter.point[0] - minBounds[0]) / (maxBounds[0] - minBounds[0])
                                    v = (planeInter.point[1] - minBounds[1]) / (maxBounds[1] - minBounds[1])

                                coords = [u, v]

        if intersect is None:
            return None

        return Intersect(distance=intersect.distance,
                         point=intersect.point,
                         texCoords=coords,
                         normal=intersect.normal)

class Texture(object):
  def __init__(self, path):
    self.path = path
    self.read()

  def read(self):
    image = open(self.path, 'rb')
    image.seek(10)
    headerSize = struct.unpack('=l', image.read(4))[0]

    image.seek(14 + 4)
    self.width = struct.unpack('=l', image.read(4))[0]
    self.height = struct.unpack('=l', image.read(4))[0]
    image.seek(headerSize)

    self.pixels = []

    for y in range(self.height):
      self.pixels.append([])
      for x in range(self.width):
        b = ord(image.read(1)) / 255
        g = ord(image.read(1)) / 255
        r = ord(image.read(1)) / 255
        self.pixels[y].append(color(r, g, b))

    image.close()