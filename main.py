import os
import random
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1400, 850
FPS = 60
PLAYER_VEL = 5

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
        if self.complete == True:
            return "Desappearing (96x96)"
            sprite_sheet = "Desappearing (96x96)"
            sprite_sheet_name = sprite_sheet + "_" + self.direction
            sprites = self.SPRITES[sprite_sheet_name]
            sprite_index = self.animation_count // self.ANIMATION_DELAY % len(sprites)
            self.sprite = sprites[sprite_index]
            self.animation_count += 1
            self.update()
        else:
            pass

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

    def draw(self, win, offset_x): #win = window
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height), pygame.SRCALPHA,32)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self,win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self,x,y,size):
        super().__init__(x , y, size, size)
        block = load_block(size)
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


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _,_, width, height, = image.get_rect()
    tiles = []

    for i in range(WIDTH// width + 1):
        for j in range(HEIGHT//height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)
    for obj in objects:
        obj.draw(window, offset_x)
    player.draw(window, offset_x)

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
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
        elif obj and obj.name == "spike":
            player.make_hit()
        elif obj and obj.name == "spikehead":
            player.make_hit()
        elif obj and obj.name == "saw":
            player.make_hit()
    

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brown.png")

    #block size can be 32 for smaller scaled down version
    block_size = 96

    # player = Player(100,100,50,50)
    player = Player(0,HEIGHT - block_size * 4,50,50)
    fire = Fire(100,HEIGHT - block_size - 64, 16, 32) #size of fire is 16*32
    fire.on()
    spikehead = SpikeHead(500, 400, 54,52)
    spikehead.moving()
    platform = Platform(400, 300, block_size, 10)
    spike = Spike(150, HEIGHT-block_size-16, block_size,32)
    saw = Saw(700, 300, 38, 38)
    saw.moving()
    fallplat = FallingPlatform(700, 200, 32, 10)
    fallplat.moving()
    floor = [Block(i*block_size, HEIGHT - block_size, block_size) 
            for i in range(-WIDTH // block_size, (WIDTH*2) // block_size)]
    # *floor breaks all elements in floor and passes them into the list
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
            Block(block_size * 3, HEIGHT - block_size * 4, block_size), 
            fire, platform, spike, spikehead, saw, fallplat]

    offset_x = 0
    scroll_area_width = 200

    run = True
    spawn_timer = 0
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and player.jump_count < 2:
                    player.jump()
        if (player.spawnstate()):
            player.appear()
            spawn_timer += 1
        else:
            player.loop(FPS)
        if spawn_timer == 25:
            player.stopappearing()
        fire.loop()
        spikehead.loop()
        saw.loop()
        fallplat.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player,objects, offset_x)

        #for scrolling background
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pass

if __name__ == "__main__":
    main(window)

