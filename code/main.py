
import pygame, sys, time, settings
from pygame.math import Vector2
from collections import deque
from random import choice
from timer import Timer
from sprites import *
from support import *

# THIS IS A WORK IN PROGRESS
# while it is completely playable, some features are still missing
# (boss, game ending, high score tables, ball acceleration, etc)

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


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Arkanoid')

        # define sprite groups
        # * = groups that are also killed in kill_sprites()
        self.ball_sprites = pygame.sprite.Group() # die when they leave the screen *
        self.sparkle_sprites = pygame.sprite.Group() # dies on a timer *
        self.explosion_sprites = pygame.sprite.Group() # *
        self.powerup_sprites = pygame.sprite.Group() #  dies on player collision or out of bounds *
        self.NPC_spawner_sprites = pygame.sprite.Group() #  dies on a timer *
        self.bullet_sprites = pygame.sprite.Group() # dies on collision with blocks, wall, npcs *
        self.enemy_sprites = pygame.sprite.Group() # dies on collision with player, bullets or out of bounds *
        self.bumper_sprites = pygame.sprite.Group() # dies with npc death *
        self.thruster_sprites = pygame.sprite.Group() # dies with Hatch() spawn during story *
        self.story_sprites = pygame.sprite.Group() # *

        self.ticker_sprites = pygame.sprite.GroupSingle() # dies at end of lines during story *
        self.teleporter_sprites = pygame.sprite.GroupSingle() # dies on timer or player escape *
        self.player_sprites = pygame.sprite.GroupSingle() # immortal
        self.background_sprites = pygame.sprite.GroupSingle() # immortal

        self.border_sprites = pygame.sprite.Group() # immortal
        self.border_shadow_sprites = pygame.sprite.Group() # immortal
        self.notification_sprites = pygame.sprite.Group() # die on timer (unless persist == True)
        self.block_sprites = pygame.sprite.Group() # die on ball or bullet collison and in setup_blocks()

        # load sounds
        self.opening_music = pygame.mixer.Sound('ExternalData/Sounds/opening_song.ogg')
        self.glare_sound = pygame.mixer.Sound('ExternalData/Sounds/glare_sound.ogg')
        self.insert_coin_sound = pygame.mixer.Sound('ExternalData/Sounds/insert_coin.ogg')
        self.stage_start_sound = pygame.mixer.Sound('ExternalData/Sounds/stage_start.ogg')
        self.NPC_die_sound = pygame.mixer.Sound('ExternalData/Sounds/npc_die.ogg')
        self. paddle_hit_sound = pygame.mixer.Sound('ExternalData/Sounds/paddlehit.ogg')
        self.inf_hit_sound = pygame.mixer.Sound('ExternalData/Sounds/inf_hit.ogg')
        self.block_hit_sound = pygame.mixer.Sound('ExternalData/Sounds/blockhit.ogg')
        self.shoot_sound = pygame.mixer.Sound('ExternalData/Sounds/player_shoot.ogg')
        self.paddle_grow_sound = pygame.mixer.Sound('ExternalData/Sounds/paddle_grow.ogg')
        self.one_up_sound = pygame.mixer.Sound('ExternalData/Sounds/one_up.ogg')
        self.teleport_sound = pygame.mixer.Sound('ExternalData/Sounds/teleport.ogg')
        self.player_die_sound = pygame.mixer.Sound('ExternalData/Sounds/player_die.ogg')
        self.ball_catch_sound = pygame.mixer.Sound('ExternalData/Sounds/ball_catch.ogg')

        # load single images
        self.taito_surf = pygame.image.load('ExternalData/Splash/taito.png').convert_alpha()
        self.starfield_surf = pygame.image.load('ExternalData/Backgrounds/starfield1.png').convert_alpha()
        self.ark_surf = pygame.image.load('ExternalData/Story/Ark/ark2.png').convert_alpha()
        self.ark_mask_surf = pygame.image.load('ExternalData/Story/Ark/ark_mask.png').convert_alpha()
        self.ark_hatch_surf = pygame.image.load('ExternalData/Story/Ark/ark_hatch.png').convert_alpha()
        self.ark_hatch_blown_surf = pygame.image.load('ExternalData/Story/Ark/ark_hatch_blown.png').convert_alpha()
        self.title_surf = pygame.image.load('ExternalData/Splash/Arkanoid.png').convert_alpha()
        self.game_over_surf = pygame.image.load('ExternalData/Splash/GameOver.png').convert_alpha()
        self.lives_left_surf = pygame.image.load('ExternalData/PaddleSprites/livesleft.png').convert_alpha()
        self.ball_surf = pygame.image.load('ExternalData/Ball/BallTex3.png').convert_alpha()
        # not currently used, experimenting for the ending animation that I haven't made
        self.tractorFX_image = pygame.image.load('ExternalData/Story/FX/TractorBeam/glowring1.png')

        # load image sequences
        # intro
        self.blastFX_images = import_folder('ExternalData/Story/FX/Explosion/')
        self.glare_images = import_folder('ExternalData/Story/FX/Glare/')
        self.intro_laser_images = import_folder('ExternalData/Story/FX/Lasers/')
        self.fighter_images = import_folder('ExternalData/Story/Fighter/')
        self.engine_images = import_folder('ExternalData/Story/Thrusters/Large/')
        self.thruster_images = import_folder('ExternalData/Story/Thrusters/Small/')
        # other
        self.sparkle_images = import_folder('ExternalData/Sparkle/')
        self.spawner_images = import_folder('ExternalData/Spawner/')
        self.explosion_images = import_folder('ExternalData/EnemyExplosion/')
        # player
        self.extend_images = import_folder('ExternalData/PaddleSprites/to_extended/')
        self.laser_images = import_folder('ExternalData/PaddleSprites/to_laser/')
        self.spawn_images = import_folder('ExternalData/PaddleSprites/spawn/')
        self.splash_images = import_folder('ExternalData/BulletFX/')
        self.teleporter_images = import_folder('ExternalData/Teleporter/')

        # populate dictionaries
        self.block_dict = {'W': [], 'B': [], 'G': [], 'R': [], 'O': [], 
                            'P': [], 'Y': [], 'E': [], 'T': [], 'D': []}
        for block in self.block_dict.keys():
            full_path = 'ExternalData/Blocks/' + block
            self.block_dict[block] = import_folder(full_path)

        self.powerups = {'C': [], 'E': [], 'P': [], 'L': [], 'D': [], 'S': [], 'B': []}
        for powerup in self.powerups.keys():
            full_path = 'ExternalData/PowerUpSprites/' + powerup
            self.powerups[powerup] = import_folder(full_path)

        self.enemy_dict = {'Cone': [], 'Pyramid': [], 'Balls': [], 'Cube': []}
        for enemy in self.enemy_dict.keys():
            full_path = 'ExternalData/NPCSprites/' + enemy
            self.enemy_dict[enemy] = import_folder(full_path)

        # create/load border sprites
        left_border = pygame.sprite.Sprite()
        left_border.image = pygame.image.load('ExternalData/Backgrounds/border_vertical.png').convert_alpha()
        left_border.rect = left_border.image.get_rect(topleft = (0, TOPMARGIN - 7))
        right_border = pygame.sprite.Sprite()
        right_border.image = left_border.image
        right_border.rect = right_border.image.get_rect(topleft = (WIDTH - 29, TOPMARGIN - 7))
        top_border = pygame.sprite.Sprite()
        top_border.image = pygame.image.load('ExternalData/Backgrounds/border_horizontal.png').convert_alpha()
        top_border.rect = top_border.image.get_rect(topleft = (0, TOPMARGIN - 36))
        # and border shadows
        left_shadow = pygame.sprite.Sprite()
        left_shadow.image = pygame.Surface((32, HEIGHT)).convert_alpha()
        left_shadow.image.fill((0, 0, 0, 90))
        left_shadow.rect = left_shadow.image.get_rect(topleft = (MARGIN - 4, TOPMARGIN - 7))
        top_shadow = pygame.sprite.Sprite()
        top_shadow.image = pygame.Surface((WIDTH - MARGIN * 2 - 24, 28)).convert_alpha()
        top_shadow.image.fill((0, 0, 0, 90))
        top_shadow.rect = top_shadow.image.get_rect(topleft = (MARGIN + 28, TOPMARGIN - 7))

        self.border_sprites.add(left_border, right_border, top_border)
        self.border_shadow_sprites.add(left_shadow, top_shadow)
        
        self.background = Backgrounds(self.background_sprites, (MARGIN - 10, TOPMARGIN - 7))

        # instance the player
        self.player = Player([self.bullet_sprites, # so player can add bullets during shoot
                            self.block_sprites, # sent to balls for multiball powerup
                            self.powerup_sprites, # collision with powerups
                            self.player_sprites, # ...
                            self.explosion_sprites, # for player explosion
                            self.teleporter_sprites, # so player can instance and add teleporter on powerup collision
                            self.enemy_sprites, # sent to balls and to bullets during player shoot
                            self.ball_sprites, # ...
                            self.notification_sprites], # for start stage notification
                            [self.paddle_hit_sound, # sounds
                            self.shoot_sound, 
                            self.paddle_grow_sound, 
                            self.one_up_sound, 
                            self.teleport_sound, 
                            self.inf_hit_sound, 
                            self.block_hit_sound, 
                            self.ball_catch_sound],
                            [self.ball_surf, # images
                            self.extend_images, 
                            self.laser_images, 
                            self.spawn_images, 
                            self.splash_images, 
                            self.teleporter_images], 
                            self.start_sparkles) # method for sparkling grey and gold blocks at stage starts

        # set initial state and dict with all states and their methods
        self.state = 'insert_coin'
        self.init_state = True
        self.states = {'insert_coin': self.insert_coin, 
                        'story': self.story, 
                        'demo': self.demo, 
                        'playing': self.playing,
                        'gameover': self.gameover, 
                        'dying': self.dying}
        self.active = False
        self.age = 0
        self.credits = 0
        self.ball_added = False
        self.debug = False
        self.enemy_controller = self.dump_enemies
        self.enemy_spawn_timer = Timer(30000, self.inc_current_enemy_max)
        self.end_stage_timer = Timer(1000, self.end_stage)
        self.feed_levels = [0, 3, 4, 5, 11, 16, 17, 18, 20, 21, 24, 26, 29, 31]
        self.skip_levels = [9, 22, 27, 32]
        self.dump_levels = [1, 2, 6, 7, 8, 10, 12, 13, 14, 15, 19, 23, 25, 28, 30, 33]

        # number of enemies to spawn at stage start during feed_enemies
        self.enemy_nums = [0, 8, 8, 1, 1, 
                            2, 8, 8, 8, 0, 
                            8, 0, 8, 8, 8, 
                            8, 0, 0, 0, 8, 
                            0, 0, 0, 0, 0, 
                            0, 0, 0, 0, 0, 
                            0, 0, 0]

        self.enemy_maxs = [3, 8, 8, 3, 3, 
                            3, 8, 8, 8, 0, 
                            8, 2, 8, 8, 8, 
                            8, 3, 3, 3, 8, 
                            2, 3, 3, 3, 3, 
                            3, 3, 3, 3, 3, 
                            3, 3, 3]

    def setup_new_game(self):
        self.stage = 0
        self.player.lives_left = 10 # overwrites default of 3 in Player() sprite
        self.player.int_score = 0
        if self.state == 'gameover':
            self.state = 'playing'
        self.init_state = True
        self.start_stage()

    def start_stage(self):
        print('starting stage', self.stage + 1)

        self.background.image = self.background.images[self.stage % 4]

        self.setup_blocks()

        if self.stage in self.feed_levels:
            self.enemy_controller = self.feed_enemies
        elif self.stage in self.dump_levels:
            self.enemy_controller = self.dump_enemies
        else:
            self.enemy_controller = self.skip_enemies
        self.current_enemy_max = self.enemy_nums[self.stage]

        pygame.mixer.Sound.stop(self.opening_music)
        pygame.mixer.Sound.play(self.stage_start_sound)

    def end_stage(self):
        # print('ending stage')
        self.kill_sprites()
        self.init_state = True
        self.end_stage_timer.deactivate()
        self.stage += 1
        if self.stage > len(BLOCK_MAPS) - 1:
            self.stage = 0
        self.start_stage()

    def setup_blocks(self):
        for block in self.block_sprites.sprites():
            block.die()
        for row_index, row in enumerate(BLOCK_MAPS[self.stage]):
            for col_index, col in enumerate(row):
                block_type = col
                if block_type != ' ':
                    x = col_index * (BLOCK_WIDTH + GAP_SIZE)
                    y = row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2

                    powerup_type = ''
                    if (col_index, row_index) in powerup_dicts[self.stage]:
                        powerup_type = powerup_dicts[self.stage][(col_index, row_index)]
                    powerup_type = choice('PLEDSCB') # comment this line to disable random powerup on every block
                    image = self.block_dict[block_type][0]
                    Block(  self.player, 
                            (x + MARGIN + GAP_SIZE + 1, y + Y_OFFSETS[self.stage] + TOPMARGIN), 
                            image, 
                            self.powerups[powerup_type], 
                            self.sparkle_images, 
                            block_type, 
                            powerup_type, 
                            self.powerup_sprites, self.block_sprites, self.sparkle_sprites, 
                            self.stage)

    def inc_credits(self):
        self.credits += 1
        self.credits = min(99, self.credits)
        pygame.mixer.Sound.play(self.insert_coin_sound)
        
    def kill_sprites(self):
        self.player.reset()
        for explosion in self.explosion_sprites.sprites():
            explosion.kill()
        for sprite in self.story_sprites.sprites():
            sprite.kill()
        for enemy in self.enemy_sprites.sprites():
            enemy.kill()
        for bumper in self.bumper_sprites.sprites():
            bumper.kill()
        for teleporter in self.teleporter_sprites.sprites():
            teleporter.kill()
        for bullet in self.bullet_sprites.sprites():
            bullet.kill()
        for ball in self.ball_sprites.sprites():
            ball.shadow.kill()
            ball.kill()
        self.ball_added = False
        for powerup in self.powerup_sprites.sprites():
            powerup.kill()
        for thruster in self.thruster_sprites.sprites():
            thruster.kill()
        for sparkle in self.sparkle_sprites.sprites():
            sparkle.kill()
        for spawner in self.NPC_spawner_sprites.sprites():
            spawner.kill()
        for ticker in self.ticker_sprites.sprites():
            ticker.kill()

    def start_sparkles(self): # gets passed to Player()
        for block in self.block_sprites.sprites():
            if block.block_type == 'D' or block.block_type == 'E':
                Sparkle(self.sparkle_images, block.pos, self.sparkle_sprites)
                
    def add_ball(self, extraball):
        self.player.add_ball(extraball)

    def player_follow_ball(self):
            offset = -5 if self.ball_sprites.sprites()[0].direction.x > 0 else 5
            self.player.rect.centerx = self.ball_sprites.sprites()[0].rect.centerx + offset
            self.player.screen_constraint()
            self.player.pos.x = self.player.rect.x

    ##############################################################################################
    ##                                                                                          ##
    ##                                     input                                                ##
    ##                                                                                          ##
    ##############################################################################################

    def get_events(self):
        for event in pygame.event.get():
            # print('getting events')
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # space, c, period, comma, p, right bracket, left bracket, up, m, l, d, pageup, pagedown, t
            elif event.type == pygame.KEYDOWN:# and self.player.state == 'default':
                if event.key == pygame.K_SPACE: # shoot, activate ball and self 
                    if self.player.laser_timer.active:
                        self.player.shoot()
                    if self.ball_sprites.sprites():
                        play_sound = False
                        for ball in self.ball_sprites.sprites():
                            ball.active = True
                            if ball.sticky_timer_ball.active:
                                play_sound = True
                                ball.sticky_timer_ball.deactivate()
                        if play_sound:
                            pygame.mixer.Sound.play(self.paddle_hit_sound)
                        self.active = True
                elif event.key == pygame.K_c: # toggle cheats
                    settings.CHEATS = not settings.CHEATS
                elif event.key == pygame.K_PERIOD: # increase ball speed
                    for ball in self.ball_sprites.sprites():
                        ball.speed += 400
                elif event.key == pygame.K_COMMA: # decrease ball speed
                    for ball in self.ball_sprites.sprites():
                        ball.speed -= 400
                elif event.key == pygame.K_p: # toggle pause
                    settings.PAUSED = not settings.PAUSED
                    if settings.PAUSED:
                        Notification(self.notification_sprites,   'PAUSED  ', True)
                        Notification(self.notification_sprites, 'PRESS P TO', True)
                        Notification(self.notification_sprites,   'RESUME  ', True)
                    else:
                        self.notification_sprites.empty()
                elif event.key == pygame.K_RIGHTBRACKET: # next stage
                    self.end_stage()
                elif event.key == pygame.K_LEFTBRACKET: # previous stage
                    self.stage -= 2
                    self.stage = self.stage % len(BLOCK_MAPS)
                    self.end_stage()
                elif event.key == pygame.K_UP: # add multiballs
                    if self.player in self.player_sprites:
                        self.player.add_multiballs()
                elif event.key == pygame.K_m: # laser
                    if self.player.active:
                        if self.player.state != 'to_laser' and self.player.state != 'lasered':
                            self.player.state = 'to_laser'
                            self.player.init_state = True
                        else:
                            self.player.laser_timer.duration += 8000
                elif event.key == pygame.K_l: # extend
                    if self.player.active:
                        if self.player.state != 'to_extend' and self.player.state != 'extended':
                            self.player.state = 'to_extend'
                            self.player.init_state = True
                        else:
                            self.player.extend_timer.duration += 8000
                elif event.key == pygame.K_d: # kill NPCs
                    for enemy in self.enemy_sprites.sprites():
                        enemy.die()
                elif event.key == pygame.K_PAGEUP: # NPC speed increase
                    for enemy in self.enemy_sprites.sprites():
                        enemy.movement_speed += 20
                elif event.key == pygame.K_PAGEDOWN: # NPC speed decrease
                    for enemy in self.enemy_sprites.sprites():
                        enemy.movement_speed -= 20
                elif event.key == pygame.K_t: # teleporter
                    Teleporter(self.player, 
                                self.teleporter_sprites, 
                                self.player.teleporter_images, 
                                (WIDTH - MARGIN + 3, HEIGHT - 148))

                for ball in self.ball_sprites.sprites():
                    ball.speed = max(400, min(3000, ball.speed))

    @staticmethod 
    def getAnyKey():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                return event.key

    @staticmethod
    def getMouseClick():
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    wait = False
 
    @staticmethod
    def getSpaceKey():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True

    ##############################################################################################
    ##                                                                                          ##
    ##                                  draw subs                                               ##
    ##                                                                                          ##
    ##############################################################################################
        
    def draw_stage(self):
        self.screen.fill((0, 0, 0))
        self.draw_scores()
        self.notification_sprites.update()
        self.notification_sprites.draw(self.screen)

        if self.state != 'story' and self.state != 'insert_coin':
            self.background_sprites.draw(self.screen)
            self.border_shadow_sprites.draw(self.screen)
            self.block_sprites.draw(self.screen)
            self.border_sprites.draw(self.screen)

    def draw_prompt(self):
        if self.credits:
            self.screen.blit(get_spaced_surf('PUSH', (0, 0, 0, 120)), (344, 556))
            self.screen.blit(get_spaced_surf('PUSH', 'white'), (338, 550))
            self.screen.blit(get_spaced_surf('ONLY 1 PLAYER BUTTON', (0, 0, 0, 120)), (124, 620))
            self.screen.blit(get_spaced_surf('ONLY 1 PLAYER BUTTON', 'white'), (118, 614))
        else:
            self.screen.blit(get_spaced_surf('INSERT COIN', (0, 0, 0, 120)), (250, 562))
            self.screen.blit(get_spaced_surf('INSERT COIN','white'), (244, 556))

    def draw_lives_left(self):
        for i in range(self.player.lives_left - 1):
            location = (MARGIN + 2 + i * (self.lives_left_surf.get_width() - 4), HEIGHT - 35)
            self.screen.blit(self.lives_left_surf, location)
    
    def draw_scores(self):
        self.screen.blit(get_spaced_surf('1UP   HIGH SCORE', 'red'), (92, 0))
        score_string = '00' if self.player.int_score == 0 else str(self.player.int_score)
        score_surf = get_spaced_surf(score_string, 'white')
        self.screen.blit(score_surf, (204 - score_surf.get_width(), 32))

        high_score_surf = get_spaced_surf(str(self.player.int_high_score), 'white')
        self.screen.blit(high_score_surf, (484 - high_score_surf.get_width(), 32))

    def draw_debug(self):
        for ticker in self.ticker_sprites.sprites():
            pygame.draw.rect(self.screen, 'red', ticker.rect, 1)
        for powerup in self.powerup_sprites.sprites():
            pygame.draw.rect(self.screen, 'red', powerup.rect, 1)
        for explosion in self.explosion_sprites.sprites():
            pygame.draw.rect(self.screen, 'red', explosion.rect, 1)
        for block in self.block_sprites.sprites():
            pygame.draw.rect(self.screen, 'red', block.rect, 1)
        if self.ball_sprites:
            for ball in self.ball_sprites.sprites():
                pygame.draw.rect(self.screen, 'red', ball.hitbox.rect)
                pygame.draw.rect(self.screen, 'red', ball.rect, 1)
        for enemy in self.enemy_sprites.sprites():
            pygame.draw.rect(self.screen, 'red', enemy.rect, 1)
            for waypoint in enemy.waypoints:
                pygame.draw.circle(self.screen, 'red', waypoint, 3)
        pygame.draw.rect(self.screen, 'red', self.player.rect, 2)
        self.bumper_sprites.draw(self.screen)
        
    ##############################################################################################
    ##                                                                                          ##
    ##                               enemy controls                                             ##
    ##                                                                                          ##
    ##############################################################################################
        
    def dump_enemies(self):
        self.age += 1
        if self.age % 200 == 0:
            if len(self.enemy_sprites) < 3 and not self.NPC_spawner_sprites.sprites():
                enemy = self.get_enemy()
                EnemySpawner(self.spawner_images, self.explosion_images, enemy, self.enemy_sprites, 
                            self.explosion_sprites, self.block_sprites, self.bumper_sprites, self.player, 
                            choice([(556, TOPMARGIN - 7), (155, TOPMARGIN - 7)]), 
                            self.NPC_spawner_sprites, choice(['left', 'right']), self.NPC_die_sound)

    def feed_enemies(self):
        if (len(self.enemy_sprites) < self.current_enemy_max) and not self.NPC_spawner_sprites.sprites():
            enemy = self.get_enemy()
            EnemySpawner(self.spawner_images, self.explosion_images, enemy, self.enemy_sprites, 
                        self.explosion_sprites, self.block_sprites, self.bumper_sprites, self.player, 
                        choice([(556, TOPMARGIN - 7), (155, TOPMARGIN - 7)]), 
                        self.NPC_spawner_sprites, choice(['left', 'right']), self.NPC_die_sound)

    def skip_enemies(self):
        return

    def get_enemy(self):
        if self.player.demo_mode:
            enemy = self.enemy_dict[choice(list(self.enemy_dict.keys()))]
        else:
            enemy = self.enemy_dict[list(self.enemy_dict.keys())[self.stage % 4]]
        return enemy

    ##############################################################################################
    ##                                                                                          ##
    ##                          timed events/state setters                                      ##
    ##                                                                                          ##
    ##############################################################################################
    
    def inc_current_enemy_max(self): # enemy control event
        if self.current_enemy_max < self.enemy_maxs[self.stage]:
            self.current_enemy_max += 1
            self.enemy_spawn_timer.activate()
        else:
            self.enemy_spawn_timer.deactivate()

    def add_fighter(self): # story event 
        Fighter(self.story_sprites, (652, 306), self.fighter_images)
        self.fighter_timer.deactivate()

    def add_laser(self):  # story event
        LaserAttack(self.story_sprites, self.intro_laser_images, (686, 394))
        self.laser_timer.deactivate()

    def add_hatch(self):  # story event
        Hatch(self.story_sprites, self.ark_hatch_surf, self.blastFX_images,
                        self.player.extend_images[0], (361, 657), self.ark_mask_surf)

    def add_explode(self):  # story event
        self.ark_exploded = True
        for thruster in self.thruster_sprites.sprites():
            thruster.kill()
        self.explode_timer.deactivate()

    def add_glare(self):  # story event
        Glare(self.glare_images, (225, 530),self. story_sprites)
        self.glare_timer.deactivate()
        pygame.mixer.Sound.play(self.glare_sound)

    def set_playing(self): # story event
        self.kill_sprites()
        self.state = 'playing'
        self.init_state = True
        self.setup_new_game()

    def set_demo(self): # insert_coin event
        self.kill_sprites()
        self.state = 'demo'
        self.init_state = True

    def set_insert_coin(self): # demo and gameover event
        self.kill_sprites()
        for block in self.block_sprites.sprites():
            block.kill()
        self.state = 'insert_coin'
        self.init_state = True
        
    ##############################################################################################
    ##                                                                                          ##
    ##                                     states                                               ##
    ##                                                                                          ##
    ##############################################################################################

    def insert_coin(self): # set by demo, gameover and __init__()
        if self.init_state:
            # self.getMouseClick()
            self.init_state = False
            if self.credits:
                Notification(self.notification_sprites, 'PRESS  SPACE')
                Notification(self.notification_sprites, 'TO START ')
            else:
                Notification(self.notification_sprites, 'PRESS ANY KEY')
                Notification(self.notification_sprites, 'TO INSERT COIN')
            self.insert_coin_timer = Timer(6000, self.set_demo)
            self.insert_coin_timer.activate()
            # insert_coin init complete, begin insert_coin loop

        # insert_coin loop
        # update
        self.insert_coin_timer.update()

        # draw
        self.screen.blit(self.taito_surf, (220, 700))
        self.screen.blit(self.title_surf, (48, 230))
        self.screen.blit(get_spaced_surf(chr(169) + ' 1986 TAITO CORP JAPAN', 'white'), (66, 800))
        self.screen.blit(get_spaced_surf('ALL RIGHTS RESERVED', 'white'), (130, 864))
        self.screen.blit(get_spaced_surf('CREDITS  '+str(self.credits), 'white'), (486, 940))
        self.draw_prompt()
        
        # player can increase credits if they want to or just press space to start
        key = self.getAnyKey()
        if key == pygame.K_SPACE: # if space key, begin story
            for sprite in self.notification_sprites.sprites():
                sprite.kill()
            self.state = 'story'
            self.init_state = True
        elif key: # if any other key, increase credits and update notification
            self.insert_coin_timer.activate()
            for sprite in self.notification_sprites.sprites():
                sprite.kill()
            Notification(self.notification_sprites, 'PRESS SPACE')
            Notification(self.notification_sprites, 'TO START ')
            self.inc_credits()
            
    def demo(self): # set by insert_coin
        if self.init_state:
            for ball in self.ball_sprites.sprites():
                ball.die()
            self.player.reset()
            self.player.state = 'spawning'
            self.player.init_state = True
            self.stage = choice([0, 2, 11, 17, 24])
            self.setup_blocks()
            if self.player not in self.player_sprites:
                self.player_sprites.add(self.player)
            if not self.player.endball_sprites:
                self.player.endball_sprites.add(self.player.endball1)
                self.player.endball_sprites.add(self.player.endball2)
            self.player.demo_mode = True
            self.init_state = False
            self.start_sparkles()
            self.enemy_controller = self.dump_enemies
            self.enemy_spawn_timer.activate()
            self.demo_timer = Timer(20000, self.set_insert_coin)
            self.demo_timer.activate()
            # demo init complete, begin demo loop

        # demo loop
        # update timer
        self.demo_timer.update()

        # demo update sprites
        self.player.update(self.dt)
        self.NPC_spawner_sprites.update()
        self.enemy_sprites.update(self.dt)
        self.explosion_sprites.update(self.dt)
        self.ball_sprites.update(self.dt)
        self.sparkle_sprites.update()
        self.enemy_controller()

        # demo draw
        self.NPC_spawner_sprites.draw(self.screen)
        self.enemy_sprites.draw(self.screen)
        self.explosion_sprites.draw(self.screen)
        self.ball_sprites.draw(self.screen)
        self.player.draw_player(self.screen)
        self.sparkle_sprites.draw(self.screen)
        self.screen.blit(self.title_surf, (48, 230))
        self.draw_prompt()

        # add ball
        if not self.ball_added and self.player.state == 'default':
            self.player.add_ball(True)
            self.ball_added = True

        # constrain player to ball
        if self.ball_added:
            self.player_follow_ball()

        # check input, if space, start the game, if anything else, inc credits and return to insert_coin
        key = self.getAnyKey()
        if key:
            for block in self.block_sprites.sprites():
                block.kill()
            self.kill_sprites()
            if key == pygame.K_SPACE:
                self.state = 'story'
                self.init_state = True
            else:
                self.inc_credits()
                self.state = 'insert_coin'
                self.init_state = True
                Notification(self.notification_sprites, 'PRESS SPACE')
                Notification(self.notification_sprites, 'TO START')

    def story(self): # set by insert_coin and demo
        if self.init_state:
            self.init_state = False
            if self.credits:
                self.credits -= 1
            # self.getMouseClick()
            self.kill_sprites()
            self.ark_image = self.ark_surf
            self.ark_exploded = False

            # instance flashing thrusters
            positions = [(47, 786), (47, 837), (400, 845), (400, 896)]
            for position in positions:
                Engine(self.thruster_sprites, position, self.engine_images)
            positions = [(230, 724), (365, 746)]
            for position in positions:
                Engine(self.thruster_sprites, position, self.thruster_images)

            # define lists for ticker
            self.ticker_deque = deque([['THE ERA AND TIME OF', 'THIS STORY IS UNKNOWN.', 
                                '                      '], 
                                ['AFTER THE MOTHERSHIP', '"ARKANOID" WAS DESTROYED,', 'A SPACECRAFT "VAUS"', 'SCRAMBLED AWAY FROM IT.', 
                                '                      '], 
                                ['BUT ONLY TO BE', 'TRAPPED IN SPACE WARPED', 'BY SOMEONE........', 
                                '                                                                ']])
            
            pygame.mixer.Sound.play(self.opening_music)
            # init and activate story event timers
            self.story_timer = Timer(10000, self.set_playing) # wait 10 seconds then change state to 'demo'
            self.fighter_timer = Timer(1300, self.add_fighter) # wait 1.3 seconds then spawn fighter
            self.laser_timer = Timer(1700, self.add_laser) # fighter shoots
            self.hatch_timer = Timer(2100, self.add_hatch) # hatch changes to show damage
            self.explode_timer = Timer(2400, self.add_explode) # hatch explodes and launches other animations 
            self.glare_timer = Timer(6100, self.add_glare) # finally, add a glare in the distance
            self.story_timer.activate() # activate timers
            self.fighter_timer.activate()
            self.laser_timer.activate()
            self.hatch_timer.activate()
            self.explode_timer.activate()
            self.glare_timer.activate()
            # story init complete, begin story loop

        # story loop
        # update timers
        self.story_timer.update()
        if self.fighter_timer.active:
            self.fighter_timer.update()
        if self.laser_timer.active:
            self.laser_timer.update()
        if self.hatch_timer.active:
            self.hatch_timer.update()
        if self.explode_timer.active:
            self.explode_timer.update()
        if self.glare_timer.active:
            self.glare_timer.update()

        # instance ticker
        if self.ticker_deque and not self.ticker_sprites:
            self.ticker = Ticker(self.ticker_sprites, (36, 97), self.ticker_deque.popleft())

        # update sprites
        self.ticker_sprites.update()
        self.thruster_sprites.update(self.dt)
        self.story_sprites.update(self.dt)

        # draw
        self.screen.blit(self.starfield_surf, (0, 0))
        self.screen.blit(self.ark_image, (40, 590))
        if self.ark_exploded:
            self.screen.blit(self.ark_hatch_blown_surf, (358, 650))
        self.draw_scores()
        self.ticker_sprites.draw(self.screen)
        self.thruster_sprites.draw(self.screen)
        self.story_sprites.draw(self.screen)

        # check input, if any, cleanup, change state and start new game
        if self.getAnyKey():
            self.story_timer.deactivate()
            self.fighter_timer.deactivate()
            self.laser_timer.deactivate()
            self.hatch_timer.deactivate()
            self.explode_timer.deactivate()
            self.glare_timer.deactivate()
            self.player.int_score = 0
            self.player.update_score(0)
            self.player_sprites.remove(self.player)
            self.kill_sprites()
            self.state = 'playing'
            self.init_state = True
            self.player.demo_mode = False
            self.setup_new_game()

    def playing(self): # set by setup_new_game and story (by timer or keypress)
        if self.init_state:
            # print('starting play')
            self.player_sprites.add(self.player)
            self.player.state = 'spawning'
            self.player.stage = self.stage
            self.player.init_state = True
            self.init_state = False
            self.ball_added = False
            self.playing_time = 0.0
            # repeat test blocks, spawn, launch, move left just a bit and ball will repeatedly hit these blocks]]
            # Block(  self.player, 
            #                 (500, 768 - BLOCK_HEIGHT), 
            #                 self.block_dict['D'][0], 
            #                 self.powerups['D'], 
            #                 self.sparkle_images, 
            #                 'D', 
            #                 'D', 
            #                 self.powerup_sprites, self.block_sprites, self.sparkle_sprites, 
            #                 self.stage)
            # Block(  self.player, 
            #                 (296, 810), 
            #                 self.block_dict['D'][0], 
            #                 self.powerups['D'], 
            #                 self.sparkle_images, 
            #                 'D', 
            #                 'D', 
            #                 self.powerup_sprites, self.block_sprites, self.sparkle_sprites, 
            #                 self.stage)
            # Block(  self.player, 
            #                 (600, 868), 
            #                 self.block_dict['D'][0], 
            #                 self.powerups['D'], 
            #                 self.sparkle_images, 
            #                 'D', 
            #                 'D', 
            #                 self.powerup_sprites, self.block_sprites, self.sparkle_sprites, 
            #                 self.stage)
            # Block(  self.player, 
            #                 (570, 566 - BLOCK_HEIGHT), 
            #                 self.block_dict['D'][0], 
            #                 self.powerups['D'], 
            #                 self.sparkle_images, 
            #                 'D', 
            #                 'D', 
            #                 self.powerup_sprites, self.block_sprites, self.sparkle_sprites, 
            #                 self.stage)
            # Block(  self.player, 
            #                 (self.player.rect.midtop + Vector2(0, -9)), 
            #                 self.block_dict['D'][0], 
            #                 self.powerups['D'], 
            #                 self.sparkle_images, 
            #                 'D', 
            #                 'D', 
            #                 self.powerup_sprites, self.block_sprites, self.sparkle_sprites, 
            #                 self.stage)
            if self.enemy_controller == self.feed_enemies:
                self.enemy_spawn_timer.activate()
            # playing init complete, begin playing loop

        # playing loop
        if self.enemy_spawn_timer.active and not settings.PAUSED:
            self.enemy_spawn_timer.update()

        if not self.ball_added and self.player.state == 'default':
            self.player.add_ball(False)
            self.ball_added = True
            self.player.active = True

        if self.end_stage_timer.active:
            self.end_stage_timer.update()
            return

        # playing update sprites
        self.explosion_sprites.update(self.dt)
        self.player_sprites.update(self.dt)
        self.NPC_spawner_sprites.update()
        self.powerup_sprites.update(self.dt)
        self.ball_sprites.update(self.dt)
        self.enemy_sprites.update(self.dt)
        self.bullet_sprites.update(self.dt)
        self.sparkle_sprites.update()
        self.teleporter_sprites.update()
        if self.player.state != 'spawning':
            self.enemy_controller()
    
        # playing draw
        self.teleporter_sprites.draw(self.screen)
        self.ball_sprites.draw(self.screen)
        self.explosion_sprites.draw(self.screen)
        self.sparkle_sprites.draw(self.screen)
        self.NPC_spawner_sprites.draw(self.screen)
        self.draw_lives_left()
        self.enemy_sprites.draw(self.screen)
        self.powerup_sprites.draw(self.screen)
        self.bullet_sprites.draw(self.screen)
        self.player.draw_player(self.screen)

        if not self.ball_sprites.sprites() and self.ball_added and self.player.active:
            self.state = 'dying'
            self.init_state = True
        
        # if self.player.next_stage or self.gold_blocks == len(self.block_sprites):
        if self.player.next_stage:
            self.kill_sprites()
            self.player.reset()
            self.end_stage_timer.activate()

        if settings.CHEATS and self.ball_sprites.sprites():
            self.player_follow_ball()
        
    def dying(self): # set by playing
        if self.init_state:
            self.player.explode()
            pygame.mixer.Sound.play(self.player_die_sound)
            self.player.reset()
            self.init_state = False
            for enemy in self.enemy_sprites.sprites():
                enemy.kill()
            for bumper in self.bumper_sprites.sprites():
                bumper.kill()
            for powerup in self.powerup_sprites.sprites():
                powerup.kill()
            for bullet in self.bullet_sprites.sprites():
                bullet.kill()
            # dying init complete, begin dying loop

        # dying loop
        self.explosion_sprites.update(self.dt)
        self.explosion_sprites.draw(self.screen)
        if not self.explosion_sprites:
            self.player.lives_left -= 1
            self.state = 'gameover' if self.player.lives_left < 1 else 'playing'
            self.init_state = True
    
    def gameover(self): # set by dying
        if self.init_state:
            print('starting gameover')
            self.init_state = False
            self.gameover_insert_coin_timer = Timer(10000, self.set_insert_coin)
            self.gameover_insert_coin_timer.activate()
            # gameover init complete, begin gameover loop

        # gameover loop
        # update
        self.gameover_insert_coin_timer.update()
        self.explosion_sprites.update(self.dt)

        # gameover draw
        self.explosion_sprites.draw(self.screen)
        self.screen.blit(self.game_over_surf, (36, 242))
        self.screen.blit(get_spaced_surf('PRESS SPACE', 'black'), (256, 602))
        self.screen.blit(get_spaced_surf('PRESS SPACE', 'white'), (250, 596))
        self.screen.blit(get_spaced_surf('TO TRY AGAIN', 'black'), (242, 696))
        self.screen.blit(get_spaced_surf('TO TRY AGAIN', 'white'), (236, 690))

        if self.getAnyKey():
            self.gameover_insert_coin_timer.deactivate()
            self.setup_new_game()
            
    ##############################################################################################
    ##                                                                                          ##
    ##                                  main loop                                               ##
    ##                                                                                          ##
    ##############################################################################################

    def run(self):
        self.ticks = pygame.time.get_ticks()
        while True:
            self.dt = (pygame.time.get_ticks() - self.ticks) / 1000
            self.ticks = pygame.time.get_ticks()
            if self.dt > 0:
                pygame.display.set_caption(str(self.dt))

            # print(self.dt)
            self.draw_stage()

            self.states[self.state]()

            self.get_events()

            if self.debug:
                self.draw_debug()
                
            pygame.display.update()
        
if __name__ == '__main__':
    game = Game()
    game.run()