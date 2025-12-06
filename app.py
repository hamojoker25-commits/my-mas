import pygame
import sys
import random

# --- 1. الإعدادات الأساسية ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Level Deceiver"
FPS = 60

# الألوان
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GROUND_COLOR = (100, 150, 50) # لون الأرضية الأخضر

# --- 2. إعدادات اللاعب (Sprite) ---
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 40
JUMP_VELOCITY = -15
GRAVITY = 0.8
WALK_SPEED = 5

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(BLACK) # لون اللاعب أسود (مثل الفيديو)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.velocity_y = 0
        self.on_ground = True

    def update(self, platforms):
        # تطبيق الجاذبية
        self.velocity_y += GRAVITY
        
        # الحركة الأفقية (المحاكاة للتنقل)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= WALK_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += WALK_SPEED

        # تطبيق الحركة العمودية
        self.rect.y += self.velocity_y
        
        self.on_ground = False
        # اكتشاف التصادمات (للقفز)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0 and self.rect.bottom <= platform.rect.bottom:
                    # الهبوط على المنصة
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0 and self.rect.top >= platform.rect.top:
                    # ضرب الرأس في منصة من الأسفل
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False

# --- 3. إعدادات المنصة والعقبات ---

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color=GROUND_COLOR):
        super().__init__()
        self.image = pygame.Surface([w, h])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# --- 4. منطق المستوى الخادع ---

def setup_level(level_id):
    # مسح جميع المجموعات
    platforms = pygame.sprite.Group()
    hazards = pygame.sprite.Group()
    
    # منصة الأرض الرئيسية
    platforms.add(Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, GROUND_COLOR))

    if level_id == 1:
        # المستوى 1: سهل في البداية
        platforms.add(Platform(150, 450, 100, 20))
        platforms.add(Platform(400, 350, 150, 20))
        # إضافة منطقة خداع: المنصة الأخيرة تختفي!
        platforms.add(Platform(650, 250, 80, 20, (200, 200, 200))) # لون مختلف للتضليل
        
        # مؤشر الخروج
        exit_point = Platform(750, SCREEN_HEIGHT - 90, 40, 40, (180, 180, 180)) 
        platforms.add(exit_point)
        
    elif level_id == 2:
        # المستوى 2: تبدأ الأرضية بالاختفاء!
        # هذه المنصة ستختفي بعد 5 ثواني
        platforms.add(Platform(50, SCREEN_HEIGHT - 150, 700, 50, (150, 50, 50)))
        # يمكن إضافة منطق داخل حلقة اللعبة لمسح المنصة بعد وقت معين
        
        # عقبة مفاجئة (الأشواك)
        hazards.add(Platform(300, SCREEN_HEIGHT - 50, 100, 10, (255, 0, 0))) # لون أحمر
        
    return platforms, hazards, exit_point

# --- 5. حلقة اللعبة الرئيسية ---

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    current_level = 1
    
    # إعداد المستويات
    platforms, hazards, exit_point = setup_level(current_level)
    player = Player(50, SCREEN_HEIGHT - 100)
    all_sprites = pygame.sprite.Group(player, platforms, hazards)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()

        # --- تحديث المنطق ---
        player.update(platforms)
        
        # 1. اكتشاف الخروج (انتهاء المستوى)
        if player.rect.colliderect(exit_point.rect):
            # تحقق خادع: يجب أن نمرر اللاعب إلى المستوى التالي فقط في المستويات الفردية
            if current_level % 2 != 0:
                 current_level += 1
                 if current_level <= 2:
                    # إعادة تحميل المستوى
                    platforms, hazards, exit_point = setup_level(current_level)
                    player = Player(50, SCREEN_HEIGHT - 100)
                    all_sprites = pygame.sprite.Group(player, platforms, hazards)
                 else:
                     print("مبروك! لقد وصلت لنهاية الديمو!")
                     running = False
            else:
                 # الخدعة: إذا كان المستوى زوجي، المخرج يقتلك!
                 print("خدعة! هذا المخرج يقتل! الموت!")
                 current_level = 1
                 platforms, hazards, exit_point = setup_level(current_level)
                 player = Player(50, SCREEN_HEIGHT - 100)
                 all_sprites = pygame.sprite.Group(player, platforms, hazards)


        # 2. اكتشاف العقبات والموت
        if pygame.sprite.spritecollideany(player, hazards) or player.rect.top > SCREEN_HEIGHT:
            print("موت! إعادة المحاولة!")
            # إعادة ضبط المستوى الحالي
            platforms, hazards, exit_point = setup_level(current_level)
            player = Player(50, SCREEN_HEIGHT - 100)
            all_sprites = pygame.sprite.Group(player, platforms, hazards)

        # --- الرسم ---
        screen.fill(WHITE) # خلفية بيضاء أو بلون متغير
        all_sprites.draw(screen)

        # تحديث الشاشة
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
