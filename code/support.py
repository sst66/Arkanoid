
from os import walk
import pygame

# THIS IS A WORK IN PROGRESS
# while it is completely playable, some features are still missing
# (boss, game ending, high score tables, maybe others)

# written using VSCode with Pygame 2.1.2 (SDL 2.0.18) and Python 3.9.5

# open the 'code' folder in VSCode (not the files). 
# either right click the 'code' folder and select 'Open with Code'
# or within the VSCode File menu, select 'Open Folder' and browse
# to and select the 'code' folder 

# run 'main.py' from within VSCode or navigate your cmd window to
# the 'code' folder containing the .py files and execute 'main.py'

# This code is free and open source
# Feel free to use/edit/distribute as you see fit
# I will not be responsible for anything it does 
# to anything or anything anyone does to it
# use at your own risk

# most assets created using the latest Blender and GIMP
# some were downloaded (font, image of Ark, enemy explosion)

def import_folder(path):
    surface_list = []
    for _, __, image_names in walk(path):
        for image in image_names:
            # print(path, image)
            surface_list.append(pygame.image.load(path + '/' + image).convert_alpha())
    
    return surface_list

pygame.font.init()
font = pygame.font.Font('ExternalData/Font/ARCADEPI.ttf', 40)
small_font = pygame.font.Font('ExternalData/Font/ARCADEPI.ttf', 18)
def scaled_surf(surf):
    surf = pygame.transform.scale(surf, (surf.get_width() * .85, surf.get_height()))
    return surf

def get_spaced_surf(string, color):
    new_surf = pygame.Surface((len(string) * 28, 30)).convert_alpha()
    new_surf.fill((0, 0, 0, 0))
    for index, character in enumerate(string):
        new_surf.blit(scaled_surf(font.render(character, False, color)).convert_alpha(), (index * 28, -5))
    return new_surf