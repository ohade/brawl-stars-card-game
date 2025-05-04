"""Main portal for the Brawl Stars games."""
import sys
from typing import Tuple, Callable, Dict, List, Optional

import pygame

from src.menu import Menu, Button
from src.main import BrawlStarsMemoryGame
from src.game_manager_match import MatchGameManager


class MatchCardGame:
    """Match Card Game implementation for the second game mode.
    
    This game mode shows all cards face up for a preview period, then asks
    the player to find a specific card chosen by the computer.
    """
    
    def __init__(
        self, 
        screen_size: Tuple[int, int] = (1024, 768),
        title: str = "Brawl Stars Match Card Game"
    ) -> None:
        """Initialize the game.
        
        Args:
            screen_size: The (width, height) of the game window.
            title: The title of the game window.
        """
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(title)
        
        self.clock = pygame.time.Clock()
        self.running = False
        self.game_phase = "difficulty_select"
        self.character_count = 5  # Default character count
        
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
    
    def _start_game_with_character_count(self, character_count: int) -> None:
        """Start the game with the selected number of characters.
        
        Args:
            character_count: Number of different characters to use in the game.
        """
        self.character_count = character_count
        self.game_phase = "playing"
        
        # Create game manager with the selected character count
        self.game_manager = MatchGameManager(self.screen_size, character_count=self.character_count)
    
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
        # Update the game state
        self.game_manager.update()
        
        # Don't automatically exit when game is over
        # Let the player view their score and decide when to exit
    
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


class GamePortal:
    """Main portal for selecting and playing Brawl Stars games."""
    
    def __init__(self, screen_size: Tuple[int, int] = (1024, 768)) -> None:
        """Initialize the game portal.
        
        Args:
            screen_size: The (width, height) of the game window.
        """
        pygame.init()
        pygame.display.set_caption("Brawl Stars Games Portal")
        
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create menu
        self.menu = Menu(screen_size, "Brawl Stars Games")
        
        # Add buttons for the different game modes
        button_width, button_height = 300, 80
        button_x = (screen_size[0] - button_width) // 2
        
        # Memory Game Button
        memory_button = Button(
            pygame.Rect(button_x, 250, button_width, button_height),
            "Memory Card Game",
            self.start_memory_game,
            color=(70, 80, 200),
            hover_color=(100, 120, 255)
        )
        self.menu.add_button(memory_button)
        
        # Match Game Button
        match_button = Button(
            pygame.Rect(button_x, 350, button_width, button_height),
            "Match Card Challenge",
            self.start_match_game,
            color=(200, 70, 70),
            hover_color=(255, 100, 100)
        )
        self.menu.add_button(match_button)
        
        # Exit Button
        exit_button = Button(
            pygame.Rect(button_x, 450, button_width, button_height),
            "Exit",
            self.exit_game,
            color=(70, 70, 70),
            hover_color=(100, 100, 100)
        )
        self.menu.add_button(exit_button)
        
        # Add game descriptions
        self.descriptions = [
            {
                "title": "Memory Card Game",
                "text": "Classic memory game! Find matching pairs of Brawl Stars characters.",
                "position": (screen_size[0] // 2, 600)
            },
            {
                "title": "Match Card Challenge",
                "text": "Can you remember where the cards are? Find the card that matches the one shown!",
                "position": (screen_size[0] // 2, 630)
            }
        ]
    
    def start_memory_game(self) -> None:
        """Start the classic memory card game."""
        game = BrawlStarsMemoryGame()
        try:
            game.run()
        except Exception as e:
            print(f"Error running memory game: {e}")
        finally:
            # Ensure the menu is still displayed after returning
            pygame.display.set_mode(self.screen_size)
            pygame.display.set_caption("Brawl Stars Games Portal")
    
    def start_match_game(self) -> None:
        """Start the match card challenge game."""
        game = MatchCardGame()
        try:
            game.run()
        except Exception as e:
            print(f"Error running match game: {e}")
        finally:
            # Ensure the menu is still displayed after returning
            pygame.display.set_mode(self.screen_size)
            pygame.display.set_caption("Brawl Stars Games Portal")
    
    def exit_game(self) -> None:
        """Exit the portal and quit the game."""
        self.running = False
    
    def run(self) -> None:
        """Run the main portal loop."""
        while self.running:
            events = pygame.event.get()
            
            # Handle quit events
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Handle menu events
            self.menu.handle_events(events)
            
            # Draw menu
            self.menu.draw(self.screen)
            
            # Draw game descriptions
            self._draw_descriptions()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
    
    def _draw_descriptions(self) -> None:
        """Draw game descriptions on the menu screen."""
        font = pygame.font.SysFont("Arial", 18)
        
        for desc in self.descriptions:
            # Draw the description text
            text_surface = font.render(desc["text"], True, (200, 200, 200))
            text_rect = text_surface.get_rect(center=desc["position"])
            self.screen.blit(text_surface, text_rect)
    
    def quit(self) -> None:
        """Clean up and quit."""
        pygame.quit()


def main() -> None:
    """Main entry point for the Brawl Stars Games Portal."""
    portal = GamePortal()
    try:
        portal.run()
    except Exception as e:
        print(f"Error running portal: {e}")
    finally:
        portal.quit()


if __name__ == "__main__":
    main()
