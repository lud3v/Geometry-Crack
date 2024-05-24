import sys
import random
import json
import pygame.draw
import pygame, pygame_gui, pygame.transform
import moviepy.editor as mp
import threading

pygame.init()

# Constants
run = True
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 500

# Ground Configuration
GROUND_HEIGHT = 20
GROUND_WIDTH = MIN_SCREEN_WIDTH  # Set ground width to match screen width
ground_y = MIN_SCREEN_HEIGHT - GROUND_HEIGHT
ground_color = (0, 0, 255)  # Blue

# Obstacle Configuration
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 65
INITIAL_OBSTACLE_SPEED = 9
TRIGGERED_OBSTACLE_COLOR = (222, 0, 255)
TRIGGERED_STAY_COLOR = (0, 255, 0)
DEFAULT_OBSTACLE_COLOR = (255, 0, 0)
MINIMUM_RANGE = [1500, 1800, 2000, 2500]
JUMP_OVER = 0
DUCK_UNDER = 1
STAY_STILL = 2

COOLDOWN_TIME = 300
last_button_click_time = 0
previous_slider_value = None

# Coin Configuration
COIN_WIDTH = 10
COIN_HEIGHT = 15
COIN_SPEED = 10
COIN_COLOR = (255, 215, 0)
COIN_SPAWN_INTERVAL = 1000
LAST_COIN_SPAWN_TIME = 0
coins = []



# colour
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# lgbtq+ Title
COL_SPD = 10
COL_DIR= [-1, 1, -1]
DEF_COL = [50, 100, 255]
MINIMUM = 20
MAXIMUM = 200

