import arcade.key
import random
from maps import *

MOVEMENT_SPEED = 5

DIR_STILL = 0
DIR_UP = 1
DIR_RIGHT = 2
DIR_LEFT = 4

DIR_OFFSETS = { DIR_STILL: (0,0), 
                DIR_UP: (0,1), 
                DIR_RIGHT: (1,0), 
                DIR_LEFT: (-1,0)}

JUMP_SPEED = 17
GRAVITY = -1
PLAYER_MARGIN = 50


class Sound:
    def __init__(self, world):
        self.world = world

        self.jump = arcade.load_sound('sounds/jump.wav')
        self.picked_item = arcade.load_sound('sounds/collect.wav')
        self.picked_coin = arcade.load_sound('sounds/picked-coin.wav')
        self.hited = arcade.load_sound('sounds/die.wav')
        self.level_comp = arcade.load_sound('sounds/level-complete.wav')

        self.start_game = arcade.load_sound('sounds/start-game.wav')
        self.gameover = arcade.load_sound('sounds/game-over.wav')

    def play(self, sound):
        arcade.play_sound(sound)

    def start_game(self):
        self.play(self.start_game)

    def level_pass(self):
        self.play(self.level_comp)

    def coin_sound(self):
        self.play(self.picked_coin)

    def item_sound(self):
        self.play(self.picked_item)

    def game_over(self):
        self.play(self.gameover)

    def hit_sound(self):
        if self.world.state == World.DEAD:
            self.play(self.hited)


class Model:
    def __init__(self, world, x, y, angle):
        self.world = world
        self.x = x
        self.y = y
        self.angle = 0


class MrCorn(Model):
    def __init__(self, world, x, y):
        super().__init__(world, x, y, 0)
        self.vx = 0
        self.vy = 0
        self.direction = DIR_STILL
        self.is_jump = False
        self.jump_count = 0
        self.platform = None
        self.heart_count = 3
        self.score = 0
        self.lv_platform = None

    def move(self, direction):
        self.x += MOVEMENT_SPEED * DIR_OFFSETS[direction][0]
        self.y += MOVEMENT_SPEED * DIR_OFFSETS[direction][1]

    def jump(self):
        if self.jump_count <= 1:
            self.is_jump = True
            self.vy = JUMP_SPEED
            self.jump_count += 1

    def top(self):
        return self.y + 100

    def bottom(self):
        return self.y - 100

    def set_platform(self, platform):
        self.is_jump = False
        self.platform = platform
        self.y = platform.y + 100

    def is_on_platform(self, platform):
        if not platform.in_top_range(self.x):
            return False

        if abs(platform.y - self.bottom()) <= 50:
            return True

        return False

    def is_falling_on_platform(self, platform):
        if not platform.in_top_range(self.x):
            return False

        if self.bottom() - self.vy > platform.y > self.bottom():
            return True

        return False

    def find_touching_platform(self):
        platforms = self.world.lv1.platforms
        for p in platforms:
            if self.is_falling_on_platform(p):
                return p

    def check_out_of_world(self):
        if self.x <= PLAYER_MARGIN or self.x - PLAYER_MARGIN >= self.world.width:
            self.direction = DIR_STILL
            if self.x <= 0:
                self.x = PLAYER_MARGIN
            if self.x >= self.world.width:
                self.x = self.world.width - PLAYER_MARGIN

    def update(self, delta):
        self.move(self.direction)
        self.check_out_of_world()
        if self.is_jump:
            self.y += self.vy
            self.vy += GRAVITY

            new_platform = self.find_touching_platform()
            if new_platform:
                self.vy = 0
                self.jump_count = 0
                self.set_platform(new_platform)
        else:
            if (self.platform) and (not self.is_on_platform(self.platform)):
                self.platform = None
                self.is_jump = True
                self.jump_count = 0
                self.vy = 0


class Fire:
    def __init__(self, world, x, y, width, height, level):
        self.world = world
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.level = level

    def top(self):
        return self.y + self.height//2

    def update_level(self):
        self.level += (self.world.level-1)/4

    def update(self, delta):
        self.y += self.level


class Platform:
    def __init__(self, world, x, y, width, height):
        self.world = world
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.avaliable = True

    def in_top_range(self, x):
        return self.x - self.width//2 <= x <= self.x + self.width//2

    def in_bottom_range(self, x):
        return self.x - self.width//2 <= x <= self.x + self.width//2

    def item_on(self):
        self.avaliable = False


class Item:
    ITEM_HIT_MARGIN = 30

    def __init__(self, world, x, y):
        self.world = world
        self.x = x
        self.y = y
        self.is_collected = False

    def collected(self, mrcorn):
        return ((abs(self.x - mrcorn.x) < Item.ITEM_HIT_MARGIN) and
                (abs(self.y - mrcorn.y) < Item.ITEM_HIT_MARGIN))


