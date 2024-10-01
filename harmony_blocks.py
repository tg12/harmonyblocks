"""Copyright (C) 2024 James Sawyer
All rights reserved.

DISCLAIMER: This script is provided 'as is' without warranty
of any kind, either express or implied, including, but not
limited to, the implied warranties of merchantability,
fitness for a particular purpose, or non-infringement. In no
event shall the authors or copyright holders be liable for
any claim, damages, or other liability, whether in an action
of contract, tort or otherwise, arising from, out of, or in
connection with the script or the use or other dealings in
the script.
"""

# -*- coding: utf-8 -*-
# pylint: disable=C0116, W0621, W1203, C0103, C0301, W1201, W0511, E0401, E1101, E0606
# C0116: Missing function or method docstring
# W0621: Redefining name %r from outer scope (line %s)
# W1203: Use % formatting in logging functions and pass the % parameters as arguments
# C0103: Constant name "%s" doesn't conform to UPPER_CASE naming style
# C0301: Line too long (%s/%s)
# W1201: Specify string format arguments as logging function parameters
# W0511: TODOs

import pygame
import random
import sys
import logging

# Initialize logging
logging.basicConfig(
    filename='harmony_blocks.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    # Initialize Pygame
    pygame.init()
except Exception as e:
    logging.exception("Pygame initialization failed.")
    sys.exit()

# Constants and Configuration
WIDTH, HEIGHT = 400, 600
SCREEN_SIZE = (WIDTH, HEIGHT)
SCREEN_TITLE = "Harmony Blocks by James Sawyer"
FPS = 60

# Colors (RGB)
# Colors for gradient background
TOP_COLOR = (173, 216, 230)  # Light blue
BOTTOM_COLOR = (144, 238, 144)  # Light green

SHAPE_COLOR = (255, 255, 255)       # White
OUTLINE_COLOR = (240, 255, 255)     # Azure
TEXT_COLOR = (50, 50, 50)           # Dark gray
PROGRESS_BAR_BG_COLOR = (200, 200, 200)
PROGRESS_BAR_FILL_COLOR = (100, 200, 100)

# Fonts
FONT_NAME = "Verdana"
FONT_SMALL_SIZE = 24
FONT_LARGE_SIZE = 48

# Game Mechanics
LEVEL_UP_SCORE = 50      # Points required to level up
SHAPE_SIZE = 50          # Size of the shapes
INITIAL_FALL_SPEED = 2
FALL_SPEED_INCREMENT = 0.5
PLAYER_MOVE_SPEED = 5


class Shape:
    """Class representing the falling shape."""

    def __init__(self, shape_size, fall_speed):
        self.shape_size = shape_size
        # Introduce variability in fall speed
        self.fall_speed = fall_speed + random.uniform(-0.5, 0.5)
        self.x = random.randint(0, WIDTH - self.shape_size)
        self.y = -self.shape_size
        self.rect = pygame.Rect(self.x, self.y, self.shape_size, self.shape_size)

    def fall(self):
        """Move the shape down the screen."""
        self.y += self.fall_speed
        self.rect.y = self.y

    def draw(self, surface):
        """Draw the shape on the given surface."""
        pygame.draw.rect(surface, SHAPE_COLOR, self.rect)


class Outline:
    """Class representing the outline at the bottom of the screen."""

    def __init__(self, shape_size):
        self.shape_size = shape_size
        self.x = random.randint(0, WIDTH - self.shape_size)
        self.y = HEIGHT - self.shape_size - 10
        self.rect = pygame.Rect(self.x, self.y, self.shape_size, self.shape_size)

    def draw(self, surface):
        """Draw the outline on the given surface."""
        pygame.draw.rect(surface, OUTLINE_COLOR, self.rect, 3)


class HarmonyBlocksGame:
    """Class representing the Harmony Blocks game."""

    def __init__(self):
        """Initialize the game."""
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_small = pygame.font.SysFont(FONT_NAME, FONT_SMALL_SIZE)
        self.font_large = pygame.font.SysFont(FONT_NAME, FONT_LARGE_SIZE)

        # Game variables
        self.score = 0
        self.level = 1
        self.running = True
        self.fall_speed = INITIAL_FALL_SPEED
        self.shape_landed = False  # Flag to prevent movement after collision

        # Message handling
        self.message = ''
        self.message_start_time = 0
        self.message_duration = 2000  # Display message for 2000 milliseconds

        # Initialize shape and outline
        self.shape = Shape(SHAPE_SIZE, self.fall_speed)
        self.outline = Outline(SHAPE_SIZE)

    def run(self):
        """Main game loop."""
        logging.info("Game started.")
        try:
            while self.running:
                self.handle_events()
                self.update_game_state()
                self.render()
                self.clock.tick(FPS)
        except Exception as e:
            logging.exception("An error occurred during the game loop.")
        finally:
            pygame.quit()
            logging.info("Game exited.")

    def handle_events(self):
        """Handle user input and events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                logging.info("User requested to quit the game.")

        keys = pygame.key.get_pressed()
        if not self.shape_landed:
            if keys[pygame.K_LEFT] and self.shape.x > 0:
                self.shape.x -= PLAYER_MOVE_SPEED
            if keys[pygame.K_RIGHT] and self.shape.x < WIDTH - SHAPE_SIZE:
                self.shape.x += PLAYER_MOVE_SPEED
            self.shape.rect.x = self.shape.x

    def update_game_state(self):
        """Update the game state."""
        if not self.shape_landed:
            self.shape.fall()

            # Check if the shape has reached the outline's vertical position
            if self.shape.rect.bottom >= self.outline.rect.top:
                x_difference = abs(self.shape.rect.centerx - self.outline.rect.centerx)
                alignment_tolerance = 10  # Allowable pixel difference for alignment

                if x_difference <= alignment_tolerance:
                    # Successful alignment
                    self.shape_landed = True
                    self.score += 10
                    logging.info(f"Score increased to {self.score}. Level: {self.level}")
                    progress_percentage = int(
                        ((self.score % LEVEL_UP_SCORE) / LEVEL_UP_SCORE) * 100
                    )
                    if 50 <= progress_percentage < 60:
                        self.display_message("You're halfway to the next level!")
                    else:
                        self.display_message("Great Job!")
                    self.check_level_up()
                else:
                    # Missed alignment
                    self.shape_landed = True
                    logging.info("Shape missed the outline.")
                    self.display_message("Try Again!")
        else:
            # Wait until the message has been displayed before resetting
            current_time = pygame.time.get_ticks()
            if not self.message or current_time - self.message_start_time >= self.message_duration:
                self.reset_shape_and_outline()

    def check_level_up(self):
        """Increase the level and difficulty if necessary."""
        if self.score % LEVEL_UP_SCORE == 0:
            self.level += 1
            self.fall_speed += FALL_SPEED_INCREMENT
            logging.info(
                f"Level up! New level: {self.level}, Fall speed: {self.fall_speed}"
            )
            self.display_message(f"Level {self.level}!")
            if self.level % 3 == 0:
                self.display_message("Take a deep breath and continue!")

    def reset_shape_and_outline(self):
        """Reset the shape and outline for the next turn."""
        self.shape = Shape(SHAPE_SIZE, self.fall_speed)
        self.outline = Outline(SHAPE_SIZE)
        self.shape_landed = False  # Reset the flag
        self.message = ''  # Clear any messages

    def render(self):
        """Render the game elements on the screen."""
        self.draw_gradient_background()
        self.shape.draw(self.screen)
        self.outline.draw(self.screen)
        self.display_score_and_level()
        self.display_progress_bar()

        # Display message if it's within the duration
        if self.message:
            current_time = pygame.time.get_ticks()
            if current_time - self.message_start_time < self.message_duration:
                text = self.font_small.render(self.message, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
                self.screen.blit(text, text_rect)
            else:
                # Message duration has passed
                self.message = ''

        pygame.display.update()

    def draw_gradient_background(self):
        """Draw a vertical gradient background from light blue to light green."""
        top_color = TOP_COLOR
        bottom_color = BOTTOM_COLOR
        gradient_rect = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            red = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            green = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            blue = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(gradient_rect, (red, green, blue), (0, y), (WIDTH, y))
        self.screen.blit(gradient_rect, (0, 0))

    def display_message(self, message):
        """Set the message to be displayed and record the start time."""
        self.message = message
        self.message_start_time = pygame.time.get_ticks()

    def display_score_and_level(self):
        """Display the current score and level."""
        score_text = self.font_small.render(f"Score: {self.score}", True, TEXT_COLOR)
        level_text = self.font_small.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (WIDTH - 100, 10))

    def display_progress_bar(self):
        """Display a progress bar towards the next level."""
        progress_bar_width = WIDTH - 20
        progress_bar_height = 20
        points_into_level = self.score % LEVEL_UP_SCORE
        progress = points_into_level / LEVEL_UP_SCORE
        fill_width = int(progress_bar_width * progress)

        # Position the progress bar at the top of the screen
        progress_bar_x = 10
        progress_bar_y = 60  # Adjusted to be below the score and level text

        # Background bar
        progress_bar_bg_rect = pygame.Rect(
            progress_bar_x, progress_bar_y, progress_bar_width, progress_bar_height
        )
        pygame.draw.rect(self.screen, PROGRESS_BAR_BG_COLOR, progress_bar_bg_rect)

        # Filled portion
        progress_bar_rect = pygame.Rect(
            progress_bar_x, progress_bar_y, fill_width, progress_bar_height
        )
        pygame.draw.rect(self.screen, PROGRESS_BAR_FILL_COLOR, progress_bar_rect)

        # Border
        pygame.draw.rect(self.screen, TEXT_COLOR, progress_bar_bg_rect, 2)

        # Progress text
        progress_percentage = int(progress * 100)
        progress_text = self.font_small.render(
            f"{progress_percentage}% to Next Level", True, TEXT_COLOR
        )
        text_rect = progress_text.get_rect(
            center=(WIDTH / 2, progress_bar_y + progress_bar_height / 2)
        )
        self.screen.blit(progress_text, text_rect)


if __name__ == "__main__":
    game = HarmonyBlocksGame()
    game.run()
