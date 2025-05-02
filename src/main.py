"""Main module for the Brawl Stars themed memory card game."""
import os
import sys
from typing import Tuple

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
        
        # Check if assets exist, otherwise create placeholders
        self._ensure_assets_exist()
        
        # Create game manager after assets are created
        self.game_manager = GameManager(screen_size)
    
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
    
    def run(self) -> None:
        """Run the main game loop."""
        self.running = True
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(60)  # 60 FPS
    
    def _handle_events(self) -> None:
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_manager.game_over:
                    # Reset game if it's over
                    self.game_manager.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.game_manager.handle_click(event.pos)
    
    def _update(self) -> None:
        """Update game state."""
        self.game_manager.update()
    
    def _draw(self) -> None:
        """Draw the current frame."""
        # Clear the screen
        self.screen.fill((0, 128, 0))  # Dark green background
        
        # Draw game elements
        self.game_manager.draw(self.screen)
        
        # Game over message with restart instruction
        if self.game_manager.game_over:
            font = pygame.font.SysFont("Arial", 24)
            restart_text = font.render("Press 'R' to play again", True, (255, 255, 255))
            text_x = (self.screen_size[0] - restart_text.get_width()) // 2
            text_y = (self.screen_size[1] + 200) // 2
            self.screen.blit(restart_text, (text_x, text_y))
        
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
