import sys
import pygame
import random
import json

pygame.init()

# Game Setup
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumping Game")

# Background music
music = pygame.mixer.music.load('song1.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# sound effects
fu_sound = pygame.mixer.Sound('f_u.mp3')
fu_sound.set_volume(1)

# Game Constants
is_paused = False
run = True
clock = pygame.time.Clock()

# Score saving
def save_high_score(score):
    with open('data.json', 'w') as f:
        json.dump({'high_score': score}, f)

def load_high_score():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)['high_score']
    except:
        return 0

# Player Configuration
normal_width = 40
normal_height = 40
duck_width = 40  # Width when ducking
duck_height = 10  # Height when ducking
is_left_width = 10
is_left_height = 40
is_right_width = 10
is_right_height = 40
player_size = (normal_width, normal_height)  # Default player size
player_x = 50
player_y = SCREEN_HEIGHT - normal_height  # Ground level
player_color = (255, 255, 255)  # White
player_velocity = 0
jump_force = -15
gravity = 1
is_ducking = False  # State to track ducking
is_left = False  # State to track left movement
is_right = False  # State to track right movement

# Ground Configuration
ground_height = 20
ground_y = SCREEN_HEIGHT - ground_height
ground_color = (0, 0, 255)  # Blue

# Obstacle Configuration
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 65
OBSTACLE_SPEED = 9
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
animation_speed = 1.5
animation_trigger_distance = 250  # Distance to trigger "Duck Under" animation
animation_target_y = ground_y - 120  # Final height for duck under

# Reset Function
def reset_game():
    global player_x, player_y, player_velocity, player_size, is_ducking, obstacles, is_left, is_right
    # Reset player position
    player_x = 50
    player_y = SCREEN_HEIGHT - normal_height  # Ground level
    player_velocity = 0
    player_size = (normal_width, normal_height)  # Default size
    is_ducking = False  # Reset ducking state
    is_left = False  # Reset left state
    is_right = False  # Reset right state

    # Reset obstacles
    obstacles = []
    obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER])
    obstacle_color = DEFAULT_OBSTACLE_COLOR
    if obstacle_type == DUCK_UNDER:
        obstacle_color = DEFAULT_OBSTACLE_COLOR
    new_obstacle = {
        "x": random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300),
        "type": obstacle_type,
        "y": set_obstacle_position(obstacle_type),  # Use defined function
        "color": obstacle_color,
        "is_moving": False
    }
    obstacles.append(new_obstacle)

# Initialize Game
reset_game()  # Initialize game variables

# Load the overlay image
overlay_image = pygame.image.load('rührei.png')

