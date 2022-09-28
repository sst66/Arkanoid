
import pygame, random, math, settings, time, sys, copy
from settings import *
from support import *
from pygame.math import Vector2
from timer import Timer

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

class Player(pygame.sprite.Sprite): # instanced in main.Game.__init__()

    def __init__(self, sprite_groups, sounds, images, start_sparkles):
        # super().__init__(sprite_groups[3])
        super().__init__()
        self.bullet_sprites = sprite_groups[0] # for shooting
        self.block_sprites = sprite_groups[1] # sent to ball
        self.powerup_sprites = sprite_groups[2] # for collision with upgrades
        self.player_sprites = sprite_groups[3] # 
        # self.shadow_sprites = sprite_groups[4] # 
        self.explosion_sprites = sprite_groups[4] # for particle explosion
        self.teleporter_sprites = sprite_groups[5] # for spawning at upgrade collision
        self.enemy_sprites = sprite_groups[6] # sent to bullets and balls
        self.ball_sprites = sprite_groups[7] # for multiballs
        self.notification_sprites = sprite_groups[8] # for start stage info in top right
        self.endball_sprites = pygame.sprite.Group()
        
        self.paddle_hit_sound = sounds[0]
        self.shoot_sound = sounds[1]
        self.paddle_grow_sound = sounds[2]
        self.one_up_sound = sounds[3]
        self.teleport_sound = sounds[4]
        self.inf_hit_sound = sounds[5]
        self.block_hit_sound = sounds[6]
        self.ball_catch_sound = sounds[7]

        self.ball_image = images[0]
        self.extend_images = images[1]
        self.laser_images = images[2]
        self.spawn_images = images[3]
        self.splash_images = images[4]
        self.teleporter_images = images[5]
        
        self.start_sparkles = start_sparkles

        self.round_surf = scaled_surf(font.render('ROUND', False, 'white').convert_alpha())
        self.round_shadow = scaled_surf(font.render('ROUND', False, 'black').convert_alpha())
        # self.round_shadow.set_alpha(120)

        self.ready_surf = scaled_surf(font.render('READY', False, 'white').convert_alpha())
        self.ready_shadow = scaled_surf(font.render('READY', False, 'black').convert_alpha())
        # self.ready_shadow.set_alpha(120)
        
        self.image = self.extend_images[0]

        self.state = 'default' # set default state and define methods for all states
        self.states = {'spawning': self.spawning, 
                        'default': self.default, 
                        'to_laser': self.to_laser, 
                        'from_laser': self.from_laser, 
                        'to_extend': self.to_extend, 
                        'from_extend': self.from_extend, 
                        'extended': self.extended, 
                        'lasered': self.lasered, 
                        'teleporting': self.teleporting}

        self.speed = 600 # movement speed scalar, multiplied by dt and direction vector
        self.stage = 0 # for round start message including the round number
        self.int_score = 0
        self.lives_left = 3
        self.int_high_score = 50000
        self.blocks_left = 0
        self.direction = Vector2()
        self.active = False
        self.sticky = False
        self.next_stage = False
        self.isPlayer = True
        self.init_state = True
        self.demo_mode = True

        self.rect = pygame.Rect(0, 0, 121, 31)
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 58)
        self.old_rect = self.rect.copy()
        self.pos = Vector2(self.rect.topleft)
        self.new_rect = pygame.Rect(0, 0, 121, 31)
        self.new_rect.center = self.rect.center
                            
        self.endball1 = EndBalls(self.endball_sprites, self, 'left') # pulsing balls for the ends of the paddle
        self.endball2 = EndBalls(self.endball_sprites, self, 'right')


        self.extend_timer = Timer(0, self.set_from_extend) # timer for extended paddle, will have duration added to it
        self.laser_timer = Timer(0, self.set_from_laser) # same as above but for laser
        self.spawn_frame_timer = Timer(80, self.next_spawn_image) # milliseconds between frames for spawning animation
        self.score_timer = Timer(30, self.tally_score) # ms between score updates for teleport bonus score
        self.sticky_timer_player = Timer(10000, self.reset_sticky) # ten second timer for catch powerup duration
        self.round_timer = Timer(2000)

    def input(self): # called from self.update()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.direction.x += .03
        elif keys[pygame.K_LEFT]:
            self.direction.x -= .03
        else:
            self.direction.x = 0
        self.direction.x = max(-2, (min(self.direction.x, 2)))
    
    def add_ball(self, isExtraBall):
        return Ball(self.ball_image, self.player_sprites, self.ball_sprites, self.explosion_sprites, self, 
                        self.block_sprites, self.enemy_sprites, isExtraBall, self.paddle_hit_sound, 
                        self.inf_hit_sound, self.block_hit_sound, self.ball_catch_sound)

    def add_multiballs(self):
        for vector in extraball_vectors:
            if vector != self.ball_sprites.sprites()[0].vel:
                temp = self.add_ball(True)
                temp.direction = vector.copy()

    def shoot(self):
        pygame.mixer.Sound.play(self.shoot_sound)
        Bullet(self, self.bullet_sprites, self.block_sprites, self.enemy_sprites, Vector2(self.rect.midtop[0] - 20, HEIGHT - 80), self.splash_images) # bullet_sprites, block_sprites, pos
        Bullet(self, self.bullet_sprites, self.block_sprites, self.enemy_sprites, Vector2(self.rect.midtop[0] + 20, HEIGHT - 80), self.splash_images)

    def update_score(self, amount):
        self.int_score += amount
        if self.int_score > self.int_high_score:
            self.int_high_score = self.int_score
            
    def tally_score(self):
        if self.points_list:
            self.update_score(self.points_list[0])
            self.points_list.pop(0)
            self.score_timer.activate()
        else:
            self.score_timer.deactivate()

    def die(self):
        return

    def screen_constraint(self): # called from self.update()
        if self.rect.left < MARGIN:
            self.rect.left = MARGIN
            self.pos.x = self.rect.x
            self.direction.x = 0
        if self.rect.right > WIDTH - MARGIN and not self.teleporter_sprites:
            self.rect.right = WIDTH - MARGIN
            self.pos.x = self.rect.x
            self.direction.x = 0
    
    def upgrade_collide(self):
        overlap_sprites = pygame.sprite.spritecollide(self, self.powerup_sprites, True)
        if overlap_sprites: # 'PLEDSCB'
            for sprite in overlap_sprites:
                if sprite.powerup_type == 'P':
                    if self.lives_left < 10:
                        pygame.mixer.Sound.play(self.one_up_sound)
                        self.lives_left += 1

                elif sprite.powerup_type == 'L':
                    if self.state != 'to_laser' and self.state != 'lasered':
                        self.state = 'to_laser'
                        self.init_state = True
                    else:
                        self.laser_timer.duration += 8000

                elif sprite.powerup_type == 'E':
                    if self.state != 'to_extend' and self.state != 'extended':
                        self.state = 'to_extend'
                        self.init_state = True
                    else:
                        self.extend_timer.duration += 8000

                elif sprite.powerup_type == 'D':
                    if len(self.ball_sprites) == 1:
                        self.add_multiballs()
                elif sprite.powerup_type == 'S':
                    for ball in self.ball_sprites.sprites():
                        ball.speed = 400
                elif sprite.powerup_type == 'C':
                    self.sticky = True
                    self.sticky_timer_player.activate()
                elif sprite.powerup_type == 'B':
                    Teleporter(self, self.teleporter_sprites, self.teleporter_images, (WIDTH - MARGIN + 3, HEIGHT - 148))

    def reset_sticky(self):
        self.sticky = False

    def reset(self):
        # deactivate timers
        self.extend_timer.deactivate()
        self.laser_timer.deactivate()
        # reset flags
        self.active = False
        self.sticky = False
        self.demo_mode = False
        self.next_stage = False
        # cleanup
        self.endball_sprites.remove(self.endball1)
        self.endball_sprites.remove(self.endball2)
        self.player_sprites.empty()
        self.teleporter_sprites.empty()
        # reset misc
        self.image = self.extend_images[0]
        self.rect = pygame.Rect(0, 0, 121, 31)
        self.rect.midbottom = (WIDTH // 2, HEIGHT - 58)
        self.new_rect.center = self.rect.center
        self.endball_sprites.update()
        self.pos = Vector2(self.rect.topleft)
        self.direction.x = 0

    def explode(self):
        # new_image = self.image.copy()
        # for y in range(0, new_image.get_height(), 8):
        #     for x in range(0, new_image.get_width(), 8):
        #         pos_x = self.rect.left + x
        #         pos_y = self.rect.top + y
        #         direction = Vector2(pos_x, pos_y) - Vector2(self.rect.center)
        #         new_image.set_clip((x, y, 8, 8))
        #         sprite = new_image.subsurface(new_image.get_clip()).convert_alpha()
        #         direction *= .03

        #         Particle(self.explosion_sprites, # group
        #                 self.shadow_sprites, # group
        #                 direction, # vel
        #                 sprite, # image
        #                 (self.rect.topleft[0] + x, self.rect.topleft[1] + y))
        new_image = self.image.copy()
        for y in range(0, new_image.get_height(), 8):
            for x in range(0, new_image.get_width(), 8):
                pos_x = self.rect.left + x
                pos_y = self.rect.top + y
                direction = Vector2(pos_x, pos_y) - Vector2(self.rect.center)
                direction.rotate_ip(random.randint(0, 50) - 25)
                new_image.set_clip((x, y, 8, 8))
                sprite = new_image.subsurface(new_image.get_clip()).convert_alpha()
                direction *= .07

                # HatchParticle(self.explosion_sprites, 
                #             sprite, 
                #             (self.rect.topleft[0] + x, self.rect.topleft[1] + y), 
                #             direction)
                Particle(self.explosion_sprites, # group
                        direction, # vel
                        sprite, # image
                        (self.rect.topleft[0] + x, self.rect.topleft[1] + y))

    ###################################################################################################
    ##                                                                                               ##
    ##                                          draw                                                 ##
    ##                                                                                               ##
    ###################################################################################################

    def draw_player(self, screen):
        if self.round_timer.active:
            screen.blit(self.round_shadow, (290, 704))
            screen.blit(self.round_surf, (284, 698))
            self.round_number_surf = scaled_surf(font.render(str(self.stage + 1), False, 'white'))
            self.round_number_shadow = scaled_surf(font.render(str(self.stage + 1), False, 'black'))
            screen.blit(self.round_number_shadow, (471, 704))
            screen.blit(self.round_number_surf, (465, 698))
            if pygame.time.get_ticks() - self.round_timer.start_time > 1000:
                screen.blit(self.ready_shadow, (334, 766))
                screen.blit(self.ready_surf, (328, 760))
            self.round_timer.update()
        else:
            self.endball_sprites.draw(screen)
            self.player_sprites.draw(screen)

    ###################################################################################################
    ##                                                                                               ##
    ##                                       animators                                               ##
    ##                                                                                               ##
    ###################################################################################################
    
    def next_spawn_image(self):
        self.spawn_index += 1
        if self.spawn_index == 4 and not self.endball_sprites:
            self.start_sparkles() # method is sent from Game()
            self.endball_sprites.add(self.endball1)
            self.endball_sprites.add(self.endball2)
        if self.spawn_index > 5:
            self.state = 'default'
            self.init_state = True
        else:
            self.image = self.spawn_images[self.spawn_index]
            self.spawn_frame_timer.activate()

    def next_extend_image(self):
        self.extend_index += 1
        if self.extend_index == 1:
            self.endball1.retracted = False
            self.endball2.retracted = False
            self.endball1.laser_mode = False
            self.endball2.laser_mode = False
        if self.extend_index > 9:
            self.state = 'extended'
            self.init_state = True
        else:
            self.set_extend_image()
            self.to_extend_timer.activate()
            
    def prev_extend_image(self):
        self.extend_index -= 1
        if self.extend_index < 0:
            self.state = 'default'
            self.init_state = True
            self.from_extend_timer.deactivate()
        else:
            self.set_extend_image()
            self.from_extend_timer.activate()

    def next_laser_image(self):
        self.laser_index += 1
        if self.laser_index > 9:
            self.state = 'lasered'
            self.init_state = True
            self.to_laser_timer.deactivate()
        else:
            self.set_laser_image()
            self.to_laser_timer.activate()
            
    def prev_laser_image(self):
        self.laser_index -= 1
        if self.laser_index == 1:
            self.endball1.retracted = False
            self.endball2.retracted = False
            self.endball1.laser_mode = False
            self.endball2.laser_mode = False
        if self.laser_index < 0:
            self.state = 'default'
            self.init_state = True
            self.from_laser_timer.deactivate()
        else:
            self.set_laser_image()
            self.from_laser_timer.activate()
            
    def set_laser_image(self):
            self.image = self.laser_images[self.laser_index]
            self.new_rect = pygame.Rect(0, 0, 121, 31)
            self.new_rect.center = self.rect.center
            self.rect = self.new_rect
            self.pos.x = self.rect.left
            
    def set_extend_image(self):
            self.image = self.extend_images[self.extend_index]
            self.new_rect = pygame.Rect(0, 0, 121 + self.extend_index * 6, 31)
            self.new_rect.center = self.rect.center
            self.rect = self.new_rect
            self.pos.x = self.rect.left

    ###################################################################################################
    ##                                                                                               ##
    ##                                     state setters                                             ##
    ##                                                                                               ##
    ###################################################################################################
    
    def set_from_extend(self):
        self.state = 'from_extend'
        self.init_state = True
        
    def set_from_laser(self):
        self.state = 'from_laser'
        self.init_state = True

    def set_next_stage(self): # not a state but a setter, so it's here
        self.next_stage = True

    ###################################################################################################
    ##                                                                                               ##
    ##                                        states                                                 ##
    ##                                                                                               ##
    ###################################################################################################

    def to_extend(self):
        if self.init_state:
            self.init_state = False
            self.laser_timer.duration = 0
            self.laser_timer.deactivate()
            self.extend_index = 0
            self.to_extend_timer = Timer(70, self.next_extend_image)
            self.extend_timer.duration += 8000
            self.extend_timer.activate()
            self.to_extend_timer.activate()
            pygame.mixer.Sound.play(self.paddle_grow_sound)
        self.to_extend_timer.update()

    def from_extend(self):
        if self.init_state:
            self.init_state = False
            self.extend_index = 9
            self.from_extend_timer = Timer(70, self.prev_extend_image)
            self.from_extend_timer.activate()
        self.from_extend_timer.update()
            
    def to_laser(self):
        if self.init_state:
            self.extend_timer.duration = 0
            self.extend_timer.deactivate()
            self.endball1.retracted = True
            self.endball2.retracted = True
            self.endball1.laser_mode = False
            self.endball2.laser_mode = False
            self.init_state = False
            self.laser_index = 0
            self.to_laser_timer = Timer(70, self.next_laser_image)
            self.to_laser_timer.activate()
            self.laser_timer.duration += 8000
            self.laser_timer.activate()
        self.to_laser_timer.update()

    def from_laser(self):
        if self.init_state:
            self.init_state = False
            self.endball1.retracted = True
            self.endball2.retracted = True
            self.endball1.laser_mode = False
            self.endball2.laser_mode = False
            self.laser_index = 9
            self.from_laser_timer = Timer(70, self.prev_laser_image)
            self.from_laser_timer.activate()
        self.from_laser_timer.update()

    def spawning(self):
        if self.init_state:
            self.spawn_index = 0
            if not self.demo_mode:
                Notification(self.notification_sprites,   'PRESS P TO PAUSE  ')
                Notification(self.notification_sprites,    'ARROWS TO MOVE   ')
                Notification(self.notification_sprites, 'SPACE TO LAUNCH/FIRE') 
                self.round_timer.activate()
            self.blocks_left = 0
            self.gold_blocks = 0
            for block in self.block_sprites.sprites():
                if block.block_type != 'D':
                    self.blocks_left += 1
                else:
                    self.gold_blocks += 1
            # print(self.blocks_left, self.gold_blocks)

            self.spawn_frame_timer.activate()
            self.init_state = False
        if not self.round_timer.active:
            self.spawn_frame_timer.update()

    def default(self):
        if self.init_state:
            self.extend_timer.deactivate()
            self.laser_timer.deactivate()
            self.extend_timer.duration = 0
            self.laser_timer.duration = 0
            self.extend_index = 0
            self.set_extend_image()
            if not self.endball_sprites and self in self.player_sprites:
                self.endball_sprites.add(self.endball1)
                self.endball_sprites.add(self.endball2)
            self.endball1.laser_mode = False
            self.endball2.laser_mode = False
            self.endball1.retracted = False
            self.endball2.retracted = False
            self.init_state = False

    def teleporting(self):
        if self.init_state:
            print('teleporting')
            self.sound_played = False
            self.init_state = False

        if self.rect.right < WIDTH - MARGIN:
            self.teleporter_sprites.empty()
            self.state = 'default'
            self.init_state = True

        self.pos.x += 1
        self.rect.x = round(self.pos.x)
        self.endball1.rect.midleft = self.rect.midleft
        self.endball2.rect.midright = self.rect.midright

        if self.pos.x >= WIDTH and not self.sound_played:
            pygame.mixer.Sound.play(self.teleport_sound)
            self.sound_played = True
            self.active = False
            self.points_list = [100 for i in range(100)]
            self.score_timer.activate()
            self.next_stage = True

    def extended(self):
        if self.init_state:
            # print('extended')
            self.init_state = False
        self.extend_timer.update()

    def lasered(self):
        if self.init_state:
            # print('lasered')
            self.endball1.retracted = False
            self.endball2.retracted = False
            self.endball1.laser_mode = True
            self.endball2.laser_mode = True
            self.init_state = False
        self.laser_timer.update()

    ##############################################################################################
    ##                                                                                          ##
    ##                                      update                                              ##
    ##                                                                                          ##
    ##############################################################################################

    def update(self, dt): # called from main.run()
        if self.score_timer.active:
            self.score_timer.update()

        if self.sticky_timer_player.active:
            self.sticky_timer_player.update()
        
        if self.state != 'spawning' and not self.blocks_left:
            self.set_next_stage()
            
        self.states[self.state]()
            
        self.old_rect = self.rect.copy()

        if not settings.PAUSED and self.active:
            self.input()
            self.pos.x += self.direction.x * self.speed * dt
            self.rect.x = round(self.pos.x)
        self.upgrade_collide()
        self.screen_constraint()
        self.endball_sprites.update()
        # self.draw_player()


class Backgrounds(pygame.sprite.Sprite): # instanced in main.Game.__init__()
    def __init__(self, group, pos):
        super().__init__(group)
        self.images = [pygame.image.load('ExternalData/Backgrounds/BG_Blue.PNG'), 
                        pygame.image.load('ExternalData/Backgrounds/BG_Green.PNG'), 
                        pygame.image.load('ExternalData/Backgrounds/BG_BlueWire.PNG'), 
                        pygame.image.load('ExternalData/Backgrounds/BG_Red.PNG')]
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)


