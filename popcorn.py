import arcade
from models import World, MrCorn
import random
import time

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 800
SCREEN_TITLE = 'I AM NOT POPCORN!'
SCALE = 0.5

VIEWPORT_MARGIN = 40

class ModelSprite(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
 
        super().__init__(*args, **kwargs)
 
    def sync_with_model(self):
        if self.model:
            self.set_position(self.model.x, self.model.y)
    
    def top(self):
        return self.model.y + 100
    
    def bottom(self):
        return self.model.y - 100

    def draw(self):
        self.sync_with_model()
        super().draw()

class ImNotPopcorn(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.setup()
    
    def setup(self):
        self.background = arcade.load_texture("images/bg.png")
        self.view_bottom = 0
        self.n = 1
    
        self.world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.mrcorn_sprite = ModelSprite('images/mrcorn.png', model=self.world.mrcorn, scale=SCALE)
        
        self.fire_sprite = ModelSprite('images/fire.png', model=self.world.fire)
        self.fire_sprite.append_texture(arcade.load_texture('images/fire2.png'))
        
        self.coin_list = self.init_coin()
        self.checkpoint = self.init_checkpoint()
        self.wingmans = self.init_wingman()
        
        self.coin_score = arcade.Sprite('images/score/coin1.png')

        self.timeCount = time.time()
        self.cur_texture = 0

    def init_level(self, lv):
        self.fire_sprite = ModelSprite('images/fire.png', model=lv.fire)
        self.fire_sprite.append_texture(arcade.load_texture('images/fire2.png'))
        self.coin_list = self.init_coin(lv.coins)
        self.checkpoint = self.init_checkpoint(lv.checkpoint)

    def draw_platforms(self, platforms):
        i = 1
        for platform in platforms:
            if i < 9:
                p = ModelSprite(f'images/platforms/lv{self.n}_1.png', model=platform, scale=SCALE)
            else:
                p = ModelSprite(f'images/platforms/lv{self.n}_2.png', model=platform, scale=SCALE)
            i += 1
            p.draw()
    
    def init_coin(self):
        coins_lst = []
        for coin in self.world.lv1.coins:
            c = ModelSprite('images/coin/coin1.png', model=coin)
            c.append_texture(arcade.load_texture('images/coin/coin2.png'))
            c.append_texture(arcade.load_texture('images/coin/coin3.png'))
            c.append_texture(arcade.load_texture('images/coin/coin4.png'))
            coins_lst.append(c)
        return coins_lst

    def draw_coin(self):
        for c in self.coin_list:
            if not c.model.is_collected:
                c.draw()
    
    def init_checkpoint(self):
        cp = ModelSprite('images/flags/lv1_flag1.png', model=self.world.lv1.checkpoint)
        cp.append_texture(arcade.load_texture('images/flags/lv1_flag2.png'))
        cp.append_texture(arcade.load_texture('images/flags/lv1_flag3.png'))
        return cp
    
    def draw_score(self):
        self.coin_score.append_texture(arcade.load_texture('images/score/coin2.png'))
        self.coin_score.append_texture(arcade.load_texture('images/score/coin3.png'))
        self.coin_score.append_texture(arcade.load_texture('images/score/coin4.png'))
        self.coin_score.set_position(50, SCREEN_HEIGHT + self.view_bottom - 50)
        x = arcade.Sprite('images/score/times.png')
        x.set_position(90, SCREEN_HEIGHT + self.view_bottom - 50)
        score = str(self.world.mrcorn.score)
        for i in range(len(score)):
            char = arcade.Sprite(f'images/score/{int(score[i])}.png')
            char.set_position(100+(i+1)*20, SCREEN_HEIGHT + self.view_bottom - 50)
            char.draw()
        x.draw()
        self.coin_score.draw()

    def draw_heart_bar(self):
        sp1 = ['images/score/heart.png', 'images/score/heart_empty.png', 'images/score/heart_empty.png']
        sp2 = ['images/score/heart.png', 'images/score/heart.png', 'images/score/heart_empty.png']
        sp3 = ['images/score/heart.png', 'images/score/heart.png', 'images/score/heart.png']
        n = 0
        for i in range(50, 151, 45):
            if self.world.mrcorn.heart_count == 1:
                h = arcade.Sprite(sp1[n])
            elif self.world.mrcorn.heart_count == 2:
                h = arcade.Sprite(sp2[n])
            else:
                h = arcade.Sprite(sp3[n])
            h.center_x = i
            h.center_y = SCREEN_HEIGHT + self.view_bottom - 90
            h.draw()
            n += 1

    def draw_spikes(self):
        for sp in self.world.lv1.spikes:
            sp = ModelSprite('images/spikes.png', model=sp)
            sp.draw()
    
    def init_wingman(self):
        wingmans = []
        for e in self.world.lv1.wingman:
            wm = ModelSprite('images/enemy/wingman1.png', model=e)
            wm.append_texture(arcade.load_texture('images/enemy/wingman2.png'))
            wm.append_texture(arcade.load_texture('images/enemy/wingman3.png'))
            wm.append_texture(arcade.load_texture('images/enemy/wingman4.png'))
            wm.append_texture(arcade.load_texture('images/enemy/wingman5.png'))
            wingmans.append(wm)
        return wingmans
    
    def draw_item(self):
        items = self.world.lv1.items
        n = self.world.lv1.item_no
        if n == 0:
            t = ModelSprite('images/jetpack.png', model=items[0])
        elif n == 1:
            t = ModelSprite('images/star.png', model=items[0])
        t.draw()  

    def sprite_move(self):
        if self.cur_texture == 0:
            self.fire_sprite.set_texture(1)
            self.checkpoint.set_texture(2)
            self.coin_score.set_texture(3)
            for c in self.coin_list:
                c.set_texture(3)
            for wm in self.wingmans:
                wm.set_texture(4)
            self.cur_texture = 1
        else:
            self.fire_sprite.set_texture(0)
            self.checkpoint.set_texture(0)
            self.coin_score.set_texture(0)
            for c in self.coin_list:
                c.set_texture(0)
            for wm in self.wingmans:
                wm.set_texture(0)
            self.cur_texture = 0
        self.timeCount = time.time()
    
    def draw_game_over(self):
        self.view_bottom = 0
        arcade.set_viewport(0, SCREEN_WIDTH, self.view_bottom, 
                        SCREEN_HEIGHT + self.view_bottom)
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 
                                     SCREEN_WIDTH, SCREEN_HEIGHT + self.view_bottom, arcade.color.BABY_BLUE)
        arcade.draw_text('PRESS SPACE TO RESTART', 200, 500, arcade.color.BLACK, 20)
        score = str(self.world.mrcorn.score)
        for i in range(len(score)):
            char = arcade.Sprite(f'images/score/{int(score[i])}.png')
            char.set_position(SCREEN_WIDTH//2+(i+1)*20, (SCREEN_HEIGHT + self.view_bottom)//2)
            char.draw()
    
    def draw_game(self):
        arcade.draw_rectangle_filled(SCREEN_WIDTH//2, SCREEN_HEIGHT + self.view_bottom//2, 
                                     SCREEN_WIDTH, SCREEN_HEIGHT + self.view_bottom, arcade.color.BABY_BLUE)
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, 6000 // 2,
                                      SCREEN_WIDTH, 6000, self.background)
        self.draw_platforms(self.world.lv1.platforms)
        self.checkpoint.draw()
        self.draw_coin()
        self.draw_spikes()
        for wm in self.wingmans:
            wm.draw()
        self.draw_item()
        for i in self.world.lv1.heart:
            h = ModelSprite('images/heart.png', model=i)
            h.draw()
        self.mrcorn_sprite.draw()
        self.fire_sprite.draw()
    
    def next_level(self):
        if self.n >= 6:
            self.n = 1
        else:
            self.n += 1
        self.view_bottom = 0
        arcade.set_viewport(0, SCREEN_WIDTH, self.view_bottom, 
                        SCREEN_HEIGHT + self.view_bottom)
        self.coin_list = self.init_coin()
        self.checkpoint = self.init_checkpoint()
        self.wingmans = self.init_wingman()

    def on_key_press(self, key, key_modifiers):
        self.world.on_key_press(key, key_modifiers)
        if key == arcade.key.SPACE and self.world.state == World.GAME_OVER:
            self.world.restart()
            self.n = 1
            self.coin_list = self.init_coin()
            self.checkpoint = self.init_checkpoint()
            self.wingmans = self.init_wingman()
            self.view_bottom = 0
            arcade.set_viewport(0, SCREEN_WIDTH, self.view_bottom, 
                            SCREEN_HEIGHT + self.view_bottom)
            self.world.state = World.START
    
    def on_key_release(self, key, key_modifiers):
        self.world.on_key_release(key, key_modifiers)
    
    def update(self, delta):
        changed = False
        self.world.update(delta)

        if time.time() - self.timeCount > 0.2:
            self.sprite_move()

        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.mrcorn_sprite.top() > top_bndry:
            self.view_bottom += self.mrcorn_sprite.top() - top_bndry
            changed = True

        if changed:
            arcade.set_viewport(0, SCREEN_WIDTH, self.view_bottom, 
                                SCREEN_HEIGHT + self.view_bottom)
            if self.fire_sprite.model.top() < self.view_bottom:
                self.fire_sprite.model.y = self.view_bottom - 200

    def on_draw(self):
        arcade.start_render()
        if self.world.state == World.GAME_OVER:
            self.draw_game_over()
        else:
            if self.world.state == World.PASS:
                self.next_level()
            self.draw_game()
            self.draw_score()
            self.draw_heart_bar()
            arcade.draw_text(str(self.world.level), SCREEN_WIDTH - 50, SCREEN_HEIGHT + self.view_bottom - 50, arcade.color.RED, 20)

def main():
    window = ImNotPopcorn(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.set_window(window)
    arcade.run()

if __name__ == '__main__':
    main()
