"""Menu system for the Brawl Stars games."""
import pygame
from typing import Tuple, Callable, Dict, List, Optional


class Button:
    """Interactive button for the game menu.
    
    Attributes:
        rect: The button's rectangle bounds.
        text: Text displayed on the button.
        action: Function to call when button is clicked.
        color: Button background color.
        hover_color: Button color when mouse is hovering.
        text_color: Color of the button text.
        font: Font used for the button text.
    """
    
    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        action: Callable[[], None],
        color: Tuple[int, int, int] = (70, 80, 200),
        hover_color: Tuple[int, int, int] = (100, 120, 255),
        text_color: Tuple[int, int, int] = (255, 255, 255),
        font_size: int = 24
    ) -> None:
        """Initialize the button.
        
        Args:
            rect: The button's rectangle bounds.
            text: Text displayed on the button.
            action: Function to call when button is clicked.
            color: Button background color.
            hover_color: Button color when mouse is hovering.
            text_color: Color of the button text.
            font_size: Size of the font for button text.
        """
        self.rect = rect
        self.text = text
        self.action = action
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.is_hovered = False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button on the screen.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Draw button background (use hover color if hovered)
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        
        # Draw button border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos: Tuple[int, int]) -> bool:
        """Check if mouse position is hovering over the button.
        
        Args:
            pos: The (x, y) mouse position.
            
        Returns:
            True if mouse is hovering over button.
        """
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for the button.
        
        Args:
            event: The pygame event to handle.
            
        Returns:
            True if button was clicked.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left mouse button
                self.action()
                return True
        return False


class Menu:
    """Game selection menu.
    
    Attributes:
        screen_size: The size of the game window.
        background_color: Color of the menu background.
        title: Title text for the menu.
        buttons: List of interactive buttons.
    """
    
    def __init__(
        self,
        screen_size: Tuple[int, int],
        title: str = "Brawl Stars Games",
        background_color: Tuple[int, int, int] = (30, 30, 70)
    ) -> None:
        """Initialize the menu.
        
        Args:
            screen_size: The size of the game window.
            title: Title text for the menu.
            background_color: Color of the menu background.
        """
        self.screen_size = screen_size
        self.background_color = background_color
        self.title = title
        self.buttons: List[Button] = []
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("Arial", 24)
    
    def add_button(self, button: Button) -> None:
        """Add a button to the menu.
        
        Args:
            button: The button to add.
        """
        self.buttons.append(button)
    
    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events for the menu.
        
        Args:
            events: List of pygame events to handle.
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        for button in self.buttons:
            button.check_hover(mouse_pos)
        
        # Handle button clicks
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu on the screen.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Draw background
        screen.fill(self.background_color)
        
        # Draw title
        title_surface = self.title_font.render(self.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_size[0] // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Draw subtitle
        subtitle_surface = self.subtitle_font.render("Select a Game Mode", True, (220, 220, 220))
        subtitle_rect = subtitle_surface.get_rect(center=(self.screen_size[0] // 2, 150))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
        
        # Draw Brawl Stars decoration
        self._draw_decorations(screen)
    
    def _draw_decorations(self, screen: pygame.Surface) -> None:
        """Draw decorative elements on the menu.
        
        Args:
            screen: The pygame surface to draw on.
        """
        # Draw stars in the background
        for i in range(20):
            x = (i * 50 + (i % 3) * 20) % self.screen_size[0]
            y = (i * 40 + (i % 5) * 30) % self.screen_size[1]
            
            # Star size varies
            size = 3 + (i % 4) * 2
            
            # Star color varies
            colors = [(255, 255, 0), (255, 200, 0), (200, 255, 0)]
            color = colors[i % len(colors)]
            
            pygame.draw.circle(screen, color, (x, y), size)
        
        # Draw a decorative frame around the menu
        border_rect = pygame.Rect(50, 50, self.screen_size[0] - 100, self.screen_size[1] - 100)
        pygame.draw.rect(screen, (100, 100, 180), border_rect, 3)
        
        # Draw corner accents
        accent_size = 20
        for corner in [(50, 50), (self.screen_size[0] - 50, 50), 
                       (50, self.screen_size[1] - 50), 
                       (self.screen_size[0] - 50, self.screen_size[1] - 50)]:
            pygame.draw.rect(screen, (255, 200, 0), 
                             pygame.Rect(corner[0] - accent_size // 2, 
                                      corner[1] - accent_size // 2,
                                      accent_size, accent_size), 3)
