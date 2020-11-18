#Juan Diego Solorzano 18151
#RT2: Phong Model

import random
from math import tan, pi
from sphere import Sphere
from lib import *
from materials import *
from light import *

background = color(60, 60, 60)
black = color(0, 0, 0)
white = color(255, 255, 255)
class Raytracer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clearC = background
        self.current_color = white
        self.scene = []
        self.light = None
        self.clear()

    def glInit(self, width, height):
        return

    #Area para pintar
    def glViewPort(self, x, y, width, height):
        self.xw = x
        self.yw = y
        self.widthw = width
        self.heightw = height

    #Pintar imagen   
    def clear(self):
        self.framebuffer = [
            [black for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    #Crear archivo de la imagen
    def write(self, filename):
        writebmp(filename, self.width, self.height, self.framebuffer)

    def display(self, filename='out.bmp'):
        """
        Displays the image, a external library (wand) is used, but only for convenience during development
        """
        self.render()
        self.write(filename)

        try:
            from wand.image import Image
            from wand.display import display

            with Image(filename=filename) as image:
                display(image)
        except ImportError:
            pass  # do nothing if no wand is installed

    #Pintar punto
    def point(self, x, y, color = None):
        try:
            self.framebuffer[y][x] = color or self.current_color
        except:
            pass
    
    #Ver si hay objeto y donde
    def scene_intersect(self, orig, direction):
        zbuffer = float('inf')
        material = None
        intersect = None

        for obj in self.scene:
            hit = obj.ray_intersect(orig, direction)
            if hit is not None: 
                if hit.distance < zbuffer:
                    zbuffer = hit.distance
                    material = obj.material
                    intersect = hit
        return material, intersect
    
    #Renderizar con material
    def cast_ray(self, orig, direction):
        impacted_material, intersect = self.scene_intersect(orig, direction)
        if impacted_material is None:
            return self.clearC

        light_dir = norm(sub(self.light.position, intersect.point))
        light_distance = length(sub(self.light.position, intersect.point))

        #Offset para que no choque con si mismo
        offset_normal = mul(intersect.normal, 1.1)

        if dot(light_dir, intersect.normal) < 0:
            shadow_orig = sub(intersect.point, offset_normal)
        else:
            shadow_orig = sum(intersect.point, offset_normal)
        
        shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
        shadow_intensity = 0

        if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
            #esta en la sombra
            shadow_intensity = 0.9

        intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)
        
        reflection = reflect(light_dir, intersect.normal)
        specular_intensity = self.light.intensity * (max(0, -dot(reflection, direction))**impacted_material.spec)

        diffuse = impacted_material.diffuse * intensity * impacted_material.albedo[0]
        specular = color(255, 255, 255) * specular_intensity * impacted_material.albedo[1]
        return diffuse + specular


    def render(self):
      #field of view
      fov = int(pi/2)

      for y in range(self.height):
        for x in range(self.width):
          i = (2 * (x + 0.5)/self.width - 1) * self.width/self.height * tan(fov/2)
          j = (2 * (y + 0.5)/self.height - 1) * tan(fov/2)

          direction = norm(V3(i, j, -1))
          self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)

r = Raytracer(500, 500)

ivory = Material(diffuse=color(100, 100, 80), albedo=(0.6, 0.4), spec=50)
red = Material(diffuse=color(220, 0, 0), albedo=(0.8,  0.2), spec=100)
blackm = Material(diffuse=color(0, 0, 0), albedo=(.9, 0.1), spec=10)
whitem = Material(diffuse=color(255, 255, 255), albedo=(0.8, 0.2), spec=5)
whitem2 = Material(diffuse=color(255, 255, 255), albedo=(0.7, 0.3), spec=10)
whitem3 = Material(diffuse=color(255, 255, 255), albedo=(0.6, 0.4), spec=10)
brown1 = Material(diffuse=color(239, 162, 94), albedo=(0.8, 0.2), spec=10)
brown2 = Material(diffuse=color(162, 81, 10), albedo=(0.8, 0.2), spec=10)

r.light = Light(
    color = color(255, 255, 255),
    position = V3(20, 0, 20),
    intensity = 2
)
r.scene = [
    #White bear
    #Head
    Sphere(V3(-2.1, 1.6, -10), 1.2, whitem3),
    Sphere(V3(-1.65, 0.9, -8), 0.5, whitem),
    Sphere(V3(-3.3, 2.6, -11), 0.6, whitem2),
    Sphere(V3(-1.4, 2.6, -11), 0.6, whitem2),
    Sphere(V3(-1.2, 1.5, -8), 0.1, blackm),
    Sphere(V3(-2.1, 1.5, -8), 0.1, blackm),
    Sphere(V3(-1.43, 0.85, -7), 0.1, blackm),

    #Body
    Sphere(V3(-2.2, -0.8, -11), 1.7, whitem3),
    Sphere(V3(-3.8, -0.1, -10), 0.75, whitem2),
    Sphere(V3(-0.4, -0.1, -10), 0.75, whitem2),
    Sphere(V3(-3.2, -2.2, -10), 0.75, whitem2),
    Sphere(V3(-0.8, -2.2, -10), 0.75, whitem2),

    #Brown bear
    #Head
    Sphere(V3(3.1, 1.6, -10), 1.2, brown1),
    Sphere(V3(2.65, 1, -8), 0.4, brown2),
    Sphere(V3(2.3, 2.6, -11), 0.6, brown2),
    Sphere(V3(4.4, 2.6, -11), 0.6, brown2),
    Sphere(V3(3, 1.5, -8), 0.1, blackm),
    Sphere(V3(2.2, 1.5, -8), 0.1, blackm),
    Sphere(V3(2.35, 0.95, -7), 0.1, blackm),

    #Body
    Sphere(V3(3.2, -0.8, -11), 1.7, red),
    Sphere(V3(1.6, -0.1, -10), 0.75, brown1),
    Sphere(V3(4.6, -0.1, -10), 0.75, brown1),
    Sphere(V3(1.7, -2.2, -10), 0.75, brown1),
    Sphere(V3(4.5, -2.2, -10), 0.75, brown1),

]
r.display()