# Screen Setup
screen = pygame.display.set_mode((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Crack")

# UI Manager
ui_manager = pygame_gui.UIManager((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))

# Font 
font = pygame.font.Font(None, 36)  # Choose font and size

# save and load Song volume
def save_volume(volume, volume_slider_position):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['Music_Volume'] = round(volume, 1)
    data['volume_slider_position'] = round(volume_slider_position, 1)

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_volume():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('Music_Volume', 0.1)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0.1

def save_sound_volume(volume, sound_slider_position):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['Sound_Volume'] = round(volume, 1)
    data['sound_slider_position'] = round(sound_slider_position, 1)

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_sound_volume():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('Sound_Volume', 0.1)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0.1
    
# Sound settings
SOUND_VOLUME = 0.1
CURRENT_VOLUME = 0.1

music = pygame.mixer.music.load('./Music/song1.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(CURRENT_VOLUME)

# Load initial Soundvolume
SOUND_VOLUME = load_sound_volume()

sound_effects = {
    'fu_sound': pygame.mixer.Sound('./Sounds/f_u.mp3'),
    'button_click': pygame.mixer.Sound('./Sounds/click.mp3'),
    'death': pygame.mixer.Sound('./Sounds/death.mp3'),
    'jump': pygame.mixer.Sound('./Sounds/boing.mp3')
}

for sound in sound_effects:
    sound_obj = sound_effects[sound]
    sound_obj.set_volume(SOUND_VOLUME) 
    globals()[sound] = sound_obj


# Title video
TARGET_WIDTH = MIN_SCREEN_WIDTH
TARGET_HEIGHT = MIN_SCREEN_HEIGHT
title_vid = mp.VideoFileClip("title_screen.mp4")
title_vid_width, title_vid_height = title_vid.size
title_vid_surface = pygame.Surface((title_vid.size))

# Player Configuration
player_config = {
    'normal_width': 40,
    'normal_height': 40,
    'duck_width': 40,
    'duck_height': 10,
    'stretch_width': 10,
    'stretch_height': 250,
    'extended_stretch': 300,
    'player_x': 50,
    'player_y': MIN_SCREEN_HEIGHT - 40,
    'player_color': (255, 255, 255),
    'player_velocity': 0,
    'jump_force': -15,
    'gravity': 1,
    'is_ducking': False,
    'is_stretching': False,
    'normal_state:': None
}

# Animation for Duck under Configuration
animation_config = {
    'animation_speed' : 3,
    'animation_trigger_distance' : 285,  # Distance to trigger "Duck Under" animation
    'animation_target_y' : ground_y - 380  # Final height for duck under
}
# Color change for Stay Stil obj
stay_config = {
    'color_change_distance' : 320,
    'triggered_height' : 150
}

def update_video():
    global t, run
    while run:
        t += dt
        display_frame(t)
        pygame.time.wait(int(1000 / 30))

video_thread = threading.Thread(target=update_video)
video_thread.start()

def display_frame(t):
    if t >= title_vid.duration:
        t = t % title_vid.duration  # Loop the video
    frame = title_vid.get_frame(t)
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    scaled_surface = pygame.transform.scale(frame_surface, (TARGET_WIDTH, TARGET_HEIGHT))
    title_vid_surface.blit(scaled_surface, (0, 0))


# Load initial Volume
current_volume = load_volume()
pygame.mixer.music.set_volume(current_volume)
volume_slider_position = int(current_volume * 10) # convert volume to slider position

# load initial Soundvolume
SOUND_VOLUME = load_sound_volume()
sound_slider_position = int(SOUND_VOLUME * 10)

# Score saving
def save_high_score(score):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['high_score'] = score

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_high_score():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def save_recent_score(score):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['recent_score'] = score

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_recent_score():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('recent_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0    
    

def save_coin_ammount(coin_ammount):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    data['coins'] = coin_ammount

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_coin_ammount():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('coins', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

coin_y_high = 370
coin_y_low = 470

# Define Spawn coins
def spawn_coins():
    coin_x = MIN_SCREEN_WIDTH
    coin_y = random.randint(coin_y_high, coin_y_low)
    coins.append({"x": coin_x, "y": coin_y})

# Define movement from coins
def move_and_draw_coins(screen):
    global coins
    for coin in coins:
        coin["x"] -= COIN_SPEED
        pygame.draw.rect(screen, COIN_COLOR, (coin["x"], coin["y"], COIN_WIDTH, COIN_HEIGHT))
    
    # Remove coins when off-screen
    coins = [coin for coin in coins if coin["x"] + COIN_WIDTH > 0]

# Define obstacle positions based on type
def set_obstacle_position(obstacle_type):
    if obstacle_type == JUMP_OVER:
        return ground_y - OBSTACLE_HEIGHT  # Ground level for "Jump Over"
    elif obstacle_type == DUCK_UNDER:
        return ground_y - OBSTACLE_HEIGHT  # Ground level at start, then moves up if triggered
    elif obstacle_type == STAY_STILL:
        return ground_y - OBSTACLE_HEIGHT

# Reset Function
def reset_game():
    global player_x, player_y, player_velocity, player_size, is_ducking, is_stretching, obstacles, score, recent_score, coins, coin_ammount
    player_x = 50
    player_y = MIN_SCREEN_HEIGHT - player_config['normal_height']  # Ground level
    player_velocity = 0
    player_size = (player_config['normal_width'], player_config['normal_width'])  # Default size
    is_ducking = False  # Reset ducking state
    is_stretching = False
    coins = []
    obstacles = []
    obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER, STAY_STILL])
    obstacle_color = DEFAULT_OBSTACLE_COLOR
    new_obstacle = {
        "x": random.randint(MIN_SCREEN_WIDTH, MIN_SCREEN_WIDTH + 300),
        "type": obstacle_type,
        "y": set_obstacle_position(obstacle_type),
        "color": obstacle_color,
        "is_moving": False,
        "height": OBSTACLE_HEIGHT
    }
    obstacles.append(new_obstacle)
    recent_score = load_recent_score()

# Initialize Game
reset_game()

# Icon
Icon = pygame.image.load('./Images/icon.png')
pygame.display.set_icon(Icon)

# Load the overlay image
overlay_image = pygame.image.load('rührei.png')
overlay_image = pygame.transform.scale(overlay_image, (MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))

# Score Loading
high_score = load_high_score()
recent_score = load_recent_score()

# Coin ammount Loading
coin_ammount = load_coin_ammount()

# Flag to track whether rührei.png is shown
show_overlay = False

# xy Variables for buttons/sliders
volume_slidersx= 650

# Game states
MAIN_MENU = 0
OPTIONS = 1
PLAYING = 2
PAUSED = 3
QUIT = 4

    

game_state = MAIN_MENU
# Title
def draw_text(text, size, col, x, y):
    font = "Ldfcomicsans-jj7l.ttf"
    font = pygame.font.Font(font, size)
    text_surface = font.render(text, True, col)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def col_change(color: list, direction: list) -> None:
    for i in range(3):
        color[i] += COL_SPD * direction[i]
        if color[i] >= MAXIMUM or color[i] <= MINIMUM:
            direction[i] *= -1
        if color[i] >= MAXIMUM:
            color[i] = MAXIMUM
        elif color[i] <= MINIMUM:
            color[i] = MINIMUM


# Function to create and hide a button
def create_hidden_button(rect, text, manager):
    button = pygame_gui.elements.UIButton(relative_rect=rect, text=text, manager=manager)
    button.hide()
    return button

# Function to create and hide a slider
def create_hidden_slider(rect, start_value, value_range, manager):
    slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=rect, start_value=start_value, value_range=value_range, manager=manager)
    slider.hide()
    return slider

# Main Buttons
start_button = create_hidden_button(pygame.Rect((350, 190), (300, 50)), 'START', ui_manager)
start_button.show()
quit_button = create_hidden_button(pygame.Rect((350, 310), (300, 50)), 'QUIT', ui_manager)
quit_button.show()
options_button = create_hidden_button(pygame.Rect((350, 250), (300, 50)), 'OPTIONS', ui_manager)
options_button.show()
back_main_button = create_hidden_button(pygame.Rect((80, 30), (100, 50)), 'BACK', ui_manager)
# Pause Buttons
higher_options_button = create_hidden_button(pygame.Rect((350, 160), (300, 50)), 'OPTIONS', ui_manager)
back_game_button = create_hidden_button(pygame.Rect((80, 30), (100, 50)), 'BACK', ui_manager)
resume_button = create_hidden_button(pygame.Rect((350, 100), (300, 50)), 'RESUME', ui_manager)
menu_button = create_hidden_button(pygame.Rect((350, 220), (300, 50)), 'BACK TO MENU', ui_manager)

# Volume Slider
volume_slider = create_hidden_slider(pygame.Rect((volume_slidersx, 150), (140, 20)), current_volume * 10, (0, 10), ui_manager)

# Sound Slider
sound_slider = create_hidden_slider(pygame.Rect((volume_slidersx, 180), (140, 20)), SOUND_VOLUME * 10, (0, 10), ui_manager)

# Initialize Game

clock = pygame.time.Clock()
score = 0


# Timer Variables
t = 0.0
dt = 1 / 30.0


player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])

