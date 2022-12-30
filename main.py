import asyncio
import os
import random
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()
pygame.font.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1200, 800
FPS = 60
PLAYER_VEL = 5
HEALTH_ANIMATIONS = [pygame.image.load(join("assets","Health","0.png")),
                    pygame.image.load(join("assets","Health","1.png")),
                    pygame.image.load(join("assets","Health","2.png")),
                    pygame.image.load(join("assets","Health","3.png"))]
HIT_COOLDOWN = pygame.USEREVENT + 1
NEXT_LEVEL = pygame.USEREVENT + 2
RESTART_LEVEL = pygame.USEREVENT + 3

window = pygame.display.set_mode((WIDTH,HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites
    
    return all_sprites

def load_smaller_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale(surface,(64,64)))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites
    
    return all_sprites

def load_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),  pygame.SRCALPHA, 32)
    #x,y position of the desired sprite in the sprite sheet
    rect = pygame.Rect(96,64,size,size) 
    surface.blit(image,(0,0), rect)
    #can don't scale if the block needs to be smaller
    return pygame.transform.scale2x(surface) 
    # return surface

def load_small_ceiling(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),  pygame.SRCALPHA, 32)
    #x,y position of the desired sprite in the sprite sheet
    rect = pygame.Rect(0,64,size,size) 
    surface.blit(image,(0,0), rect)
    #can don't scale if the block needs to be smaller
    # return pygame.transform.scale2x(surface) 
    return surface

def load_ceiling(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),  pygame.SRCALPHA, 32)
    rect = pygame.Rect(0,64,size,size) 
    surface.blit(image,(0,0), rect)
    return pygame.transform.scale2x(surface) 

def load_platform(width,height):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((width,height),  pygame.SRCALPHA, 32)
    rect = pygame.Rect(272,16,width,height) 
    surface.blit(image,(0,0), rect)
    return pygame.transform.scale2x(surface) 

def load_spike(width,height):
    path = join("assets", "Traps", "Spikes", "Idle.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((width,height),  pygame.SRCALPHA, 32)
    rect = pygame.Rect(0,8,width,height) 
    surface.blit(image,(0,0), rect)
    return pygame.transform.scale2x(surface) 

class HealthBar(pygame.sprite.Sprite):
      def __init__(self):
            super().__init__()
            self.image = pygame.image.load(join("assets","Health","3.png"))

      def render(self,win):
        win.blit(self.image, (10,10))

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3
    SPAWNING = load_smaller_sprite_sheets("MainCharacters","spawning",96,96, True)
    SPRITES.update(SPAWNING)

    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.spawn = True
        self.complete = False
        self.cooldown = False
        self.health = 3

    def spawnstate(self):
        if self.spawn == True:
            return True
        else:
            return False

    def appear(self):
        if self.spawn == True:
            sprite_sheet = "Appearing (96x96)"
            sprite_sheet_name = sprite_sheet + "_" + self.direction
            sprites = self.SPRITES[sprite_sheet_name]
            sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
            self.sprite = sprites[sprite_index]
            self.animation_count += 1
            self.update()
        else:
            pass

    def stopappearing(self):
        self.spawn = False

    def disappear(self):
        # if self.complete == True:
        sprite_sheet = "Desappearing (96x96)"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
        # else:
        #     pass
        
    def jump(self):
        # uses this upward velocity to go up, then the gravity from the loop function will pull the player back down
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def player_hit(self):
        if self.cooldown == False:      
            self.cooldown = True # Enable the cooldown
            pygame.time.set_timer(HIT_COOLDOWN, 500) # Resets cooldown in 0.5 second
    
            self.health = self.health - 1
            health.image = HEALTH_ANIMATIONS[self.health]
            if self.health <= 0:
                pygame.event.post(pygame.event.Event(RESTART_LEVEL))
                self.kill()
                pygame.display.update()

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = 'left'
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != 'right':
            self.direction = 'right'
            self.animation_count = 0

    def landed(self):
        self.fall_count = 0 #gravity part resets
        self.y_vel = 0
        self.jump_count = 0 #for double jump

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1 #to allow player to start moving down instead of continue upwards


    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
    
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()        

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count/fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        self.fall_count += 1
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps: #fps * 2 is 2 seconds since fps is 1 second
            self.hit = False
            self.hit_count = 0

        self.update_sprite()

    def draw(self, win, offset_x, offset_y): #win = window
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height), pygame.SRCALPHA,32)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self,win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))

