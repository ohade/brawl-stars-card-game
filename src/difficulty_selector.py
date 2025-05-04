"""Difficulty selector module for Brawl Stars games."""
import pygame
from typing import Tuple, List, Optional, Callable

from src.menu import Button


class DifficultySelector:
    """Screen for selecting the number of characters to use in a game.
    
    Allows players to customize their gameplay experience by selecting
    how many different characters will appear in the game.
    """
    
    def __init__(
        self, 
        screen: pygame.Surface,
        min_characters: int = 5,
        max_characters: int = 10,
        on_select: Callable[[int], None] = None,
        on_back: Callable[[], None] = None
    ) -> None:
        """Initialize the difficulty selector.
        
        Args:
            screen: The pygame surface to draw on.
            min_characters: Minimum number of characters that can be selected.
            max_characters: Maximum number of characters that can be selected.
            on_select: Callback function when difficulty is selected.
            on_back: Callback function when back button is pressed.
        """
        self.screen = screen
        self.screen_size = screen.get_size()
        self.min_characters = min_characters
        self.max_characters = max_characters
        self.on_select = on_select
        self.on_back = on_back
        
        self.selected_count = min_characters
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 32)
        self.text_font = pygame.font.SysFont("Arial", 24)
        
        # Create buttons
        self.create_buttons()
    
    def create_buttons(self) -> None:
        """Create the selector buttons."""
        button_width, button_height = 50, 50
        middle_x = self.screen_size[0] // 2
        
        # Create decrement button (-)
        self.decrement_button = Button(
            pygame.Rect(middle_x - 100, 300, button_width, button_height),
            "-",
            self.decrement_count,
            color=(200, 50, 50),
            hover_color=(255, 100, 100),
            font_size=36
        )
        
        # Create increment button (+)
        self.increment_button = Button(
            pygame.Rect(middle_x + 50, 300, button_width, button_height),
            "+",
            self.increment_count,
            color=(50, 200, 50),
            hover_color=(100, 255, 100),
            font_size=36
        )
        
        # Create confirm button
        confirm_width, confirm_height = 200, 60
        self.confirm_button = Button(
            pygame.Rect(middle_x - confirm_width // 2, 400, confirm_width, confirm_height),
            "Start Game",
            self.confirm_selection,
            color=(70, 120, 200),
            hover_color=(100, 150, 255),
            font_size=28
        )
        
        # Create back button
        back_width, back_height = 150, 50
        self.back_button = Button(
            pygame.Rect(middle_x - back_width // 2, 500, back_width, back_height),
            "Back",
            self.go_back,
            color=(100, 100, 100),
            hover_color=(150, 150, 150),
            font_size=24
        )
    
    def decrement_count(self) -> None:
        """Decrease the character count if above minimum."""
        if self.selected_count > self.min_characters:
            self.selected_count -= 1
    
    def increment_count(self) -> None:
        """Increase the character count if below maximum."""
        if self.selected_count < self.max_characters:
            self.selected_count += 1
    
    def confirm_selection(self) -> None:
        """Confirm the selected character count."""
        if self.on_select:
            self.on_select(self.selected_count)
    
    def go_back(self) -> None:
        """Return to the previous screen."""
        if self.on_back:
            self.on_back()
    
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events for the difficulty selector.
        
        Args:
            events: List of pygame events to handle.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        self.decrement_button.check_hover(mouse_pos)
        self.increment_button.check_hover(mouse_pos)
        self.confirm_button.check_hover(mouse_pos)
        self.back_button.check_hover(mouse_pos)
        
        # Handle button clicks
        for event in events:
            self.decrement_button.handle_event(event)
            self.increment_button.handle_event(event)
            self.confirm_button.handle_event(event)
            self.back_button.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
                elif event.key == pygame.K_RETURN:
                    self.confirm_selection()
                elif event.key == pygame.K_LEFT:
                    self.decrement_count()
                elif event.key == pygame.K_RIGHT:
                    self.increment_count()
    
    def draw(self) -> None:
        """Draw the difficulty selector interface."""
        # Draw background
        self.screen.fill((30, 30, 70))
        
        # Draw title
        title_surface = self.title_font.render("Game Difficulty", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_size[0] // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw instructions
        subtitle_surface = self.subtitle_font.render("Select number of characters:", True, (220, 220, 220))
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_size[0] // 2, 180))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw count display
        count_surface = self.title_font.render(str(self.selected_count), True, (255, 255, 100))
        count_rect = count_surface.get_rect(center=(self.screen_size[0] // 2, 300))
        self.screen.blit(count_surface, count_rect)
        
        # Draw difficulty label
        label = "Easy" if self.selected_count <= 6 else "Medium" if self.selected_count <= 8 else "Hard"
        label_color = (100, 255, 100) if self.selected_count <= 6 else (255, 255, 100) if self.selected_count <= 8 else (255, 100, 100)
        label_surface = self.subtitle_font.render(label, True, label_color)
        label_rect = label_surface.get_rect(center=(self.screen_size[0] // 2, 240))
        self.screen.blit(label_surface, label_rect)
        
        # Draw explanation
        if self.selected_count <= 6:
            desc = "Fewer characters make the game easier to remember"
        elif self.selected_count <= 8:
            desc = "A balanced challenge for most players"
        else:
            desc = "More characters create a greater memory challenge"
        
        desc_surface = self.text_font.render(desc, True, (200, 200, 200))
        desc_rect = desc_surface.get_rect(center=(self.screen_size[0] // 2, 340))
        self.screen.blit(desc_surface, desc_rect)
        
        # Draw buttons
        self.decrement_button.draw(self.screen)
        self.increment_button.draw(self.screen)
        self.confirm_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        # Draw decorative elements
        self._draw_decorations()
    
    def _draw_decorations(self) -> None:
        """Draw decorative elements on the selector screen."""
        # Draw side bars representing difficulty
        bar_height = 30 * self.selected_count
        bar_width = 20
        bar_x = self.screen_size[0] // 4
        bar_y = (self.screen_size[1] - bar_height) // 2
        
        # Left bar
        pygame.draw.rect(self.screen, (50, 100, 200), pygame.Rect(bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (200, 200, 200), pygame.Rect(bar_x, bar_y, bar_width, bar_height), 2)
        
        # Right bar (mirror of left)
        pygame.draw.rect(self.screen, (50, 100, 200), 
                         pygame.Rect(self.screen_size[0] - bar_x - bar_width, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (200, 200, 200), 
                         pygame.Rect(self.screen_size[0] - bar_x - bar_width, bar_y, bar_width, bar_height), 2)
        
        # Draw card icons representing number of characters
        card_size = (30, 40)
        card_spacing = 35
        total_width = self.selected_count * card_spacing
        start_x = (self.screen_size[0] - total_width) // 2
        
        for i in range(self.selected_count):
            x = start_x + i * card_spacing
            y = self.screen_size[1] - 100
            
            # Card background
            pygame.draw.rect(self.screen, (50, 50, 200), pygame.Rect(x, y, card_size[0], card_size[1]))
            
            # Card border
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(x, y, card_size[0], card_size[1]), 1)