class Block(pygame.sprite.Sprite): # instanced in main.Game.setup_blocks()
    ''' Block objects for Breakout '''
    def __init__(self, 
                player, 
                pos, 
                image, 
                PU_images, 
                sparkle_images, 
                block_type, 
                powerup_type, 
                powerup_sprites, 
                block_sprites, 
                sparkle_sprites,  
                stage_number):

        super().__init__(block_sprites)
        self.player = player
        self.image = image
        self.powerup_type = powerup_type
        self.powerup_sprites = powerup_sprites
        self.block_sprites = block_sprites
        self.sparkle_sprites = sparkle_sprites
        self.pos = pos
        self.stage_number = stage_number
        self.health = 1
        self.sparkle_images = []
        self.powerups_remaining = 0
        # WBGROPYETD
        points_dict = {'W': 50, 'B': 100, 'G': 80, 'R': 90, 'O': 60, 'P': 110, 
                    'Y': 120, 'E': 50 * (stage_number + 1), 'T': 70, 'D': 0}
        self.points = points_dict[block_type]

        if block_type == 'E': # 50 * stage number
            self.health = 2 + stage_number // 8
            self.sparkle_images = sparkle_images

        elif block_type == 'D': #
            self.health = 255
            self.sparkle_images = sparkle_images

        # self.rect = self.image.get_rect(topleft = pos)
        self.rect = pygame.Rect(0, 0, 54, 29)
        self.rect.topleft = pos
        self.old_rect = self.rect.copy()
        self.block_type = block_type
        self.sparkle = None

        # P = extra paddle, B = teleport, L = lasers, D = multiball, S = slow, C = catch, E = wider paddle

        if self.powerup_type:# in 'PBLDSCE':
            self.powerup_sprite = PowerUp(self.powerup_type, self.rect.topleft + Vector2(3, 0), PU_images)
            self.powerups_remaining = 1

    def get_damage(self, amount): # called from ball.collision()
        if self.health != 255:
            self.health -= amount
        if self.powerup_type and self.powerups_remaining > 0 and not self.player.demo_mode:
            self.powerup_sprites.add(self.powerup_sprite)
            self.powerups_remaining -= 1

        if self.health == 255: # immortal block
            Sparkle(self.sparkle_images, self.pos, self.sparkle_sprites)
        elif self.health > 0:
            self.sparkle = Sparkle(self.sparkle_images, self.pos, self.sparkle_sprites)
        elif self.health == 0:
            self.die()

    def die(self):
        if self.sparkle:
            self.sparkle.kill()
        if self.player.alive():
            self.player.update_score(self.points)
        # self.shadow.kill()
        self.player.blocks_left -= 1
        self.kill()