default_y_pos = player_rect.y

# Main Game Loop
while run:
    time_delta = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
    t += dt

    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        ui_manager.process_events(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                buttons = [start_button, quit_button, options_button, higher_options_button, back_main_button, back_game_button, resume_button, menu_button]

                if event.ui_element in buttons:
                    sound_effects['button_click'].play()

                if event.ui_element == start_button:
                    game_state = PLAYING
                    score = 0
                    reset_game()
                    pygame.time.delay(500)
                    
                elif event.ui_element == options_button:
                    game_state = OPTIONS
                    volume_slider.show()
                    sound_slider.show()
                    back_main_button.show()

                elif event.ui_element == higher_options_button:
                    game_state = OPTIONS
                    volume_slider.show()
                    sound_slider.show()
                    back_game_button.show()     

                elif event.ui_element == back_main_button:
                    game_state = MAIN_MENU
                    volume_slider.hide()
                    sound_slider.hide()
                    back_main_button.hide()

                elif event.ui_element == back_game_button:
                    game_state = PAUSED
                    volume_slider.hide()
                    sound_slider.hide()
                    back_game_button.hide()

                elif event.ui_element == resume_button:
                    game_state = PLAYING
                elif event.ui_element == quit_button:      
                    game_state = QUIT
                    pygame.time.delay(500)
                    run = False

                elif event.ui_element == menu_button:
                    game_state = MAIN_MENU

            
                if game_state == PLAYING:
                    start_button.visible = False
                    options_button.visible = False
                    resume_button.visible = False
                    quit_button.visible = False
                    menu_button.visible = False
                    higher_options_button.visible = False

                elif game_state == PAUSED:
                    menu_button.visible = True
                    resume_button.visible = True
                    higher_options_button.visible = True
                    back_game_button.visible = False
                    
                elif game_state == MAIN_MENU:
                    resume_button.visible = False
                    menu_button.visible = False
                    higher_options_button.visible = False
                    start_button.visible = True
                    options_button.visible = True
                    quit_button.visible = True

                elif game_state == OPTIONS:
                    menu_button.visible = False
                    resume_button.visible = False
                    higher_options_button.visible = False
                    start_button.visible = False
                    options_button.visible = False
                    quit_button.visible = False


            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == volume_slider:
                    current_volume = event.value / 10.0
                    pygame.mixer.music.set_volume(current_volume)
                    save_volume(current_volume, event.value)
                
                if event.ui_element == sound_slider:
                    SOUND_VOLUME = event.value / 10.0
                    sound_effects['fu_sound'].set_volume(SOUND_VOLUME)
                    sound_effects['button_click'].set_volume(SOUND_VOLUME)
                    sound_effects['death'].set_volume(SOUND_VOLUME)
                    sound_effects['jump'].set_volume(SOUND_VOLUME)
                    current_time = pygame.time.get_ticks()
                    save_sound_volume(SOUND_VOLUME, event.value)

                    current_slider_value = event.value
                    if previous_slider_value is None or current_slider_value != previous_slider_value:
                        current_time = pygame.time.get_ticks()
                        if current_time - last_button_click_time >= COOLDOWN_TIME:
                            sound_effects['jump'].play()
                            last_button_click_time = current_time
                    # Update the previous slider value
                    previous_slider_value = current_slider_value
                    
    
        ui_manager.process_events(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_state != MAIN_MENU and game_state != PAUSED and game_state != OPTIONS:
                game_state = PAUSED
                menu_button.show()
                resume_button.show()
                higher_options_button.show()

    # Update game state
    if game_state == PLAYING and game_state != PAUSED:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not is_ducking and player_y >= ground_y - player_config['normal_height']:
            player_velocity = player_config['jump_force']
            sound_effects['jump'].play()

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if player_y == ground_y - player_config['normal_height']:
                is_ducking = True
                player_size = (player_config['duck_width'], player_config['duck_height'])
                player_y = ground_y - player_config['duck_height']

        elif keys[pygame.K_p]:
            if keys[pygame.K_a]:
                player_x -= 8
            elif keys[pygame.K_d]:
                player_x += 8

        elif keys[pygame.K_m]:
            show_overlay = True
            pygame.mixer.Sound.play(sound_effects['fu_sound'])
            
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s or pygame.K_DOWN:
                is_ducking = False
                player_size = (player_config['normal_width'], player_config['normal_height'])               

            elif event.key == pygame.K_m:
                show_overlay = False
            
        is_player_moving = keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_SPACE] or keys[pygame.K_s] or keys[pygame.K_DOWN]
        
        # Update score
        score += 10
        
        # Gravity and player movement
        player_velocity += player_config['gravity']
        player_y += player_velocity
        if player_y > ground_y - player_size[1]:  # Ground contact check
            player_y = ground_y - player_size[1]
            player_velocity = 0

    
        # Obstacle creation and update
        new_obstacle = {}
        if len(obstacles) == 0 or MIN_SCREEN_WIDTH - obstacles[-1].get("x", MIN_SCREEN_WIDTH) >= random.choice(MINIMUM_RANGE):
            obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER, STAY_STILL])
            obstacle_color = DEFAULT_OBSTACLE_COLOR
            new_obstacle = {
                "x": MIN_SCREEN_WIDTH,
                "type": obstacle_type,
                "y": set_obstacle_position(obstacle_type),
                "color": obstacle_color,
                "is_moving": False,
                "height": OBSTACLE_HEIGHT
            }
            obstacles.append(new_obstacle)
        
        # Coin spawning
        current_time = pygame.time.get_ticks()
        if current_time - LAST_COIN_SPAWN_TIME > COIN_SPAWN_INTERVAL:
            spawn_coins()
            LAST_COIN_SPAWN_TIME = current_time

        # Move and draw coins
        move_and_draw_coins(screen)

        # Collision detection for coins
        
        for coin in coins:
            coin_rect = pygame.Rect(coin["x"], coin["y"], COIN_WIDTH, COIN_HEIGHT)
            if player_rect.colliderect(coin_rect):
                coins.remove(coin)
                coin_ammount += 1

        # Move obstacles
        for obstacle in obstacles:
            # Move obstacles
            obstacle["x"] -= INITIAL_OBSTACLE_SPEED

            if obstacle["type"] == DUCK_UNDER and obstacle["x"] - player_x <= animation_config['animation_trigger_distance']:
                obstacle["is_moving"] = True  # Trigger animation for duck under
                obstacle["color"] = TRIGGERED_OBSTACLE_COLOR

            if obstacle["is_moving"] and obstacle["y"] > ground_y - animation_config['animation_target_y']:
                obstacle["y"] -= animation_config['animation_speed']

            if obstacle["type"] == STAY_STILL and obstacle["x"] - player_x <= stay_config['color_change_distance']:
                obstacle["color"] = TRIGGERED_STAY_COLOR
                obstacle["y"] = ground_y - stay_config['triggered_height']  # Adjust position
                obstacle["height"] = stay_config['triggered_height']  # Change height

            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, obstacle["height"])

            if player_rect.colliderect(obstacle_rect):  # Collision check
                if obstacle["type"] == STAY_STILL:
                    if not is_player_moving and not is_ducking and player_y >= ground_y - player_config['normal_height']:
                        # Player is not moving, not ducking, and on the ground
                        pass  # Player survives collision
                    else:
                        # Player is moving or ducking or stretching
                        sound_effects['death'].play()
                        save_recent_score(score)
                        recent_score = score  # Update recent_score before resetting
                        if score > high_score:
                            high_score = score
                            save_high_score(high_score)
                        save_coin_ammount(coin_ammount)
                        score = 0
                        reset_game()
                        break
                else:
                    # For other types of obstacles
                    sound_effects['death'].play()
                    save_recent_score(score)
                    recent_score = score  # Update recent_score before resetting
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    save_coin_ammount(coin_ammount)
                    score = 0
                    reset_game()
                    break
                
            
                # Adjust player position if collided with the ground
            if player_y >= ground_y - player_size[1]:
                player_y = ground_y - player_size[1]

        

    # Draw everything
    volume_number = load_volume()
    sound_volume_number = load_sound_volume()

    # Title
    if game_state == MAIN_MENU:
        screen.fill((BLACK))
        display_frame(t)
        screen.blit(title_vid_surface, (0, 1))
        draw_text("Geometry Crack", 130, DEF_COL, MIN_SCREEN_WIDTH / 2, 100)
        col_change(DEF_COL, COL_DIR)
        draw_text("Version: Alpha 3.0", 20, WHITE, 90, 485)

    if game_state == OPTIONS:
        draw_text("Volume", 25, WHITE, 720, 135)

        draw_text("Music", 20, WHITE, 614, 162)
        song_volume_int = int(volume_number * 10)
        draw_text(str(song_volume_int), 20, WHITE, 800, 162)
        
        draw_text("Sounds", 20, WHITE, 614, 191)
        sound_volume_int = int(sound_volume_number * 10)
        draw_text(str(sound_volume_int), 20, WHITE, 800, 191)
    
    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)

    if game_state == PLAYING or game_state == PAUSED:
        pygame.draw.rect(screen, ground_color, (0, ground_y, GROUND_WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(screen, player_config['player_color'], (player_x, player_y, player_size[0], player_size[1]))
        

        for obstacle in obstacles:
            pygame.draw.rect(screen, obstacle["color"], (obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, obstacle["height"]))
        
        if show_overlay:
            screen.blit(overlay_image, (0, 0))


        score_text = font.render(f"Score: {score}", True, (WHITE))
        screen.blit(score_text, (10, 10))

        high_score_text = font.render(f"Highscore: {high_score}", True, (255, 230, 0))
        screen.blit(high_score_text, (10, 70))

        recent_score_text = font.render(f"Recent Score: {recent_score}", True, (WHITE))
        screen.blit(recent_score_text, (10, 40))

        coin_text = font.render(f"Coins: {coin_ammount}", True, (255, 230, 0))
        screen.blit(coin_text, (850, 10))    
    
    pygame.display.flip()
video_thread.join()
pygame.quit()
sys.exit()