# Scale the image to match the screen size
overlay_image = pygame.transform.scale(overlay_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font Configuration
font = pygame.font.Font(None, 36)  # Choose font and size

# Score Var
score = 0
high_score = load_high_score()

# Flag to track whether the overlay should be shown
show_overlay = False

# Game states
MAIN_MENU = 0
PLAYING = 1
PAUSED = 2
QUIT = 3

game_state = MAIN_MENU

start_button_rect = pygame.Rect(350, 200, 300, 50)
quit_button_rect = pygame.Rect(350, 270, 300, 50)

# Main Game Loop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_paused:
                # Jump logic
                if not is_ducking and player_y >= ground_y - normal_height:
                    player_velocity = jump_force
            elif event.key == pygame.K_s and not is_paused:
                # Duck logic
                if player_y == ground_y - normal_height:
                    is_ducking = True
                    player_size = (duck_width, duck_height)
                    player_y = ground_y - duck_height
            elif event.key == pygame.K_a and not is_paused:
                if player_y == ground_y - normal_height:
                    is_left = True
                    player_size = (is_left_width, is_left_height)
                    player_y = ground_y - is_left_height
            elif event.key == pygame.K_d and not is_paused:
                if player_y == ground_y - normal_height:
                    is_right = True
                    player_x += 30
                    player_size = (is_right_width, is_right_height)
                    player_y = ground_y - is_right_height
            elif event.key == pygame.K_m:
                # Toggle the flag to show/hide the overlay
                show_overlay = not show_overlay
                # Play the "fu_sound" sound effect
                pygame.mixer.Sound.play(fu_sound)
            elif event.key == pygame.K_ESCAPE:
                # Toggle the paused state
                is_paused = not is_paused

        elif event.type == pygame.KEYUP:
            # Handle key releases for stopping actions
            if event.key == pygame.K_s and is_ducking:
                is_ducking = False
                player_size = (normal_width, normal_height)
                player_y = ground_y - normal_height
            elif event.key == pygame.K_a and is_left:
                is_left = False
                player_size = (normal_width, normal_height)
                player_y = ground_y - normal_height
            elif event.key == pygame.K_d and is_right:
                is_right = False
                player_x -= 30
                player_size = (normal_width, normal_height)
                player_y = ground_y - normal_height

    # Update the paused text if the game is paused
    if is_paused:
        paused_text = font.render("Paused", True, (255, 0, 0))


    if not is_paused:
        # Updtade score
        score += 1

        # Gravity and player movement
        player_velocity += gravity
        player_y += player_velocity
        if player_y > ground_y - player_size[1]:  # Ground contact check
            player_y = ground_y - player_size[1]
            player_velocity = 0  # Reset velocity when touching the ground

        # Obstacle movement and collision check
        for obstacle in obstacles:
            obstacle["x"] -= OBSTACLE_SPEED  # Move to the left
            
            # Proximity check for "Duck Under"
            if obstacle["type"] == DUCK_UNDER and obstacle["x"] - player_x <= animation_trigger_distance:
                obstacle["is_moving"] = True  # Trigger animation for duck under
                obstacle["color"] = TRIGGERED_OBSTACLE_COLOR

            # Move obstacle up gradually if animation is triggered
            if obstacle["is_moving"] and obstacle["y"] > ground_y - animation_target_y:
                obstacle["y"] -= animation_speed

            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

            if player_rect.colliderect(obstacle_rect):  # Collision check
                if obstacle["type"] == JUMP_OVER:
                    if  score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    score = 0
                    reset_game()  # Reset the game upon collision
                elif obstacle["type"] == DUCK_UNDER:
                    if not is_ducking:  # Check if the player is not ducking
                        if  score > high_score:
                            high_score = score
                            save_high_score(high_score)
                        score = 0
                        reset_game()  # Reset the game upon collision
                break

        # Remove off-screen obstacles and add new ones
        if obstacles and obstacles[0]["x"] < -OBSTACLE_WIDTH:
            obstacles.pop(0)  # Remove off-screen obstacles
            # Create a new obstacle
            obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER])
            obstacle_color = DEFAULT_OBSTACLE_COLOR
            if obstacle_type == DUCK_UNDER:
                obstacle_color = DEFAULT_OBSTACLE_COLOR
            new_obstacle = {
                "x": random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 300),
                "type": obstacle_type,
                "y": set_obstacle_position(obstacle_type),  # Use defined function
                "color": obstacle_color,
                "is_moving": False
            }
            obstacles.append(new_obstacle)

    # Drawing
    screen.fill((0, 0, 0))  # Clear the screen with black
    pygame.draw.rect(screen, ground_color, (0, ground_y, SCREEN_WIDTH, SCREEN_WIDTH))

    # Draw the player
    pygame.draw.rect(screen, player_color, (player_x, player_y, player_size[0], player_size[1]))

    # Draw obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, obstacle["color"], (obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

    # Draw the overlay if the flag is active
    if show_overlay:
        screen.blit(overlay_image, (0, 0))

    # Draw score
    score_text = font.render(f"Score: {score}", True, (255, 230, 0))
    screen.blit(score_text, (10, 10))

    # Draw highscore
    high_score_text = font.render(f"Highscore: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (10, 40))

    # Draw the paused text if the game is paused
    if is_paused:
        screen.blit(paused_text, ((SCREEN_WIDTH - paused_text.get_width()) // 2, (SCREEN_HEIGHT - paused_text.get_height()) // 2))

    # Update the display and maintain the frame rate
    pygame.display.flip()       
    clock.tick(60)  # Maintain frame rate

pygame.quit()
sys.exit()