class Ball(pygame.sprite.Sprite): # instanced in main.Game.run()
    ''' ball for breakout with collisions '''
    def __init__(self, 
                image, 
                player_sprites, 
                ball_sprites, 
                explosion_sprites, 
                player, 
                block_sprites,
                enemy_sprites,  
                extraball, 
                paddle_hit_sound, 
                inf_hit_sound, 
                block_hit_sound, 
                ball_catch_sound):

        super().__init__(ball_sprites)
        self.image = image
        self.player_sprites = player_sprites
        self.ball_sprites = ball_sprites
        self.explosion_sprites = explosion_sprites
        self.player = player
        self.block_sprites = block_sprites
        self.enemy_sprites = enemy_sprites
        self.rect = self.image.get_rect(midbottom = self.player.rect.midtop)
        self.hitbox = pygame.sprite.Sprite()
        self.hitbox.image = pygame.Surface((8, 8))
        self.hitbox.image.fill((255, 0, 0))
        self.hitbox.rect = self.hitbox.image.get_rect(midtop = self.rect.midtop)
        self.hitbox_old_rect = self.hitbox.rect.copy()
        
        self.old_rect = self.rect.copy()
        self.pos = Vector2(self.rect.topleft)
        self.offset_on_paddle = 0
        self.rect.midbottom = (self.player.rect.midtop[0] + self.offset_on_paddle, self.player.rect.top)

        self.directions = [Vector2(-1, -.5), Vector2(-1, -1), Vector2(-.5, -1), 
                        Vector2(.5, -1), Vector2(1, -1), Vector2(1, -.5)]
        self.direction = self.directions[3].copy()
        self.vel = self.direction.normalize()
        self.speed = 300
        self.active = False

        self.shadow = pygame.sprite.Sprite()
        self.shadow.image = pygame.Surface((self.image.get_size())).convert_alpha()
        self.shadow.image.fill((0, 0, 0, 0))
        self.shadow.rect = self.shadow.image.get_rect()
        pygame.draw.circle(self.shadow.image, (0, 0, 0, 100), self.shadow.rect.center, self.shadow.image.get_width() // 2)
        # self.shadow_sprites.add(self.shadow)
        self.explosion_sprites.add(self.shadow)

        self.sticky_timer_ball = Timer(10000, self.activate)
        self.sticky_timer_ball.activate()

        if extraball:
            self.pos = self.ball_sprites.sprites()[0].pos.copy()
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))
            self.active = True
            self.sticky_timer_ball.deactivate()
        self.paddle_hit_sound = paddle_hit_sound
        self.inf_hit_sound = inf_hit_sound
        self.block_hit_sound = block_hit_sound
        self.ball_catch_sound = ball_catch_sound
        self.history = []
        self.old_history = []
        self.repeats = 0

    def die(self):
        self.shadow.kill()
        self.kill()

    def set_speed(self, speed):
        self.speed = speed

    def activate(self):
        self.active = True
        self.sticky_timer_ball.deactivate()

    def window_collision(self, direction): # called from self.update()
        if direction == 'horizontal':
            if self.rect.left < MARGIN:
                self.rect.left = MARGIN
                self.pos.x = self.rect.x
                self.direction.x *= -1
            elif self.rect.right > WIDTH - MARGIN:
                self.rect.right = WIDTH - MARGIN
                self.pos.x = self.rect.x
                self.direction.x *= -1

        elif direction == 'vertical':
            if self.rect.top < TOPMARGIN + 10:
                self.rect.top = TOPMARGIN + 10
                self.pos.y = self.rect.y
                self.direction.y *= -1
            elif self.rect.bottom > HEIGHT + 99:
                if not self.ball_sprites.sprites():
                    self.player.active = False
                self.die()

    def collision(self, direction): # called from self.update()
        if self.repeats:
            print('repeats', self.repeats)
        # collisions with blocks
        hitbox_sprites = pygame.sprite.spritecollide(self.hitbox, self.block_sprites, False)
        if hitbox_sprites:
            sprite = hitbox_sprites[0] # ball can collide with only one block at a time, get the first
            # check for repeats
            # if sprite.block_type == 'D': # must be an immortal block to be relevent
            #                              # any other block will die and never be hit again
            #     self.history.append(sprite)
            #     if self.history.count(sprite)  == 3:
            #         mid_index = [index for index, block in enumerate(self.history) if block == sprite][1]
            #         first = self.history[:mid_index + 1]
            #         second = self.history[mid_index:]
            #         if first == second:
            #             self.repeats += 1
            #             self.history = second
            #         else:
            #             self.repeats = 0
            #             self.history = []
            # else:
            #     self.repeats = 0

            if hitbox_sprites[0].health == 1:
                pygame.mixer.Sound.play(self.block_hit_sound)
            else:
                pygame.mixer.Sound.play(self.inf_hit_sound)
            if direction == 'horizontal':
                if self.hitbox.rect.right >= sprite.rect.left and self.hitbox_old_rect.right <= sprite.old_rect.left:
                    self.hitbox.rect.right = sprite.rect.left - 1
                    self.rect.midtop = self.hitbox.rect.midtop
                    self.pos.x = self.rect.x
                    self.direction.x *= -1
                if self.hitbox.rect.left <= sprite.rect.right and self.hitbox_old_rect.left >= sprite.rect.right:
                    self.hitbox.rect.left = sprite.rect.right + 1
                    self.rect.midtop = self.hitbox.rect.midtop
                    self.pos.x = self.rect.x
                    self.direction.x *= -1
                    self.horizontal = True
                sprite.get_damage(1)
                    

            if direction == 'vertical':
                # for sprite in hitbox_sprites:
                if self.hitbox.rect.bottom >= sprite.rect.top and self.hitbox_old_rect.bottom <= sprite.old_rect.top:
                    self.hitbox.rect.bottom = sprite.rect.top - 1
                    self.rect.midtop = self.hitbox.rect.midtop
                    self.pos.y = self.rect.y
                    self.direction.y *= -1
                    self.vertical = True
                if self.hitbox.rect.top <= sprite.rect.bottom and self.hitbox_old_rect.top >= sprite.rect.bottom:
                    self.hitbox.rect.top = sprite.rect.bottom + 1
                    self.rect.midtop = self.hitbox.rect.midtop
                    self.pos.y = self.rect.y
                    self.direction.y *= -1
                    self.vertical = True
                sprite.get_damage(1)

        # collisions with player and enemies
        # overlap_sprites = pygame.sprite.spritecollide(self, self.player_sprites, False)
        # enemy_overlaps = pygame.sprite.spritecollide(self, self.enemy_sprites, False)
        # if enemy_overlaps:
        #     for enemy in enemy_overlaps:
        #         overlap_sprites.append(enemy)
        overlap_sprites = []
        if self.enemy_sprites:
            for enemy in self.enemy_sprites.sprites():
                if self.rect.colliderect(enemy):
                    overlap_sprites.append(enemy)
        if self.rect.colliderect(self.player.rect):
            overlap_sprites.append(self.player)

        if overlap_sprites:
            if direction == 'horizontal':
                for sprite in overlap_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left - 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right + 1
                        self.pos.x = self.rect.x
                        self.direction.x *= -1

                    self.collide_overlap_sprites(sprite)

            if direction == 'vertical':
                for sprite in overlap_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom + 1
                        self.pos.y = self.rect.y
                        self.direction.y *= -1

                    self.collide_overlap_sprites(sprite)
    
    def collide_overlap_sprites(self, sprite):
        if getattr(sprite, 'enemy', None):
            sprite.die()
        if getattr(sprite, 'isPlayer', None) and self.rect.centery < self.player.rect.top + 5:
            # self.repeats = 0
            if self.player.sticky and not settings.CHEATS:
                pygame.mixer.Sound.play(self.ball_catch_sound)
                self.active = False
                self.sticky_timer_ball.activate()
            else:
                pygame.mixer.Sound.play(self.paddle_hit_sound)
            self.offset_on_paddle = self.rect.centerx - self.player.rect.centerx
            if self.direction.x > 0:
                offset = self.rect.centerx - self.player.rect.left
            else:
                offset = self.player.rect.right - self.rect.centerx

            if offset < int(self.player.image.get_width() * .25):
                zone = 0
            elif offset < int(self.player.image.get_width() * .5):
                zone = 1
            elif offset < int(self.player.image.get_width() * .75):
                zone = 2
            else:
                zone = 3

            dir_x = abs(self.direction.x)
            dir_y = abs(self.direction.y)
            if dir_x < dir_y:
                # print('high angle at zone ', zone, ' from ', self.direction)
                if zone == 0:
                    if self.direction.x > 0:
                        self.direction.x = -1
                        self.direction.y = -1
                    else:
                        self.direction.x = 1
                        self.direction.y = -1
                elif zone == 1:
                    if self.direction.x > 0:
                        self.direction.x = -.5
                        self.direction.y = -1
                    else:
                        self.direction.x = .5
                        self.direction.y = -1
                elif zone == 2:
                    if self.direction.x > 0:
                        self.direction.x = .5
                        self.direction.y = -1
                    else:
                        self.direction.x = -.5
                        self.direction.y = -1
                elif zone == 3:
                    if self.direction.x > 0:
                        self.direction.x = 1
                        self.direction.y = -1
                    else:
                        self.direction.x = -1
                        self.direction.y = -1
            elif dir_x == dir_y:
                # print('medium angle at zone ', zone, ' from ', self.direction)
                if zone == 0:
                    if self.direction.x > 0:
                        self.direction.x = -1
                        self.direction.y = -1
                    else:
                        self.direction.x = 1
                        self.direction.y = -1
                elif zone == 1:
                    if self.direction.x > 0:
                        self.direction.x = -.5
                        self.direction.y = -1
                    else:
                        self.direction.x = .5
                        self.direction.y = -1
                elif zone == 2:
                    if self.direction.x > 0:
                        self.direction.x = 1
                        self.direction.y = -1
                    else:
                        self.direction.x = -1
                        self.direction.y = -1
                elif zone == 3:
                    if self.direction.x > 0:
                        self.direction.x = 1
                        self.direction.y = -.5
                    else:
                        self.direction.x = -1
                        self.direction.y = -.5
            elif dir_y < dir_x:
            # print('shallow angle at zone ', zone, ' from ', self.direction)
                if zone == 0:
                    if self.direction.x > 0:
                        self.direction.x = -1
                        self.direction.y = -.5
                    else:
                        self.direction.x = 1
                        self.direction.y = -.5
                elif zone == 1:
                    if self.direction.x > 0:
                        self.direction.x = -1
                        self.direction.y = -1
                    else:
                        self.direction.x = 1
                        self.direction.y = -1
                elif zone == 2:
                    if self.direction.x > 0:
                        self.direction.x = 1
                        self.direction.y = -.5
                    else:
                        self.direction.x = -1
                        self.direction.y = -.5
                elif zone == 3:
                    if self.direction.x > 0:
                        self.direction.x = 1
                        self.direction.y = -.5
                    else:
                        self.direction.x = -1
                        self.direction.y = -.5

    def update(self, dt): # called in main.run()
        self.shadow.rect.x = self.rect.x + BLOCK_WIDTH // 4
        self.shadow.rect.y = self.rect.y + BLOCK_HEIGHT // 2
        if not settings.PAUSED:
            if self.sticky_timer_ball.active:
                self.sticky_timer_ball.update()
                self.rect.midbottom = (self.player.rect.midtop[0] + self.offset_on_paddle, self.player.rect.top)
                self.pos.x = self.rect.left
                self.pos.y = self.rect.top
                self.hitbox.rect.midtop = self.rect.midtop
                return
            if self.direction.magnitude() != 0:
                self.vel = self.direction.normalize()
            self.old_rect = self.rect.copy()
            self.hitbox_old_rect = self.hitbox.rect.copy()

            self.horizontal = False
            self.vertical = False
            # self.pos = Vector2(pygame.mouse.get_pos())
            # self.rect.topleft = self.pos
            self.pos.x += self.vel.x * self.speed * dt
            self.rect.x = round(self.pos.x)
            self.hitbox.rect.midtop = self.rect.midtop
            self.collision('horizontal') # direction
            self.window_collision('horizontal') # direction

            # if not settings.PAUSED:
            self.pos.y += self.vel.y * self.speed * dt
            self.rect.y = round(self.pos.y)
            self.hitbox.rect.midtop = self.rect.midtop
            self.collision('vertical') # direction
            self.window_collision('vertical') # direction
            if self.vertical and self.horizontal:
                print('corner collision!!!!!!!!!!!!!!!!!!!!!')