class Block(Object):
    def __init__(self,x,y,size):
        super().__init__(x , y, size, size)
        block = load_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class SmallCeiling(Object):
    def __init__(self,x,y,size):
        super().__init__(x , y, size, size)
        block = load_small_ceiling(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Ceiling(Object):
    def __init__(self,x,y,size):
        super().__init__(x , y, size, size)
        block = load_ceiling(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Platform(Object):
    def __init__(self,x,y,width, height):
        super().__init__(x , y, width, height)
        platform = load_platform(width,height)
        self.image.blit(platform, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Spike(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "spike")
        spike = load_spike(width,height)
        self.image.blit(spike,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
    
    def on(self):
        self.animation_name = "on"
    
    def off(self):
        self.animation_name = "off"

    def loop(self):
        #animation name is for wat sprite u wna use so either on or off
        sprites = self.fire[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        #so that animation count dun get too big, otherwise the animation would not reset properly
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class SpikeHead(Object):
    ANIMATION_DELAY = 30

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "spikehead")
        self.spikehead = load_sprite_sheets("Traps", "Spike Head", width, height)
        self.image = self.spikehead["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle"
    
    def moving(self):
        self.animation_name = "Blink (54x52)"

    def loop(self):
        sprites = self.spikehead[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Saw(Object):
    ANIMATION_DELAY = 30

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "saw")
        self.saw = load_sprite_sheets("Traps", "Saw", width, height)
        self.image = self.saw["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
    
    def moving(self):
        self.animation_name = "on"
    def loop(self):
        sprites = self.saw[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class FallingPlatform(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fallingplatform")
        self.fallingplatform = load_sprite_sheets("Traps", "Falling Platforms", width, height)
        self.image = self.fallingplatform["Off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Off"
    
    def moving(self):
        self.animation_name = "On (32x10)"

    def falling(self):
        pass

    def loop(self):
        sprites = self.fallingplatform[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Plant(Object):
    ANIMATION_DELAY = 10

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "plant")
        self.plant = load_sprite_sheets("Enemies", "Plant", width, height)
        self.image = self.plant["Idle (44x42)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle (44x42)"
    
    def moving(self):
        self.animation_name = "Idle (44x42)"

    def loop(self):
        sprites = self.plant[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Chicken(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "chicken")
        self.chicken = load_sprite_sheets("Enemies", "Chicken", width, height)
        self.image = self.chicken["Idle (32x34)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "Idle (32x34)"
    
    def moving(self):
        self.animation_name = "Idle (32x34)"

    def loop(self):
        sprites = self.chicken[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Endpoint(Object):
    ANIMATION_DELAY = 15

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "endpoint")
        self.end = load_smaller_sprite_sheets("Checkpoints", "End", width, height)
        self.image = self.end["End (Idle)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "End (Idle)"
    
    def moving(self):
        self.animation_name = "End (Pressed) (64x64)"

    def loop(self):
        sprites = self.end[self.animation_name]
        sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _,_, width, height, = image.get_rect()
    tiles = []

    for i in range(WIDTH// width + 1):
        for j in range(HEIGHT//height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x, offset_y, health):
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        obj.draw(window, offset_x, offset_y)
    player.draw(window, offset_x, offset_y)
    health.render(window)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            #for jumping when it hits something on top, top of rect will hit the bottom of the obstacle
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
        
            collided_objects.append(obj)
    
    return collided_objects

#checks if the player would hit any object, if it does, it will return the obj, if it doesnt, then it will return None
def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
     
    player.move(-dx,0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL*2) #player vel *2 will allow for some gap between player and block but allows for collision to happen
    collide_right = collide(player, objects, PLAYER_VEL*2)

    #player only allowed to move left or right if the premeptive collide function returns none which means there is nth obstructing the player
    if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and not collide_left:
        player.move_left(PLAYER_VEL)
    if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and not collide_right:
        player.move_right(PLAYER_VEL)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
            player.player_hit()
        elif obj and obj.name == "spike":
            player.make_hit()
            player.player_hit()
        elif obj and obj.name == "spikehead":
            player.make_hit()
            player.player_hit()
        elif obj and obj.name == "saw":
            player.make_hit()
            player.player_hit()
        elif obj and obj.name == "plant":
            player.make_hit()
            player.player_hit()
        elif obj and obj.name == "endpoint":
            pygame.event.post(pygame.event.Event(NEXT_LEVEL))

def getobjects(level):
    block_size = 96
    if level == 1:
        floor = [Block(i*block_size, HEIGHT - block_size, block_size) 
                for i in range(1, 12)]
        ceiling = [Ceiling(i*block_size, HEIGHT - block_size*11, block_size) 
                for i in range(0,13)]
        end = Endpoint(block_size*11 + 32, HEIGHT-block_size*7 + 32, 64, 64)
        end.moving()
        blocks = [Block(0, HEIGHT-block_size*6, block_size), Block(0, HEIGHT-block_size*7, block_size),Block(0, HEIGHT-block_size*8, block_size),Block(0, HEIGHT-block_size*9, block_size),Block(0, HEIGHT-block_size*10, block_size),
                Block(block_size, HEIGHT-block_size*2, block_size),Block(block_size, HEIGHT-block_size*3, block_size), Block(block_size, HEIGHT-block_size*4, block_size),Block(block_size, HEIGHT-block_size*5, block_size), Block(block_size, HEIGHT-block_size*6, block_size),
                Block(block_size * 6, HEIGHT-block_size*2, block_size),Block(block_size * 7, HEIGHT-block_size*2, block_size),Block(block_size * 8, HEIGHT-block_size*2, block_size),Block(block_size * 3, HEIGHT - block_size * 4, block_size) ,Block(block_size * 4, HEIGHT - block_size * 4, block_size), 
                Block(block_size * 11, HEIGHT-block_size*2, block_size),Block(block_size * 11, HEIGHT-block_size*3, block_size), Block(block_size * 11, HEIGHT-block_size*4, block_size),Block(block_size * 11, HEIGHT-block_size*5, block_size), Block(block_size * 11, HEIGHT-block_size*6, block_size),
                Block(block_size * 6, HEIGHT-block_size*7, block_size),Block(block_size * 5, HEIGHT-block_size*7, block_size),
                Block(block_size * 12, HEIGHT-block_size*6, block_size), Block(block_size * 12, HEIGHT-block_size*7, block_size), Block(block_size * 12, HEIGHT-block_size*8, block_size),Block(block_size* 12, HEIGHT-block_size*9, block_size),Block(block_size * 12, HEIGHT-block_size*10, block_size)]
        animated_things = []
        objects = [*floor,*ceiling ,*blocks, *animated_things, end]

    elif level == 2:
        floor = [Block(i*block_size, HEIGHT - block_size, block_size) 
                for i in range(0, 15)]
        ceiling = [Ceiling(i*block_size, HEIGHT - block_size*10, block_size) 
                for i in range(0,15)]
        surrounding_walls_left = [Ceiling(0,HEIGHT - i*block_size, block_size)
                            for i in range(0,10)]
        surrounding_walls_right = [Ceiling(block_size*14 ,HEIGHT - i*block_size, block_size) 
                                for i in range(0,10)]
        blocks = [Ceiling(block_size,HEIGHT-block_size*6,block_size),Ceiling(block_size*2,HEIGHT-block_size*6,block_size),Ceiling(block_size*3,HEIGHT-block_size*6,block_size),Ceiling(block_size*4,HEIGHT-block_size*6,block_size),Ceiling(block_size*5,HEIGHT-block_size*6,block_size),Ceiling(block_size*6,HEIGHT-block_size*6,block_size),
                Ceiling(block_size,HEIGHT-block_size*7,block_size),Ceiling(block_size*2,HEIGHT-block_size*7,block_size),Ceiling(block_size*3,HEIGHT-block_size*7,block_size),Ceiling(block_size*4,HEIGHT-block_size*7,block_size),Ceiling(block_size*5,HEIGHT-block_size*7,block_size), Ceiling(block_size*6,HEIGHT-block_size*7,block_size),
                Platform(block_size*13,HEIGHT-block_size*6,block_size,10),Platform(block_size*13,HEIGHT-block_size*3,block_size,10),]
        animated_things = [Fire(block_size*5+16,HEIGHT - block_size - 64, 16, 32),Fire(block_size*5+48,HEIGHT - block_size - 64, 16, 32),Fire(block_size*7+16,HEIGHT - block_size - 64, 16, 32), Fire(block_size*7+48,HEIGHT - block_size - 64, 16, 32),
                        FallingPlatform(block_size*9, HEIGHT-block_size*4-15,32,10),FallingPlatform(block_size*10, HEIGHT-block_size*7-15,32,10),]
        
        end = Endpoint(block_size + 16, HEIGHT-block_size*8 + 32, 64, 64)
        end.moving()
        objects = [*floor, *ceiling, *blocks, *animated_things, *surrounding_walls_left, *surrounding_walls_right, end]

    elif level == 3:
        ceiling1 = [Ceiling(i*block_size, HEIGHT - block_size*11, block_size) 
                for i in range(-4,4)]
        ceiling2 = [Ceiling(i*block_size, HEIGHT - block_size*11, block_size) 
                for i in range(7,15)]
        floor = [Block(i*block_size, HEIGHT - block_size*2, block_size) 
                for i in range(0, 5)]
        surrounding_walls_left = [Block(0,HEIGHT - i*block_size, block_size)
                            for i in range(2,9)]
        surrounding_walls_right = [Block(block_size*14 ,HEIGHT - i*block_size, block_size) 
                                for i in range(0,11)]
        blocks = [Block(block_size*9, HEIGHT - block_size*2, block_size),Block(block_size*10, HEIGHT - block_size*2, block_size),Block(block_size*11, HEIGHT - block_size*2, block_size),
                Block(block_size*4, HEIGHT-block_size, block_size),Block(block_size*5, HEIGHT-block_size, block_size),Block(block_size*8, HEIGHT-block_size, block_size),Block(block_size*9, HEIGHT-block_size, block_size),Block(block_size*11, HEIGHT-block_size, block_size),
                Block(block_size*5, HEIGHT, block_size),Block(block_size*6, HEIGHT, block_size),Block(block_size*7, HEIGHT, block_size),Block(block_size*8, HEIGHT, block_size),Block(block_size*11, HEIGHT, block_size),Block(block_size*12, HEIGHT, block_size),Block(block_size*13, HEIGHT, block_size),Block(block_size*14, HEIGHT, block_size),
                Platform(block_size*13,HEIGHT-block_size*4,block_size,10),Platform(block_size*9, HEIGHT-block_size*5, block_size,10),Platform(block_size, HEIGHT-block_size*7, block_size,10),Platform(block_size*4, HEIGHT-block_size*8.5, block_size,10),Platform(block_size*6, HEIGHT-block_size*10.5, block_size,10),
                Block(-block_size, HEIGHT - block_size*8, block_size),Block(-block_size*2, HEIGHT - block_size*8, block_size),Block(-block_size*3, HEIGHT - block_size*8, block_size),Block(-block_size*4, HEIGHT - block_size*8, block_size),Block(-block_size*4, HEIGHT - block_size*9, block_size),Block(-block_size*4, HEIGHT - block_size*10, block_size),
                Ceiling(block_size*3, HEIGHT - block_size*10, block_size),Ceiling(block_size*3, HEIGHT - block_size*9, block_size),Ceiling(block_size*7, HEIGHT - block_size*10, block_size),
                Spike(block_size*6, HEIGHT-16, block_size,32),Spike(block_size*6+32, HEIGHT-16, block_size,32),Spike(block_size*6+64, HEIGHT-16, block_size,32),Spike(block_size*7, HEIGHT-16, block_size,32),Spike(block_size*7+32, HEIGHT-16, block_size,32),Spike(block_size*7+64, HEIGHT-16, block_size,32),
                Spike(block_size*12, HEIGHT-16, block_size,32),Spike(block_size*12+32, HEIGHT-16, block_size,32),Spike(block_size*12+64, HEIGHT-16, block_size,32),Spike(block_size*13, HEIGHT-16, block_size,32),Spike(block_size*13+32, HEIGHT-16, block_size,32),Spike(block_size*13+64, HEIGHT-16, block_size,32)]
        animated_things = [FallingPlatform(block_size*5+25, HEIGHT-block_size*6-32,32,10),FallingPlatform(block_size*4+56, HEIGHT-block_size*6-32,32,10),
                        Chicken(-block_size*3,HEIGHT - block_size*9+28,32,34)]
        end = Endpoint(block_size*14 + 16, HEIGHT-block_size*12 + 32, 64, 64)
        end.moving()     
        objects = [*floor,*ceiling1,*ceiling2,*blocks,*surrounding_walls_left,*surrounding_walls_right, *animated_things,end]

    elif level == 4:
        floor = [Block(i*block_size, HEIGHT - block_size*2, block_size) 
                for i in range(0, 5)]
        surrounding_walls_left = [Block(0,HEIGHT - i*block_size, block_size)
                    for i in range(-10,2)]
        surrounding_walls_right = [Block(block_size*21,HEIGHT - i*block_size, block_size)
                    for i in range(-9,-3)]
        floor1 = [Block(i*block_size, HEIGHT+block_size*10, block_size) 
                for i in range(0, 10)]
        floor2 = [Block(i*block_size, HEIGHT+block_size*9, block_size) 
                for i in range(9, 22)]
        floor3 = [Block(i*block_size, HEIGHT - block_size*2, block_size) 
                for i in range(6, 9)]
        floor4 = [Block(i*block_size, HEIGHT - block_size*2, block_size) 
                for i in range(11, 16)]
        floor5 = [Block(i*block_size, HEIGHT - block_size*6, block_size) 
                for i in range(7, 12)]
        floor6 = [Block(i*block_size, HEIGHT - block_size*6, block_size) 
                for i in range(15, 23)]
        floor7 = [Block(i*block_size, HEIGHT - block_size*15, block_size) 
                for i in range(14, 21)]
        floor8 = [Block(i*block_size, HEIGHT - block_size*19, block_size) 
                for i in range(21, 26)]
        floor9 = [Block(i*block_size, HEIGHT - block_size*8, block_size) 
                for i in range(24, 30)]
        left_walls1 = [Block(block_size*11,HEIGHT - i*block_size, block_size)
                    for i in range(7,12)]
        left_walls2 = [Block(block_size*13,HEIGHT - i*block_size, block_size)
                    for i in range(12,16)]
        right_walls1 = [Block(block_size*25,HEIGHT - i*block_size, block_size)
                    for i in range(12,17)]
        right_walls2 = [Block(block_size*26,HEIGHT - i*block_size, block_size)
                    for i in range(10,17)]
        blocks = [Block(block_size*6, HEIGHT - block_size*3, block_size),Block(block_size*7, HEIGHT - block_size*3, block_size),Block(block_size*8, HEIGHT - block_size*3, block_size),Block(block_size*6, HEIGHT - block_size*4, block_size),Block(block_size*6, HEIGHT - block_size*5, block_size),Block(block_size*6, HEIGHT - block_size*6, block_size),
                Block(block_size*4, HEIGHT + block_size*9, block_size),Block(block_size*5, HEIGHT + block_size*9, block_size), Block(block_size*12, HEIGHT + block_size*8, block_size),Block(block_size*13, HEIGHT + block_size*8, block_size),
                Platform(block_size,HEIGHT+block_size*8,block_size,10),Platform(block_size,HEIGHT+block_size*3.5,block_size,10),Platform(block_size*4,HEIGHT+block_size*2,block_size,10),Platform(block_size*5,HEIGHT-block_size*4,block_size,10),
                Spike(block_size*6, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*6+32, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*6+64, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*7, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*7+32, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*7+64, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*8, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*8+32, HEIGHT+block_size*10-16, block_size,32),Spike(block_size*8+64, HEIGHT+block_size*10-16, block_size,32),
                Block(block_size*5, HEIGHT + block_size*2, block_size),Block(block_size*6, HEIGHT + block_size*2, block_size),Block(block_size*7, HEIGHT + block_size*2, block_size),Block(block_size*8, HEIGHT + block_size*2, block_size),Block(block_size*8, HEIGHT + block_size, block_size),Block(block_size*8, HEIGHT, block_size),Block(block_size*8, HEIGHT - block_size, block_size),
                Platform(block_size*18,HEIGHT+block_size*7,block_size,10),Platform(block_size*14,HEIGHT+block_size*6,block_size,10),Platform(block_size*9,HEIGHT+block_size,block_size,10),Platform(block_size*10,HEIGHT-block_size,block_size,10)]
        more_blocks = [Block(block_size*17, HEIGHT + block_size*6, block_size),Block(block_size*16, HEIGHT + block_size*6, block_size),Block(block_size*15, HEIGHT + block_size*6, block_size),Block(block_size*15, HEIGHT + block_size*5, block_size),Block(block_size*15, HEIGHT + block_size*4, block_size),Block(block_size*15, HEIGHT + block_size*3, block_size),Block(block_size*15, HEIGHT + block_size*2, block_size),Block(block_size*15, HEIGHT + block_size, block_size),Block(block_size*15, HEIGHT, block_size),Block(block_size*15, HEIGHT-block_size, block_size),Block(block_size*16, HEIGHT + block_size*2, block_size),Block(block_size*17, HEIGHT + block_size*2, block_size),Block(block_size*18, HEIGHT + block_size*2, block_size),Block(block_size*19, HEIGHT + block_size*2, block_size),Block(block_size*19, HEIGHT + block_size*3, block_size),Block(block_size*19, HEIGHT + block_size*4, block_size),Block(block_size*20, HEIGHT + block_size*4, block_size),
                    Block(block_size*11, HEIGHT-block_size*3, block_size),Block(block_size*11, HEIGHT-block_size*4, block_size),Block(block_size*12, HEIGHT-block_size*4, block_size),Block(block_size*13, HEIGHT-block_size*4, block_size),Block(block_size*14, HEIGHT-block_size*4, block_size),Block(block_size*14, HEIGHT-block_size*5, block_size),Block(block_size*14, HEIGHT-block_size*6, block_size),Block(block_size*14, HEIGHT-block_size*7, block_size),
                    Platform(block_size*12,HEIGHT-block_size*5-10,block_size,10),Platform(block_size*14,HEIGHT-block_size*12-10,block_size,10),Platform(block_size*19, HEIGHT-block_size*8-10, block_size,10),
                    Block(block_size*12, HEIGHT-block_size*11, block_size),Block(block_size*13, HEIGHT-block_size*11, block_size),Block(block_size*20, HEIGHT-block_size*9, block_size),Block(block_size*20, HEIGHT-block_size*10, block_size),Block(block_size*20, HEIGHT-block_size*11, block_size),Block(block_size*20, HEIGHT-block_size*12, block_size),Block(block_size*20, HEIGHT-block_size*13, block_size),
                    Block(20*block_size, HEIGHT - block_size*16, block_size),Block(20*block_size, HEIGHT - block_size*17, block_size),Block(20*block_size, HEIGHT - block_size*18, block_size),Block(20*block_size, HEIGHT - block_size*19, block_size), 
                    Block(21*block_size, HEIGHT - block_size*13, block_size),Block(21*block_size, HEIGHT - block_size*10, block_size),Block(22*block_size, HEIGHT - block_size*9, block_size),Block(22*block_size, HEIGHT - block_size*8, block_size),Block(22*block_size, HEIGHT - block_size*7, block_size),Block(22*block_size, HEIGHT - block_size*10, block_size),Block(23*block_size, HEIGHT - block_size*10, block_size),Block(23*block_size, HEIGHT - block_size*9, block_size),Block(23*block_size, HEIGHT - block_size*8, block_size),
                    Platform(block_size*22,HEIGHT-block_size*12-10,block_size,10),Platform(block_size*23,HEIGHT-block_size*11-10,block_size,10),
                    Block(24*block_size, HEIGHT - block_size*12, block_size),Block(24*block_size, HEIGHT - block_size*13, block_size),
                    Platform(block_size*27,HEIGHT-block_size*10-10,block_size,10),Block(29*block_size, HEIGHT - block_size*11, block_size),Block(29*block_size, HEIGHT - block_size*10, block_size),Block(29*block_size, HEIGHT - block_size*9, block_size),Block(30*block_size, HEIGHT - block_size*11, block_size),Block(31*block_size, HEIGHT - block_size*11, block_size),Block(31*block_size, HEIGHT - block_size*12, block_size),Block(31*block_size, HEIGHT - block_size*13, block_size),
                    Block(30*block_size, HEIGHT - block_size*13, block_size),Block(29*block_size, HEIGHT - block_size*13, block_size),Block(28*block_size, HEIGHT - block_size*13, block_size),Block(27*block_size, HEIGHT - block_size*13, block_size),
                     Platform(block_size*21,HEIGHT-block_size*14-10,block_size,10)]
        animated_things = [FallingPlatform(block_size*3+25, HEIGHT+block_size*6-32,32,10),FallingPlatform(block_size*11+25, HEIGHT+block_size*4-32,32,10),FallingPlatform(block_size*13+25, HEIGHT+block_size*3-32,32,10),FallingPlatform(block_size*7+25, HEIGHT+block_size*5-32,32,10),
                        FallingPlatform(block_size*16+25, HEIGHT-block_size*10-32,32,10),FallingPlatform(block_size*16+95, HEIGHT-block_size*9-32,32,10),FallingPlatform(block_size*17+95, HEIGHT-block_size*12-32,32,10),
                        SpikeHead(block_size*21-8,HEIGHT - block_size*9,54,52),Chicken(block_size*21,HEIGHT - block_size*11+28,32,34),Chicken(block_size*30,HEIGHT - block_size*12+28,32,34),
                        Chicken(block_size*7,HEIGHT + block_size+28,32,34),Chicken(block_size*7,HEIGHT - block_size*4+28,32,34),Chicken(block_size*16,HEIGHT + block_size*5+28,32,34)]
        end =  Endpoint(block_size*30 + 16, HEIGHT-block_size*14 + 32, 64, 64)
        end.moving()
        objects = [*floor,*floor1,*floor2,*floor3,*floor4,*floor5,*floor6,*floor7,*floor8,*floor9,*left_walls1,*left_walls2,*right_walls1,*right_walls2,*surrounding_walls_left,*surrounding_walls_right,*blocks,*more_blocks,*animated_things, end]
    
    elif level == 5:
        small_block_size = 48
        floor = [Ceiling(i*block_size, HEIGHT - block_size, block_size) 
                for i in range(0, 15)]
        t = [SmallCeiling(i*small_block_size, HEIGHT - small_block_size*17, small_block_size) 
                for i in range(4, 7)]
        text = [SmallCeiling(5*small_block_size, HEIGHT - small_block_size*16, small_block_size),SmallCeiling(5*small_block_size, HEIGHT - small_block_size*15, small_block_size),SmallCeiling(5*small_block_size, HEIGHT - small_block_size*14, small_block_size),
            SmallCeiling(8*small_block_size, HEIGHT - small_block_size*17, small_block_size),SmallCeiling(8*small_block_size, HEIGHT - small_block_size*16, small_block_size),SmallCeiling(8*small_block_size, HEIGHT - small_block_size*15, small_block_size),SmallCeiling(8*small_block_size, HEIGHT - small_block_size*14, small_block_size),
            SmallCeiling(9*small_block_size, HEIGHT - small_block_size*15.5, small_block_size),SmallCeiling(10*small_block_size, HEIGHT - small_block_size*17, small_block_size),SmallCeiling(10*small_block_size, HEIGHT - small_block_size*16, small_block_size),SmallCeiling(10*small_block_size, HEIGHT - small_block_size*15, small_block_size),SmallCeiling(10*small_block_size, HEIGHT - small_block_size*14, small_block_size),
            SmallCeiling(12*small_block_size, HEIGHT - small_block_size*17, small_block_size),SmallCeiling(12*small_block_size, HEIGHT - small_block_size*16, small_block_size),SmallCeiling(12*small_block_size, HEIGHT - small_block_size*15, small_block_size),SmallCeiling(12*small_block_size, HEIGHT - small_block_size*14, small_block_size),
            SmallCeiling(13*small_block_size, HEIGHT - small_block_size*17, small_block_size),SmallCeiling(14*small_block_size, HEIGHT - small_block_size*17, small_block_size),SmallCeiling(13*small_block_size, HEIGHT - small_block_size*15.5, small_block_size),SmallCeiling(13*small_block_size, HEIGHT - small_block_size*14, small_block_size),SmallCeiling(14*small_block_size, HEIGHT - small_block_size*14, small_block_size),
            
            SmallCeiling(12*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(12*small_block_size, HEIGHT - small_block_size*11, small_block_size),SmallCeiling(12*small_block_size, HEIGHT - small_block_size*10, small_block_size),SmallCeiling(12*small_block_size, HEIGHT - small_block_size*9, small_block_size),
            SmallCeiling(13*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(14*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(13*small_block_size, HEIGHT - small_block_size*10.5, small_block_size),SmallCeiling(13*small_block_size, HEIGHT - small_block_size*9, small_block_size),SmallCeiling(14*small_block_size, HEIGHT - small_block_size*9, small_block_size),
            SmallCeiling(16*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(16*small_block_size, HEIGHT - small_block_size*11, small_block_size),SmallCeiling(16*small_block_size, HEIGHT - small_block_size*10, small_block_size),SmallCeiling(16*small_block_size, HEIGHT - small_block_size*9, small_block_size),
            SmallCeiling(17*small_block_size, HEIGHT - small_block_size*11, small_block_size),SmallCeiling(17.5*small_block_size, HEIGHT - small_block_size*10, small_block_size),
            SmallCeiling(18.5*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(18.5*small_block_size, HEIGHT - small_block_size*11, small_block_size),SmallCeiling(18.5*small_block_size, HEIGHT - small_block_size*10, small_block_size),SmallCeiling(18.5*small_block_size, HEIGHT - small_block_size*9, small_block_size),
            SmallCeiling(20.5*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(20.5*small_block_size, HEIGHT - small_block_size*11, small_block_size),SmallCeiling(20.5*small_block_size, HEIGHT - small_block_size*10, small_block_size),SmallCeiling(20.5*small_block_size, HEIGHT - small_block_size*9, small_block_size),
            SmallCeiling(21.5*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(22.5*small_block_size, HEIGHT - small_block_size*12, small_block_size),SmallCeiling(21.5*small_block_size, HEIGHT - small_block_size*9, small_block_size),SmallCeiling(22.5*small_block_size, HEIGHT - small_block_size*9, small_block_size),SmallCeiling(23*small_block_size, HEIGHT - small_block_size*10, small_block_size),SmallCeiling(23*small_block_size, HEIGHT - small_block_size*11, small_block_size),]
        surrounding_walls_left = [Ceiling(0,HEIGHT - i*block_size, block_size)
                                for i in range(2,11)]
        surrounding_walls_right = [Ceiling(block_size*14 ,HEIGHT - i*block_size, block_size) 
                                for i in range(0,11)]
        animated_things = []
        end = Endpoint(block_size*30 + 16, HEIGHT-block_size*14 + 32, 64, 64)
        end.moving()
        objects = [*floor,*t,*text,*surrounding_walls_left,*surrounding_walls_right,*animated_things, end]

    return objects, animated_things, end

def level_manager(level):
    if level == 1:
        level = 2
    elif level == 2:
        level = 3
    elif level == 3:
        level = 4 
    elif level == 4:
        level = 5
    return level 

health = HealthBar()

async def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brown.png")
    
    block_size = 96
    level = 1

    player = Player(block_size*2,HEIGHT - block_size * 3,50,50)
    objects, animated_things, end = getobjects(level)

    offset_x = 0
    offset_y = 0
    scroll_area_width = 200
    scroll_area_height = 150

    run = True
    spawn_timer = 0
    while run:
        clock.tick(FPS)
        await asyncio.sleep(0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_w or event.key == pygame.K_UP)and player.jump_count < 2:
                    player.jump()
            
            if event.type == HIT_COOLDOWN:
                player.cooldown = False

            if event.type == NEXT_LEVEL:
                level = level_manager(level)
                player = Player(block_size*2,HEIGHT - block_size * 3,50,50)
                objects, animated_things, end = getobjects(level)
                spawn_timer = 0
                offset_x = 0
                offset_y=0
            if event.type == RESTART_LEVEL:
                player.disappear()
                player = Player(block_size*2,HEIGHT - block_size * 3,50,50)
                player.health = 3
                health.image = HEALTH_ANIMATIONS[player.health]
                objects, animated_things, end = getobjects(level)
                spawn_timer = 0
                offset_x = 0
                offset_y = 0
            
            if offset_x > 3000 or offset_y > 1500:
                pygame.event.post(pygame.event.Event(RESTART_LEVEL))

        if (player.spawnstate()):
            player.appear()
            spawn_timer += 1
        else:
            player.loop(FPS)
        if spawn_timer == 25:
            player.stopappearing()

        for trap in animated_things:
            if (isinstance(trap,Fire)):
                trap.on()
                trap.loop()
            elif (isinstance(trap,FallingPlatform) or isinstance(trap,SpikeHead)):
                trap.moving()
                trap.loop()
            elif (isinstance(trap,Chicken)):
                trap.moving()
                trap.loop()
        end.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, offset_y, health)

        #for scrolling background
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        if ((player.rect.top - offset_y >= HEIGHT-scroll_area_height) and player.y_vel > 0) or ((player.rect.bottom - offset_y <= scroll_area_height) and player.y_vel < 0):
            offset_y += player.y_vel
        
    pass

asyncio.run(main(window))

if __name__ == "__main__":
    main(window)

