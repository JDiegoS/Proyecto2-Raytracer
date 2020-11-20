#Juan Diego Solorzano 18151
#RT2: Phong Model

import random
from math import tan, pi
from figures import *
from lib import *
from materials import *
from light import *

background = color(138, 183, 248)
black = color(0, 0, 0)
white = color(255, 255, 255)
MAX_RECURSION_DEPTH = 3

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
    def cast_ray(self, orig, direction, recursion=0):
        material, intersect = self.scene_intersect(orig, direction)
        if material is None or recursion >= MAX_RECURSION_DEPTH:
            return self.clearC

        light_dir = norm(sub(self.light.position, intersect.point))
        light_distance = length(sub(self.light.position, intersect.point))

        #Offset para que no choque con si mismo
        offset_normal = mul(intersect.normal, 1.1)

        if material.albedo[2] > 0:
            reverse_direction = mul(direction, -1)
            reflected_dir = reflect(reverse_direction, intersect.normal)
            reflect_orig = sub(intersect.point, offset_normal) if dot(reflected_dir, intersect.normal) < 0 else sum(
            intersect.point, offset_normal)
            reflected_color = self.cast_ray(reflect_orig, reflected_dir, recursion + 1)
        else:
            reflected_color = color(0, 0, 0)

        if material.albedo[3] > 0:
            refract_dir = refract(direction, intersect.normal, material.refractive_index)
            refract_orig = sub(intersect.point, offset_normal) if dot(refract_dir, intersect.normal) < 0 else sum(
            intersect.point, offset_normal)
            refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
        else:
            refract_color = color(0, 0, 0)

        
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
        specular_intensity = self.light.intensity * (max(0, -dot(reflection, direction))**material.spec)

        diffuse = material.diffuse * intensity * material.albedo[0]
        specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
        reflection = reflected_color * material.albedo[2]
        refraction = refract_color * material.albedo[3]
        return diffuse + specular + reflection + refraction


    def render(self):
      #field of view
      fov = int(pi/2)

      for y in range(self.height):
        for x in range(self.width):
          i = (2 * (x + 0.5)/self.width - 1) * self.width/self.height * tan(fov/2)
          j = (2 * (y + 0.5)/self.height - 1) * tan(fov/2)

          direction = norm(V3(i, j, -1))
          self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)

r = Raytracer(600, 500)

ivory = Material(diffuse=color(100, 100, 80), albedo=(0.6, 0.4, 0, 0), spec=50)
red = Material(diffuse=color(220, 0, 0), albedo=(0.8,  0.2, 0, 0), spec=100)
blackm = Material(diffuse=color(0, 0, 0), albedo=(.9, 0.1, 0, 0), spec=10)
brown1 = Material(diffuse=color(239, 162, 94), albedo=(0.8, 0.2, 0, 0), spec=10)
brown2 = Material(diffuse=color(162, 81, 10), albedo=(0.8, 0.2, 0, 0), spec=10)
lake = Material(diffuse=color(80, 80, 120), albedo=(0, 0.5, 0.1, 0.8), spec=125, refractive_index=1.5)
sun = Material(diffuse=color(244, 128, 55), albedo=(0.9,  0.1, 0, 0), spec=100)
#249, 215, 28
r.light = Light(
    color = color(255, 255, 255),
    position = V3(20, 0, 20),
    intensity = 2
)
r.scene = [
    #Sun
    Sphere(V3(-15, 16, -30), 6, sun),

    #House
    Cube(V3(0, 1, -10), 2, ivory),

    #Mountains
    Pyramid([V3(4, 2.5, -18), V3(6, 5, -15), V3(9, 2, -15), V3(5, 1.7, -15)], red),
    Pyramid([V3(8, 3.5, -20), V3(10, 6, -17), V3(13, 3, -17), V3(9, 2.7, -17)], red),
    
    #Lake
    Plane( V3(0, -1, 0), V3(0, -4, 0), lake),
    
]
r.display()