class Level:
    def __init__(self, world, player, width, height):
        self.world = world
        self.player = player
        self.width = width
        self.height = height

        self.setup()

        self.sound = Sound(self.world)

    def setup(self):
        self.map = random_map()
        self.platforms = self.gen_map(self.map)
        self.ava_platforms = self.avaliable_platforms()
        self.coin = random_coin(self.ava_platforms)
        self.coins = self.gen_coin(self.coin)
        self.items, self.item_no = self.gen_item()
        self.spikes = self.gen_enemies(5, 75)
        self.wingman = self.gen_enemies(5, 100)
        self.heart = self.gen_heart()
        self.checkpoint = Item(self, self.platforms[-2].x, self.platforms[-2].y + 100)

    def gen_map(self, map):
        platforms = []
        for r in range(len(map)):
            for c in range(len(map[0])):
                if map[r][c] != '.':
                    if map[r][c] == '#':
                        p = Platform(self, (c)*100, (r+1)*100, 100, 100)
                    elif map[r][c] == '$':
                        p = Platform(self, (c)*100, 50, 100, 100)
                    platforms.append(p)
        return platforms

    def avaliable_platforms(self):
        p_lst = []
        for p in self.platforms[8:-8]:
            if p.avaliable:
                p_lst.append(p)
        return p_lst

    def gen_coin(self, coin_array):
        coins = []
        for coin in coin_array:
            c = Item(self, coin[0], coin[1])
            coins.append(c)
        return coins

    def gen_item(self):
        items = [Item(self, -100, -100)]
        for i in range(1):
            p = random.choice(self.platforms[8:-8])
            if p.avaliable:
                t = Item(self, p.x, p.y + 80)
                p.item_on()
                items.insert(0, t)
        n = random.randint(1,10)
        return items, n

    def gen_enemies(self, n, pos):
        enemies = []
        for i in range(n):
            p = random.choice(self.ava_platforms)
            if p.avaliable:
                e = Item(self, p.x, p.y + pos)
                p.item_on()
                self.ava_platforms.remove(p)
                enemies.append(e)
        return enemies

    def gen_heart(self):
        heart = [Item(self, -100, -100)]
        for i in range(1):
            p = random.choice(self.ava_platforms[10:])
            if p.avaliable:
                h = Item(self, p.x, p.y + 80)
                p.item_on()
                self.ava_platforms.remove(p)
                heart.insert(0, h)
        return heart

    def collect_coins(self):
        for c in self.coins:
            if not c.is_collected and c.collected(self.player):
                c.is_collected = True
                self.player.score += 100
                self.sound.coin_sound()

    def collect_heart(self):
        for h in self.heart:
            if not h.is_collected and h.collected(self.player):
                h.is_collected = True
                self.sound.item_sound()
                if self.player.heart_count < 3:
                    self.player.heart_count += 1

    def collect_item(self):
        t = self.items[0]
        if not t.is_collected and t.collected(self.player):
            t.is_collected = True
            self.sound.item_sound()
            if self.item_no % 2 == 0:
                self.player.y += 500
                self.player.jump()
            elif self.item_no % 2 != 0:
                self.player.score += 1000

    def hit_spikes(self, enemies):
        for sp in enemies:
            if not sp.is_collected and sp.collected(self.player):
                self.world.state = World.DEAD

    def kill_item(self, lst):
        for t in lst:
            if t.is_collected:
                index = lst.index(t)
                lst.pop(index)

    def at_check_point(self):
        return self.checkpoint.x - 40 == self.player.x and self.checkpoint.y == self.player.y

    def update(self, delta):
        self.collect_coins()
        self.kill_item(self.coins)
        self.collect_heart()
        self.kill_item(self.heart)
        self.hit_spikes(self.spikes)
        self.hit_spikes(self.wingman)
        self.collect_item()
        self.kill_item(self.items)


class World:
    START = 0
    DEAD = 1
    GAME_OVER = 2
    PASS = 3
    STILL = 4

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = World.STILL
        self.level = 1

        self.mrcorn = MrCorn(self, 100, 150)
        self.fire = Fire(self, self.width//2, -500, self.width, self.height, self.level)
        self.lv1 = Level(self, self.mrcorn, 700, 800)

        self.sound = Sound(self)

    def move_near_platform(self):
        for p in self.lv1.platforms:
            if self.mrcorn.y < p.y <= self.mrcorn.y + 100:
                self.mrcorn.x = p.x
                self.mrcorn.y = p.y + 100
                break

    def is_dead(self):
        if self.mrcorn.bottom()+70 < self.fire.top():
            self.state = World.DEAD

    def game_over(self):
        if self.mrcorn.heart_count == 0:
            self.state = World.GAME_OVER

    def next_level(self):
        if self.lv1.at_check_point():
            self.lv1.setup()
            self.state = World.PASS

    def pass_level(self):
        self.mrcorn.x = 100
        self.mrcorn.y = 150
        self.fire.x = self.width//2
        self.fire.y = -500 - (self.level * 100)
        self.level += 1
        self.fire.update_level()

    def restart(self):
        self.lv1.setup()
        self.level = 1
        self.mrcorn.x = 100
        self.mrcorn.y = 150
        self.mrcorn.heart_count = 3
        self.mrcorn.score = 0
        self.fire.level = 1
        self.fire.x = self.width//2
        self.fire.y = -500 - (self.level * 100)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.mrcorn.jump()
        elif key == arcade.key.LEFT:
            self.mrcorn.direction = DIR_LEFT
        elif key == arcade.key.RIGHT:
            self.mrcorn.direction = DIR_RIGHT

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.mrcorn.direction = DIR_STILL

    def sound_on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE and self.state == World.START:
            self.sound.play(self.sound.jump)

    def start_update(self, delta):
        self.is_dead()
        self.next_level()
        self.mrcorn.update(delta)
        self.fire.update(delta)
        self.lv1.update(delta)

    def update(self, delta):
        self.game_over()
        if self.state == World.START:
            self.start_update(delta)
        elif self.state == World.PASS:
            self.pass_level()
            self.sound.level_pass()
            self.state = World.START
        elif self.state == World.DEAD:
            self.mrcorn.heart_count -= 1
            if self.mrcorn.heart_count > 0:
                self.sound.hit_sound()
                self.state = World.START
                self.move_near_platform()
            else:
                self.sound.game_over()
                self.state = World.GAME_OVER
