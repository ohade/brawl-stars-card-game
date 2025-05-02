"""Script to create a Brawl Stars themed card back image."""
import os
import pygame

def create_card_back(output_path, size=(150, 200)):
    """Create a Brawl Stars themed card back image.
    
    Args:
        output_path: Path to save the card back image.
        size: Size of the card back image.
    """
    # Initialize pygame
    pygame.init()
    
    # Create surface
    surface = pygame.Surface(size)
    
    # Fill with Brawl Stars blue color
    surface.fill((27, 67, 186))  # Brawl Stars blue
    
    # Add star in the center
    star_color = (255, 230, 0)  # Bright yellow
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Draw a simple star shape
    star_points = [
        (center_x, center_y - 20),  # Top point
        (center_x + 7, center_y - 7),
        (center_x + 20, center_y - 5),  # Right top
        (center_x + 10, center_y + 7),
        (center_x + 15, center_y + 20),  # Right bottom
        (center_x, center_y + 15),
        (center_x - 15, center_y + 20),  # Left bottom
        (center_x - 10, center_y + 7),
        (center_x - 20, center_y - 5),  # Left top
        (center_x - 7, center_y - 7),
    ]
    pygame.draw.polygon(surface, star_color, star_points)
    
    # Add border
    pygame.draw.rect(surface, (255, 204, 0), pygame.Rect(0, 0, size[0], size[1]), 3)
    
    # Add "BS" text in the center
    font = pygame.font.SysFont("Arial", 24, bold=True)
    text_surface = font.render("BS", True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, text_rect)
    
    # Save the image
    pygame.image.save(surface, output_path)
    
if __name__ == "__main__":
    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "assets", "images", "card_back.png")
    
    # Create the card back image
    create_card_back(output_path)
    print(f"Created card back image at: {output_path}")