class EnemySpawner(pygame.sprite.Sprite): # instanced in main.Game.run()
    # enemy_sprites, explosion_sprites, block_sprites, bumper_sprites, player, 
    def __init__(self, 
                spawner_images, 
                explosion_images, 
                enemy_images, 
                enemy_sprites, 
                explosion_sprites, 
                block_sprites, 
                bumper_sprites, 
                player,
                pos, 
                NPC_spawner_sprites, 
                climb_side, 
                NPC_die_sound):
        super().__init__(NPC_spawner_sprites)
        image = pygame.Surface((86, 29)).convert_alpha()
        self.images = spawner_images
        self.explosion_images = explosion_images
        self.enemy_images = enemy_images
        self.enemy_sprites = enemy_sprites
        self.explosion_sprites = explosion_sprites
        self.block_sprites = block_sprites
        self.bumper_sprites = bumper_sprites
        self.player = player
        self.NPC_spawner_sprites = NPC_spawner_sprites
        self.climb_side = climb_side
        self.NPC_die_sound = NPC_die_sound
        self.image = self.images[0]
        self.rect = self.image.get_rect(bottomleft = pos)
        self.pos = pos
        self.life_timer = Timer(2000, self.die)
        self.life_timer.activate()
        self.frame_index = 0
        self.frame_timer = Timer(100, self.next_enemyspawner_image)
        self.frame_timer.activate()

    def next_enemyspawner_image(self):
        self.frame_index += 1
        if self.frame_index > len(self.images) - 1:
            self.image = pygame.Surface((0, 0))
            self.frame_timer.deactivate()
            return
        self.image = self.images[self.frame_index]
        self.frame_timer.activate()
        if self.frame_index == 3:
            Enemy(self.explosion_images, self.enemy_images, self.enemy_sprites, self.explosion_sprites, self.block_sprites, 
                self.bumper_sprites, self.player, self.pos + Vector2(20, -20), self.climb_side, self.NPC_die_sound)

    def die(self):
        self.kill()

    def update(self):
        if not settings.PAUSED:
            self.frame_timer.update()
            self.life_timer.update()


class Particle(pygame.sprite.Sprite): # instanced in sprites.Player.explode()
    def __init__(self, 
                explosion_sprites, 
                vel, 
                image, 
                pos):

        super().__init__(explosion_sprites)
        self.explosion_sprites = explosion_sprites # for adding self

        self.image = image.convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.aging_speed = 40
        self.vel_speed = 500
        self.reversed = False

        self.shadow = pygame.sprite.Sprite()
        self.shadow.image = pygame.Surface((self.image.get_size())).convert_alpha()
        self.shadow.image.fill((0, 0, 0, 70))
        self.shadow.rect = self.shadow.image.get_rect(topleft = self.rect.topleft + Vector2(30, 30))
        explosion_sprites.add(self.shadow)

        self.life_timer = Timer(1200, self.die)
        self.life_timer.activate()

    def die(self):
        self.shadow.kill()
        self.kill()

    def update(self, dt):
        self.life_timer.update()
        self.shadow.rect.topleft = self.rect.topleft + Vector2(30, 30)
        self.pos += self.vel * self.vel_speed * dt
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        # self.vel_speed -= 20
        self.vel.y += .002
        if self.rect.left < MARGIN or self.rect.right > WIDTH - MARGIN or self.rect.top < TOPMARGIN:
            self.die()
        self.shadow.pos = self.rect.topleft + Vector2(30, 30)


