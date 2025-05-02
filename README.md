# Brawl Stars Memory Card Game

A Python-based memory card game featuring Brawl Stars characters, implemented using Pygame.

## Features

- Classic memory card matching gameplay
- Brawl Stars character-themed cards
- Score tracking and timing
- Game statistics (attempts, completion time)
- Simple and intuitive interface

## Requirements

- Python 3.6+
- Pygame 2.6.1+

## Installation

1. Clone or download this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:

```bash
python -m src.main
```

2. Click on cards to flip them over
3. Find matching pairs of Brawl Stars characters
4. Match all pairs to win the game
5. Press 'R' to restart after completing the game
6. Press 'ESC' to exit the game

## Customization

The game creates placeholder images by default. For a better experience:

1. Replace the placeholder images in the `assets/images` directory with actual Brawl Stars character images
2. The image filenames should match the character names (lowercase, spaces replaced with underscores)
   - Example: `shelly.png`, `el_primo.png`, etc.

## Future Enhancements

- Sound effects and background music
- Difficulty levels (more cards, faster card flipping)
- Animations for card flipping
- Leaderboard to track best scores
- More Brawl Stars-specific themes and mechanics
