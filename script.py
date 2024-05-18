import sys
import pygame
import pygame_gui
import random
import json

pygame.init()

# Game Setup
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Geometry Crack")

# Function to toggle fullscreen
def toggle_fullscreen():
    if screen.get_flags() & pygame.FULLSCREEN:
        pygame.display.set_mode((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT), pygame.RESIZABLE)
    else:
        pygame.display.set_mode((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT), pygame.FULLSCREEN)

# Background music
music = pygame.mixer.music.load('song1.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Sound effects
fu_sound = pygame.mixer.Sound('f_u.mp3')
fu_sound.set_volume(1)

# Game Constants
is_paused = False
run = True
clock = pygame.time.Clock()

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

# Player Configuration
normal_width = 40
normal_height = 40
duck_width = 40  # Width when ducking
duck_height = 10  # Height when ducking
player_size = (normal_width, normal_height)  # Default player size
player_x = 50
player_y = MIN_SCREEN_HEIGHT - normal_height  # Ground level
player_color = (255, 255, 255)  # White
player_velocity = 0
jump_force = -15
gravity = 1
is_ducking = False  # State to track ducking

# Ground Configuration
ground_height = 20
ground_width = MIN_SCREEN_WIDTH  # Set ground width to match screen width
ground_y = MIN_SCREEN_HEIGHT - ground_height
ground_color = (0, 0, 255)  # Blue

# Obstacle Configuration
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 65
OBSTACLE_SPEED = 9
TRIGGERED_OBSTACLE_HEIGHT = 120
TRIGGERED_OBSTACLE_COLOR = (222, 0, 255)
DEFAULT_OBSTACLE_COLOR = (255, 0, 0)

# Obstacle Types
JUMP_OVER = 0
DUCK_UNDER = 1

# Define obstacle positions based on type
def set_obstacle_position(obstacle_type):
    if obstacle_type == JUMP_OVER:
        return ground_y - OBSTACLE_HEIGHT  # Ground level for "Jump Over"
    elif obstacle_type == DUCK_UNDER:
        return ground_y - OBSTACLE_HEIGHT  # Ground level at start, then moves up if triggered

# Animation Configuration
animation_speed = 3
animation_trigger_distance = 285  # Distance to trigger "Duck Under" animation
animation_target_y = ground_y - 280  # Final height for duck under

# Reset Function
def reset_game():
    global player_x, player_y, player_velocity, player_size, is_ducking, obstacles, score, recent_score
    player_x = 50
    player_y = MIN_SCREEN_HEIGHT - normal_height  # Ground level
    player_velocity = 0
    player_size = (normal_width, normal_height)  # Default size
    is_ducking = False  # Reset ducking state
    obstacles = []
    obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER])
    obstacle_color = DEFAULT_OBSTACLE_COLOR
    new_obstacle = {
        "x": random.randint(MIN_SCREEN_WIDTH, MIN_SCREEN_WIDTH + 300),
        "type": obstacle_type,
        "y": set_obstacle_position(obstacle_type),
        "color": obstacle_color,
        "is_moving": False
    }
    obstacles.append(new_obstacle)
    recent_score = load_recent_score()

# Initialize Game
reset_game()

# Load the overlay image
overlay_image = pygame.image.load('rührei.png')

# Scale the image to match the screen size
overlay_image = pygame.transform.scale(overlay_image, (MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))

# Font Configuration
font = pygame.font.Font(None, 36)  # Choose font and size

# Score Variables
score = 0
high_score = load_high_score()
recent_score = load_recent_score()

# Flag to track whether the overlay should be shown
show_overlay = False

# Game states
MAIN_MENU = 0
PLAYING = 1
PAUSED = 2
QUIT = 3

game_state = MAIN_MENU

# Create UI manager
ui_manager = pygame_gui.UIManager((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))

# Create Start Button
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 200), (300, 50)),
                                            text='START',
                                            manager=ui_manager)

# Create Quit Button
quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 270), (300, 50)),
                                           text='QUIT',
                                           manager=ui_manager)