class EndBalls(pygame.sprite.Sprite): # instanced in sprites.Player.__init__()
    def __init__(self, 
                endball_sprites, 
                player, 
                side):
        super().__init__(endball_sprites)
        self.player = player
        self.side = side
        
        self.images = import_folder('ExternalData/PaddleSprites/endballs')

        self.image = self.images[0]
        self.rect = self.image.get_rect(center = (10, 10))
        self.pos = Vector2(self.rect.midleft)
        self.laser_mode = False
        self.retracted = False
        self.frame_index = 0
        self.frame_timer = Timer(150, self.next_endball_image)
        self.frame_timer.activate()

    def next_endball_image(self):
        self.frame_index += 1
        self.frame_index = self.frame_index % len(self.images)
        self.image = self.images[self.frame_index]
        self.frame_timer.activate()

    def update(self):
        self.frame_timer.update()
        if self.laser_mode:
            if self.side == 'left':
                self.rect.midleft = self.player.rect.midleft + Vector2(9, -2)
                return
            self.rect.midright = self.player.rect.midright + Vector2(-9, -2)
        elif self.retracted:
            if self.side == 'left':
                self.rect.midright = self.player.rect.center
                return
            self.rect.midleft = self.player.rect.center
            
        else:
            if self.side == 'left':
                self.rect.midleft = self.player.rect.midleft
                return
            self.rect.midright = self.player.rect.midright
            

class Teleporter(pygame.sprite.Sprite): # instanced in sprites.Player.upgrade_collide()
    def __init__(self, player, teleporter_sprites, teleporter_images, pos):
        super().__init__(teleporter_sprites)
        self.player = player
        self.teleporter_sprites = teleporter_sprites
        self.images = teleporter_images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = (pos[0], pos[1]))
        self.image_index = 0
        self.frame_timer = Timer(60, self.next_teleporter_image)
        self.life_timer = Timer(6000, self.remove_teleporter)
        self.life_timer.activate()
        self.frame_timer.activate()

    def next_teleporter_image(self):
        self.image_index += 1
        self.image_index = self.image_index % len(self.images)
        self.image = self.images[self.image_index]
        self.frame_timer.activate()

    def remove_teleporter(self):
        self.kill()

    def update(self):
        if pygame.sprite.spritecollide(self.player, self.teleporter_sprites, False) and not settings.CHEATS:
            if self.player.state != 'teleporting':
                self.player.state = 'teleporting'
                self.player.init_state = True
            self.life_timer.duration += 10
        self.frame_timer.update()
        self.life_timer.update()


class Bullet(pygame.sprite.Sprite): # instanced in sprites.Player.shoot() # runtime
    def __init__(self, 
                player, 
                bullet_sprites, # goes into
                block_sprites, # collides with
                enemy_sprites, # collides with
                pos, 
                splash_images): # gets passed to BulletSplash() instanced here
        super().__init__(bullet_sprites)
        self.player = player
        self.bullet_sprites = bullet_sprites
        self.block_sprites = block_sprites
        self.enemy_sprites = enemy_sprites
        self.image = pygame.Surface((6, 10))
        self.rect = self.image.get_rect(midbottom = pos)
        self.image.fill((255, 255, 255, 255))
        self.pos = pos
        self.direction = Vector2(0, -1)
        self.speed = 600
        self.splash_images = splash_images

    def block_collide(self):
        overlap_sprites = pygame.sprite.spritecollide(self, self.block_sprites, False)
        if overlap_sprites:
            for sprite in overlap_sprites:
                if sprite.block_type != 'D':
                    sprite.get_damage(1)
            self.die()

    def enemy_collide(self):
        overlap_sprites = pygame.sprite.spritecollide(self, self.enemy_sprites, False)
        if overlap_sprites:
            for sprite in overlap_sprites:
                sprite.die()
            self.die()

    def die(self):
        BulletSplash(self.bullet_sprites, self.pos, self.splash_images)
        # self.shadow.kill()
        self.kill()

    def update(self, dt):
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.block_collide()
        self.enemy_collide()
        if self.rect.top < TOPMARGIN:
            self.die()


class BulletSplash(pygame.sprite.Sprite): # instanced in sprites.Bullet.die()
    def __init__(self, group, pos, images):
        super().__init__(group)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.life_timer = Timer(300, self.die)
        self.life_timer.activate()
        self.frame_timer = Timer(150, self.next_bulletsplash_image)
        self.frame_timer.activate()

    def next_bulletsplash_image(self):
        self.image = self.images[1]

    def die(self):
        self.kill()

    def update(self, dt):
        self.frame_timer.update()
        self.life_timer.update()


class Sparkle(pygame.sprite.Sprite): # instanced in Block.get_damage()
    def __init__(self, 
                images, 
                pos, 
                groups):
        super().__init__(groups)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = pos

        self.frame_index = 0
        self.frame_timer = Timer(50, self.next_sparkle_image)
        self.frame_timer.activate()

    def die(self):
        self.kill()

    def next_sparkle_image(self):
        self.frame_index += 1
        if self.frame_index > 4:
            self.die()
        else:
            self.image = self.images[self.frame_index]
            self.frame_timer.activate()

    def update(self): # called from main.run()
            self.frame_timer.update()


class PowerUp(pygame.sprite.Sprite): # instanced in sprites.Block.__init__()
    def __init__(self, powerup_type, pos, images):
        super().__init__()
        self.powerup_type = powerup_type
        self.images = images
        self.image = self.images[0]
        self.rect = self.images[0].get_rect(topleft = pos)
        self.pos = Vector2(pos)
        self.pos.y = self.rect.y

        self.movement_speed = 150
        self.direction = Vector2(0, 1)
        self.active = True
        self.frame_index = 0
        self.frame_timer = Timer(50, self.next_powerup_image)
        self.frame_timer.activate()

    def next_powerup_image(self):
        self.frame_index += 1
        self.frame_index = self.frame_index % len(self.images)
        self.image = self.images[self.frame_index]
        self.frame_timer.activate()

    def die(self):
        self.kill()

    def update(self, dt):
        self.frame_timer.update()
        # if self.active:
        if not settings.PAUSED:
            self.pos.y += self.movement_speed * dt

        self.rect.y = round(self.pos.y)

        if self.rect.y > HEIGHT + 50:
            self.die()


