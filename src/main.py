"""Main module for the Brawl Stars themed memory card game."""
import os
import sys
from typing import List, Tuple

import pygame

from src.game_manager import GameManager


class BrawlStarsMemoryGame:
    """Main game class for the Brawl Stars memory card game.
    
    This class handles the game initialization, main loop, and event handling.
    """
    
    def __init__(
        self, 
        screen_size: Tuple[int, int] = (1024, 768),
        title: str = "Brawl Stars Memory Game"
    ) -> None:
        """Initialize the game.
        
        Args:
            screen_size: The (width, height) of the game window.
            title: The title of the game window.
        """
        pygame.init()
        pygame.display.set_caption(title)
        
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.running = False
        self.game_phase = "difficulty_select"
        self.character_count = 5  # Default character count
        
        # Check if assets exist, otherwise create placeholders
        self._ensure_assets_exist()
        
        # Create difficulty selector
        from src.difficulty_selector import DifficultySelector
        self.difficulty_selector = DifficultySelector(
            self.screen,
            min_characters=5,
            max_characters=10,
            on_select=self._start_game_with_character_count,
            on_back=self._exit_to_menu
        )
        
        # Game manager will be created after selecting difficulty
        self.game_manager = None
    
    def _ensure_assets_exist(self) -> None:
        """Ensure necessary asset files exist, creating placeholders if needed."""
        # Ensure directories exist
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images")
        os.makedirs(assets_dir, exist_ok=True)
        
        print(f"Creating placeholder images in: {assets_dir}")
        
        # Create card back if it doesn't exist
        card_back_path = os.path.join(assets_dir, "card_back.png")
        if not os.path.exists(card_back_path):
            self._create_placeholder_image(card_back_path, (80, 120), (50, 50, 200), "BRAWL")
            print(f"Created card back: {card_back_path}")
        
        # Create character cards if they don't exist
        characters = [
            "Shelly", "Colt", "Bull", "Jessie", "Brock", "Dynamike", 
            "Bo", "Tick", "El Primo", "Barley", "Poco", "Rosa"
        ]
        
        for char in characters:
            char_filename = f"{char.lower().replace(' ', '_')}.png"
            char_path = os.path.join(assets_dir, char_filename)
            if not os.path.exists(char_path):
                # Create a unique color for each character
                color = (
                    (hash(char) % 200) + 55,  # R: 55-255
                    ((hash(char) * 2) % 200) + 55,  # G: 55-255
                    ((hash(char) * 3) % 200) + 55,  # B: 55-255
                )
                self._create_placeholder_image(char_path, (80, 120), color, char[:5])
                print(f"Created character image: {char_path}")
    
    def _create_placeholder_image(
        self, 
        path: str, 
        size: Tuple[int, int], 
        color: Tuple[int, int, int], 
        text: str
    ) -> None:
        """Create a placeholder image with text.
        
        Args:
            path: The file path to save the image.
            size: The (width, height) of the image.
            color: The RGB background color.
            text: The text to display on the image.
        """
        # Create a surface
        surface = pygame.Surface(size)
        surface.fill(color)
        
        # Add text
        font = pygame.font.SysFont("Arial", 18)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(size[0]//2, size[1]//2))
        surface.blit(text_surface, text_rect)
        
        # Add border
        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(0, 0, size[0], size[1]), 2)
        
        # Save to file
        pygame.image.save(surface, path)
    
    def _start_game_with_character_count(self, character_count: int) -> None:
        """Start the game with the selected number of characters.
        
        Args:
            character_count: Number of different characters to use in the game.
        """
        self.character_count = character_count
        self.game_phase = "playing"
        
        # Create game manager with the selected character count
        self.game_manager = GameManager(self.screen_size, character_count=self.character_count)
    
    def _exit_to_menu(self) -> None:
        """Exit to the main menu."""
        self.running = False
        
    def run(self) -> None:
        """Run the main game loop."""
        self.running = True
        while self.running:
            events = pygame.event.get()
            
            if self.game_phase == "difficulty_select":
                self._handle_difficulty_selection(events)
            else:  # playing phase
                self._handle_game_events(events)
                self._update()
            
            self._draw()
            self.clock.tick(60)  # 60 FPS
    
    def _handle_difficulty_selection(self, events: List[pygame.event.Event]) -> None:
        """Handle events for the difficulty selection screen.
        
        Args:
            events: List of pygame events to handle.
        """
        # Process quit events
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        
        # Let the difficulty selector handle its own events
        self.difficulty_selector.handle_events(events)
    
    def _handle_game_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events for the game play screen.
        
        Args:
            events: List of pygame events to handle.
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to difficulty selection
                    self.game_phase = "difficulty_select"
                elif event.key == pygame.K_r and self.game_manager and self.game_manager.game_over:
                    # Reset game if it's over
                    self.game_manager.reset()
                elif event.key == pygame.K_m and self.game_manager and self.game_manager.game_over:
                    # Return to difficulty selection when game is over
                    self.game_phase = "difficulty_select"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.game_manager:  # Left mouse button
                    self.game_manager.handle_click(event.pos)
    
    def _update(self) -> None:
        """Update game state."""
        self.game_manager.update()
    
    def _draw(self) -> None:
        """Draw the current frame."""
        # Clear the screen
        self.screen.fill((0, 128, 0))  # Dark green background
        
        # Draw the appropriate interface based on game phase
        if self.game_phase == "difficulty_select":
            self.difficulty_selector.draw()
        elif self.game_manager:
            # Draw game elements
            self.game_manager.draw(self.screen)
            
            # Game over message with restart instruction
            if self.game_manager.game_over:
                font = pygame.font.SysFont("Arial", 24)
                restart_text = font.render("Press 'R' to play again", True, (255, 255, 255))
                menu_text = font.render("Press 'M' to return to difficulty selection", True, (255, 255, 255))
                
                text_x = (self.screen_size[0] - restart_text.get_width()) // 2
                text_y = (self.screen_size[1] + 200) // 2
                self.screen.blit(restart_text, (text_x, text_y))
                
                menu_x = (self.screen_size[0] - menu_text.get_width()) // 2
                menu_y = text_y + 40
                self.screen.blit(menu_text, (menu_x, menu_y))
        
        # Update the display
        pygame.display.flip()
    
    def quit(self) -> None:
        """Clean up and quit the game."""
        pygame.quit()


def main() -> None:
    """Main entry point for the game."""
    game = BrawlStarsMemoryGame()
    print("Game initialized. Starting main loop...")
    try:
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
    finally:
        game.quit()


if __name__ == "__main__":
    main()
