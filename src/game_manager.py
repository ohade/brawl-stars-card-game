"""Game manager module for the Brawl Stars memory card game."""
import math
import os
import random
import time
from typing import Dict, List, Optional, Tuple

import pygame

from src.card import Card


class GameManager:
    """Manages the memory card game logic and state.
    
    This class handles the game's state, including cards, matching logic,
    scoring, and game progression.
    """
    
    def __init__(
        self, 
        screen_size: Tuple[int, int],
        character_count: int = 5,
        card_size: Tuple[int, int] = (150, 200),
        padding: int = 30
    ) -> None:
        """Initialize the game manager.
        
        Args:
            screen_size: The (width, height) of the game screen.
            card_size: The (width, height) of each card.
            padding: Spacing between cards.
        """
        self.screen_size = screen_size
        self.character_count = character_count
        self.card_size = card_size
        self.padding = padding
        
        # Game state
        self.cards: List[Card] = []
        self.flipped_cards: List[Card] = []
        self.score = 0
        self.attempts = 0
        self.start_time = time.time()
        self.game_over = False
        
        # Timer for non-matching cards
        self.flip_back_time = 0
        self.waiting_to_flip_back = False
        self.flip_delay = 1.5  # Seconds to show non-matching cards
        self.mismatch_time = 0  # Time when mismatch was detected
        self.is_mismatch = False  # Flag to indicate a mismatch
        
        # Load assets and setup
        self._setup_cards()
    
    def _setup_cards(self) -> None:
        """Set up the game cards with Brawl Stars characters."""
        # Map the actual image files to character names
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assets_dir = os.path.join(base_dir, "assets", "images")
        
        # Define character images that we have available
        character_images = {
            "Spacesuit": os.path.join(assets_dir, "Brawl Stars Character in Spacesuit.png"),
            "Colt": os.path.join(assets_dir, "Brawl Stars Colt Action Pose.png"),
            "Leon": os.path.join(assets_dir, "Brawl Stars Leon Render.png"),
            "Nita": os.path.join(assets_dir, "Brawl Stars Nita and Bruce Costumes.png"),
            "Robo": os.path.join(assets_dir, "Brawl Stars Robo Rumble Brawler.png"),
            # New character images
            "Figure1": os.path.join(assets_dir, "ChatGPT Image May 2 2025 (1).png"),
            "Figure2": os.path.join(assets_dir, "ChatGPT Image May 2 2025 (2).png"),
            "Figure3": os.path.join(assets_dir, "ChatGPT Image May 2 2025 (3).png"),
            "Figure4": os.path.join(assets_dir, "ChatGPT Image May 2 2025 (4).png"),
            "Figure5": os.path.join(assets_dir, "ChatGPT Image May 2 2025.png"),
        }
        
        # Extract just the character names for selection
        characters = list(character_images.keys())
        
        # For a memory game, we need pairs
        # Select the requested number of characters based on difficulty
        # First shuffle to randomize which characters are selected
        random.shuffle(characters)
        # Then take only the number requested (minimum of available characters or requested count)
        selected_chars = characters[:min(self.character_count, len(characters))]
        
        # We need two of each character
        pairs = selected_chars + selected_chars
        random.shuffle(pairs)
        
        # Calculate grid dimensions for card layout
        grid_width = 5  # 5 cards across to accommodate more cards
        grid_height = math.ceil(len(pairs) / grid_width)
        
        # Calculate starting position for centering the grid
        start_x = (self.screen_size[0] - ((self.card_size[0] + self.padding) * grid_width - self.padding)) // 2
        start_y = (self.screen_size[1] - ((self.card_size[1] + self.padding) * grid_height - self.padding)) // 2
        
        # Create the cards
        self.cards = []
        for i, char in enumerate(pairs):
            # Calculate position
            row = i // grid_width
            col = i % grid_width
            
            pos_x = start_x + col * (self.card_size[0] + self.padding)
            pos_y = start_y + row * (self.card_size[1] + self.padding)
            
            # Use the specific image for this character
            if char in character_images:
                image_path = character_images[char]
            else:
                # Fallback to placeholder if needed
                image_path = os.path.join(base_dir, "assets", "images", f"{char.lower().replace(' ', '_')}.png")
            
            back_image_path = os.path.join(base_dir, "assets", "images", "card_back.png")
            
            card = Card(
                name=char,
                image_path=image_path,
                back_image_path=back_image_path,
                position=(pos_x, pos_y),
                size=self.card_size
            )
            
            self.cards.append(card)
    
    def handle_click(self, position: Tuple[int, int]) -> None:
        """Handle a mouse click on the game board.
        
        Args:
            position: The (x, y) coordinates of the click.
        """
        if self.game_over or len(self.flipped_cards) >= 2 or self.waiting_to_flip_back:
            return
        
        for card in self.cards:
            if card.contains_point(position) and not card.flipped and not card.matched:
                card.flip()
                self.flipped_cards.append(card)
                
                if len(self.flipped_cards) == 2:
                    # Check for a match
                    self.attempts += 1
                    if self.flipped_cards[0].name == self.flipped_cards[1].name:
                        # Match found
                        self.score += 1
                        for card in self.flipped_cards:
                            card.matched = True
                        self.flipped_cards = []
                        self.is_mismatch = False
                    break  # Only flip one card per click
    
    def update(self) -> None:
        """Update game state for the current frame."""
        current_time = time.time()
        
        # If two cards are flipped but don't match, flip them back after a delay
        if len(self.flipped_cards) == 2 and all(not card.matched for card in self.flipped_cards):
            # If we're waiting for the flip-back timer
            if self.waiting_to_flip_back:
                # Check if enough time has passed
                if current_time >= self.flip_back_time:
                    # Time to flip cards back
                    for card in self.flipped_cards:
                        card.flipped = False
                    self.flipped_cards = []
                    self.waiting_to_flip_back = False
                    self.is_mismatch = False
            else:
                # Start the timer for flipping back
                self.flip_back_time = current_time + self.flip_delay
                self.waiting_to_flip_back = True
                self.mismatch_time = current_time
                self.is_mismatch = True
        
        # Check for game over
        if all(card.matched for card in self.cards):
            self.game_over = True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the current game state.
        
        Args:
            screen: The Pygame surface to draw on.
        """
        # Draw all cards
        for card in self.cards:
            card.draw(screen)
            
        # Draw mismatch indicator if cards don't match
        if self.is_mismatch and self.waiting_to_flip_back:
            # Draw a red flash effect around the mismatched cards
            for card in self.flipped_cards:
                x, y = card.position
                width, height = card.size
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x-3, y-3, width+6, height+6), 3)
            
            # Draw visual countdown bar - kid-friendly timer
            current_time = time.time()
            total_delay = self.flip_delay
            elapsed = current_time - self.mismatch_time
            remaining_ratio = max(0, (total_delay - elapsed) / total_delay)
            
            # Position the timer bar at the top center of the screen
            bar_width = 300
            bar_height = 30
            bar_x = (self.screen_size[0] - bar_width) // 2
            bar_y = 20
            
            # Draw a container for the timer bar
            pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            
            # Calculate the current width of the timer bar based on remaining time
            current_bar_width = int(bar_width * remaining_ratio)
            
            # Draw the timer bar - red bar that gets smaller as time passes
            if current_bar_width > 0:
                pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(bar_x, bar_y, current_bar_width, bar_height))
            
            # Add decorative elements to make it more interesting for kids
            # Draw tick marks on the bar
            for i in range(1, 10):
                tick_x = bar_x + (i * (bar_width // 10))
                pygame.draw.line(screen, (200, 200, 200), (tick_x, bar_y), (tick_x, bar_y + bar_height), 1)
            
            # Add a simple clock icon next to the bar
            clock_center = (bar_x - 25, bar_y + (bar_height // 2))
            clock_radius = 15
            pygame.draw.circle(screen, (250, 250, 150), clock_center, clock_radius)  # Clock face
            pygame.draw.circle(screen, (0, 0, 0), clock_center, clock_radius, 2)  # Clock outline
            
            # Draw clock hands
            # Hour hand (moves with the timer)
            angle = 2 * 3.14159 * (1 - remaining_ratio)
            hour_length = clock_radius * 0.5
            hour_x = clock_center[0] + hour_length * math.sin(angle)
            hour_y = clock_center[1] - hour_length * math.cos(angle)
            pygame.draw.line(screen, (0, 0, 0), clock_center, (hour_x, hour_y), 3)
            
            # Minute hand (moves faster)
            angle = 2 * 3.14159 * (1 - remaining_ratio) * 2
            minute_length = clock_radius * 0.8
            minute_x = clock_center[0] + minute_length * math.sin(angle)
            minute_y = clock_center[1] - minute_length * math.cos(angle)
            pygame.draw.line(screen, (0, 0, 0), clock_center, (minute_x, minute_y), 2)
        
        # Draw UI elements (score, time, etc.)
        font = pygame.font.SysFont("Arial", 24)
        
        # Calculate elapsed time
        elapsed_time = int(time.time() - self.start_time)
        mins, secs = divmod(elapsed_time, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Display score and time
        score_text = font.render(f"Score: {self.score}/{len(self.cards)//2}", True, (255, 255, 255))
        time_text = font.render(f"Time: {time_str}", True, (255, 255, 255))
        attempts_text = font.render(f"Attempts: {self.attempts}", True, (255, 255, 255))
        
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 40))
        screen.blit(attempts_text, (10, 70))
        
        # Display game over message if applicable
        if self.game_over:
            overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.SysFont("Arial", 48)
            game_over_text = game_over_font.render("Game Over!", True, (255, 255, 255))
            
            # Calculate center position
            text_x = (self.screen_size[0] - game_over_text.get_width()) // 2
            text_y = (self.screen_size[1] - game_over_text.get_height()) // 2
            
            screen.blit(game_over_text, (text_x, text_y))
            
            # Display final stats
            stats_font = pygame.font.SysFont("Arial", 32)
            time_stats = stats_font.render(f"Time: {time_str}", True, (255, 255, 255))
            attempts_stats = stats_font.render(f"Attempts: {self.attempts}", True, (255, 255, 255))
            
            screen.blit(time_stats, (text_x, text_y + 60))
            screen.blit(attempts_stats, (text_x, text_y + 100))
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        self.flipped_cards = []
        self.score = 0
        self.attempts = 0
        self.start_time = time.time()
        self.game_over = False
        
        # Re-setup cards with new positions
        self._setup_cards()
