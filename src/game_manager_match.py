"""Game manager for the Brawl Stars match-the-card game mode."""
import math
import os
import random
import time
from typing import Dict, List, Optional, Tuple

import pygame

from src.card import Card


class MatchGameManager:
    """Manages the match-the-card game logic and state.
    
    This class handles the game where the player must match cards chosen by the computer.
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
        self.cards: List[Card] = []  # Cards on the board
        self.current_card: Optional[Card] = None  # Card to match
        self.previous_card_name: Optional[str] = None  # Track previous card name to avoid duplicates
        self.score = 0
        self.total_rounds = 0
        self.start_time = time.time()
        self.game_over = False
        
        # Game phase tracking
        self.phase = "preview"  # phases: preview, playing, showing_result, game_over
        self.phase_time = time.time()
        self.preview_duration = 5.0  # seconds to show all cards
        self.result_duration = 1.5  # seconds to show match result
        self.is_correct_match = False
        
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
        
        # Extract just the character names
        characters = list(character_images.keys())
        
        # Shuffle the characters to randomize their positions on the board
        # This ensures a different layout each time the game starts
        random.shuffle(characters)
        
        # Select only the number of characters based on difficulty setting
        # Limited to the minimum of available characters or requested count
        characters = characters[:min(self.character_count, len(characters))]
        
        # Calculate grid dimensions for card layout - just one of each character on the board
        grid_width = 5  # 5 cards across to better fit all characters
        grid_height = math.ceil(len(characters) / grid_width)
        
        # Calculate starting position for centering the grid
        start_x = (self.screen_size[0] - ((self.card_size[0] + self.padding) * grid_width - self.padding)) // 2
        
        # Move cards further down to avoid overlap with the target card
        # The target card needs about 300px of vertical space (card height + text + padding)
        start_y = (self.screen_size[1] - ((self.card_size[1] + self.padding) * grid_height - self.padding)) // 2 + 150
        
        # Create the cards for the board
        self.cards = []
        for i, char in enumerate(characters):
            # Calculate position
            row = i // grid_width
            col = i % grid_width
            
            pos_x = start_x + col * (self.card_size[0] + self.padding)
            pos_y = start_y + row * (self.card_size[1] + self.padding)
            
            # Use the specific image for this character
            image_path = character_images[char]
            back_image_path = os.path.join(base_dir, "assets", "images", "card_back.png")
            
            card = Card(
                name=char,
                image_path=image_path,
                back_image_path=back_image_path,
                position=(pos_x, pos_y),
                size=self.card_size
            )
            
            self.cards.append(card)
        
        # Set all cards face up initially for preview phase
        for card in self.cards:
            card.flipped = True
    
    def _choose_target_card(self) -> None:
        """Choose a card for the player to match.
        
        This creates a copy of a random card to display as the target match.
        Ensures we don't select the same card twice in a row.
        """
        if not self.cards:
            return
        
        # Get all available cards
        available_cards = self.cards.copy()
        
        # If we have a previous card and there are multiple options,
        # filter out the previously shown card to avoid repeats
        if self.previous_card_name and len(available_cards) > 1:
            available_cards = [card for card in available_cards if card.name != self.previous_card_name]
        
        # Choose a random card from the available options
        source_card = random.choice(available_cards)
        
        # Remember this card name to avoid consecutive duplicates
        self.previous_card_name = source_card.name
        
        # Create a copy of this card to display at the top
        pos_x = (self.screen_size[0] - self.card_size[0]) // 2
        pos_y = 120  # Top part of the screen, with enough space for text above
        
        self.current_card = Card(
            name=source_card.name,
            image_path=source_card.image_path,
            back_image_path=source_card.back_image_path,
            position=(pos_x, pos_y),
            size=self.card_size
        )
        self.current_card.flipped = True
    
    def handle_click(self, position: Tuple[int, int]) -> None:
        """Handle a mouse click on the game board.
        
        Args:
            position: The (x, y) coordinates of the click.
        """
        # Only process clicks during the playing phase
        if self.phase != "playing" or self.game_over:
            return
        
        for card in self.cards:
            if card.contains_point(position) and not card.flipped:
                card.flip()
                self.total_rounds += 1
                
                # Check if it's a match with the current target card
                if self.current_card and card.name == self.current_card.name:
                    # Correct match
                    self.score += 1
                    self.is_correct_match = True
                else:
                    # Incorrect match
                    self.is_correct_match = False
                
                # Move to the result phase
                self.phase = "showing_result"
                self.phase_time = time.time()
                break
    
    def update(self) -> None:
        """Update game state for the current frame."""
        current_time = time.time()
        
        if self.phase == "preview":
            # Show all cards for preview duration
            if current_time - self.phase_time >= self.preview_duration:
                # Preview time is over, flip all cards face down
                for card in self.cards:
                    card.flipped = False
                
                # Choose the first card to match
                self._choose_target_card()
                
                # Move to playing phase
                self.phase = "playing"
        
        elif self.phase == "showing_result":
            # Show the result (correct/incorrect) for a short time
            if current_time - self.phase_time >= self.result_duration:
                # Flip ALL cards back face down - regardless of correct or incorrect match
                for card in self.cards:
                    card.flipped = False
                
                # Prepare for the next matching card - always remove the current card
                self.current_card = None
            
                # Move back to playing phase
                self.phase = "playing"
            
                # Choose the next card to match - but only if the game isn't over
                if not self.game_over:
                    self._choose_target_card()
        
        # Check for game over condition
        if self.total_rounds >= 10 and self.phase != "game_over":  # Play 10 rounds
            self.game_over = True
            self.phase = "game_over"  # Set explicit game over phase
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the current game state.
        
        Args:
            screen: The Pygame surface to draw on.
        """
        # Get current time at the beginning to ensure it's always defined
        current_time = time.time()
        # Draw all board cards
        for card in self.cards:
            card.draw(screen)
        
        # Draw the current card to match (if in playing or result phase)
        if self.current_card and (self.phase == "playing" or self.phase == "showing_result"):
            self.current_card.draw(screen)
            
            # Draw a "Match this card" text above the current card
            font = pygame.font.SysFont("Arial", 28, bold=True)
            text = font.render("Find this card!", True, (255, 255, 0))
            text_rect = text.get_rect(center=(self.screen_size[0] // 2, 80))
            screen.blit(text, text_rect)
        
        # Draw preview phase countdown
        if self.phase == "preview":
            current_time = time.time()
            remaining_time = max(0, self.preview_duration - (current_time - self.phase_time))
            
            # Draw the message
            font = pygame.font.SysFont("Arial", 32, bold=True)
            text = font.render(f"Memorize the cards! {int(remaining_time)}s", True, (255, 255, 0))
            text_rect = text.get_rect(center=(self.screen_size[0] // 2, 50))
            screen.blit(text, text_rect)
            
            # Add a progress bar
            bar_width = 400
            bar_height = 20
            bar_x = (self.screen_size[0] - bar_width) // 2
            bar_y = 90
            
            # Draw background
            pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(bar_x, bar_y, bar_width, bar_height))
            
            # Draw progress
            progress_width = int(bar_width * (remaining_time / self.preview_duration))
            if progress_width > 0:
                pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(bar_x, bar_y, progress_width, bar_height))
        
        # Draw match result feedback
        if self.phase == "showing_result":
            feedback_text = "CORRECT!" if self.is_correct_match else "WRONG!"
            feedback_color = (0, 255, 0) if self.is_correct_match else (255, 0, 0)
            
            font = pygame.font.SysFont("Arial", 48, bold=True)
            text = font.render(feedback_text, True, feedback_color)
            text_rect = text.get_rect(center=(self.screen_size[0] // 2, self.screen_size[1] // 2))
            
            # Add a semi-transparent background
            bg_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20))
            bg_surface.set_alpha(180)
            bg_surface.fill((0, 0, 0))
            screen.blit(bg_surface, (text_rect.x - 20, text_rect.y - 10))
            
            # Draw the text
            screen.blit(text, text_rect)
        
        # Draw UI elements (score, time, etc.)
        font = pygame.font.SysFont("Arial", 24)
        
        # Calculate elapsed time
        elapsed_time = int(current_time - self.start_time)
        mins, secs = divmod(elapsed_time, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Display score and time
        score_text = font.render(f"Score: {self.score}/{self.total_rounds}", True, (255, 255, 255))
        time_text = font.render(f"Time: {time_str}", True, (255, 255, 255))
        progress_text = font.render(f"Round: {self.total_rounds}/10", True, (255, 255, 255))
        
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 40))
        screen.blit(progress_text, (10, 70))
        
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
            accuracy = int((self.score / max(1, self.total_rounds)) * 100)
            time_stats = stats_font.render(f"Time: {time_str}", True, (255, 255, 255))
            score_stats = stats_font.render(f"Score: {self.score}/{self.total_rounds}", True, (255, 255, 255))
            accuracy_stats = stats_font.render(f"Accuracy: {accuracy}%", True, (255, 255, 255))
            
            screen.blit(time_stats, (text_x, text_y + 60))
            screen.blit(score_stats, (text_x, text_y + 100))
            screen.blit(accuracy_stats, (text_x, text_y + 140))
            
            # Display restart instruction
            restart_font = pygame.font.SysFont("Arial", 24)
            restart_text = restart_font.render("Press 'R' to play again", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.screen_size[0] // 2, text_y + 200))
            screen.blit(restart_text, restart_rect)
            
            # Display return to menu instruction
            menu_text = restart_font.render("Press 'M' to return to menu", True, (255, 255, 255))
            menu_rect = menu_text.get_rect(center=(self.screen_size[0] // 2, text_y + 230))
            screen.blit(menu_text, menu_rect)
    
    def reset(self) -> None:
        """Reset the game to initial state."""
        self.score = 0
        self.total_rounds = 0
        self.start_time = time.time()
        self.game_over = False
        self.previous_card_name = None
        
        # Reset phase
        self.phase = "preview"
        self.phase_time = time.time()
        
        # Reset cards with a fresh shuffle
        self._setup_cards()