class Enemy(pygame.sprite.Sprite): # instanced in sprites.EnemySpawner.next_image()
    def __init__(self, 
                explosion_images, 
                images, 
                enemy_sprites, 
                explosion_sprites, 
                block_sprites, 
                bumper_sprites, 
                player, 
                pos, 
                climb_side, 
                NPC_die_sound):
        super().__init__(enemy_sprites)
        self.enemy_sprites = enemy_sprites
        self.explosion_sprites = explosion_sprites
        self.block_sprites = block_sprites
        self.bumper_sprites = bumper_sprites
        self.player = player
        self.pos = Vector2(pos)
        self.explosion_images = explosion_images
        self.images = images
        self.image = self.images[0]
        self.NPC_die_sound = NPC_die_sound
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.image.get_width(), self.image.get_height() - 10)
        self.old_rect = self.rect.copy()
        self.direction = Vector2(0, 1)
        self.top_bumper = EnemyBumper(bumper_sprites, (self.image.get_width() - 6, 3)) # group, size
        self.bottom_bumper = EnemyBumper(bumper_sprites, (self.image.get_width() - 6, 3))
        self.left_bumper = EnemyBumper(bumper_sprites, (3, self.rect.size[1]))
        self.right_bumper = EnemyBumper(bumper_sprites, (3, self.rect.size[1]))

        self.active = True
        self.moving = True
        self.fleeing = False
        self.movement_speed = 80
        self.waypoint_index = 0
        self.image_index = 0
        self.last_border_hit = 'left'

        self.waypoints = []
        # self.dive_waypoints = [Vector2(0, 98), Vector2(31, 145), Vector2(94, 166), 
        #                     Vector2(170, 154), Vector2(207, 97), Vector2(184, 22), 
        #                     Vector2(110, -2),  Vector2(42, 29), Vector2(1, 119), 
        #                     Vector2(0, 204), Vector2(36, 256), Vector2(94, 295), 
        #                     Vector2(139, 342), Vector2(149, 412), Vector2(149, 600)]
        self.dive_waypoints = [Vector2(2, 77), Vector2(27, 113), Vector2(78, 114), 
                            Vector2(108, 75), Vector2(110, 31), Vector2(143, -2), 
                            Vector2(198, -3), Vector2(228, 30), Vector2(230, 78), 
                            Vector2(190, 115), Vector2(133, 114), Vector2(104, 65), 
                            Vector2(102, 29), Vector2(71, -6), Vector2(20, -7), 
                            Vector2(-6, 25), Vector2(-7, 84), Vector2(31, 127), 
                            Vector2(76, 153), Vector2(135, 156), Vector2(193, 156), 
                            Vector2(232, 190), Vector2(232, 235), Vector2(187, 275), 
                            Vector2(148, 333), Vector2(148, 387), Vector2(149, 440)]

        self.enemy = True
        self.frame_timer = Timer(50, self.next_enemy_image)
        self.frame_timer.activate()

        self.init_state = True
        self.state = 'spawning'
        self.states = {'spawning': self.spawning, 
                        'dropping': self.dropping,
                        'patrolling': self.patrolling, 
                        'block_climb': self.block_climb, 
                        'wall_climb': self.climb_right_wall, 
                        'follow_waypoints': self.follow_waypoints, 
                        'retreat': self.retreat
                        }

        self.dive_height = 500
        self.climb_side = climb_side
        if self.climb_side == 'right':
            self.states['wall_climb'] = self.climb_right_wall
            self.init_direction = Vector2(1, 0)
        else:
            self.states['wall_climb'] = self.climb_left_wall
            self.init_direction = Vector2(-1, 0)

        ###########################################################################################
        ##                                                                                       ##
        ##                                       states                                          ##
        ##                                                                                       ##
        ###########################################################################################

    def spawning(self):
        if self.init_state:
            self.init_state = False
        if self.rect.top >= TOPMARGIN - 5:
            self.state = 'follow_waypoints'
            self.get_spawn_waypoints()
            self.init_state = True

    def follow_waypoints(self):
        if self.init_state:
            self.init_state = False
        waypoint = self.waypoints[0]
        self.direction = waypoint - self.rect.center
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        distsq = Vector2(self.rect.center).distance_squared_to(waypoint)
        if distsq  < 10:
            self.waypoints.pop(0)
            if not self.waypoints:
                self.state = 'dropping'
                self.init_state = True

    def dropping(self):
        if self.init_state:
            self.init_state = False
            self.direction.x = 0
            self.direction.y = 1
        # self.update_bumper_positions()
        if pygame.sprite.spritecollide(self.bottom_bumper, self.block_sprites, False):
            self.state = 'patrolling'
            self.init_state = True
        if self.rect.centery > self.dive_height:
            self.get_dive_waypoints()
            self.state = 'follow_waypoints'
            self.kill_bumpers()
            self.init_state = True


    def patrolling(self):
        if self.init_state:
            self.init_state = False
            self.direction = self.init_direction.copy()
        # self.update_bumper_positions()
        if not pygame.sprite.spritecollide(self.bottom_bumper, self.block_sprites, False):
            self.state = 'dropping'
            self.init_state = True
        if self.direction.x > 0:
            if pygame.sprite.spritecollide(self.right_bumper, self.block_sprites, False):
                self.state = 'block_climb'
                self.init_state = True
            if self.right_bumper.rect.right > WIDTH - MARGIN:
                if self.climb_side == 'right':
                    self.state = 'wall_climb'
                    self.init_state = True
                else:
                    self.rect.right = WIDTH - MARGIN - 3
                    self.direction.x = -1
                    self.direction.y = 0
                    self.init_direction.x = -1
        else:
            if pygame.sprite.spritecollide(self.left_bumper, self.block_sprites, False):
                self.state = 'block_climb'
                self.init_state = True
            if self.left_bumper.rect.left < MARGIN:
                if self.climb_side == 'left':
                    self.state = 'wall_climb'
                    self.init_state = True
                else:
                    self.rect.left = MARGIN + 3
                    self.pos.x = self.rect.left
                    self.direction.x = 1
                    self.init_direction.x = 1

    def block_climb(self):
        if self.init_state:
            self.init_state = False
            self.direction.x = 0
            self.direction.y = -1
        # self.update_bumper_positions()
        if self.init_direction.x > 0:
            if not pygame.sprite.spritecollide(self.right_bumper, self.block_sprites, False):
                self.pos.x += 3
                self.rect.x = round(self.pos.x)
                self.state = 'patrolling'
                self.init_state = True
            if pygame.sprite.spritecollide(self.top_bumper, self.block_sprites, False):
                self.init_direction.x = -1
                self.init_direction.y = 0
                self.state = 'dropping'
                self.init_state = True
        else:
            if not pygame.sprite.spritecollide(self.left_bumper, self.block_sprites, False):
                self.pos.x -= 3
                self.rect.x = round(self.pos.x)
                self.state = 'patrolling'
                self.init_state = True
            if pygame.sprite.spritecollide(self.top_bumper, self.block_sprites, False):
                self.init_direction.x = 1
                self.init_direction.y = 0
                self.state = 'dropping'
                self.init_state = True



    def climb_right_wall(self):
        if self.init_state:
            self.init_state = False
            self.direction.x = 0
            self.direction.y = -1
        # self.update_bumper_positions()
        if self.top_bumper.rect.top < TOPMARGIN:
            self.state = 'spawning'
            self.init_state = True
            self.init_direction.x = -1
            self.init_direction.y = 0
        if pygame.sprite.spritecollide(self.top_bumper, self.block_sprites, False):
            self.init_direction.x = -1
            self.init_direction.y = 0
            self.state = 'dropping'
            self.init_state = True

    def climb_left_wall(self):
        if self.init_state:
            self.init_state = False
            self.direction.x = 0
            self.direction.y = -1
        # self.update_bumper_positions()
        if self.top_bumper.rect.top < TOPMARGIN:
            self.state = 'spawning'
            self.init_state = True
            self.init_direction.x = 1
            self.init_direction.y = 0
        if pygame.sprite.spritecollide(self.top_bumper, self.block_sprites, False):
            self.init_direction.x = 1
            self.init_direction.y = 0
            self.state = 'dropping'
            self.init_state = True

    def retreat(self):
        if self.init_state:
            self.init_state = False
            self.direction.x = 0
            self.direction.y = -1
            self.init_direction.x = 1
        # self.update_bumper_positions()
        if self.top_bumper.rect.top < TOPMARGIN:
            self.waypoints = [Vector2(self.rect.center) + Vector2(50, 0)]
            if self.waypoints[0].x > WIDTH - MARGIN - 25:
                self.waypoints[0].x = WIDTH - MARGIN - 25
            self.state = 'follow_waypoints'
            self.init_state = True
        if pygame.sprite.spritecollide(self.top_bumper, self.block_sprites, False):
            self.state = 'patrolling'
            self.init_state = True

    ###########################################################################################
    ##                                                                                       ##
    ##                                state helpers                                          ##
    ##                                                                                       ##
    ###########################################################################################

    def get_spawn_waypoints(self):
        target1 = Vector2(random.randint(25, 75), TOPMARGIN + 16)
        target2 = target1 + Vector2(15, 15)
        self.spawn_waypoints = [target1, target2]
        for waypoint in self.spawn_waypoints:
            if self.rect.centerx > WIDTH // 2:
                waypoint.x = -waypoint.x
            waypoint.x += self.rect.centerx
            self.waypoints.append(waypoint)

    def get_dive_waypoints(self):
        for waypoint in self.dive_waypoints:
            if self.rect.center[0] > WIDTH // 2:
                waypoint.x = -waypoint.x
            waypoint += self.rect.center
            self.waypoints.append(waypoint)
        self.waypoint_index = 0

    def update_bumper_positions(self):
        self.top_bumper.rect.topleft = (self.rect.left + 2, self.rect.top - 3)

        self.bottom_bumper.rect.topleft = (self.rect.left + 3, self.rect.bottom + 1)
        self.left_bumper.rect.topleft = (self.rect.left, self.rect.top + 2)
        self.right_bumper.rect.topleft = (self.rect.right - 3, self.rect.top + 2)

    def kill_bumpers(self):
        self.top_bumper.kill()
        self.bottom_bumper.kill()
        self.left_bumper.kill()
        self.right_bumper.kill()
            
    ###########################################################################################
    ##                                                                                       ##
    ##                                other methods                                          ##
    ##                                                                                       ##
    ###########################################################################################

    def next_enemy_image(self):
        self.image_index += 1
        self.image_index = self.image_index % 36
        self.image = self.images[self.image_index]
        self.frame_timer.activate()


    def die(self):
        pygame.mixer.Sound.play(self.NPC_die_sound)
        self.player.int_score += 100
        EnemyExplosion(self.explosion_sprites, self.pos - Vector2(10, 5), self.explosion_images)
        self.top_bumper.kill()
        self.bottom_bumper.kill()
        self.left_bumper.kill()
        self.right_bumper.kill()
        self.kill()

    def make_waypoints(self): # not currently used, used for making new list of dive waypoints
        return
        # mouse = pygame.mouse.get_pos()
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()
        #         sys.exit()
        #     elif event.type == pygame.MOUSEBUTTONDOWN:
        #         if event.button == 1:
        #             print('mouse clicked')
        #             print(Vector2(mouse) - Vector2(self.rect.center))
        #             self.waypoints.append(Vector2(mouse) - Vector2(self.rect.center))
        #             print(self.waypoints)

    def collide_npcs(self, direction):
        overlap_sprites = pygame.sprite.spritecollide(self, self.enemy_sprites, False)
        if overlap_sprites:
            # print('hitting sprite')
            if direction == 'horizontal':
                for sprite in overlap_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        # self.rect.right = sprite.rect.left - 1
                        self.pos.x = self.rect.x
                        self.direction.x = -1
                        self.init_direction.x = -1
                        
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        # self.rect.left = sprite.rect.right + 1
                        # self.climbing_right = True
                        self.pos.x = self.rect.x
                        self.state = 'retreat'
                        self.init_state = True

            if direction == 'vertical':
                for sprite in overlap_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        # self.rect.bottom = sprite.rect.top
                        # self.pos.y = self.rect.y
                        self.state = 'retreat'
                        self.init_state = True

                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom and not sprite.fleeing:
                        # self.rect.top = sprite.rect.bottom
                        # self.pos.y = self.rect.y
                        self.direction.x = -1
                        self.init_direction.x = -1

    def update(self, dt):
        if self.frame_timer.active:
            self.frame_timer.update()
        if not settings.PAUSED:
            
            self.update_bumper_positions()
            self.states[self.state]()
            if self.state != 'follow_waypoints':
                self.collide_npcs('horizontal')
                self.collide_npcs('vertical')
            
            self.old_rect = self.rect.copy()
            self.old_pos = self.pos.copy()
            if self.moving:
                self.pos += self.direction * self.movement_speed * dt
            # self.pos = Vector2(pygame.mouse.get_pos())
            self.rect.x = round(self.pos.x)
            self.rect.y = round(self.pos.y)

            self.window_constraint()

            if self.pos.y > HEIGHT:
                self.kill() 
            if self.rect.colliderect(self.player.rect):
                self.die()

    def window_constraint(self):
        if self.rect.left < MARGIN - 3:
            self.rect.left = MARGIN + 2
            self.pos.x = self.rect.x
        if self.rect.right > WIDTH - MARGIN + 3:
            self.rect.right = WIDTH - MARGIN + 3
            self.pos.x = self.rect.x
        

