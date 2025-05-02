"""Module containing the Card class for the Brawl Stars memory card game."""
from dataclasses import dataclass
from typing import Optional, Tuple

import pygame


@dataclass
class Card:
    """A playing card in the memory game with Brawl Stars characters.
    
    Attributes:
        name: The name of the Brawl Stars character on the card.
        image_path: Path to the image file for the character.
        back_image_path: Path to the image file for card back.
        position: The (x, y) position of the card on the screen.
        size: The (width, height) dimensions of the card.
        flipped: Whether the card is currently flipped face up.
        matched: Whether this card has been matched with its pair.
    """
    name: str
    image_path: str
    back_image_path: str
    position: Tuple[int, int]
    size: Tuple[int, int] = (80, 120)
    flipped: bool = False
    matched: bool = False
    
    _front_image: Optional[pygame.Surface] = None
    _back_image: Optional[pygame.Surface] = None
    
    def __post_init__(self) -> None:
        """Initialize the card images after instance creation."""
        try:
            # Load the front image and scale it properly
            original_image = pygame.image.load(self.image_path)
            
            # Calculate the aspect ratio to maintain proportions
            original_width, original_height = original_image.get_size()
            target_width, target_height = self.size
            
            # Calculate new dimensions maintaining aspect ratio
            ratio = min(target_width / original_width, target_height / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            # Scale the image
            scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
            
            # Create a blank surface of the target size
            self._front_image = pygame.Surface(self.size, pygame.SRCALPHA)
            
            # Calculate position to center the image
            x_offset = (target_width - new_width) // 2
            y_offset = (target_height - new_height) // 2
            
            # Blit the scaled image onto the blank surface at the calculated position
            self._front_image.blit(scaled_image, (x_offset, y_offset))
            
            # Load and scale the back image
            self._back_image = pygame.image.load(self.back_image_path)
            self._back_image = pygame.transform.scale(self._back_image, self.size)
            
        except pygame.error as e:
            print(f"Error loading image {self.image_path}: {e}")
            # Create a fallback image
            self._create_fallback_image()
    
    def _create_fallback_image(self) -> None:
        """Create a fallback image if the original image cannot be loaded."""
        # Create a surface for the front image
        self._front_image = pygame.Surface(self.size, pygame.SRCALPHA)
        self._front_image.fill((200, 200, 200))  # Light gray background
        
        # Add a colored rectangle
        color = (
            (hash(self.name) % 200) + 55,  # R: 55-255
            ((hash(self.name) * 2) % 200) + 55,  # G: 55-255
            ((hash(self.name) * 3) % 200) + 55,  # B: 55-255
        )
        pygame.draw.rect(self._front_image, color, pygame.Rect(5, 5, self.size[0]-10, self.size[1]-10))
        
        # Add the character name
        font = pygame.font.SysFont("Arial", 18)
        text_surface = font.render(self.name[:8], True, (0, 0, 0))  # Limit name length
        text_rect = text_surface.get_rect(center=(self.size[0]//2, self.size[1]//2))
        self._front_image.blit(text_surface, text_rect)
        
        # Add border
        pygame.draw.rect(self._front_image, (0, 0, 0), pygame.Rect(0, 0, self.size[0], self.size[1]), 2)
        
        # Create a back image too (in case it's also missing)
        self._back_image = pygame.Surface(self.size)
        self._back_image.fill((50, 50, 200))  # Blue background
        pygame.draw.rect(self._back_image, (255, 255, 255), pygame.Rect(0, 0, self.size[0], self.size[1]), 2)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the card on the screen.
        
        Args:
            screen: The Pygame surface to draw on.
        """
        if self.matched:
            # Draw a faded version if the card is matched
            image = self._front_image.copy()
            image.set_alpha(128)  # Semi-transparent
            screen.blit(image, self.position)
        elif self.flipped:
            screen.blit(self._front_image, self.position)
        else:
            screen.blit(self._back_image, self.position)
    
    def flip(self) -> None:
        """Flip the card over."""
        if not self.matched:  # Only allow flipping if not already matched
            self.flipped = not self.flipped
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """Check if the given point is within the card's boundaries.
        
        Args:
            point: The (x, y) coordinates to check.
        
        Returns:
            True if the point is within the card, False otherwise.
        """
        x, y = point
        card_x, card_y = self.position
        card_width, card_height = self.size
        
        return (card_x <= x <= card_x + card_width and 
                card_y <= y <= card_y + card_height)