# Main Game Loop
while run:
    time_delta = clock.tick(60) / 1000.0  # Convert milliseconds to seconds

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.VIDEORESIZE:
            MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT), pygame.RESIZABLE)
            ground_width = MIN_SCREEN_WIDTH
            ground_y = MIN_SCREEN_HEIGHT - ground_height

            start_button.set_relative_position((MIN_SCREEN_WIDTH // 2 - 150, 200))
            quit_button.set_relative_position((MIN_SCREEN_WIDTH // 2 - 150, 270))

        elif event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button or event.ui_element == quit_button:
                    start_button.visible = False
                    quit_button.visible = False
                if event.ui_element == start_button:
                    game_state = PLAYING
                elif event.ui_element == quit_button:
                    run = False
        ui_manager.process_events(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_state != MAIN_MENU:
                is_paused = not is_paused
            elif event.key == pygame.K_f:
                toggle_fullscreen()

    # Update game state
    if game_state == PLAYING and not is_paused:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not is_ducking and player_y >= ground_y - normal_height:
            player_velocity = jump_force
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if player_y == ground_y - normal_height:
                is_ducking = True
                player_size = (duck_width, duck_height)
                player_y = ground_y - duck_height
        elif keys[pygame.K_p]:
            if keys[pygame.K_a]:
                player_x -= 8
            elif keys[pygame.K_d]:
                player_x += 8

        elif keys[pygame.K_m]:
            show_overlay = True
            pygame.mixer.Sound.play(fu_sound)
            pygame.mixer.Sound.set_volume(fu_sound, 1)
            
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s or pygame.K_DOWN:
                is_ducking = False
                player_size = (normal_width, normal_height)
            elif event.key == pygame.K_m:
                show_overlay = False

        # Update score
        score += 1 
        # Definition of the minimum range
        minimum_range = [1500, 1800, 2000, 2500]

        # Gravity and player movement
        player_velocity += gravity
        player_y += player_velocity
        if player_y > ground_y - player_size[1]:  # Ground contact check
            player_y = ground_y - player_size[1]
            player_velocity = 0

        # Obstacle creation and update
        if len(obstacles) == 0 or MIN_SCREEN_WIDTH - obstacles[-1]["x"] >= random.choice(minimum_range):
            obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER])
            obstacle_color = DEFAULT_OBSTACLE_COLOR
            new_obstacle = {
                "x": MIN_SCREEN_WIDTH,
                "type": obstacle_type,
                "y": set_obstacle_position(obstacle_type),
                "color": obstacle_color,
                "is_moving": False
            }
            obstacles.append(new_obstacle)

        # Move obstacles
        for obstacle in obstacles:
            obstacle["x"] -= OBSTACLE_SPEED
                    
            if obstacle["type"] == DUCK_UNDER and obstacle["x"] - player_x <= animation_trigger_distance:
                obstacle["is_moving"] = True  # Trigger animation for duck under
                obstacle["color"] = TRIGGERED_OBSTACLE_COLOR
                

            if obstacle["is_moving"] and obstacle["y"] > ground_y - animation_target_y:
                obstacle["y"] -= animation_speed

            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

            if player_rect.colliderect(obstacle_rect):  # Collision check
                save_recent_score(score)
                recent_score = score  # Update recent_score before resetting
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                score = 0
                reset_game()
                break

    # Draw everything
    screen.fill((0, 0, 0))

    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)

    if game_state == PLAYING:
        pygame.draw.rect(screen, ground_color, (0, ground_y, ground_width, ground_height))

        pygame.draw.rect(screen, player_color, (player_x, player_y, player_size[0], player_size[1]))

        for obstacle in obstacles:
            pygame.draw.rect(screen, obstacle["color"], (obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

        if show_overlay:
            screen.blit(overlay_image, (0, 0))

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        high_score_text = font.render(f"Highscore: {high_score}", True, (255, 230, 0))
        screen.blit(high_score_text, (10, 70))

        recent_score_text = font.render(f"Recent Score: {recent_score}", True, (255, 255, 255))
        screen.blit(recent_score_text, (10, 40))

        if is_paused:
            paused_text = font.render("Paused", True, (255, 0, 0))
            screen.blit(paused_text, ((MIN_SCREEN_WIDTH - paused_text.get_width()) // 2, (MIN_SCREEN_HEIGHT - paused_text.get_height()) // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()