class EnemyBumper(pygame.sprite.Sprite): # instanced in sprites.Enemy.__init__()
    def __init__(self, group, size):
        super().__init__(group)
        self.image = pygame.Surface(size)
        self.image.fill((0, 255, 0, 255))
        self.rect = self.image.get_rect()


class EnemyExplosion(pygame.sprite.Sprite): # instanced in sprites.Enemy.die()
    def __init__(self, group, pos, images):
        super().__init__(group)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.image_index = 0
        self.frame_timer = Timer(30, self.next_enemyexplosion_image)
        self.frame_timer.activate()
        # self.age = 0

    def die(self):
        self.kill()

    def next_enemyexplosion_image(self):
        self.image_index += 1
        if self.image_index > len(self.images) - 1:
            self.kill()
        else:
            self.image = self.images[self.image_index]
            self.frame_timer.activate()

    def update(self, dt):
        self.frame_timer.update()


class BlastFX(pygame.sprite.Sprite):
    def __init__(self, pos, images, group):
        super().__init__(group)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame_timer = Timer(100, self.next_blastFX_image)
        self.frame_timer.activate()
        self.frame_index = 0

    def die(self):
        self.kill()

    def next_blastFX_image(self):
        self.frame_index += 1
        if self.frame_index > len(self.images) - 1:
            self.die()
        else:
            self.image = self.images[self.frame_index]
            self.frame_timer.activate()

    def update(self, dt):
        self.frame_timer.update()


class Hatch(pygame.sprite.Sprite):
    def __init__(self, group, image, blastFX_images, paddle_image, pos, mothership_mask):
        super().__init__(group)
        self.explosion_sprites = group
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.blastFX_images = blastFX_images
        self.paddle_image = pygame.transform.rotozoom(paddle_image, 0, .7)
        self.mothership_mask = mothership_mask
        self.mothership_mask.set_alpha(0)
        self.pos = Vector2(pos)
        self.explode_timer = Timer(180, self.die)
        self.explode_timer.activate()

    def die(self):
        BlastFX((365, 625), self.blastFX_images, self.explosion_sprites)
        MotherShipMask((40, 590), self.mothership_mask, self.explosion_sprites)
        EscapeVaus(self.explosion_sprites, self.paddle_image, self.pos + Vector2(70, 30))
        new_image = self.image.copy()
        for y in range(0, new_image.get_height(), 16):
            for x in range(0, new_image.get_width(), 16):
                pos_x = self.rect.left + x
                pos_y = self.rect.top + y
                direction = Vector2(pos_x, pos_y) - Vector2(self.rect.center)
                direction.rotate_ip(random.randint(0, 50) - 25)
                new_image.set_clip((x, y, 16, 16))
                sprite = new_image.subsurface(new_image.get_clip()).convert_alpha()
                direction *= .07

                HatchParticle(self.explosion_sprites, 
                            sprite, 
                            (self.rect.topleft[0] + x, self.rect.topleft[1] + y), 
                            direction)
        self.kill()

    def update(self, dt):
        self.explode_timer.update()


class HatchParticle(pygame.sprite.Sprite):
    def __init__(self, explosion_sprites, image, pos, vel):
        super().__init__(explosion_sprites)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.life_timer = Timer(300, self.die)
        self.life_timer.activate()
        self.speed = 150

    def die(self):
        self.kill()

    def update(self, dt):
        self.life_timer.update()
        self.pos += self.vel * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)


