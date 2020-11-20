#Juan Diego Solorzano 18151
#Proyecto 2: Raytracer

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

#Materials
housec = Material(diffuse=color(200, 200, 200), albedo=(0.6, 0.4, 0, 0), spec=50)
door = Material(diffuse=color(80, 80, 80), albedo=(0.9, 0.1, 0, 0), spec=50)
whitec = Material(diffuse=color(235, 235, 235), albedo=(.7, 0.3, 0, 0), spec=1)
blackc = Material(diffuse=color(0, 0, 0), albedo=(.7, 0.3, 0, 0), spec=100)
roof = Material(diffuse=color(85, 65, 36), albedo=(0.8, 0.2, 0, 0), spec=100)
wood = Material(diffuse=color(106, 75, 53), albedo=(0.8, 0.2, 0, 0), spec=10)
lake = Material(diffuse=color(80, 80, 120), albedo=(0, 0.5, 0.1, 0.8), spec=125, refractive_index=1.5)
grass = Material(diffuse=color(42, 76, 0), albedo=(1, 0, 0, 0), spec=0)
window = Material(diffuse=color(150, 180, 200), albedo=(0, 0.5, 0.2, 0.8), spec=125, refractive_index=1.5)
lightp = Material(diffuse=color(250, 253, 15), albedo=(1, 0, 0, 0), spec=0)


r.light = Light(
    color = color(255, 255, 255),
    position = V3(20, 0, 20),
    intensity = 2
)
r.scene = [
    #House by the lake
    #House
    Cube(V3(-3, 1.7, -10), 2.5, housec),
    Cube(V3(-0.5, 1.7, -10), 2.5, housec),
    Cube(V3(-1.7, 0.7, -9), 0.6, door),
    Cube(V3(-1.7, 1.2, -9), 0.6, door),
    Cube(V3(-3.3, 2.1, -9), 0.85, window),
    Cube(V3(-0.2, 2.1, -9), 0.85, window),

    #Light post
    Sphere(V3(-6, 1.9, -10), 0.2, lightp),
    Cube(V3(-6, 0.6, -10), 0.2, blackc),
    Cube(V3(-6, 0.8, -10), 0.2, blackc),
    Cube(V3(-6, 1, -10), 0.2, blackc),
    Cube(V3(-6, 1.2, -10), 0.2, blackc),
    Cube(V3(-6, 1.4, -10), 0.2, blackc),
    Cube(V3(-6, 1.6, -10), 0.2, blackc),

    #Cabin
    Cube(V3(3.2, 1.2, -10), 1.5, wood),
    #Cabin roof
    Pyramid([V3(3.1, 3.4, -18), V3(5, 4.5, -15), V3(7.3, 2.8, -15), V3(3.2, 2.8, -15)], roof),

    #Tree
    Cube(V3(6, 0.5, -10), 0.4, wood),
    Cube(V3(6, 0.9, -10), 0.4, wood),
    Cube(V3(6, 1.3, -10), 0.4, wood),
    Cube(V3(6, 1.7, -10), 0.4, grass),
    Cube(V3(5.6, 1.7, -10), 0.4, grass),
    Cube(V3(6.4, 1.7, -10), 0.4, grass),
    Cube(V3(6, 2.1, -10), 0.4, grass),
    Cube(V3(5.6, 2.1, -10), 0.4, grass),
    Cube(V3(6.4, 2.1, -10), 0.4, grass),
    Cube(V3(6, 2.3, -10), 0.4, grass),
    
    #Grass
    Triangle([V3(-10, 0.6, -12), V3(-10, -1.85, -12), V3(10, 0.6, -12)], grass),

    #Lake
    Plane(V3(0, -1.5, -10), V3(0, 1, 0.05), lake),

    #Clouds
    Cube(V3(-3, 5, -10), 0.4, whitec),
    Cube(V3(-3, 4.6, -10), 0.4, whitec),
    Cube(V3(-2.6, 4.6, -10), 0.4, whitec),
    Cube(V3(-3.2, 4.6, -10), 0.4, whitec),

    Cube(V3(3.2, 4, -10), 0.4, whitec),
    Cube(V3(3.4, 4, -10), 0.4, whitec),
    Cube(V3(3.4, 4.4, -10), 0.4, whitec),
    Cube(V3(3.8, 4, -10), 0.4, whitec),

    Cube(V3(0, 5, -10), 0.4, whitec),
    Cube(V3(0.4, 5, -10), 0.4, whitec),
    Cube(V3(0.4, 5.4, -10), 0.4, whitec),
    Cube(V3(0.6, 5, -10), 0.4, whitec),

    Cube(V3(-6, 4.5, -10), 0.4, whitec),
    Cube(V3(-6, 4.1, -10), 0.4, whitec),
    Cube(V3(-5.8, 4.1, -10), 0.4, whitec),
    Cube(V3(-6.4, 4.1, -10), 0.4, whitec),
    
]
r.display()