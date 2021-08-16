import pygame, sys
import os
import time
import random
from pygame.locals import *
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")# değiştirilecek

# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player player
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel+1)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel): # Düşman aşağıya doğru hareket, red düşmanlar player ı takip etsin
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    pygame.mouse.set_visible(False)
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()
    mouseX=0
    mouseY=0
    while run:
        clock.tick(FPS) # Same FPS for all devices
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0: # düşman kalmayınca yeni levele geç
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == MOUSEBUTTONDOWN:
                player.shoot()
        keys = pygame.key.get_pressed() 
        #if keys[pygame.K_a] and player.x - player_vel > 0: # left
        #    player.x -= player_vel
        #if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
         #   player.x += player_vel
        #if keys[pygame.K_w] and player.y - player_vel > 0: # up
         #   player.y -= player_vel
        #if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
          #  player.y += player_vel
        mouseX,mouseY = pygame.mouse.get_pos()
        U_boyutuX,U_boyutuY=YELLOW_SPACE_SHIP.get_size()[0],YELLOW_SPACE_SHIP.get_size()[1]
        #if mouseX  < 750 or mouseX>0:
            #mouseX = 750 - U_boyutuX
        player.x = mouseX
        #if mouseY >(750) or mouseY<0:
            #mouseY = 750- U_boyutuY
        player.y = mouseY
        #screen.blit(U_gemisi,(mouseX,mouseY))
        
        #if keys[pygame.K_SPACE]:
            #player.shoot()
        
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if enemy.ship_img == RED_SPACE_SHIP: # red enemy player'ı yavaş yavaş takip etsin
                if (enemy.x - player.x) > 0: # bizim gemi soldaysa
                    enemy.x -= 1#(2*abs(enemy.x-player.x)+1)%2
                if (enemy.x - player.x) < 0: # bizim gemi sağdaysa
                    enemy.x += 1#(2*abs(enemy.x-player.x)+1)%2    
                else :
                    enemy.move(enemy_vel)

            if enemy.ship_img == GREEN_SPACE_SHIP:# yeşil gemi hateketleri
                if abs(enemy.x-player.x)<=150 and player.y-enemy.y <= 150:
                    if (enemy.x - player.x) > 0: # player soldaysa
                        if WIDTH-enemy.x > 36+enemy.get_width():
                            enemy.x += 3
                    if (enemy.x - player.x) < 0: # player sağdaysa
                        if enemy.x > 10:
                            enemy.x -= 3
            
            if enemy.ship_img == BLUE_SPACE_SHIP: # blue enemy yi durdur
                if enemy.y == 30:
                    enemy.y -= 1

                    if (enemy.x - player.x) > 25: # player soldaysa
                        enemy.x -= 1
                    if (enemy.x - player.x) < 25: # player sağdaysa
                        enemy.x += 1


            if collide(enemy, player): # Enemy ve player çapışırsa
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
def options():
    running =True
    tıklama = False
    while running:
        WIN.fill((0,0,0))
        draw_text('options',font,(255,255,255),WIN,20,20) # main menu yazısının rengi

        mx1,my1=pygame.mouse.get_pos()

        o_button_1 = pygame.Rect(50,100,200,50)
        o_button_2 = pygame.Rect(50,200,200,50)
        o_button_3 = pygame.Rect(50,300,200,50)
        
        if o_button_1.collidepoint((mx1,my1)):
            if tıklama:
                screen1 = pygame.display.set_mode(1024,768,pygame.RESIZABLE)
                screen1.fill((0,0,0))

        if o_button_2.collidepoint((mx1,my1)):
            if tıklama:
                screen2 = pygame.display.set_mode(400,300,pygame.RESIZABLE)

        if o_button_3.collidepoint((mx1,my1)):
            if tıklama:
                screen3 = pygame.display.set_mode(640,480,pygame.RESIZABLE)

        pygame.draw.rect(WIN,(255,0,0),o_button_1)
        draw_text('gemi rengi : kırmızı',font,(255,255,255),WIN,50,100)
        pygame.draw.rect(WIN,(255,0,0),o_button_2)
        draw_text('gemi rengi : sarı',font,(255,255,255),WIN,50,200)
        pygame.draw.rect(WIN,(255,0,0),o_button_3)
        draw_text('çözünürlük : 640-480',font,(255,255,255),WIN,50,300)
        tıklama = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    running  = False
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    tıklama = True
        pygame.display.update()
        mainClock.tick(60)
def score():
    running =True
    while running:
        WIN.blit(BG, (0,0))
        draw_text('score',font,(255,255,255),WIN,20,20) # score yazısının rengi

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    running  = False
        pygame.display.update()
        mainClock.tick(60)

## Hazırlayanların gözükeceği sekme credits butonuna basıldığında işlem gercekleştirilir
def credits():
    running =True
    while running:
        WIN.blit(BG, (0,0))
        draw_text('HAZIRLAYANLAR',font,(255,255,255),WIN,300,200) # credits yazısının rengi
        draw_text('Reha BİLİR',font,(255,255,255),WIN,300,300)
        draw_text('Emre SARIMEHMET',font,(255,255,255),WIN,300,400)
        draw_text('Uğurcan YİĞİT',font,(255,255,255),WIN,300,500)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    running  = False
        pygame.display.update()
        mainClock.tick(60)
        
## Exit fonksiyonu çıkış butonuna basıldığı zaman çıkış işleminin yapılamasını sağlar
def exit():
    pygame.quit()
    sys.exit()

mainClock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

def draw_text(text,font,color,surface,x,y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x,y)
    surface.blit(textobj, textrect)
   
def start():
    
    while True:
        WIN.blit(BG, (0,0))
        pygame.mouse.set_visible(True)
##        WIN.fill((0,0,0))
##        screen.fill((0,0,0)) # arkaplan rengi
        draw_text('main menu',font,(255,255,255),WIN,20,20) # main menu yazısının rengi

## Mouse pozisyonu alınır
        mx, my = pygame.mouse.get_pos() 
## Butonlar tanımlanır        
        button_1 = pygame.Rect(50,100,200,50)
        button_2 = pygame.Rect(50,200,200,50)
        button_3 = pygame.Rect(50,300,200,50)
        button_4 = pygame.Rect(50,400,200,50)
        button_5 = pygame.Rect(50,500,200,50)
        
## Butonlara tıklandığı zaman ilgili sekmeye gidilir
        if button_1.collidepoint((mx,my)):
            if click:
                main()
##                game()
                
        if button_2.collidepoint((mx,my)):
            if click:
                options()
        if button_3.collidepoint((mx,my)):
            if click:
                score()
        if button_4.collidepoint((mx,my)):
            if click:
                credits()
        if button_5.collidepoint((mx,my)):
            if click:
                exit()
                
## Butonlar ekrana bastırılır
        pygame.draw.rect(WIN, (255,0,0), button_1)
        draw_text('game',font,(255,255,255),WIN,50,100)
        pygame.draw.rect(WIN, (255,0,0), button_2)
        draw_text('options',font,(255,255,255),WIN,50,200)
        pygame.draw.rect(WIN, (255,0,0), button_3)
        draw_text('score',font,(255,255,255),WIN,50,300)
        pygame.draw.rect(WIN, (255,0,0), button_4)
        draw_text('credits',font,(255,255,255),WIN,50,400)
        pygame.draw.rect(WIN, (255,0,0), button_5)
        draw_text('exit',font,(255,255,255),WIN,50,500)
        
        
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        pygame.display.update()
        mainClock.tick(60)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, HEIGHT/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                start()
                #main()
    pygame.quit()


main_menu()