class Ticker(pygame.sprite.Sprite):
    def __init__(self, ticker_sprites, pos, lines):
        super().__init__(ticker_sprites)
        self.pos = Vector2(pos)
        self.lines_buffer = lines # ex: ['blah blah', 'bleh bleh']
        self.image = pygame.Surface((WIDTH - MARGIN * 2, (len(lines) * 32) + (len(lines) - 3) * 32)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect(topleft = pos)
        self.x = 0; self.y = 0; self.letters_blitted = 0 # letters_blitted can be used for timing other events
        self.letter_buffer = [letter for letter in self.lines_buffer[0]] # populate letter buffer
        self.lines_buffer.pop(0) # letters added to letter buffer, revove the line now
        self.ticker_timer = Timer(33, self.next_letter) # letters appear every 33ms
        self.ticker_timer.activate()

    def next_letter(self):
        self.image.blit(scaled_surf(font.render(self.letter_buffer[0], False, 'white')), (self.x, self.y))
        self.x += 28 # first letter blitted, adjust where the next will go
        self.letter_buffer.pop(0) # and remove the letter from the buffer
        self.letters_blitted += 1 # inc counter
        if self.letter_buffer: # any letters left?
            self.ticker_timer.activate() # yes, reactivate the timer
        elif self.lines_buffer: # no letters left, any lines left?
            self.x = 0 # yes...reset x
            self.y += 64 # first line's been blitted, adjust y for the next line
            for letter in self.lines_buffer[0]: # repopulate the letter buffer
                self.letter_buffer.append(letter)
            self.lines_buffer.pop(0) # remove the first line from the buffer
        else:
            self.die()

    def die(self):
        self.kill()

    def update(self):
        if self.letter_buffer:
            self.ticker_timer.update()


class MotherShipMask(pygame.sprite.Sprite):
    def __init__(self, pos, image, explosion_sprites):
        super().__init__(explosion_sprites)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.alpha = 0
        self.alpha_step = .5
        self.alpha_timer = Timer(33, self.set_alpha)
        self.alpha_timer.activate()

    def die(self):
        self.kill()

    def set_alpha(self):
        self.image.set_alpha(self.alpha)
        self.alpha += self.alpha_step
        if self.alpha >= 100:
            self.alpha_step = -.5
        elif self.alpha <= 0:
            self.alpha_step = .5
    
    def update(self, dt):
        self.alpha_timer.update()


class EscapeVaus(pygame.sprite.Sprite):
    def __init__(self, group, image, pos):
        super().__init__(group)
        self.image = pygame.transform.rotozoom(image, 0, .8)
        self.image_backup = self.image.copy()
        self.rect = self.image.get_rect(center = pos)
        self.pos = Vector2(pos)
        self.direction = Vector2()
        self.waypoints = [Vector2(-160, -160) + self.rect.center]
        self.speed = 70
        self.scale_timer = Timer(78, self.scale)
        self.scale_timer.activate()
        self.angle = 0
        self.angle_step = 8
        self.scale = 1

    def follow_waypoints(self):
        waypoint = self.waypoints[0]
        self.direction = waypoint - self.rect.center
        if self.direction.length() > 0:
            self.direction.normalize_ip()
        distsq = Vector2(self.rect.center).distance_squared_to(waypoint)
        if distsq  < 25 * 25:
            self.waypoints.pop(0)
            if not self.waypoints:
                self.die()
    
    def scale(self):
        self.scale -= .025
        self.angle += self.angle_step
        if self.angle > 45:
            self.angle_step -= 2
        elif self.angle < -45:
            self.angle_step += 2
        loc = self.image.get_rect().center
        self.image = pygame.transform.rotozoom(self.image_backup, self.angle, self.scale)
        self.rect = self.image.get_rect(center = loc)
        self.scale_timer.activate()
    
    def die(self):
        self.kill()

    def update(self, dt):
        self.scale_timer.update()
        self.follow_waypoints()
        self.pos += self.direction * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        self.rect.centery = round(self.pos.y)


class Glare(pygame.sprite.Sprite):
    def __init__(self, images, pos, explosion_sprites):
        super().__init__(explosion_sprites)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame_index = 0
        self.frame_timer = Timer(75, self.next_glare_image)
        self.frame_timer.activate()

    def next_glare_image(self):
        self.frame_index += 1
        if self.frame_index > len(self.images) - 1:
            self.die()
        else:
            self.image = self.images[self.frame_index]
            self.frame_timer.activate()

    def die(self):
        self.kill()

    def update(self, dt):
        self.frame_timer.update()


class LaserAttack(pygame.sprite.Sprite):
    def __init__(self, group, images,  pos):
        super().__init__(group)
        self.explosion_sprites = group
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect()
        positions = [(0, 0), (-94,22), (-141,107), (-235,149), (-288,240)]
        self.sprites = [pygame.sprite.Sprite(), pygame.sprite.Sprite(), pygame.sprite.Sprite(), pygame.sprite.Sprite(), pygame.sprite.Sprite()]
        for index, sprite in enumerate(self.sprites):
            sprite.die = self.die
            sprite.image = images[index]
            sprite.rect = sprite.image.get_rect(topleft = pos + Vector2(positions[index]))
        self.add_sprite_timer = Timer(66, self.add_sprite)
        self.add_sprite_timer.activate()
        self.remove_sprite_timer = Timer(66, self.remove_sprite)
        self.explosion_sprites.add(self.sprites[0])
        self.sprites_reverse = self.sprites.copy()

    def die(self):
        self.kill()

    def add_sprite(self):
        if self.sprites:
            self.explosion_sprites.add(self.sprites[0])
            self.sprites.pop(0)
            self.add_sprite_timer.activate()
        else:
            self.add_sprite_timer.deactivate()
            self.remove_sprite_timer.activate()

    def remove_sprite(self):
        if self.sprites_reverse:
            self.explosion_sprites.remove(self.sprites_reverse[0])
            self.sprites_reverse.pop(0)
            self.remove_sprite_timer.activate()
        else:
            self.die()
        
    def update(self, dt):
        if self.add_sprite_timer.active:
            self.add_sprite_timer.update()
        if self.remove_sprite_timer.active:
            self.remove_sprite_timer.update()


class Fighter(pygame.sprite.Sprite):
    def __init__(self, group, pos, images):
        super().__init__(group)
        self.explosion_sprites = group
        self.image = images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = Vector2(pos)
        self.images = images
        self.frame_timer = Timer(20, self.next_fighter_image)
        self.frame_timer.activate()
        self.points = [(0, 0), (10, 7), (19, 13), (26, 19), (33, 25), (38, 31), (42, 37), (45, 43), 
            (47, 49), (48, 55), (47, 61), (46, 66), (44, 72), (40, 78), (36, 84), (31, 89), (25, 96), (18, 102), 
            (10, 108), (1, 115), (-9, 123), (-20, 130), (-34, 139), (-49, 147), (-67, 157), (-87, 167), 
            (-120, 177), (-164, 184), (-198, 184), (-225, 183), (-249, 181), (-271, 178), (-292, 175), 
            (-311, 171), (-330, 168), (-348, 164), (-365, 159), (-383, 155), (-402, 150), (-421, 145), 
            (-441, 139), (-462, 133), (-484, 127), (-506, 120), (-530, 112), (-554, 105), (-579, 96), 
            (-606, 87), (-633, 78), (-661, 68), (-691, 57), (-721, 46), (-753, 35), (-785, 22), (-819, 9)]

        self.points2 = [(0, 0), (5, 3), (10, 7), (14, 10), (19, 13), (23, 16), (26, 19), (30, 22), (33, 25), 
                    (36, 28), (38, 31), (40, 34), (42, 37), (44, 40), (45, 43), (46, 46), (47, 49), (47, 52), (48, 55), 
                    (48, 58), (47, 61), (47, 64), (46, 66), (45, 69), (44, 72), (42, 75), (40, 78), (38, 81), (36, 84), 
                    (33, 87), (31, 89), (28, 92), (25, 96), (21, 99), (18, 102), (14, 105), (10, 108), (6, 112), (1, 115), 
                    (-4, 119), (-9, 123), (-14, 127), (-20, 130), (-27, 134), (-34, 139), (-41, 143), (-49, 147), (-57, 152), 
                    (-67, 157), (-76, 162), (-87, 167), (-101, 172), (-120, 177), (-143, 181), (-164, 184), (-182, 184), 
                    (-198, 184), (-212, 184), (-225, 183), (-238, 182), (-249, 181), (-261, 180), (-271, 178), (-282, 177), 
                    (-292, 175), (-302, 173), (-311, 171), (-321, 170), (-330, 168), (-339, 166), (-348, 164), (-357, 162), 
                    (-365, 159), (-374, 157), (-383, 155), (-392, 153), (-402, 150), (-411, 148), (-421, 145), (-431, 142), 
                    (-441, 139), (-451, 136), (-462, 133), (-473, 130), (-484, 127), (-495, 123), (-506, 120), (-518, 116), 
                    (-530, 112), (-542, 109), (-554, 105), (-567, 100), (-579, 96), (-592, 92), (-606, 87), (-619, 83), 
                    (-633, 78), (-647, 73), (-661, 68), (-676, 63), (-691, 57), (-706, 52), (-721, 46), (-737, 40), (-753, 35), 
                    (-769, 28), (-785, 22), (-802, 16), (-819, 9)]
        
        self.frame_index = 0

    def next_fighter_image(self):
        self.image = self.images[self.frame_index]
        x, y = (self.points2[self.frame_index] + self.pos)
        self.rect = pygame.Rect(x, y, 48, 48)
        self.frame_index += 1
        if self.frame_index < len(self.images) - 1:
            self.frame_timer.activate()
        else:
            self.die()
    
    def die(self):
        self.kill()

    def update(self, dt):
        if self.frame_timer.active:
            self.frame_timer.update()


        '''
        # Blender script for making that list of positions
        import bpy

        object = bpy.data.objects["Cube"]
        curve = bpy.data.objects["NurbsPath"].data
        frames = curve.path_duration

        increment = 1

        co_list = []
        for desired_time in range(0, frames+1, increment):
            curve.eval_time = desired_time
            bpy.context.view_layer.update()
            co_list.append((object.matrix_world[0][3], object.matrix_world[2][3]))
        print(co_list)
        '''


class Engine(pygame.sprite.Sprite):
    def __init__(self, group, pos, images):
        super().__init__(group)
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft = pos)
        self.frame_index = 0
        self.frame_timer = Timer(65, self.next_engine_image)
        self.frame_timer.activate()

    def next_engine_image(self):
        self.frame_index = 0 if self.frame_index == 1 else 1
        self.image = self.images[self.frame_index]
        self.frame_timer.activate()

    def update(self, dt):
        if self.frame_timer.active:
            self.frame_timer.update()


class GlowRing(pygame.sprite.Sprite):
    def __init__(self, group, pos, image):
        super().__init__(group)
        self.explosion_sprites = group
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)
        self.pos = Vector2(pos)
        self.speed = 40
        self.min_pos = self.pos.y - 55
        self.rings = []
        self.frame_timer = Timer(300, self.add_ring)
        self.frame_timer.activate()
        self.wait_timer = Timer(2000, self.change_direction)
        self.remove_ring_timer = Timer(300, self.remove_ring)
        self.up = True

    def remove_ring(self):
        if self.rings:
            self.rings[0].kill()
            self.rings.pop(0)
            self.remove_ring_timer.activate()
        else:
            self.die()
    
    def die(self):
        self.kill()

    def change_direction(self):
        self.speed = -40
        self.pos.y += 2
        self.rect.y = round(self.pos.y)
        self.remove_ring_timer.activate()
        self.rings = self.rings[::-1]
        self.explosion_sprites.remove(self.rings[0])
        self.rings.pop(0)

    def add_ring(self):
        self.rings.append(GlowRingSingle(self.explosion_sprites, self.pos, self.image))
        self.frame_timer.activate()

    def update(self, dt):
        self.pos.y -= self.speed * dt
        self.rect.y = round(self.pos.y)
        # print(self.rect.y, self.min_pos)
        if self.rect.y < self.min_pos and self.up:
            self.speed = 0
            self.frame_timer.deactivate()
            self.wait_timer.activate()
            self.up = False
        if self.frame_timer.active:
            self.frame_timer.update()
        if self.wait_timer.active:
            self.wait_timer.update()
        if self.remove_ring_timer.active:
            self.remove_ring_timer.update()


class GlowRingSingle(pygame.sprite.Sprite):
    def __init__(self, group, pos, image):
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect(topleft = pos)

    def update(self, dt):
        return


class Notification(pygame.sprite.Sprite):
    def __init__(self, group, string, persist = False):
        super().__init__(group)
        self.notification_sprites = group
        self.image = small_font.render(string, False, 'white')
        self.rect = self.image.get_rect(topleft = (WIDTH - self.image.get_width(), 2))
        self.persist = persist
        self.timer = Timer(5000, self.die)
        self.spawning = True
        self.dying = False
        self.alpha = 255
        if not self.persist:
            self.timer.activate()

    def die(self):
        self.dying = True

    def update(self):
        self.rect.y = 16 * self.notification_sprites.sprites().index(self)
        if self.dying:
            self.alpha -= 1
            if self.alpha < 0:
                self.kill()
            self.image.set_alpha(self.alpha)

        if self.timer.active:
            self.timer.update()

