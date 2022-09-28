
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

class Timer:
    def __init__(self, duration, func = None):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            self.deactivate()
            if self.func:
                self.func()